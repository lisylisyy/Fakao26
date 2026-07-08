import contextlib
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import lark_oapi as lark  # noqa: E402
from lark_oapi.event.callback.model.p2_card_action_trigger import P2CardActionTrigger  # noqa: E402

import handlers  # noqa: E402  (bdagent 根目录下的真实业务逻辑，模拟器直接复用，不重新实现)
import storage  # noqa: E402
from cards import FORM_FIELDS, SUBMIT_ACTION_NAME  # noqa: E402
from config import TEST_GROUP_CHAT_ID  # noqa: E402

from bot.kehu.poster import post_customer_message  # noqa: E402
from bot.kehu.persona import generate_backstory, generate_customer_reply  # noqa: E402
from bot.yunying.poster import post_ops_message  # noqa: E402
from bot.yunying.persona import OPS_PERSONA_NAME, generate_ops_reply  # noqa: E402

SIM_CHAT_ID = "sim_chat"  # TEST_GROUP_CHAT_ID 没配置时的占位 chat_id，走假 webhook 兜底
SIM_SENDER_OPEN_ID = "ou_sim_customer"

# 三方模型：客户(kehu人设)和运营(yunying人设，模拟真人商务)是对话双方，
# bdagent(真实决策代码)是旁听的第三方助理——每条消息都喂给它，它自己决定弹卡/接话/沉默。
ROLE_CUSTOMER = "客户"
ROLE_OPS = "运营"
ROLE_BOT = "机器人"

AUTO_CHAT_MAX_TURNS = 20  # 安全上限：忘了点停止也不会一直烧 API
AUTO_CHAT_DELAY_SECONDS = 2.5  # 每轮之间停顿一下，看起来像真人聊天，也给 LLM 调用留余量

_auto_chat_stop_events: dict = {}  # session_id -> threading.Event，进程内存registry


def _bdagent_uses_real_api() -> bool:
    # 配了真实测试群 chat_id，bdagent 就用真实身份直接发(真实卡片、真实消息)；
    # 没配就退回旧的"打桩截获+webhook转发"兜底方案。运营人设不受影响，
    # 它永远走 yunying webhook 发言。
    return bool(TEST_GROUP_CHAT_ID)


def _bdagent_chat_id() -> str:
    return TEST_GROUP_CHAT_ID or SIM_CHAT_ID


def _fake_card_action_event(form_value: dict, chat_id: str) -> P2CardActionTrigger:
    payload = {
        "event": {
            "operator": {"open_id": SIM_SENDER_OPEN_ID},
            "action": {"name": SUBMIT_ACTION_NAME, "form_value": form_value},
            "context": {"open_chat_id": chat_id},
        }
    }
    return P2CardActionTrigger(payload)


@contextlib.contextmanager
def _capture_bdagent_output(sink: list):
    # 只有没配真实测试群时才用：打桩截获 bdagent 本该发的内容，改由 yunying webhook
    # 加前缀转发进可视化群，避免拿假 chat_id 去打真实飞书 API(会直接报错)。
    original_send_text = handlers.send_text
    original_send_card = handlers.send_card

    def fake_send_text(chat_id, text):
        sink.append(("text", text))
        return True  # 和真实 send_text 的返回语义一致，"发送成功"

    def fake_send_card(chat_id, card):
        sink.append(("card", card))
        return True

    handlers.send_text = fake_send_text
    handlers.send_card = fake_send_card
    try:
        yield
    finally:
        handlers.send_text = original_send_text
        handlers.send_card = original_send_card


def _post_captured_as_bot(captured: list) -> None:
    # 兜底模式下 bdagent 没有自己的发声通道，借 yunying webhook 加前缀可视化。
    for kind, content in captured:
        if kind == "card":
            post_ops_message("[淋浪商务机器人] (发来一张客户信息登记表单)")
        else:
            post_ops_message(f"[淋浪商务机器人] {content}")


def _sim_settings() -> dict:
    # 训练台用默认设置+打开"秒答FAQ"：训练要覆盖机器人的全部能力，
    # 不跟随生产群在后台的开关(生产 instant_faq 默认关)。
    settings = storage.get_group_settings("__sim__")
    settings["instant_faq"] = 1
    return settings


def _bdagent_observe(session_id: str, text: str, sender_name: str = "") -> None:
    # 把一条(客户或运营的)消息喂给 bdagent 真实决策代码旁听——它自己决定
    # 主动弹卡、被点名接话、还是保持沉默。消息本身调用方已经记录过。
    addressed = handlers.mentions_bot(text)
    if _bdagent_uses_real_api():
        handlers.decide_and_send(
            session_id, TEST_GROUP_CHAT_ID, text,
            sender_name=sender_name, addressed=addressed, settings=_sim_settings(),
        )
        return
    captured = []
    with _capture_bdagent_output(captured):
        handlers.decide_and_send(
            session_id, SIM_CHAT_ID, text,
            sender_name=sender_name, addressed=addressed, settings=_sim_settings(),
        )
    _post_captured_as_bot(captured)


def _submit_form_from_backstory(session_id: str, backstory: dict) -> None:
    # 表单字段清单以 cards.FORM_FIELDS 为准：卡片加字段这里自动跟上
    form_value = {name: backstory.get(name, "") for name, _label, _ph in FORM_FIELDS}
    event = _fake_card_action_event(form_value, _bdagent_chat_id())
    if _bdagent_uses_real_api():
        handlers.on_card_action(event, is_simulated=True, session_id=session_id)
        return
    captured = []
    with _capture_bdagent_output(captured):
        handlers.on_card_action(event, is_simulated=True, session_id=session_id)
    _post_captured_as_bot(captured)


def new_session(hint: str = "") -> dict:
    session_id = storage.create_session(SIM_CHAT_ID, hint=hint, is_simulated=True)
    backstory = generate_backstory(hint)
    storage.set_session_backstory(session_id, backstory)
    intro = f"[模拟客户上线] {backstory.get('company', '')} · {backstory.get('contact', '')}"
    post_customer_message(intro)
    storage.append_message(session_id, "system", intro)
    return storage.get_session(session_id)


def end_session(session_id: str) -> None:
    stop_auto_chat(session_id)
    storage.end_session(session_id)


def start_auto_chat(session_id: str) -> dict:
    session = storage.get_session(session_id)
    if session is None:
        raise ValueError(f"session not found: {session_id}")
    if session["status"] != "active":
        raise ValueError("session is not active")
    if session_id in _auto_chat_stop_events:
        return session  # 已经在跑了，不重复起线程

    stop_event = threading.Event()
    _auto_chat_stop_events[session_id] = stop_event
    storage.set_auto_chat(session_id, True)
    thread = threading.Thread(target=_auto_chat_loop, args=(session_id, stop_event), daemon=True)
    thread.start()
    return storage.get_session(session_id)


def stop_auto_chat(session_id: str) -> dict:
    stop_event = _auto_chat_stop_events.pop(session_id, None)
    if stop_event is not None:
        stop_event.set()
    storage.set_auto_chat(session_id, False)
    session = storage.get_session(session_id)
    return session if session else {}


def _auto_chat_loop(session_id: str, stop_event: threading.Event) -> None:
    # 客户/运营两个人设严格轮流说话；bdagent 不占轮次，它在每条消息落地后
    # 由 _bdagent_observe 自动反应(藏在 ai_reply 里)。不管上一轮对方有没有真的
    # 开口，都往下走一轮，避免卡在"同一个角色反复不产出"的死循环里。
    next_role = ROLE_CUSTOMER
    try:
        for _ in range(AUTO_CHAT_MAX_TURNS):
            if stop_event.is_set():
                return
            session = storage.get_session(session_id)
            if session is None or session["status"] != "active":
                return
            try:
                ai_reply(session_id, next_role, _from_auto_chat=True)
            except Exception as exc:
                lark.logger.error(f"auto_chat ai_reply failed session={session_id}: {exc}")
                return
            next_role = ROLE_OPS if next_role == ROLE_CUSTOMER else ROLE_CUSTOMER
            if stop_event.wait(AUTO_CHAT_DELAY_SECONDS):
                return
    finally:
        _auto_chat_stop_events.pop(session_id, None)
        storage.set_auto_chat(session_id, False)


def list_sessions() -> list:
    return storage.list_sessions(is_simulated=True)


def get_session(session_id: str) -> dict:
    return storage.get_session(session_id)


def _require_active(session_id: str, *, allow_during_auto_chat: bool = False) -> dict:
    # 手动发言/AI单轮的服务端守卫：前端靠2秒轮询禁用控件，挡不住第二个标签页
    # 或并发请求——已结束的会话不能再写，自动聊天跑着的时候外部入口要拒绝，
    # 否则会和循环线程抢同一个 pending_card 快照，把表单提交两次。
    session = storage.get_session(session_id)
    if session is None:
        raise ValueError(f"session not found: {session_id}")
    if session["status"] != "active":
        raise ValueError("session is not active")
    if session["auto_chat"] and not allow_during_auto_chat:
        raise ValueError("auto chat is running, stop it first")
    return session


def manual_message(session_id: str, role: str, text: str) -> dict:
    session = _require_active(session_id)

    if role == ROLE_CUSTOMER:
        storage.append_message(session_id, ROLE_CUSTOMER, text)
        post_customer_message(text)
        contact = (session["backstory"] or {}).get("contact", "")
        _bdagent_observe(session_id, text, sender_name=contact)
        if session["pending_card"]:
            _submit_form_from_backstory(session_id, session["backstory"])
    elif role == ROLE_OPS:
        # 人工扮演运营真人发言(不是 bdagent)：走 yunying webhook 可视化，同样喂给 bdagent 旁听。
        storage.append_message(session_id, ROLE_OPS, text)
        post_ops_message(text)
        _bdagent_observe(session_id, text, sender_name=OPS_PERSONA_NAME)
    else:
        raise ValueError(f"unknown role: {role}")

    return storage.get_session(session_id)


def ai_reply(session_id: str, role: str, *, _from_auto_chat: bool = False) -> dict:
    session = _require_active(session_id, allow_during_auto_chat=_from_auto_chat)

    history = [{"speaker": h["speaker"], "text": h["text"]} for h in session["history"]]
    real_turns = [h for h in history if h["speaker"] in (ROLE_CUSTOMER, ROLE_OPS, ROLE_BOT)]

    if role == ROLE_CUSTOMER:
        if session["pending_card"]:
            event = "机器人助理发来了信息登记表单，你选择配合填写"
        elif real_turns and real_turns[-1]["speaker"] == ROLE_CUSTOMER:
            # 上一条已经是你自己说的，对方还没回应——明确告诉模型不要编造对方的回复，
            # 只能继续以客户口吻补充/追问。
            event = "对方还没有回应你上一条消息，不要替对方说话或编造对方的回复"
        else:
            event = ""
        msg = generate_customer_reply(session["backstory"], history, event=event)
        storage.append_message(session_id, ROLE_CUSTOMER, msg)
        post_customer_message(msg)
        contact = (session["backstory"] or {}).get("contact", "")
        _bdagent_observe(session_id, msg, sender_name=contact)
        # 注意这里读的是本条消息之前的快照：表单是之前就在等的才填，
        # 如果是刚刚这条消息才触发弹卡，下一轮客户再填(和真人节奏一致)。
        if session["pending_card"]:
            _submit_form_from_backstory(session_id, session["backstory"])

    elif role == ROLE_OPS:
        if session["pending_card"]:
            event = "机器人助理刚给客户发了信息登记表单，你自然地引导客户填一下即可，不要再逐项要信息"
        elif real_turns and real_turns[-1]["speaker"] == ROLE_OPS:
            event = "对方还没有回应你上一条消息，不要替对方说话，耐心补充一句或换个说法"
        else:
            event = ""
        msg = generate_ops_reply(history, event=event)
        storage.append_message(session_id, ROLE_OPS, msg)
        post_ops_message(msg)
        _bdagent_observe(session_id, msg, sender_name=OPS_PERSONA_NAME)

    else:
        raise ValueError(f"unknown role: {role}")

    return storage.get_session(session_id)
