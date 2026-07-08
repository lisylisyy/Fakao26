import json
import re
import time
from collections import OrderedDict

from lark_oapi.api.im.v1 import P2ImMessageReceiveV1
from lark_oapi.event.callback.model.p2_card_action_trigger import (
    P2CardActionTrigger,
    P2CardActionTriggerResponse,
)

from bitable import sync_client_async
from cards import SUBMIT_ACTION_NAME, client_info_card
from config import MEETING_CONFIRMER_NAME
from feishu import find_member_open_id, get_member_name, send_card, send_text
from llm import faq_auto_reply, generate_bot_reply, wants_client_card
from storage import (
    append_message,
    clear_awaiting_reply,
    get_group_settings,
    get_or_create_session_by_chat_id,
    get_session,
    mark_awaiting_answered,
    mark_awaiting_reply,
    match_roster,
    save_client,
    set_client_recorded,
    set_pending_card,
    try_consume_pending_card,
)

_MENTION_TOKEN_RE = re.compile(r"@_user_\d+")  # 整词匹配一个@占位符，不含尾随空格
_TRIGGER_KEYWORDS = ("客户", "录入")
_BOT_NAME_HINTS = ("机器人",)  # "淋浪商务机器人"也包含"机器人"，一个提示词就够


_seen_event_ids = OrderedDict()  # 事件去重：飞书"至少送达一次"，处理慢会重发同一事件
_SEEN_EVENTS_MAX = 500


def _is_duplicate_event(event_id: str) -> bool:
    """同一 event_id 第二次出现返回 True(该事件已处理过，直接丢弃)。
    实测：LLM 回复耗时几秒时飞书会重投消息事件，机器人同一句话回两遍。"""
    if not event_id:
        return False
    if event_id in _seen_event_ids:
        return True
    _seen_event_ids[event_id] = True
    while len(_seen_event_ids) > _SEEN_EVENTS_MAX:
        _seen_event_ids.popitem(last=False)
    return False


def _collapse_ws(s: str) -> str:
    return re.sub(r"\s{2,}", " ", s).strip()


def _extract_texts(content_json: str, mentions=None) -> tuple:
    """把飞书消息正文拆成两份返回 (display, clean)：
    display —— @占位符 @_user_N 还原成可读的 "@姓名"，存历史/私信引用用(和飞书界面一致，
               事后能看出@了谁)；
    clean  —— @提及整体删掉，做关键词命中/意图判断/回复生成等决策用。二者必须分开：
               被@的人昵称里可能带 "客户"/"录入"/"机器人" 这些字，若混进决策文本会误触发
               弹卡/接话(如@"客户对接-小李"→命中"客户"→误发登记表单)。
    整词匹配 @_user_\\d+ 避免 @_user_1 误伤 @_user_11(子串)。"""
    content = json.loads(content_json or "{}")
    text = content.get("text", "")
    name_by_key = {m.key: m.name for m in (mentions or []) if m.key and m.name}
    display = _MENTION_TOKEN_RE.sub(
        lambda mo: f"@{name_by_key[mo.group(0)]}" if mo.group(0) in name_by_key else "", text
    )
    clean = _MENTION_TOKEN_RE.sub("", text)
    return _collapse_ws(display), _collapse_ws(clean)


def mentions_bot(text: str) -> bool:
    """这句话有没有点到机器人的名——训练台旁听模式用它判断要不要接话。"""
    return any(hint in text for hint in _BOT_NAME_HINTS)


def _is_bot_addressed(message) -> bool:
    """生产消息里机器人是不是真被叫到了：私聊永远算；群里看 mentions 里有没有它。
    开了"接收群聊中所有消息"权限后，机器人会收到每一条群消息——绝不能再默认
    都当成@它(否则见句就回)。飞书@的可见文本是占位符，真名在 mentions 数组里。"""
    if getattr(message, "chat_type", None) == "p2p":
        return True
    for mention in (message.mentions or []):
        if mention.name and any(hint in mention.name for hint in _BOT_NAME_HINTS):
            return True
    return False


def decide_and_send(
    session_id: str,
    chat_id: str,
    text: str,
    sender_name: str = "",
    addressed: bool = False,
    settings: dict = None,
) -> None:
    # bdagent 的"反应"逻辑：像旁听的助理——不负责记录消息(调用方已经记过)，
    # 检测到新客户录入时机就主动发表单卡片；闲聊只在被 @/点名(addressed)时才接一句，
    # 不抢运营的话。生产事件和训练台旁听共用这一个函数，保证测的是同一套决策代码。
    # 各分支受后台的按群设置(group_settings)门控，后台改完立即生效。
    settings = settings or get_group_settings(chat_id)
    if not settings["bot_enabled"]:
        return  # 这个群的机器人被后台关了：只记录(调用方已记)，不作任何反应

    session = get_session(session_id)
    # 主动问询模式才弹卡；且这个会话已经有表单在等着填、或已经录过客户了就不再重复弹——
    # 不然客户后面随口提一句预算/需求，会被重复当成新客户触发。
    can_send_card = settings["collection_mode"] == "proactive" and not (
        session and (session["pending_card"] or session["client_recorded"])
    )

    # 关键词命中走快速路径，省一次模型调用；不命中再交给 DeepSeek 判断更宽泛的表述
    if can_send_card and (
        any(keyword in text for keyword in _TRIGGER_KEYWORDS) or wants_client_card(text)
    ):
        # 发送成功才置 pending——发失败就置位的话，群里没有卡可填，
        # pending_card 永远清不掉，这个群的录入功能就死锁了。
        mid = send_card(chat_id, client_info_card())
        if mid:
            append_message(session_id, "机器人", "(发来一张客户信息登记表单)", is_bot=True,
                           feishu_message_id=mid)
            set_pending_card(session_id, True)
        return

    history = session["history"] if session else []

    if not (addressed or mentions_bot(text)):
        # 没人叫它：开了"秒答FAQ"的群、且是客户在问语料库覆盖的常见问题才接话，
        # 其余保持沉默旁听。运营的发言不抢答(调用方刚记录的这条就是 history 末尾)。
        # 注意：生产群目前只收得到 @机器人 的消息，此分支要等开通
        # "接收群聊中所有消息"权限后才会在生产生效；训练台旁听模式已生效。
        if not settings["instant_faq"]:
            return
        if history and history[-1]["speaker"] != "客户":
            return
        reply = faq_auto_reply(text, history=history)
        mid = send_text(chat_id, reply) if reply else ""
        if mid:
            append_message(session_id, "机器人", reply, is_bot=True, feishu_message_id=mid)
            mark_awaiting_answered(chat_id)  # 已即时答过，安抚时别复读同一答案
        return

    if not settings["reply_on_mention"]:
        return
    # 被点到名了：生成一句自然的回复(带称呼、口语化、按语料口径)，生成失败就保持沉默
    reply = generate_bot_reply(text, sender_name=sender_name, history=history)
    mid = send_text(chat_id, reply) if reply else ""
    if mid:
        append_message(session_id, "机器人", reply, is_bot=True, feishu_message_id=mid)
        mark_awaiting_answered(chat_id)


def on_message(data: P2ImMessageReceiveV1, *, session_id: str = None) -> None:
    if _is_duplicate_event(data.header.event_id if data.header else ""):
        return
    message = data.event.message
    chat_id = message.chat_id
    # display 带@姓名(存历史/私信引用)，clean 去掉@(做决策)——分开用，避免被@的人名里的字误触发
    display_text, clean_text = _extract_texts(message.content, message.mentions)

    sender = data.event.sender
    sender_open_id = sender.sender_id.open_id if sender and sender.sender_id else ""
    sender_name = get_member_name(chat_id, sender_open_id)

    # 生产场景没传 session_id：按 chat_id 找/建会话，一个真实飞书群一个会话；
    # 训练台场景会显式传自己的 session_id（同一个测试群里可以并存多个逻辑会话）。
    sid = session_id or get_or_create_session_by_chat_id(chat_id)
    settings = get_group_settings(chat_id)

    # 真·@到的人名(飞书 mention)——存下来供前端标蓝+下划线，区分手打的"@文字"
    mention_names = [m.name for m in (message.mentions or []) if m.name]
    # 命中淋浪名册=自家人(运营)，其余按客户对待。身份不冻结——存 open_id/name，
    # 读取时按当前名册现算(Approach B)，以后改名册所有历史自动跟着变。
    # (不在这里自动钉 open_id——先到先得可能把同名客户的 id 钉进员工行；
    #  钉 open_id 只在后台管理员给成员选职务时做，那时看到的是确定的本人。)
    staff = match_roster(sender_open_id, sender_name)
    inserted = append_message(
        sid, text=display_text, mentions=mention_names,
        sender_open_id=sender_open_id, sender_name=sender_name, is_bot=False,
        feishu_message_id=message.message_id,
        feishu_create_time=int(message.create_time) if message.create_time else None,
    )
    if not inserted:
        return  # 这条消息已入过库(飞书"至少一次"重投/进程重启后重放)——别重复计时和回复
    if staff:  # 自家人开口，解除"等客服回复"计时
        clear_awaiting_reply(chat_id)
    elif settings["reminder_enabled"]:  # 客户发言，且开了安抚才计时
        mark_awaiting_reply(chat_id, display_text, sender_name or sender_open_id, int(time.time()))

    # 只有机器人真被@到(或私聊)才算"点名"——开了全量消息权限后，群里每条消息都会进来，
    # 不能再默认都当@它。没被点名的消息交给 decide_and_send 里的沉默/秒答FAQ 分支处理。
    addressed = _is_bot_addressed(message) or mentions_bot(clean_text)
    decide_and_send(
        sid, chat_id, clean_text, sender_name=sender_name, addressed=addressed, settings=settings
    )


def _meeting_followup(chat_id: str) -> tuple:
    """录入完成后的拉会话术(语料库口径)。返回 (发送用文本, 存历史用纯文本, 真·@到的人名列表)。
    负责人在群里就用 <at> 真实@她(算真·@，历史里标蓝)；不在群里(或查不到)退化成纯文本@。"""
    ask = "基本情况已经了解，请问什么时间方便安排一个会议？时间以您方便为准～"
    if not MEETING_CONFIRMER_NAME:
        return ask, ask, []
    open_id = find_member_open_id(chat_id, MEETING_CONFIRMER_NAME)
    plain = f"{ask} @{MEETING_CONFIRMER_NAME} 麻烦跟进确认会议时间"
    if not open_id:
        return plain, plain, []  # 没真@到，是纯文本，不标蓝
    mention = f'<at user_id="{open_id}">{MEETING_CONFIRMER_NAME}</at>'
    return f"{ask} {mention} 麻烦跟进确认会议时间", plain, [MEETING_CONFIRMER_NAME]


def on_card_action(
    data: P2CardActionTrigger, *, is_simulated: bool = False, session_id: str = None
) -> P2CardActionTriggerResponse:
    action = data.event.action
    context = data.event.context
    operator = data.event.operator

    chat_id = context.open_chat_id if context else None
    submitted_by = operator.open_id if operator else ""
    sid = session_id or (get_or_create_session_by_chat_id(chat_id) if chat_id else None)

    if action and action.name == SUBMIT_ACTION_NAME:
        # 幂等保护：原子地消费掉 pending_card。同一张卡片被点第二次、或者群里
        # 残留的过期卡片被点，这里拿不到 pending 就直接拒绝，不会重复 INSERT。
        if sid and not try_consume_pending_card(sid):
            return P2CardActionTriggerResponse(
                {"toast": {"type": "info", "content": "这张表单已经处理过啦"}}
            )
        form = action.form_value or {}
        client_id = save_client(
            form, chat_id=chat_id or "", submitted_by=submitted_by, is_simulated=is_simulated
        )
        if sid:
            set_client_recorded(sid)
        # 机器人被后台停用的群("只记录不回复")：客户数据照常入库(不丢)，
        # 但不在群里发确认/拉会消息。训练台(is_simulated)不受此门控。
        bot_on = is_simulated or not chat_id or get_group_settings(chat_id)["bot_enabled"]
        if chat_id and bot_on:
            reply = f"已录入客户：{form.get('company') or '(未填写公司名称)'}"
            mid = send_text(chat_id, reply)
            if mid and sid:
                append_message(sid, "机器人", reply, is_bot=True, feishu_message_id=mid)
            # 语料库SOP：信息收齐后顺势推进拉会，@商务负责人确认时间。
            # client_recorded 幂等保证这条只会跟着首次录入发一次。
            meeting_text, meeting_plain, meeting_mentions = _meeting_followup(chat_id)
            meeting_mid = send_text(chat_id, meeting_text)
            if meeting_mid and sid:
                append_message(sid, "机器人", meeting_plain, mentions=meeting_mentions,
                               is_bot=True, feishu_message_id=meeting_mid)
        # 真实录入才同步多维表格《商务agent》；训练台的模拟数据只留在本地库。
        # 放在 send_text 之后再起线程：lark SDK 的 token 缓存过期清理无锁，
        # 两个线程同刻取 token 有极小概率抛 KeyError，错开就没有这个窗口。
        if not is_simulated:
            sync_client_async(client_id, form, chat_id=chat_id or "", submitted_by=submitted_by)
        return P2CardActionTriggerResponse(
            {"toast": {"type": "success", "content": "客户信息已保存"}}
        )

    return P2CardActionTriggerResponse({})
