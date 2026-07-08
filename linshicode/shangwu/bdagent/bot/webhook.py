import base64
import hashlib
import hmac
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import lark_oapi as lark  # noqa: E402  (复用 bdagent 根目录已有的 logger)


def _sign(timestamp: str, secret: str) -> str:
    # 飞书自定义机器人的官方签名算法：把 "timestamp\nsecret" 整体当 HMAC 的 key，
    # 消息体为空去算 HmacSHA256，再 base64——不是常见的"key=secret,msg=内容"用法，容易搞反。
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def send_webhook_text(webhook_url: str, secret: str, text: str) -> bool:
    if not webhook_url or not secret:
        lark.logger.error("webhook url/secret 未配置，跳过发送")
        return False

    timestamp = str(int(time.time()))
    payload = {
        "timestamp": timestamp,
        "sign": _sign(timestamp, secret),
        "msg_type": "text",
        "content": {"text": text},
    }
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        lark.logger.error(f"webhook send failed: {exc}")
        return False

    if data.get("code") not in (0, None):
        lark.logger.error(f"webhook send rejected: {data}")
        return False
    return True
