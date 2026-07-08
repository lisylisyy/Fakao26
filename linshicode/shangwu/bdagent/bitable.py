"""录入客户后，把客户信息同步写进飞书多维表格《商务agent》。

表格挂在 wiki 知识库里，wiki token 不能直接当 bitable 的 app_token 用，
必须先调 wiki get_node 解析出 obj_token。表格字段按需自动补齐：
主字段(文本)重命名为"公司名称"，其余缺什么建什么，不动已有数据。

同步失败只记日志不打断录入流程——SQLite 里已经有底账，可凭
clients.bitable_record_id 为空找出漏同步的记录事后补写。
"""
import threading
import time

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import (
    AppTableField,
    AppTableRecord,
    CreateAppTableFieldRequest,
    CreateAppTableRecordRequest,
    ListAppTableFieldRequest,
    UpdateAppTableFieldRequest,
)
from lark_oapi.api.wiki.v2 import GetNodeSpaceRequest

from config import BITABLE_TABLE_ID, BITABLE_WIKI_TOKEN
from feishu import client, get_member_name, lark_lock
from storage import set_client_bitable_record_id

PRIMARY_FIELD_NAME = "公司名称"
_TYPE_TEXT = 1
_TYPE_DATETIME = 5
# 主字段之外，写记录前要保证存在的字段
_EXTRA_FIELDS = {
    "品牌名称": _TYPE_TEXT,
    "联系人": _TYPE_TEXT,
    "产品TK链接": _TYPE_TEXT,
    "是否开店出新手村": _TYPE_TEXT,
    "店销是否1000+": _TYPE_TEXT,
    "佣金比例": _TYPE_TEXT,
    "主体入库配合": _TYPE_TEXT,
    "预算": _TYPE_TEXT,
    "需求描述": _TYPE_TEXT,
    "提交人": _TYPE_TEXT,
    "来源群": _TYPE_TEXT,
    "录入时间": _TYPE_DATETIME,
}

# 表单字段 -> 表格列名(主字段 company 单独处理)
_FORM_TO_FIELD = {
    "brand": "品牌名称",
    "contact": "联系人",
    "tk_link": "产品TK链接",
    "shop_ready": "是否开店出新手村",
    "sales_1k": "店销是否1000+",
    "commission": "佣金比例",
    "entity_coop": "主体入库配合",
    "budget": "预算",
    "need": "需求描述",
}

_lock = threading.Lock()
_ready_app_token = ""  # 解析+字段补齐都成功后缓存，进程内只做一次


def _resolve_app_token() -> str:
    req = GetNodeSpaceRequest.builder().token(BITABLE_WIKI_TOKEN).obj_type("wiki").build()
    with lark_lock:
        resp = client.wiki.v2.space.get_node(req)
    if not (resp.success() and resp.data and resp.data.node):
        raise RuntimeError(f"wiki get_node failed: code={resp.code} msg={resp.msg}")
    node = resp.data.node
    if node.obj_type != "bitable":
        raise RuntimeError(f"wiki 节点不是多维表格: obj_type={node.obj_type}")
    return node.obj_token


def _ensure_fields(app_token: str) -> None:
    req = (
        ListAppTableFieldRequest.builder()
        .app_token(app_token)
        .table_id(BITABLE_TABLE_ID)
        .page_size(100)
        .build()
    )
    with lark_lock:
        resp = client.bitable.v1.app_table_field.list(req)
    if not resp.success():
        raise RuntimeError(f"field list failed: code={resp.code} msg={resp.msg}")
    items = resp.data.items or []
    names = {f.field_name for f in items}

    # 主字段改名为"公司名称"(公司名放主字段，表格里每行标题就是公司)。
    # 如果表里已经有同名的普通字段就不动主字段，公司名会写进那个字段。
    primary = next((f for f in items if f.is_primary), None)
    if primary and primary.field_name != PRIMARY_FIELD_NAME and PRIMARY_FIELD_NAME not in names:
        update_req = (
            UpdateAppTableFieldRequest.builder()
            .app_token(app_token)
            .table_id(BITABLE_TABLE_ID)
            .field_id(primary.field_id)
            .request_body(
                AppTableField.builder().field_name(PRIMARY_FIELD_NAME).type(primary.type).build()
            )
            .build()
        )
        with lark_lock:
            update_resp = client.bitable.v1.app_table_field.update(update_req)
        if not update_resp.success():
            raise RuntimeError(
                f"primary field rename failed: code={update_resp.code} msg={update_resp.msg}"
            )
        # 改名后同步更新快照：不然主字段原名恰好是下面某个保留字段名时会漏建
        names.discard(primary.field_name)
        names.add(PRIMARY_FIELD_NAME)

    for name, field_type in _EXTRA_FIELDS.items():
        if name in names:
            continue
        create_req = (
            CreateAppTableFieldRequest.builder()
            .app_token(app_token)
            .table_id(BITABLE_TABLE_ID)
            .request_body(AppTableField.builder().field_name(name).type(field_type).build())
            .build()
        )
        with lark_lock:
            create_resp = client.bitable.v1.app_table_field.create(create_req)
        if not create_resp.success():
            raise RuntimeError(
                f"field create '{name}' failed: code={create_resp.code} msg={create_resp.msg}"
            )


def _ensure_ready() -> str:
    global _ready_app_token
    with _lock:
        if not _ready_app_token:
            app_token = _resolve_app_token()
            _ensure_fields(app_token)
            _ready_app_token = app_token
        return _ready_app_token


def _invalidate_ready() -> None:
    global _ready_app_token
    with _lock:
        _ready_app_token = ""


def sync_client(client_id: int, form: dict, chat_id: str = "", submitted_by: str = "") -> str:
    """写一条客户记录进多维表格，返回 record_id；失败返回 None(只记日志)。"""
    if not (BITABLE_WIKI_TOKEN and BITABLE_TABLE_ID):
        return None  # 没配表格就静默跳过，方便换环境部署
    try:
        app_token = _ensure_ready()
        # 提交人存真名(查得到的话)，open_id 人看不懂
        submitter = get_member_name(chat_id, submitted_by) or submitted_by
        fields = {
            PRIMARY_FIELD_NAME: form.get("company", ""),
            "提交人": submitter,
            "来源群": chat_id,
            "录入时间": int(time.time() * 1000),
        }
        for form_key, field_name in _FORM_TO_FIELD.items():
            fields[field_name] = form.get(form_key, "")
        req = (
            CreateAppTableRecordRequest.builder()
            .app_token(app_token)
            .table_id(BITABLE_TABLE_ID)
            .request_body(AppTableRecord.builder().fields(fields).build())
            .build()
        )
        with lark_lock:
            resp = client.bitable.v1.app_table_record.create(req)
        if not (resp.success() and resp.data and resp.data.record):
            raise RuntimeError(f"record create failed: code={resp.code} msg={resp.msg}")
        record_id = resp.data.record.record_id
        if client_id:
            set_client_bitable_record_id(client_id, record_id)
        return record_id
    except Exception as exc:
        # 清掉缓存让下一条记录重新走"解析token+补字段"：表格被人改名/删列之后
        # 能自愈，不用等进程重启(机器人是长驻进程，可能几周不重启)。
        _invalidate_ready()
        lark.logger.error(f"bitable sync failed (client_id={client_id}): {exc}")
        return None


def sync_client_async(client_id: int, form: dict, chat_id: str = "", submitted_by: str = "") -> None:
    """后台线程同步，不阻塞卡片回调(回调要在几秒内响应，首次同步要先解析token+建字段)。"""
    threading.Thread(
        target=sync_client,
        args=(client_id, form, chat_id, submitted_by),
        daemon=True,
    ).start()
