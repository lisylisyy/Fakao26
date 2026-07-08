"""从飞书拉群历史消息入库——断点重传。

和实时推送(handlers.on_message)互补：推送保证实时，这里负责补齐(掉线期间错过的、
机器人加群前的历史)。两边靠飞书 message_id 去重(INSERT OR IGNORE)，同一条只入库一次。

游标(chat_sync_state.last_create_time)是每个群的"版本号"：同步从游标之后续，
拉到哪推进到哪。每次都从游标所在那一秒起(start_time 精度到秒)，边界消息会重拉，
但 message_id 去重保证幂等、不会重复入库、也不会漏。
"""
import lark_oapi as lark
from lark_oapi.api.im.v1 import ListMessageRequest

import feishu
import handlers  # 复用 _extract_texts（@提及解析和实时推送完全一致）
import storage
from feishu import client, lark_lock

# 非文本消息在历史里存个占位符（原文在飞书，这里只记"发生过一条什么"）
_PLACEHOLDERS = {
    "interactive": "(卡片消息)", "image": "(图片)", "file": "(文件)",
    "audio": "(语音)", "media": "(视频)", "post": "(富文本消息)", "sticker": "(表情)",
    "share_chat": "(分享群名片)", "share_user": "(分享个人名片)",
}


def _msg_text(msg) -> str:
    if msg.msg_type == "text":
        display, _clean = handlers._extract_texts(
            msg.body.content if msg.body else "{}", msg.mentions
        )
        return display
    return _PLACEHOLDERS.get(msg.msg_type, f"({msg.msg_type})")


def sync_chat_history(chat_id: str, full: bool = False, dry_run: bool = False) -> dict:
    """拉取一个群的历史消息入库。
    full=True 从头拉(忽略游标)；dry_run=True 只统计+返回样本，不写库不推进游标。
    返回 {scanned, inserted, cursor, samples}。"""
    since_ms = 0 if (full or dry_run) else storage.get_sync_cursor(chat_id)
    sid = None if dry_run else storage.get_or_create_session_by_chat_id(chat_id)
    by_open_id, by_name = storage.roster_maps()
    # 群成员名字一次性拉好(open_id→name)，别每条消息都 get_member_name——
    # 离群成员永远缓存 miss，会导致每条历史消息都整群翻页拉一次，慢且易限流。
    name_by_oid = {m["open_id"]: m["name"] for m in feishu.get_chat_members(chat_id)}

    scanned = inserted = 0
    max_ct, max_mid = since_ms, None
    page_token = None
    samples = []
    try:
        while True:
            builder = (
                ListMessageRequest.builder()
                .container_id_type("chat").container_id(chat_id)
                .sort_type("ByCreateTimeAsc").page_size(50)
            )
            if since_ms:
                builder = builder.start_time(str(since_ms // 1000))  # start_time 单位是秒
            if page_token:
                builder = builder.page_token(page_token)
            with lark_lock:
                resp = client.im.v1.message.list(builder.build())
            if not resp.success():
                lark.logger.error(f"sync history failed chat={chat_id}: code={resp.code} msg={resp.msg}")
                break
            for msg in (resp.data.items or []):
                scanned += 1
                ct = int(msg.create_time) if msg.create_time else 0
                if ct > max_ct:
                    max_ct, max_mid = ct, msg.message_id
                if msg.msg_type == "system":  # 进群/退群通知等，跳过
                    continue
                sender = msg.sender
                is_bot = bool(sender and sender.sender_type == "app")
                open_id = (sender.id if sender else "") or ""
                name = "" if is_bot else name_by_oid.get(open_id, "")
                text = _msg_text(msg)
                mentions = [m.name for m in (msg.mentions or []) if m.name]
                if dry_run:
                    ident = storage.resolve_identity(
                        {"is_bot": is_bot, "sender_open_id": open_id, "sender_name": name, "speaker": None},
                        by_open_id, by_name,
                    )
                    if len(samples) < 30:
                        samples.append({"who": ident["who"], "speaker": ident["speaker"], "text": text[:40]})
                    continue
                if storage.append_message(
                    sid, speaker=("机器人" if is_bot else None), text=text, mentions=mentions,
                    sender_open_id=open_id, sender_name=name, is_bot=is_bot,
                    feishu_message_id=msg.message_id, feishu_create_time=ct,
                ):
                    inserted += 1
            if not resp.data.has_more:
                break
            page_token = resp.data.page_token
    except Exception as exc:
        lark.logger.error(f"sync history exception chat={chat_id}: {exc}")

    if not dry_run and max_ct > since_ms:
        storage.set_sync_cursor(chat_id, max_ct, max_mid)
    return {"scanned": scanned, "inserted": inserted, "cursor": max_ct, "samples": samples}


def catch_up_all() -> None:
    """机器人启动时追赶：对所有所在群从各自游标往后补一次(填掉线期间的缺口)。"""
    for chat in feishu.list_bot_chats():
        try:
            r = sync_chat_history(chat["chat_id"])
            if r["inserted"]:
                lark.logger.info(f"catch-up {chat['name']}: +{r['inserted']} 条")
        except Exception as exc:
            lark.logger.error(f"catch-up failed chat={chat.get('chat_id')}: {exc}")
