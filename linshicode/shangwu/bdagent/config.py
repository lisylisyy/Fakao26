import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

APP_ID = os.getenv("FEISHU_APP_ID", "")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
DEEPSEEK_FLASH_MODEL = os.getenv("DEEPSEEK_FLASH_MODEL", "deepseek-v4-flash")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

KEHU_WEBHOOK_URL = os.getenv("KEHU_WEBHOOK_URL", "")
KEHU_WEBHOOK_SECRET = os.getenv("KEHU_WEBHOOK_SECRET", "")
YUNYING_WEBHOOK_URL = os.getenv("YUNYING_WEBHOOK_URL", "")
YUNYING_WEBHOOK_SECRET = os.getenv("YUNYING_WEBHOOK_SECRET", "")

# 录入完成后拉会话术里 @ 的商务负责人(飞书群成员姓名)。留空则不@任何人。
MEETING_CONFIRMER_NAME = os.getenv("MEETING_CONFIRMER_NAME", "季倩逸")

# 多维表格《商务agent》：录入客户后同步写进去。表格挂在 wiki 知识库下，
# 这里配 wiki 节点 token(不是 app_token，运行时解析)+ 表 id。留空则不同步。
BITABLE_WIKI_TOKEN = os.getenv("BITABLE_WIKI_TOKEN", "MZQkwAf7xiEeI8kFrPWci196nyf")
BITABLE_TABLE_ID = os.getenv("BITABLE_TABLE_ID", "tblbPUaMC8WB6Zoi")

# 训练台用的真实飞书测试群 chat_id——配了这个之后，bdagent(机器人)用真实身份
# send_card/send_text 打真实飞书 API 发卡片和回复；留空则打桩截获、借 webhook 可视化。
# 客户/运营两个人设不受影响，永远分别走 kehu/yunying webhook 发言。
TEST_GROUP_CHAT_ID = os.getenv("TEST_GROUP_CHAT_ID", "")

DB_PATH = BASE_DIR / "data" / "bdagent.sqlite3"
