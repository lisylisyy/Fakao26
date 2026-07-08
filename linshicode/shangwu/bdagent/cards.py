SUBMIT_ACTION_NAME = "submit_client_info"

# (name, 标签, 占位提示) —— 字段清单按《商务Agent语料库.md》"客户基础信息搜集"一节
FORM_FIELDS = [
    ("company", "公司名称", "请输入公司名称"),
    ("brand", "品牌名称", "品牌名"),
    ("contact", "联系人", "姓名/职位"),
    ("tk_link", "产品TK链接", "产品的 TikTok Shop 链接"),
    ("shop_ready", "是否开店出新手村", "是 / 否（TK Shop 已开店并出新手村）"),
    ("sales_1k", "店销是否1000+", "是 / 否"),
    ("commission", "佣金比例", "如 open+8%（至少给到5%）"),
    ("entity_coop", "主体入库配合", "是 / 否（提供公司主体做入库，免费流程）"),
    ("budget", "预算", "大致预算范围"),
    ("need", "需求描述", "客户的核心需求"),
]


def client_info_card() -> dict:
    # input 组件必须包在 form 容器里，按钮用 action_type: form_submit 触发，
    # 否则填的内容不会汇总进回调的 form_value（飞书卡片 JSON 2.0 的要求）。
    inputs = [
        {
            "tag": "input",
            "name": name,
            "label": {"tag": "plain_text", "content": label},
            "placeholder": {"tag": "plain_text", "content": placeholder},
        }
        for name, label, placeholder in FORM_FIELDS
    ]
    submit_button = {
        "tag": "button",
        "text": {"tag": "plain_text", "content": "提交"},
        "type": "primary",
        "action_type": "form_submit",
        "name": SUBMIT_ACTION_NAME,
    }
    return {
        "schema": "2.0",
        "config": {"width_mode": "fill"},
        "header": {
            "title": {"tag": "plain_text", "content": "客户信息收集"},
            "template": "blue",
        },
        "body": {
            "elements": [
                {
                    "tag": "form",
                    "name": "client_info_form",
                    "elements": inputs + [submit_button],
                }
            ]
        },
    }
