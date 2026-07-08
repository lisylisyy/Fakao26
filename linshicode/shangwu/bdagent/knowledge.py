"""商务语料库加载。

《商务Agent语料库.md》由倩逸维护，是机器人回答业务问题的唯一权威口径
(合作模式、报价档位、信息收集清单、拉会话术、SOP)。按文件 mtime 缓存，
改完文件即热生效，不用改代码、不用重启进程。
"""
from pathlib import Path

import lark_oapi as lark

from config import BASE_DIR

CORPUS_PATH = BASE_DIR / "商务Agent语料库.md"

_cache = {"mtime": None, "text": ""}


def get_corpus() -> str:
    """返回语料库全文；文件不存在/读失败返回上次的缓存(没有缓存就空字符串)。"""
    try:
        mtime = CORPUS_PATH.stat().st_mtime
    except OSError:
        return _cache["text"]
    if _cache["mtime"] != mtime:
        try:
            _cache["text"] = CORPUS_PATH.read_text(encoding="utf-8")
            _cache["mtime"] = mtime
        except OSError as exc:
            lark.logger.error(f"corpus read failed: {exc}")
    return _cache["text"]
