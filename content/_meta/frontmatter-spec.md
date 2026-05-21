---
id: meta.frontmatter-spec
type: meta
updated_at: 2026-05-21
---

# 知识库 / 笔记 / 题目 frontmatter 规范

整个系统靠 frontmatter 把 markdown + JSON 三者拧成一张图。任何写入操作（kb-curator / feynman-coach / question-importer）都必须遵守本文件。

## 1. 通用字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | ✅ | 全局唯一标识，命名规则见下 |
| `subject` | enum | ✅ | 8 学科 + meta 之一 |
| `updated_at` | date (YYYY-MM-DD) | ✅ | 最后修改日期 |
| `syllabus_year` | int | 推荐 | 2025 / 2026，对应使用的大纲版本 |

## 2. `subject` 枚举

仅以下 9 个值（与 `content/` 顶层目录名一一对应）：

```
theory                  # 理论法（含法治理论 / 法理 / 宪法 / 法制史 / 职业道德）
international           # 三国法（含公 / 私 / 经济）
criminal                # 刑法
criminal-procedure      # 刑诉
civil                   # 民法
civil-procedure         # 民诉（含仲裁）
administrative          # 行政法与行政诉讼法
commercial              # 商经法（含商法 + 经济法）
meta                    # 元数据文档（非考试学科）
```

## 3. `concept_id` 命名规则

格式：`<subject_short>.<slug>`，全小写连字符，子级用点分。

- subject_short 缩写：
  - `theory` → `theo`
  - `international` → `intl`
  - `criminal` → `crim`
  - `criminal-procedure` → `crimproc`
  - `civil` → `civ`
  - `civil-procedure` → `civproc`
  - `administrative` → `admin`
  - `commercial` → `comm`

示例：
- `crim.causation` — 刑法 / 因果关系
- `crim.causation.intervening-factor` — 刑法 / 因果关系 / 介入因素（更细一级）
- `civ.expression-of-intent` — 民法 / 意思表示
- `comm.company-law.capital-system` — 商法 / 公司法 / 资本制度

## 4. 知识库文档（`content/**/*.md`）

```yaml
---
id: crim.causation                            # 知识点 id（同时是 concept_id）
subject: criminal
concept_ids: [crim.causation]                 # 本文档涉及的知识点（通常含 id 自己 + 子概念）
parent_concept: crim.objective-element        # 可选：上级概念
aliases: [相当因果, 条件说]                    # 别名/同义词，搜索用
weight: 4                                     # 1-5，命题热度（出题频率主观估计）
difficulty: 3                                 # 1-5，理解难度
new_in_2024_2025: false                       # 是否受 2024-2025 新法影响
syllabus_year: 2025
updated_at: 2026-05-21
---
```

文件命名：`<两位序号>-<中文标题>.md`，例如 `05-因果关系.md`。
位置：`content/<subject>/<可选子目录>/<文件名>`。

文档正文可使用：
- `[[crim.intent]]` — 知识点 wiki-link
- `[[q:crim-2023-p2-q05]]` — 题目反向引用
- 标准 markdown + GFM 表格、任务清单

## 5. 高光笔记（`progress/notes/<subject>/...md`）

```yaml
---
id: note-01HX5Q...                            # ULID
created_at: 2026-05-21T10:30:00Z              # ISO 8601 含时区
subject: civil
concept_ids: [civ.expression-of-intent]       # 关联的知识点
related_questions: [civ-2022-p2-q11]          # 关联的题目
tags: [意思表示, 易错]
---
```

文件命名：`<yyyy-mm-dd>-<slug>.md`，slug 用拼音或英文短句。

## 6. 费曼会话（`progress/feynman/...md`）

```yaml
---
session_id: fey-01HX5Q...                     # ULID
created_at: 2026-05-21T22:10:00Z
concept_ids: [crim.causation]                 # 本次讲解的主题
duration_min: 18
self_score: 3                                 # 1-5 用户自评
gaps: ["遗漏: 介入因素三层判断", "偏差: 相当因果 vs 条件说混淆"]
related_questions_tested: [crim-2022-p2-q11, crim-2023-p2-q05]
followup_due: 2026-05-22T22:00:00Z            # 首次复习时间（艾宾浩斯）
---
```

文件命名：`<yyyy-mm-dd>-<concept_id_short>.md`，例如 `2026-05-21-crim-causation.md`。

## 7. 题目（`data/questions/<subject>.jsonl`，一行一题）

字段见 `data/questions/README.md`（待写）。关键约定：
- `id` 格式：`<subject_short>-<year>-p<paper>-q<num>`（真题）或 `<subject_short>-self-<ulid>`（自录）
- `concept_ids` 数组：本题考察的知识点
- 写入前必须 diff 预览 + 用户确认

## 8. 校验

`scripts/validate-schema.ts`（待写）会扫描所有文件，校验：
- frontmatter 必填字段
- `concept_id` 命名规则
- `concept_ids` / `related_questions` 中的引用都存在
- 没有孤立文件（无人引用且无 children）

CI / pre-commit 跑这个脚本可以保证整张图不破。
