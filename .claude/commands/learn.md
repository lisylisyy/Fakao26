---
description: 把对话中学到的法考知识点沉淀到 content/ markdown 知识库
argument-hint: <知识点名 或 一段学习内容>
---

用户刚才学到了 / 想沉淀的内容：

$ARGUMENTS

请调用 **kb-curator** 子 agent 处理这件事。kb-curator 应当：

1. 判断这块内容属于哪个学科 / concept_id
2. 检查 `content/` 是否已有对应文档：
   - 有 → 准备 `Edit` 追加
   - 无 → 准备 `Write` 新建
3. **先在对话里展示 diff 预览**（文件路径 + frontmatter + 正文 + 一句话总结）
4. 等我明确说"确认"或"yes"后再执行写入
5. 写完汇报：写到哪、新增了什么 concept_id、要不要 `/feynman` 验证

注意：
- 严格遵守 `content/_meta/frontmatter-spec.md` 的字段约定和命名规则
- 不能写到 `data/questions/`、`progress/` 等非 `content/` 目录
- 如果 $ARGUMENTS 内容跨多个学科或概念，分多个文件处理，每个都单独 diff 预览
- 如果涉及 2024-2025 新法（见 `_meta/new-laws-2024-2025.md`），frontmatter 必填 `new_in_2024_2025: true`
