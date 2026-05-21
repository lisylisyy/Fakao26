# Fakao26 — 法考 2026 客观题备考系统

通过 **2026 年 9 月**法考客观题（300 分制，180 分合格）的个人备考操作系统。

## 三层架构

| 层 | 目录 | 维护方式 |
|---|---|---|
| **知识库** | `content/**/*.md` | Claude Code 通过 `/learn` 沉淀对话内容 |
| **题库** | `data/**/*.jsonl` `data/**/*.json` | `/import` 解析 PDF；手工/对话补充 |
| **学习状态** | `progress/**` | append-only jsonl + 笔记 markdown，git 同步 |

Next.js Web 应用（计划 W2 起逐步搭建）只读消费上面三层数据，做刷题 / SRS 复习 / 知识库浏览 / 笔记 / 模考 / 统计。

## 快速使用

### 在 Claude Code 里
- `/learn <学到的东西>` — 沉淀到知识库
- `/feynman <知识点>` — 自己讲一遍，让 feynman-coach 找盲区
- `/note <感想>` — 写个人笔记到 `progress/notes/`
- 后续会上线：`/quiz` `/review` `/import` `/stats` `/plan-today` `/explain` `/new-law` `/mock`

### 子 agent
- **kb-curator**：写入 / 整理 `content/`
- **feynman-coach**：陪练费曼讲解
- 后续：**question-importer** / **concept-linker** / **study-coach** / **mock-exam-evaluator**

## frontmatter 是命门

任何 markdown 文档的 frontmatter 字段约定见 [`content/_meta/frontmatter-spec.md`](content/_meta/frontmatter-spec.md)。
所有 agent 必须遵守。`concept_id` 命名 `<subject_short>.<slug>`（如 `crim.causation`）— 整个系统靠这个 ID 把知识点 / 题目 / 笔记 / 费曼记录拧成一张图。

## 学科分类

8 学科（与 `content/` 顶层目录一一对应）：

- `theory` — 理论法（法治理论 / 法理学 / 宪法 / 法制史 / 职业道德）
- `international` — 三国法（国际公法 / 国际私法 / 国际经济法）
- `criminal` — 刑法
- `criminal-procedure` — 刑诉
- `civil` — 民法
- `civil-procedure` — 民诉（含仲裁）
- `administrative` — 行政法与行政诉讼法
- `commercial` — 商经法（含商法 + 经济法）

详见 [`content/_meta/exam-structure.md`](content/_meta/exam-structure.md)。

## 多设备 git 同步

```bash
# 开始学习前
git pull --rebase

# 结束时
git add -A && git commit -m "study: <一句话>" && git push
```

`progress/` 入 git，但仓库设为 **GitHub private**，确保个人学习数据不公开。
原始 PDF 资料放 `raw/`（已 .gitignore），靠云盘同步。

## 备考节奏

- **5 月**：知识库骨架 + 三国法 / 理论法核心知识点沉淀（性价比最高，先攻）
- **6 月**：MVP Web 刷题闭环；导入 2022-2024 真题 1000+；2026 大纲发布后批量校准
- **7 月**：SRS 错题循环；硬骨头（民法、刑法、商经法）攻坚
- **8 月**：全真模考；薄弱点最后一轮
- **9 月**：冲刺背诵 + 临考模拟

详见 `/root/.claude/plans/agent-2026-wondrous-puddle.md`（本地规划文件）。

## 开发状态

| 周 | 状态 | 内容 |
|---|---|---|
| W1 | 进行中 | 知识库骨架 + kb-curator + feynman-coach + 三条核心命令 |
| W2 | 待办 | Next.js 初始化 + Zod schema + ts-fsrs + /quiz + /import 真题 |
| W3 | 待办 | /review SRS + feynman 接 SRS + 模考 + 全文搜索 |
| W4 | 待办 | 新法专题 + study-coach + 抛光 |
