import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import lark_oapi as lark  # noqa: E402
from openai import OpenAI  # noqa: E402

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_FLASH_MODEL  # noqa: E402

_client = (
    OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL) if DEEPSEEK_API_KEY else None
)

# 训练台里运营人设的名字——喂给 bdagent 旁听时作为 sender_name，机器人被点名回话时可以称呼她
OPS_PERSONA_NAME = "小淋"

_CHAT_SYSTEM_PROMPT = (
    "你在角色扮演淋浪跨境电商的商务运营「小淋」——一个真人商务人员，在飞书群里接待来咨询合作的客户。"
    "下面对话记录里，'你(运营)'是你自己说过的话，'对方(客户)'是客户说的话，"
    "'机器人助理(淋浪商务机器人)'是群里的机器人助理说的话。规则：\n"
    "1. 你的目标：热情接待客户，逐步了解对方的公司、行业、核心需求、预算范围和时间安排，"
    "推进合作意向，需要时提出约个会议细聊；\n"
    "2. 每次只说一两句话，自然、口语化，像真人在群里打字；一次最多问一件事，不要连环追问；\n"
    "3. 涉及具体报价、工期、方案细节，不当场承诺，就说了解清楚需求后整理方案再同步；\n"
    "4. 群里的机器人助理会自动在合适时机给客户发信息登记表单、自动录入客户资料，"
    "你不用自己逐项记录客户信息；它发了表单你就自然地引导客户填一下；\n"
    "5. 不要暴露自己是 AI；你只能说'你(运营)'这一方的话，绝对不能替客户或机器人助理编内容；\n"
    "6. 如果最后一条已经是你自己说的、对方还没回应，就耐心补充一句或换个说法，不要编造对方的回复。"
)


def _chat(user_prompt: str, *, max_tokens: int = 300) -> str:
    if _client is None:
        return ""
    try:
        resp = _client.chat.completions.create(
            model=DEEPSEEK_FLASH_MODEL,
            messages=[
                {"role": "system", "content": _CHAT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.8,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as exc:
        lark.logger.error(f"yunying persona deepseek call failed: {exc}")
        return ""


def _label(speaker: str) -> str:
    if speaker == "运营":
        return "你(运营)"
    if speaker == "客户":
        return "对方(客户)"
    if speaker == "机器人":
        return "机器人助理(淋浪商务机器人)"
    return None  # system 记录(如客户上线提示)含客户底牌信息，不喂给运营人设


def generate_ops_reply(history: list, event: str = "") -> str:
    lines = []
    for turn in history:
        label = _label(turn["speaker"])
        if label:
            lines.append(f"{label}: {turn['text']}")
    if event:
        lines.append(f"[系统提示: {event}]")
    if lines:
        lines.append("轮到你说话了，只输出你要说的这一两句话：")
        user_prompt = "\n".join(lines)
    else:
        user_prompt = "对话刚开始，你先跟客户打个招呼、自我介绍一下。"
    reply = _chat(user_prompt, max_tokens=300)
    # 模型偶尔会把历史里的说话人标签抄进回复开头("你(运营): xxx")，剥掉
    reply = re.sub(r"^\s*你\s*[\(（]运营[\)）]\s*[:：]\s*", "", reply)
    return reply or "收到～我看一下哈。"
