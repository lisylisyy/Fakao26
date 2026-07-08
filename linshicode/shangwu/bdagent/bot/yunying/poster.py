import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import YUNYING_WEBHOOK_SECRET, YUNYING_WEBHOOK_URL  # noqa: E402

from bot.webhook import send_webhook_text  # noqa: E402


def post_ops_message(text: str) -> bool:
    """把运营人设(真人角色)的发言可视化发进测试群。"""
    return send_webhook_text(YUNYING_WEBHOOK_URL, YUNYING_WEBHOOK_SECRET, text)
