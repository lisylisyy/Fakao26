# data/

结构化题库 + 知识点元数据 + 关联映射。所有文件入 git。

## 子目录

- `questions/<subject>.jsonl` — 题库，每题一行 JSON（见 `frontmatter-spec.md` 第 7 节）。每个学科一个文件，便于 diff。
- `concepts/<subject>.json` — 知识点元数据数组（不是 jsonl，因为量小、需要整体读）。
- `mappings/concept-question.jsonl` — 知识点 ↔ 题目的反向索引（题目内已有 `concept_ids` 字段冗余，本文件用于批量审计）。
- `exams/<year>-paper<n>.json` — 整套真题（用于 `/mock` 全真模考），保留卷面顺序。

## 命名约定

- 题目 id：`<subject_short>-<year>-p<paper>-q<num>`（真题）或 `<subject_short>-self-<ulid>`（自录）
- 知识点 id：见 `content/_meta/frontmatter-spec.md` 第 3 节

## 写入规则

- 只能由 **question-importer** agent 写入（W2 起实现）
- 任何写入必须 diff 预览 + 用户确认（详见 `.claude/agents/question-importer.md`）
- 手动编辑也允许，但记得用 `scripts/validate-schema.ts`（W2 起）跑校验
