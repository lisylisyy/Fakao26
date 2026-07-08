import json
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

_BACKSTORY_PROMPT = (
    "你要为一场角色扮演生成一个虚构的外贸/跨境电商客户背景资料。"
    "这个客户想找淋浪跨境电商谈 TikTok Shop 达人分发/短视频营销或建站方面的合作。"
    "只返回严格的 JSON，不要任何多余文字，字段："
    "company(公司名，虚构但像真的)、industry(所属行业)、"
    "contact(联系人姓名+职位)、budget(大致预算范围)、need(核心需求，一两句话)、"
    "brand(品牌名)、tk_link(产品TikTok链接，虚构即可)、"
    "shop_ready(是否已在TK Shop开店并出新手村，值只能是'是'或'否')、"
    "sales_1k(店销是否1000+，值只能是'是'或'否')、"
    "commission(能给的佣金比例，如'open+8%')、"
    "entity_coop(能否配合提供公司主体做入库，值只能是'是'或'否')。"
)

_CHAT_SYSTEM_PROMPT_TEMPLATE = (
    "你在角色扮演一个虚构客户，背景资料如下（只有你自己知道，不要一次性说出来）：\n"
    "{backstory}\n\n"
    "你正在飞书群里跟淋浪跨境电商的商务运营(真人)聊合作意向，群里还有一个机器人助理"
    "「淋浪商务机器人」，它可能会给你发信息登记表单、帮忙录入你的信息。下面对话记录里，"
    "'你(客户)'是你自己说过的话，'对方(淋浪商务运营)'是商务运营说的话，"
    "'机器人助理(淋浪商务机器人)'是机器人说的话。规则：\n"
    "1. 每次只说一两句话，像真实聊天一样，不要一次性倒出所有背景信息；\n"
    "2. 前几轮先寒暄、说明来意即可，预算和详细需求等对方问起来了再说；\n"
    "3. 语气自然、口语化，像真实的老板/采购，不要暴露自己是 AI；\n"
    "4. 如果系统提示你'机器人助理发来了信息登记表单'，说一句自然的确认话(比如'好的,我填一下')即可，"
    "不用列出表单内容，后续系统会自动帮你把背景资料填进去；\n"
    "5. 如果已经填过表单、对方也确认收到了，就自然地寒暄收尾，不要重复要求合作；\n"
    "6. 你只能说'你(客户)'这一方的话，绝对不能替商务运营或机器人助理编内容、编回复——"
    "如果最后一条已经是你自己说的、对方还没回应，就用客户的口吻自然地补充一句、换个角度说明，"
    "或者礼貌地等一下/追问，不要自己编一段'对方说了什么'。"
)


def _chat(system_prompt: str, user_prompt: str, *, max_tokens: int = 300) -> str:
    if _client is None:
        return ""
    try:
        resp = _client.chat.completions.create(
            model=DEEPSEEK_FLASH_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.8,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as exc:
        lark.logger.error(f"kehu persona deepseek call failed: {exc}")
        return ""


def generate_backstory(hint: str = "") -> dict:
    user_prompt = f"参考关键词/试点客户：{hint}" if hint else "自由发挥，不用参考特定客户。"
    raw = _chat(_BACKSTORY_PROMPT, user_prompt, max_tokens=300)
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        lark.logger.error(f"backstory json parse failed, raw={raw!r}")
        return {
            "company": hint or "某跨境电商公司",
            "industry": "跨境电商",
            "contact": "客户代表",
            "budget": "待沟通",
            "need": "建站/详情页设计合作",
        }


def _label(speaker: str) -> str:
    if speaker == "客户":
        return "你(客户)"
    if speaker == "运营":
        return "对方(淋浪商务运营)"
    if speaker == "机器人":
        return "机器人助理(淋浪商务机器人)"
    return None  # system 记录不是真实对话内容，不喂给模型


def generate_customer_reply(backstory: dict, history: list, event: str = "") -> str:
    system_prompt = _CHAT_SYSTEM_PROMPT_TEMPLATE.format(
        backstory=json.dumps(backstory, ensure_ascii=False)
    )
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
        user_prompt = "对话刚开始，你先开口打个招呼、说明来意。"
    reply = _chat(system_prompt, user_prompt, max_tokens=300)
    # 模型偶尔会把历史里的说话人标签抄进回复开头("你(客户): xxx")，剥掉
    reply = re.sub(r"^\s*你\s*[\(（]客户[\)）]\s*[:：]\s*", "", reply)
    return reply or "你好，想了解一下合作的事。"
