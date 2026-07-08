import lark_oapi as lark
from openai import OpenAI

from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_FLASH_MODEL,
    DEEPSEEK_MODEL,
)
from knowledge import get_corpus

_client = (
    OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    if DEEPSEEK_API_KEY
    else None
)

_SYSTEM_PROMPT = (
    "你是淋浪跨境电商商务飞书机器人的意图判断器。"
    "判断用户这句话是否想让你开始收集/录入一个新客户的信息"
    "（例如提到要跟进新客户、有个客户想合作、要建档、要录客户资料等）。"
    "只回答 yes 或 no，不要输出其他任何内容。"
)


_REPLY_SYSTEM_PROMPT = (
    "你是淋浪跨境电商的飞书机器人助理「淋浪商务机器人」，在群里辅助商务运营同事接待客户，"
    "只有被 @ 或点名叫到时你才说话。回复要求：\n"
    "1. 一两句话，自然、灵动、口语化，像个机灵的助理，不要机械客套；\n"
    "2. 如果知道对方姓名，用得体的称呼(比如姓'张'的负责人称'张总'；同事直接叫名字)，"
    "不知道就不用硬编称呼；\n"
    "3. 你是辅助角色：能做的是登记/录入客户信息、记录群里的沟通内容、"
    "按下面语料库口径解答商务常见问题；语料库没有覆盖的业务细节(价格、工期、案例等)"
    "绝对不要编造，只能说商务同事会跟进；\n"
    "4. 只输出回复正文，不要任何前缀(比如'收到：')、引号或解释。"
)

_CORPUS_BLOCK_TEMPLATE = (
    "\n\n【商务语料库(权威口径，由商务同事维护)】\n{corpus}\n【语料库结束】\n"
    "回答合作模式、报价档位、需要什么资料、入库流程、拉会等业务问题时，"
    "必须严格按语料库内容回答：说法可以口语化，但数字、比例、条款一个都不能改。"
)


def _reply_system_prompt() -> str:
    corpus = get_corpus()
    if not corpus:
        return _REPLY_SYSTEM_PROMPT
    return _REPLY_SYSTEM_PROMPT + _CORPUS_BLOCK_TEMPLATE.format(corpus=corpus)


_HISTORY_LABELS = {"客户": "客户", "运营": "淋浪运营同事", "机器人": "你"}


def _history_lines(history: list) -> str:
    lines = []
    for turn in (history or [])[-8:]:
        # 优先用富标签(淋浪+职务+姓名，get_session 按名册现算)，让模型知道谁是自家人、什么职务
        label = turn.get("llm") or _HISTORY_LABELS.get(turn.get("speaker", ""))
        if label:
            lines.append(f"{label}: {turn['text']}")
    return ("最近的对话：\n" + "\n".join(lines) + "\n\n") if lines else ""


def generate_bot_reply(text: str, sender_name: str = "", history: list = None) -> str:
    """被点名但不是录入意图时，生成一句自然的群聊回复。失败返回空字符串(调用方沉默兜底)。"""
    if _client is None or not text:
        return ""
    context = _history_lines(history)
    who = f"对方姓名：{sender_name}\n" if sender_name else ""
    user_prompt = f"{context}{who}对方刚发来：{text}\n\n你的回复："
    try:
        resp = _client.chat.completions.create(
            model=DEEPSEEK_FLASH_MODEL,
            messages=[
                {"role": "system", "content": _reply_system_prompt()},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=400,
            temperature=0.7,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as exc:
        lark.logger.error(f"deepseek bot reply failed: {exc}")
        return ""


_FAQ_SYSTEM_PROMPT = (
    "你是淋浪跨境电商的飞书机器人助理「淋浪商务机器人」，在群里旁听客户和商务运营的对话，"
    "这条消息没有@你。你的任务：判断这条消息是否在询问下面语料库明确覆盖的商务常见问题"
    "(比如合作模式、报价档位、需要提供什么资料、主体入库流程、怎么安排会议等)。\n"
    "- 是：直接输出你要在群里回复的话。严格按语料库口径，数字、比例、条款一个不能改；"
    "口语化、简洁，长答案可以分点；只输出回复正文，不要前缀或解释。\n"
    "- 不是(闲聊、同事间沟通、语料库没覆盖的问题、或者拿不准)：只输出 SILENT。"
    "宁可沉默也不要抢答或编造。"
    "\n\n【商务语料库(权威口径)】\n{corpus}\n【语料库结束】"
)


def faq_auto_reply(text: str, history: list = None) -> str:
    """没被点名的消息：命中语料库常见问题就返回按口径的回复，否则返回空字符串(保持沉默)。"""
    corpus = get_corpus()
    if _client is None or not text or not corpus:
        return ""
    context = _history_lines(history)
    user_prompt = f"{context}群里刚出现这条消息：{text}\n\n你的输出："
    try:
        resp = _client.chat.completions.create(
            model=DEEPSEEK_FLASH_MODEL,
            messages=[
                {"role": "system", "content": _FAQ_SYSTEM_PROMPT.format(corpus=corpus)},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=400,
            temperature=0.3,
        )
        reply = (resp.choices[0].message.content or "").strip()
        if not reply or reply.upper().startswith("SILENT"):
            return ""
        return reply
    except Exception as exc:
        lark.logger.error(f"deepseek faq reply failed: {exc}")
        return ""


ROLE_CHOICES = ("技术", "达人运营", "商务对接运营")

_ROLE_SYSTEM_PROMPT = (
    "你是淋浪跨境电商的客服分诊器。判断客户这条消息最应该由哪类同事跟进：\n"
    "- 技术：网站/系统/接口/账号授权/数据对接等技术问题\n"
    "- 达人运营：达人建联、选号、视频制作、发布节奏等达人侧执行问题\n"
    "- 商务对接运营：合作模式、报价、合同、进度、售后等商务沟通(拿不准也选这个)\n"
    "只输出以上三个词之一，不要输出其他任何内容。"
)


def classify_question_role(text: str) -> str:
    """无人回复安抚时用：判断客户问题该找哪类同事。失败/拿不准返回'商务对接运营'。"""
    fallback = "商务对接运营"
    if _client is None or not text:
        return fallback
    try:
        resp = _client.chat.completions.create(
            model=DEEPSEEK_FLASH_MODEL,
            messages=[
                {"role": "system", "content": _ROLE_SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            max_tokens=50,
            temperature=0,
        )
        answer = (resp.choices[0].message.content or "").strip()
        for role in ROLE_CHOICES:
            if role in answer:
                return role
    except Exception as exc:
        lark.logger.error(f"deepseek role classify failed: {exc}")
    return fallback


def wants_client_card(text: str) -> bool:
    if _client is None or not text:
        return False
    try:
        resp = _client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            # deepseek-v4-pro 是推理模型，答案前会先吃掉一截 reasoning_content，
            # max_tokens 给少了会在思考中途被截断，content 拿到的是空字符串。
            max_tokens=500,
            temperature=0,
        )
        answer = (resp.choices[0].message.content or "").strip().lower()
        return answer.startswith("yes")
    except Exception as exc:
        lark.logger.error(f"deepseek intent check failed: {exc}")
        return False
