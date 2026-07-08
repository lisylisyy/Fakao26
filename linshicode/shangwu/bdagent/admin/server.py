"""bdagent 生产群管理后台。

http://127.0.0.1:8898 —— 左侧机器人所在的群，右侧聊天记录；
每群可配：总开关 / 消息收集模式 / 被@回复 / 秒答FAQ / 无人回复安抚(时长) /
成员角色标注(技术·达人运营·商务对接运营)。
设置写进 SQLite，机器人进程实时读，改完立即生效，不用重启机器人。

启动(独立进程，和 main.py / bot/server.py 互不依赖)：
    .venv\\Scripts\\python.exe admin\\server.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn  # noqa: E402
from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402

import feishu  # noqa: E402
import storage  # noqa: E402
import sync_history  # noqa: E402

app = FastAPI(title="bdagent 后台")
STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/groups")
def list_groups():
    groups = []
    for chat in feishu.list_bot_chats():
        history = storage.get_chat_history(chat["chat_id"], limit=1)
        groups.append(
            {
                **chat,
                "settings": storage.get_group_settings(chat["chat_id"]),
                "last_message": history[-1] if history else None,
            }
        )
    return {"groups": groups, "roles": list(storage.ROSTER_ROLES)}


@app.get("/api/groups/{chat_id}")
def group_detail(chat_id: str):
    # 成员的身份按当前名册自动解析(不再逐群手标)：命中名册=淋浪自家人+职务，否则客户
    by_open_id, by_name = storage.roster_maps()
    members = feishu.get_chat_members(chat_id)
    for member in members:
        entry = storage.match_roster(member["open_id"], member["name"], by_open_id, by_name)
        member["role"] = (entry.get("role") or "") if entry else ""
        member["is_linlang"] = entry is not None
    return {
        "chat_id": chat_id,
        "name": feishu.get_chat_name(chat_id),
        "settings": storage.get_group_settings(chat_id),
        "members": members,
        "history": storage.get_chat_history(chat_id),
    }


@app.get("/api/groups/{chat_id}/history")
def group_history(chat_id: str):
    """只回聊天记录——给5秒轮询用，不去飞书重拉成员(省API+不打断成员面板)。"""
    return {"history": storage.get_chat_history(chat_id)}


@app.put("/api/groups/{chat_id}/settings")
def put_settings(chat_id: str, changes: dict):
    if "collection_mode" in changes and changes["collection_mode"] not in ("proactive", "silent"):
        raise HTTPException(400, "collection_mode 只能是 proactive 或 silent")
    if "reminder_minutes" in changes:
        try:
            minutes = int(changes["reminder_minutes"])
        except (TypeError, ValueError):
            raise HTTPException(400, "reminder_minutes 必须是整数")
        if not 1 <= minutes <= 60 * 24:
            raise HTTPException(400, "reminder_minutes 取值 1 ~ 1440 分钟")
        changes["reminder_minutes"] = minutes
    return {"settings": storage.update_group_settings(chat_id, changes)}


@app.post("/api/groups/{chat_id}/sync")
def sync_group(chat_id: str, body: dict = None):
    """从飞书拉取历史消息入库(断点重传)。full=True 从头全量。"""
    full = bool((body or {}).get("full"))
    result = sync_history.sync_chat_history(chat_id, full=full)
    return {"ok": True, **result, "history": storage.get_chat_history(chat_id)}


# ---- 淋浪人员名册（全局）----

@app.get("/api/roster")
def get_roster():
    return {"roster": storage.list_roster(), "roles": list(storage.ROSTER_ROLES)}


@app.put("/api/roster")
def put_roster(body: dict):
    name = (body or {}).get("name") or ""
    role = (body or {}).get("role") or ""
    if not name.strip():
        raise HTTPException(400, "姓名不能为空")
    if role and role not in storage.ROSTER_ROLES:
        raise HTTPException(400, f"职务只能是 {'/'.join(storage.ROSTER_ROLES)}")
    storage.upsert_roster(name.strip(), role, open_id=(body or {}).get("open_id"))
    return {"ok": True, "roster": storage.list_roster()}


@app.delete("/api/roster/{name}")
def del_roster(name: str):
    storage.delete_roster(name)
    return {"ok": True, "roster": storage.list_roster()}


if __name__ == "__main__":
    storage.init_db()
    uvicorn.run(app, host="127.0.0.1", port=8898)
