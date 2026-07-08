import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import KEHU_WEBHOOK_SECRET, KEHU_WEBHOOK_URL  # noqa: E402

from bot.webhook import send_webhook_text  # noqa: E402


def post_customer_message(text: str) -> bool:
    return send_webhook_text(KEHU_WEBHOOK_URL, KEHU_WEBHOOK_SECRET, text)
