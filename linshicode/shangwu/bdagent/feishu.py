import json
import threading

import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    CreateMessageRequest,
    CreateMessageRequestBody,
    GetChatMembersRequest,
    ListChatRequest,
)

from config import APP_ID, APP_SECRET

client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()

# 全局串行化所有飞书 API 调用。lark SDK 的 token 缓存(LocalCache.get)过期清理是
# 无锁的 check-then-del，多线程(ws事件循环/bitable同步/watcher)同刻取过期 token 时
# 第二个 del 会抛 KeyError。商务群调用量很小，全局锁串行化代价可忽略，换来彻底消除竞态。
# bitable.py 直接调 client 的地方也 import 这把锁。
lark_lock = threading.RLock()

_member_name_cache: dict = {}  # (chat_id, open_id) -> name


def _fetch_members(chat_id: str) -> list:
    """拉取群成员并更新姓名缓存，返回本次拉到的全部 [{open_id, name}]。
    该接口默认每页 20 人，必须翻页——不然大群里排在后面的员工在后台看不到、
    标不了角色，发言会被误判成客户触发安抚。"""
    members = []
    page_token = None
    try:
        while True:
            builder = (
                GetChatMembersRequest.builder()
                .chat_id(chat_id)
                .member_id_type("open_id")
                .page_size(100)
            )
            if page_token:
                builder = builder.page_token(page_token)
            with lark_lock:
                resp = client.im.v1.chat_members.get(builder.build())
            if not resp.success():
                lark.logger.error(f"fetch chat members failed: code={resp.code} msg={resp.msg}")
                break
            for member in resp.data.items or []:
                _member_name_cache[(chat_id, member.member_id)] = member.name or ""
                members.append({"open_id": member.member_id, "name": member.name or ""})
            if not resp.data.has_more:
                break
            page_token = resp.data.page_token
    except Exception as exc:
        lark.logger.error(f"fetch chat members failed: {exc}")
    return members


def get_member_name(chat_id: str, open_id: str) -> str:
    """查群成员姓名，用于回复时称呼对方。查不到(权限/私聊/离群)返回空字符串。"""
    if not chat_id or not open_id:
        return ""
    key = (chat_id, open_id)
    if key not in _member_name_cache:
        _fetch_members(chat_id)
    return _member_name_cache.get(key, "")


def get_chat_members(chat_id: str) -> list:
    """群成员列表 [{open_id, name}]，每次调用都重新拉取(后台成员视图用)。"""
    return _fetch_members(chat_id)


def find_member_open_id(chat_id: str, name: str) -> str:
    """按姓名反查群成员 open_id，用于在消息里 @ 某人。不在群里/查不到返回空字符串。"""
    if not chat_id or not name:
        return ""

    def _scan() -> str:
        # 快照一份再遍历：get_member_name/_fetch_members 可能在别的线程往缓存里插入，
        # 直接迭代原 dict 会 RuntimeError: dictionary changed size during iteration。
        for (cid, oid), member_name in list(_member_name_cache.items()):
            if cid == chat_id and member_name == name:
                return oid
        return ""

    open_id = _scan()
    if open_id:
        return open_id
    _fetch_members(chat_id)  # 缓存没有再拉一次：对方可能是后进群的
    return _scan()


_chat_name_cache: dict = {}  # chat_id -> 群名


def list_bot_chats() -> list:
    """机器人所在的所有群，[{chat_id, name}]。失败返回空列表(只记日志)。"""
    chats = []
    page_token = None
    try:
        while True:
            builder = ListChatRequest.builder().page_size(100)
            if page_token:
                builder = builder.page_token(page_token)
            with lark_lock:
                resp = client.im.v1.chat.list(builder.build())
            if not resp.success():
                lark.logger.error(f"list chats failed: code={resp.code} msg={resp.msg}")
                break
            for item in resp.data.items or []:
                chats.append({"chat_id": item.chat_id, "name": item.name or "(未命名群)"})
                _chat_name_cache[item.chat_id] = item.name or ""
            if not resp.data.has_more:
                break
            page_token = resp.data.page_token
    except Exception as exc:
        lark.logger.error(f"list chats failed: {exc}")
    return chats


def get_chat_name(chat_id: str) -> str:
    """查群名(私信提醒里注明是哪个群)。查不到返回空字符串。"""
    if chat_id not in _chat_name_cache:
        list_bot_chats()
    return _chat_name_cache.get(chat_id, "")


def send_text_to_user(open_id: str, text: str) -> bool:
    """给个人发私信(机器人单聊)。对方不在应用可用范围内会失败，只记日志。"""
    req = (
        CreateMessageRequest.builder()
        .receive_id_type("open_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(open_id)
            .msg_type("text")
            .content(json.dumps({"text": text}))
            .build()
        )
        .build()
    )
    with lark_lock:
        resp = client.im.v1.message.create(req)
    if not resp.success():
        lark.logger.error(f"send_text_to_user failed: code={resp.code} msg={resp.msg}")
        return ""
    return (resp.data.message_id if resp.data else "") or "sent"


def send_text(chat_id: str, text: str) -> str:
    req = (
        CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("text")
            .content(json.dumps({"text": text}))
            .build()
        )
        .build()
    )
    with lark_lock:
        resp = client.im.v1.message.create(req)
    if not resp.success():
        lark.logger.error(f"send_text failed: code={resp.code} msg={resp.msg} chat_id={chat_id}")
        return ""
    # 返回真实 message_id(供入库去重：同一条消息历史同步拉回来时不重复插)。仍是真值，
    # 调用方 `if send_text(...)` 判断不受影响；发失败返回空串(假值)。
    return (resp.data.message_id if resp.data else "") or "sent"


def send_card(chat_id: str, card: dict) -> str:
    req = (
        CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("interactive")
            .content(json.dumps(card))
            .build()
        )
        .build()
    )
    with lark_lock:
        resp = client.im.v1.message.create(req)
    if not resp.success():
        lark.logger.error(f"send_card failed: code={resp.code} msg={resp.msg} chat_id={chat_id}")
        return ""
    return (resp.data.message_id if resp.data else "") or "sent"
