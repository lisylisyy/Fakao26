"""无人回复安抚 watcher。

客户消息之后 X 分钟内没有任何"打了角色标签的员工"回复：
①群里发"XXX 正在飞快赶来"安抚 ②语料库能答的问题顺带按口径答
③私信提醒对应角色的同事(注明哪个群、哪条消息)。
每群一次性提醒(不轰炸)，员工一开口计时和提醒状态都清零。
开关和时长在后台按群配置，默认关。

依赖"接收群聊中所有消息"权限才能看到客户的普通发言；
权限没开之前生产群只有 @机器人 的消息会进入计时。
"""
import threading
import time

import lark_oapi as lark

from feishu import get_chat_members, get_chat_name, send_text, send_text_to_user
from llm import classify_question_role, faq_auto_reply
from storage import (
    append_message,
    get_group_settings,
    get_or_create_session_by_chat_id,
    list_awaiting_reply,
    mark_reminded,
    match_roster,
    roster_maps,
    unmark_reminded,
)

_CHECK_INTERVAL_SECONDS = 60


def _pick_person(chat_id: str, text: str) -> tuple:
    """挑要提醒的同事：在这个群里的淋浪自家人(名册匹配群成员)中，按问题对应职务挑，
    找不到就落商务对接运营，再不行任一自家人。群里没有名册里的人返回 (None, None)。"""
    by_open_id, by_name = roster_maps()
    staff = []
    for mem in get_chat_members(chat_id):
        entry = match_roster(mem["open_id"], mem["name"], by_open_id, by_name)
        if entry:
            staff.append((mem["open_id"], mem["name"], entry.get("role") or ""))
    if not staff:
        return None, None
    role_guess = classify_question_role(text)
    for want in (role_guess, "商务对接运营"):
        for oid, name, role in staff:
            if role == want:
                return oid, name
    return staff[0][0], staff[0][1]


def _format_wait(minutes: int) -> str:
    hours, mins = divmod(int(minutes), 60)
    if hours and mins:
        return f"{hours}小时{mins}分钟"
    if hours:
        return f"{hours}小时"
    return f"{mins}分钟"


def _soothe(entry: dict, settings: dict, now: int) -> None:
    chat_id = entry["chat_id"]
    awaiting_since = entry["awaiting_since"]
    text = entry["last_text"] or ""

    # 原子占位，且绑定到被检查的这次等待(awaiting_since)：员工刚回复清了计时、
    # 或客户追问新起了一轮，这里都拿不到，直接跳过——不会误消费别的等待。
    if not mark_reminded(chat_id, awaiting_since):
        return

    sid = get_or_create_session_by_chat_id(chat_id)
    open_id, name = _pick_person(chat_id, text)
    group_msg = (
        f"{name} 正在飞快赶来，稍等一下下～" if name else "商务同事正在飞快赶来，稍等一下下～"
    )
    # 群安抚是核心动作，发出去才算数：发送失败(限流/网络/token竞态)就回滚 reminded，
    # 下一轮重试，不让这次等待的提醒名额白白消耗掉。
    group_mid = send_text(chat_id, group_msg)
    if not group_mid:
        unmark_reminded(chat_id, awaiting_since)
        return
    append_message(sid, "机器人", group_msg, is_bot=True, feishu_message_id=group_mid)

    # 语料库能答的顺带按口径补一句——但机器人即时回复时已经答过的(answered)就别复读
    if not entry.get("answered"):
        faq = faq_auto_reply(text)
        faq_mid = send_text(chat_id, faq) if faq else ""
        if faq_mid:
            append_message(sid, "机器人", faq, is_bot=True, feishu_message_id=faq_mid)

    # 私信提醒对应同事，等待时长用真实值(不是阈值)，注明哪个群哪条消息
    if open_id:
        chat_name = get_chat_name(chat_id) or chat_id
        waited_min = max(1, (now - (awaiting_since or now)) // 60)
        dm = (
            f"【bdagent提醒】群「{chat_name}」有客户消息超过"
            f"{_format_wait(waited_min)}没人回复：\n"
            f"{entry['last_sender'] or '客户'}：{text}\n"
            "麻烦尽快去群里看看～"
        )
        send_text_to_user(open_id, dm)


def check_once(now: int = None) -> None:
    """扫一遍所有在等回复的群，到点的执行安抚。独立成函数方便测试。"""
    now = now or int(time.time())
    for entry in list_awaiting_reply():
        try:
            settings = get_group_settings(entry["chat_id"])
            if not (settings["bot_enabled"] and settings["reminder_enabled"]):
                continue
            waited = now - (entry["awaiting_since"] or now)
            if waited < settings["reminder_minutes"] * 60:
                continue
            _soothe(entry, settings, now)
        except Exception as exc:
            lark.logger.error(f"reply watcher failed chat={entry.get('chat_id')}: {exc}")


def start_watcher() -> None:
    def _loop():
        while True:
            time.sleep(_CHECK_INTERVAL_SECONDS)
            try:
                check_once()
            except Exception as exc:
                lark.logger.error(f"reply watcher cycle failed: {exc}")

    threading.Thread(target=_loop, daemon=True, name="reply-watcher").start()
