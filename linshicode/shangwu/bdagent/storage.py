import json
import sqlite3
import time
import uuid
from contextlib import closing

from config import DB_PATH

# SQLite 是 MVP 阶段的占位存储；"记录并沉淀客户知识库"最终要写公司数据库，
# 等拿到那边的连接信息后把这个模块换成对应的驱动即可，上层调用方式不用变。
_SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    contact TEXT,
    budget TEXT,
    need TEXT,
    brand TEXT,
    tk_link TEXT,
    shop_ready TEXT,
    sales_1k TEXT,
    commission TEXT,
    entity_coop TEXT,
    chat_id TEXT,
    submitted_by TEXT,
    is_simulated INTEGER DEFAULT 0,
    bitable_record_id TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    chat_id TEXT,
    is_simulated INTEGER DEFAULT 0,
    hint TEXT,
    backstory TEXT,
    status TEXT DEFAULT 'active',
    pending_card INTEGER DEFAULT 0,
    auto_chat INTEGER DEFAULT 0,
    client_recorded INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    ended_at TEXT
);

CREATE TABLE IF NOT EXISTS session_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    speaker TEXT,              -- 训练台/旧数据用；生产走 sender_open_id 在读取时按名册现算
    text TEXT,
    mentions TEXT,
    sender_open_id TEXT,       -- 生产真人消息的发送人 open_id（Approach B：读取时按当前名册解析身份）
    sender_name TEXT,          -- 发送人当时的显示名（快照，兜底显示）
    is_bot INTEGER DEFAULT 0,  -- 是不是机器人自己发的
    feishu_message_id TEXT,    -- 飞书消息唯一ID，推送/历史拉取共用它去重
    feishu_create_time INTEGER,-- 飞书消息创建时间(ms)，历史同步的游标
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 淋浪人员名册（全局，一次配好处处生效）：群成员命中名册=淋浪自家人，带职务
CREATE TABLE IF NOT EXISTS staff_roster (
    name TEXT PRIMARY KEY,
    role TEXT DEFAULT '',      -- 技术 / 达人运营 / 商务对接运营 / 其他
    open_id TEXT,              -- 第一次在群里匹配上后钉住，之后优先按它认(防重名)
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 每个群一条历史同步游标（"版本号"）：断点重传从这里续
CREATE TABLE IF NOT EXISTS chat_sync_state (
    chat_id TEXT PRIMARY KEY,
    last_create_time INTEGER DEFAULT 0,
    last_message_id TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS group_settings (
    chat_id TEXT PRIMARY KEY,
    bot_enabled INTEGER DEFAULT 1,
    collection_mode TEXT DEFAULT 'proactive',
    reply_on_mention INTEGER DEFAULT 1,
    instant_faq INTEGER DEFAULT 0,
    reminder_enabled INTEGER DEFAULT 0,
    reminder_minutes INTEGER DEFAULT 30,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS group_member_roles (
    chat_id TEXT,
    open_id TEXT,
    name TEXT,
    role TEXT DEFAULT '',
    PRIMARY KEY (chat_id, open_id)
);

CREATE TABLE IF NOT EXISTS reply_watch (
    chat_id TEXT PRIMARY KEY,
    awaiting_since INTEGER,
    last_text TEXT,
    last_sender TEXT,
    reminded INTEGER DEFAULT 0,
    answered INTEGER DEFAULT 0
);
"""


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.executescript(_SCHEMA)
        # 兼容在加这些字段之前就已经建过表的旧库文件
        for stmt in (
            "ALTER TABLE clients ADD COLUMN is_simulated INTEGER DEFAULT 0",
            "ALTER TABLE clients ADD COLUMN bitable_record_id TEXT",
            "ALTER TABLE clients ADD COLUMN brand TEXT",
            "ALTER TABLE clients ADD COLUMN tk_link TEXT",
            "ALTER TABLE clients ADD COLUMN shop_ready TEXT",
            "ALTER TABLE clients ADD COLUMN sales_1k TEXT",
            "ALTER TABLE clients ADD COLUMN commission TEXT",
            "ALTER TABLE clients ADD COLUMN entity_coop TEXT",
            "ALTER TABLE reply_watch ADD COLUMN answered INTEGER DEFAULT 0",
            "ALTER TABLE session_messages ADD COLUMN mentions TEXT",
            "ALTER TABLE session_messages ADD COLUMN sender_open_id TEXT",
            "ALTER TABLE session_messages ADD COLUMN sender_name TEXT",
            "ALTER TABLE session_messages ADD COLUMN is_bot INTEGER DEFAULT 0",
            "ALTER TABLE session_messages ADD COLUMN feishu_message_id TEXT",
            "ALTER TABLE session_messages ADD COLUMN feishu_create_time INTEGER",
            "ALTER TABLE sessions ADD COLUMN auto_chat INTEGER DEFAULT 0",
            "ALTER TABLE sessions ADD COLUMN client_recorded INTEGER DEFAULT 0",
        ):
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError:
                pass
        # 飞书消息ID唯一索引：推送和历史拉取靠 INSERT OR IGNORE 按它去重(NULL 不参与，训练台消息不冲突)
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_smsg_feishu_id "
            "ON session_messages(feishu_message_id) WHERE feishu_message_id IS NOT NULL"
        )
        # 一次性数据迁移(打标记防重复执行)：三方模型重构前 bdagent 的发言记为"运营"，
        # 现在"运营"专指真人运营、bdagent 记为"机器人"。生产会话(is_simulated=0)里
        # 旧代码只写过"客户"/"运营"，其中"运营"全部是旧 bdagent 自己的话。
        conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY)")
        migration = "2026-07-06-bot-speaker-rename"
        done = conn.execute(
            "SELECT 1 FROM schema_migrations WHERE name = ?", (migration,)
        ).fetchone()
        if not done:
            conn.execute(
                "UPDATE session_messages SET speaker = '机器人' WHERE speaker = '运营' "
                "AND session_id IN (SELECT id FROM sessions WHERE is_simulated = 0)"
            )
            conn.execute("INSERT INTO schema_migrations (name) VALUES (?)", (migration,))
        conn.commit()


_CLIENT_FORM_COLUMNS = (
    "company", "contact", "budget", "need",
    "brand", "tk_link", "shop_ready", "sales_1k", "commission", "entity_coop",
)


def save_client(form: dict, chat_id: str, submitted_by: str, is_simulated: bool = False) -> int:
    columns = ", ".join(_CLIENT_FORM_COLUMNS)
    placeholders = ", ".join("?" for _ in _CLIENT_FORM_COLUMNS)
    values = [form.get(col, "") for col in _CLIENT_FORM_COLUMNS]
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            f"INSERT INTO clients ({columns}, chat_id, submitted_by, is_simulated) "
            f"VALUES ({placeholders}, ?, ?, ?)",
            (*values, chat_id, submitted_by, 1 if is_simulated else 0),
        )
        conn.commit()
        return cur.lastrowid


# ---- 群设置 / 成员角色 / 未回复追踪(后台管理，机器人进程实时读) ----

_GROUP_SETTING_DEFAULTS = {
    "bot_enabled": 1,           # 每群总开关：关=只记录，回复/弹卡/安抚全停
    "collection_mode": "proactive",  # proactive=检测到新客户主动弹卡; silent=默默记录不弹卡
    "reply_on_mention": 1,      # 被@/点名时回复
    "instant_faq": 0,           # 未@命中语料FAQ立刻接话(默认关，语料回答走被@和安抚两条路)
    "reminder_enabled": 0,      # 无人回复安抚+私信提醒(默认关，后台按群打开)
    "reminder_minutes": 30,     # 客服多少分钟没回复触发安抚
}

_SETTING_INT_FIELDS = {
    "bot_enabled", "reply_on_mention", "instant_faq", "reminder_enabled", "reminder_minutes",
}


def get_group_settings(chat_id: str) -> dict:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM group_settings WHERE chat_id = ?", (chat_id,)
        ).fetchone()
    settings = dict(_GROUP_SETTING_DEFAULTS)
    if row:
        for key in settings:
            if row[key] is not None:
                settings[key] = row[key]
    return settings


def update_group_settings(chat_id: str, changes: dict) -> dict:
    """只更新传入的字段；未知字段/非法值忽略。返回更新后的完整设置。"""
    valid = {}
    for key, value in changes.items():
        if key not in _GROUP_SETTING_DEFAULTS:
            continue
        if key in _SETTING_INT_FIELDS:
            try:
                value = int(value)
            except (TypeError, ValueError):
                continue  # 非数字的开关值直接忽略，别让一次坏请求 500
        valid[key] = value
    if valid:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO group_settings (chat_id) VALUES (?)", (chat_id,)
            )
            assignments = ", ".join(f"{key} = ?" for key in valid)
            conn.execute(
                f"UPDATE group_settings SET {assignments}, updated_at = CURRENT_TIMESTAMP "
                "WHERE chat_id = ?",
                (*valid.values(), chat_id),
            )
            conn.commit()
    # 刚打开"无人回复安抚"：清掉开启之前积压的等待计时，避免对陈年旧消息
    # 立刻误发安抚(那些消息早被人工处理过了，只是没走到机器人这边清零)。
    if valid.get("reminder_enabled") == 1:
        clear_awaiting_reply(chat_id)
    return get_group_settings(chat_id)


# ---- 淋浪人员名册（全局，一次配好处处生效） ----
# 群成员命中名册 = 淋浪自家人(带职务)，其余按客户对待。取代旧的按群逐个标角色。

ROSTER_ROLES = ("技术", "达人运营", "商务对接运营", "其他")


def list_roster() -> list:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT name, role, open_id, note FROM staff_roster ORDER BY role, name"
        ).fetchall()
    return [dict(r) for r in rows]


def upsert_roster(name: str, role: str = "", open_id: str = None, note: str = None) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "INSERT INTO staff_roster (name, role, open_id, note) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET role = excluded.role, "
            "open_id = COALESCE(excluded.open_id, staff_roster.open_id), "
            "note = COALESCE(excluded.note, staff_roster.note)",
            (name, role, open_id, note),
        )
        conn.commit()


def delete_roster(name: str) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("DELETE FROM staff_roster WHERE name = ?", (name,))
        conn.commit()


def pin_roster_open_id(name: str, open_id: str) -> None:
    """首次在群里按姓名匹配上后，把 open_id 钉住——之后优先按 open_id 认，防重名误伤。"""
    if not (name and open_id):
        return
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "UPDATE staff_roster SET open_id = ? WHERE name = ? AND (open_id IS NULL OR open_id = '')",
            (open_id, name),
        )
        conn.commit()


def roster_maps() -> tuple:
    """(by_open_id, by_name)——一次加载，喂给 match_roster 批量解析，避免逐条查库。"""
    rows = list_roster()
    by_open_id = {r["open_id"]: r for r in rows if r["open_id"]}
    by_name = {r["name"]: r for r in rows}
    return by_open_id, by_name


def match_roster(open_id: str, name: str, by_open_id: dict = None, by_name: dict = None):
    """群成员是不是淋浪自家人：优先 open_id(唯一)，再按姓名兜底。命中返回名册条目，否则 None。
    防重名关键：名册条目一旦钉了 open_id，就只认那个 open_id——另一个同名但 open_id 不同的人
    (比如和员工重名的真客户)不再被姓名兜底误判成自家人。"""
    if by_open_id is None:
        by_open_id, by_name = roster_maps()
    if open_id and open_id in by_open_id:
        return by_open_id[open_id]
    if name and name in by_name:
        entry = by_name[name]
        pinned = entry.get("open_id")
        # 该名册条目已钉到别的 open_id → 当前这个人不是那位员工(重名)，不认
        if pinned and open_id and pinned != open_id:
            return None
        return entry
    return None


def is_staff(open_id: str, name: str) -> bool:
    return match_roster(open_id, name) is not None


def resolve_identity(row: dict, by_open_id: dict = None, by_name: dict = None) -> dict:
    """把一条消息的原始身份(is_bot/sender_open_id/sender_name/speaker)按当前名册解析成：
    speaker(客户/运营/机器人，前端上色用) + who(显示"谁说的") + llm(喂模型的富标签：淋浪+职务+姓名) + role/is_linlang。
    Approach B 的核心：解析在读取时做，改了名册所有历史立刻跟着变，不用重取。"""
    if by_open_id is None:
        by_open_id, by_name = roster_maps()
    name = (row.get("sender_name") or "").strip()
    if row.get("speaker") == "system":  # 训练台系统提示，原样保留
        return {"speaker": "system", "who": "system", "llm": None, "role": "", "is_linlang": False}
    if row.get("is_bot") or row.get("speaker") == "机器人":
        return {"speaker": "机器人", "who": "机器人", "llm": "你", "role": "", "is_linlang": True}
    entry = match_roster(row.get("sender_open_id"), name, by_open_id, by_name)
    if entry:
        role = entry.get("role") or ""
        who = f"淋浪·{role}·{name}".replace("··", "·").strip("·") if name else f"淋浪{role}"
        llm = f"淋浪{role}{name}"
        return {"speaker": "运营", "who": who, "llm": llm, "role": role, "is_linlang": True}
    if row.get("speaker") == "运营":  # 训练台模拟运营(无 open_id)
        return {"speaker": "运营", "who": name or "运营同事", "llm": f"淋浪运营同事{name}".strip(),
                "role": "", "is_linlang": True}
    who = name or "客户"
    return {"speaker": "客户", "who": who, "llm": (f"客户{name}" if name else "客户"),
            "role": "", "is_linlang": False}


def mark_awaiting_reply(chat_id: str, text: str, sender: str, now: int) -> None:
    """客户发言：开始/延续"等客服回复"计时。保留最早的未回复时刻，文本更新为最新一条。
    追问(ON CONFLICT)把 answered 重置为 0——last_text 换了，之前答过的不算数。"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "INSERT INTO reply_watch (chat_id, awaiting_since, last_text, last_sender, reminded, answered) "
            "VALUES (?, ?, ?, ?, 0, 0) "
            "ON CONFLICT(chat_id) DO UPDATE SET last_text = excluded.last_text, "
            "last_sender = excluded.last_sender, answered = 0",
            (chat_id, now, text, sender),
        )
        conn.commit()


def mark_awaiting_answered(chat_id: str) -> None:
    """机器人即时回复了这条客户消息：标记已答，安抚时就不再复读同一个语料答案。"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("UPDATE reply_watch SET answered = 1 WHERE chat_id = ?", (chat_id,))
        conn.commit()


def clear_awaiting_reply(chat_id: str) -> None:
    """客服(打了角色标签的人)发言、或后台开启安抚：解除计时和已提醒状态。"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("DELETE FROM reply_watch WHERE chat_id = ?", (chat_id,))
        conn.commit()


def list_awaiting_reply() -> list:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM reply_watch WHERE reminded = 0").fetchall()
    return [dict(r) for r in rows]


def mark_reminded(chat_id: str, awaiting_since: int) -> bool:
    """原子置位，且必须匹配被检查的那次等待(awaiting_since)——否则会误消费
    "员工回复后客户又追问"新开始的计时。返回 False 表示这次等待已被清零/已提醒，调用方跳过。"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            "UPDATE reply_watch SET reminded = 1 "
            "WHERE chat_id = ? AND awaiting_since = ? AND reminded = 0",
            (chat_id, awaiting_since),
        )
        conn.commit()
        return cur.rowcount > 0


def unmark_reminded(chat_id: str, awaiting_since: int) -> None:
    """安抚发送失败时回滚 reminded，下一轮重试(否则这轮等待的提醒名额白白消耗)。"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "UPDATE reply_watch SET reminded = 0 WHERE chat_id = ? AND awaiting_since = ?",
            (chat_id, awaiting_since),
        )
        conn.commit()


def get_chat_history(chat_id: str, limit: int = 500) -> list:
    """一个群跨所有生产会话的完整消息流(后台聊天记录视图用)。
    speaker/who 按当前名册现算(Approach B)——改了名册颜色和身份立刻跟着变。"""
    by_open_id, by_name = roster_maps()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        # 按真实消息时间排(feishu_create_time)，不是入库id——不然历史同步补进来的旧消息
        # (id大但时间早)会排到实时消息后面、时序倒挂。COALESCE 兜底防 NULL。
        rows = conn.execute(
            "SELECT m.id, m.speaker, m.text, m.mentions, m.sender_open_id, m.sender_name, "
            "m.is_bot, m.feishu_create_time, m.created_at FROM session_messages m "
            "JOIN sessions s ON s.id = m.session_id "
            "WHERE s.chat_id = ? AND s.is_simulated = 0 "
            "ORDER BY COALESCE(m.feishu_create_time, 0) DESC, m.id DESC LIMIT ?",
            (chat_id, limit),
        ).fetchall()
    result = []
    for r in reversed(rows):
        d = dict(r)
        d["mentions"] = json.loads(d["mentions"]) if d["mentions"] else []
        # 显示时间优先用真实发送时间(ms)，同步回来的历史才不会全塌成"入库那一刻"
        d["ts"] = d.get("feishu_create_time")
        ident = resolve_identity(d, by_open_id, by_name)
        d["speaker"] = ident["speaker"]   # 客户/运营/机器人（前端上色）
        d["who"] = ident["who"]           # 显示"谁说的"（淋浪·职务·姓名 / 客户名 / 机器人）
        d["is_linlang"] = ident["is_linlang"]
        d["role"] = ident["role"]
        result.append(d)
    return result


# ---- 历史同步游标（断点重传的"版本号"） ----

def get_sync_cursor(chat_id: str) -> int:
    """返回这个群已同步到的最后一条消息的 create_time(ms)，没有就 0(全量)。"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT last_create_time FROM chat_sync_state WHERE chat_id = ?", (chat_id,)
        ).fetchone()
    return row[0] if row and row[0] else 0


def set_sync_cursor(chat_id: str, last_create_time: int, last_message_id: str = None) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "INSERT INTO chat_sync_state (chat_id, last_create_time, last_message_id, updated_at) "
            "VALUES (?, ?, ?, CURRENT_TIMESTAMP) "
            "ON CONFLICT(chat_id) DO UPDATE SET last_create_time = excluded.last_create_time, "
            "last_message_id = excluded.last_message_id, updated_at = CURRENT_TIMESTAMP",
            (chat_id, last_create_time, last_message_id),
        )
        conn.commit()


def clear_chat_messages(chat_id: str) -> int:
    """清空一个真实群的聊天记录(session_messages)并重置同步游标，供"清空+重取"用。
    只删聊天流水，不动 clients 客户档案表。返回删了多少条。"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            "DELETE FROM session_messages WHERE session_id IN "
            "(SELECT id FROM sessions WHERE chat_id = ? AND is_simulated = 0)",
            (chat_id,),
        )
        conn.execute("DELETE FROM chat_sync_state WHERE chat_id = ?", (chat_id,))
        conn.commit()
        return cur.rowcount


def set_client_bitable_record_id(client_id: int, record_id: str) -> None:
    """记下同步到多维表格的 record_id；留空的行就是漏同步的，方便事后补写。"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "UPDATE clients SET bitable_record_id = ? WHERE id = ?",
            (record_id, client_id),
        )
        conn.commit()


# ---- 会话(chat_id 级别的聊天记录) ----
# 生产场景：一个真实飞书群 chat_id 对应一个会话，首次收到消息时懒创建。
# 训练台场景：同一个真实测试群里可以有多个"逻辑会话"，靠 session_id 区分，
#   互不干扰的 backstory/历史，方便一轮测完点"结束"、开新的一轮。


def get_or_create_session_by_chat_id(chat_id: str) -> str:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id FROM sessions WHERE chat_id = ? AND is_simulated = 0 AND status = 'active' "
            "ORDER BY created_at DESC LIMIT 1",
            (chat_id,),
        ).fetchone()
        if row:
            return row[0]
        session_id = uuid.uuid4().hex[:12]
        conn.execute(
            "INSERT INTO sessions (id, chat_id, is_simulated) VALUES (?, ?, 0)",
            (session_id, chat_id),
        )
        conn.commit()
        return session_id


def create_session(chat_id: str, hint: str = "", is_simulated: bool = True) -> str:
    session_id = uuid.uuid4().hex[:12]
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "INSERT INTO sessions (id, chat_id, is_simulated, hint) VALUES (?, ?, ?, ?)",
            (session_id, chat_id, 1 if is_simulated else 0, hint),
        )
        conn.commit()
    return session_id


def set_session_backstory(session_id: str, backstory: dict) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "UPDATE sessions SET backstory = ? WHERE id = ?",
            (json.dumps(backstory, ensure_ascii=False), session_id),
        )
        conn.commit()


def set_pending_card(session_id: str, pending: bool) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "UPDATE sessions SET pending_card = ? WHERE id = ?",
            (1 if pending else 0, session_id),
        )
        conn.commit()


def try_consume_pending_card(session_id: str) -> bool:
    """原子地把 pending_card 从 1 置 0。返回 False 表示本来就没有待填表单——
    用于卡片提交幂等：同一张卡片被点第二次/过期残留卡被点，直接拒绝。"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            "UPDATE sessions SET pending_card = 0 WHERE id = ? AND pending_card = 1",
            (session_id,),
        )
        conn.commit()
        return cur.rowcount > 0


def set_auto_chat(session_id: str, enabled: bool) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "UPDATE sessions SET auto_chat = ? WHERE id = ?",
            (1 if enabled else 0, session_id),
        )
        conn.commit()


def set_client_recorded(session_id: str) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "UPDATE sessions SET client_recorded = 1 WHERE id = ?",
            (session_id,),
        )
        conn.commit()


def end_session(session_id: str) -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "UPDATE sessions SET status = 'ended', ended_at = CURRENT_TIMESTAMP, auto_chat = 0 "
            "WHERE id = ?",
            (session_id,),
        )
        conn.commit()


def append_message(
    session_id: str,
    speaker: str = None,
    text: str = "",
    mentions: list = None,
    sender_open_id: str = None,
    sender_name: str = None,
    is_bot: bool = False,
    feishu_message_id: str = None,
    feishu_create_time: int = None,
) -> None:
    """记一条消息。
    - 生产真人消息：传 sender_open_id/sender_name(身份读取时按名册现算，不冻结 speaker)；
    - 机器人自己：is_bot=True；
    - 训练台：传 speaker="客户"/"运营"(无 open_id，读取时兜底用它)。
    mentions=被真·@到的人名列表(前端标蓝)。feishu_message_id 有值时 INSERT OR IGNORE 去重
    (实时推送和历史拉取共用它，同一条只入库一次)。"""
    mentions_json = json.dumps(mentions, ensure_ascii=False) if mentions else None
    # 只认真实的字符串 message_id(机器人发送stub会返回True之类，别当id存进去否则会误去重)
    if not (isinstance(feishu_message_id, str) and feishu_message_id):
        feishu_message_id = None
    # 没给发送时间就用当前时刻(ms)——让机器人自己发的/训练台的消息也有排序时间基准，
    # 和历史同步回来的按真实时间排在一起，不会因为按入库id排而时序错乱。
    if feishu_create_time is None:
        feishu_create_time = int(time.time() * 1000)
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO session_messages "
            "(session_id, speaker, text, mentions, sender_open_id, sender_name, is_bot, "
            "feishu_message_id, feishu_create_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (session_id, speaker, text, mentions_json, sender_open_id, sender_name,
             1 if is_bot else 0, feishu_message_id, feishu_create_time),
        )
        conn.commit()
        return cur.rowcount > 0  # False=被 feishu_message_id 唯一约束挡掉(已存在)


def get_session(session_id: str) -> dict:
    by_open_id, by_name = roster_maps()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            return None
        rows = conn.execute(
            "SELECT speaker, text, sender_open_id, sender_name, is_bot, created_at "
            "FROM session_messages WHERE session_id = ? "
            "ORDER BY COALESCE(feishu_create_time, 0) ASC, id ASC",
            (session_id,),
        ).fetchall()
    history = []
    for h in rows:
        d = dict(h)
        ident = resolve_identity(d, by_open_id, by_name)
        # speaker=类别(客户/运营/机器人，供 decide_and_send 判断)；llm=富标签(淋浪+职务+姓名，喂模型)
        d["speaker"] = ident["speaker"]
        d["llm"] = ident["llm"]
        history.append(d)
    return {
        "id": row["id"],
        "chat_id": row["chat_id"],
        "is_simulated": bool(row["is_simulated"]),
        "hint": row["hint"],
        "backstory": json.loads(row["backstory"]) if row["backstory"] else {},
        "status": row["status"],
        "pending_card": bool(row["pending_card"]),
        "auto_chat": bool(row["auto_chat"]),
        "client_recorded": bool(row["client_recorded"]),
        "created_at": row["created_at"],
        "history": history,
    }


def list_sessions(is_simulated: bool = True) -> list:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT s.*, "
            "(SELECT COUNT(*) FROM session_messages m WHERE m.session_id = s.id) AS message_count "
            "FROM sessions s WHERE is_simulated = ? ORDER BY created_at DESC",
            (1 if is_simulated else 0,),
        ).fetchall()
        result = []
        for row in rows:
            backstory = json.loads(row["backstory"]) if row["backstory"] else {}
            result.append(
                {
                    "id": row["id"],
                    "status": row["status"],
                    "hint": row["hint"],
                    "company": backstory.get("company", ""),
                    "message_count": row["message_count"],
                    "auto_chat": bool(row["auto_chat"]),
                    "created_at": row["created_at"],
                }
            )
        return result
