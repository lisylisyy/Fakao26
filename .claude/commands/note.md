---
description: 写一则学习笔记到 progress/notes/，自动判学科+关联知识点
argument-hint: <感想 / 易错点 / 学习心得>
---

用户的笔记内容：

$ARGUMENTS

请按以下步骤处理：

1. 判断这则笔记属于哪个学科（subject 必须是 `content/_meta/frontmatter-spec.md` 第 2 节的 8 个学科之一）
2. 用 `Grep` 在 `content/` 中找出与笔记最相关的 1-3 个 `concept_id`，填入 `concept_ids`
3. 如果笔记引用了具体题目（题号格式 `<subject>-<year>-p<paper>-q<num>`），填入 `related_questions`
4. 准备文件路径：`progress/notes/<subject>/<yyyy-mm-dd>-<英文 slug>.md`
5. 准备 frontmatter（按 `frontmatter-spec.md` 第 5 节）+ 正文 = 用户原话稍作组织
6. **先 diff 预览**，等用户确认后再写

笔记和知识库 (`content/`) 的差异：
- `content/` 是**客观知识点**，按法考大纲组织，重在准确
- `progress/notes/` 是**主观学习痕迹**：易错点、个人记忆术、对比表、学习感想

如果用户其实是想沉淀客观知识到知识库，提示一下："这看起来更像知识点，要不要走 `/learn` 而不是 `/note`？"
