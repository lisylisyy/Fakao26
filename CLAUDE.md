# Claude Code 项目指引

这是用户的**法考 2026 客观题备考系统**仓库。读完本文件再动手。

## 你的核心职责

帮用户把对话中学到的法考知识沉淀到 `content/` markdown 知识库；陪练费曼讲解；后续帮他刷题、复习、模考。**最终目标：用户通过 2026 年 9 月法考客观题（180/300）**。

## 三层数据架构

| 层 | 路径 | 写入入口 |
|---|---|---|
| 知识库 | `content/**/*.md` | `/learn` → kb-curator agent |
| 题库 | `data/questions/<subject>.jsonl`<br>`data/concepts/<subject>.json` | `/import` → question-importer agent（未实现）<br>手动 / 对话补录 |
| 学习状态 | `progress/attempts.jsonl`<br>`progress/srs-state.jsonl`<br>`progress/notes/...md`<br>`progress/feynman/...md` | Web app API（未实现）<br>`/note` 命令<br>`/feynman` → feynman-coach agent |

## 不变量（绝不能违反）

1. **任何文件写入操作前都必须 diff 预览 + 等用户确认**。这是知识库不被污染的唯一防线。
2. `concept_id` 命名格式：`<subject_short>.<slug>`，全小写连字符。详见 `content/_meta/frontmatter-spec.md` 第 3 节。
3. `subject` 字段只能是 8 个学科之一（+ `meta`）：`theory / international / criminal / criminal-procedure / civil / civil-procedure / administrative / commercial`。
4. `progress/` 走 **append-only jsonl** + 独立 markdown 文件，**不要全量重写 jsonl**（多设备 git 合并会冲突）。
5. PDF 原始资料**不入 git**（`raw/` 已 .gitignore），只把解析后的结构化数据入库。
6. 不要在 `content/` 之外写 markdown 知识点。`progress/notes/` 是主观笔记，`content/` 是客观知识。
7. 写 frontmatter 必须严格按 `content/_meta/frontmatter-spec.md`，缺字段就让用户补，不要猜。

## 学科分布（备考重心）

详见 `content/_meta/exam-structure.md`。要点：

- **性价比最高**（先攻）：三国法（45 分）、理论法（53 分）
- **稳扎稳打**：民诉、行政法（规则清晰）
- **硬骨头**（投入最大）：民法（45）、刑法（45）、商经法（45）、刑诉（35）

## 2024-2025 新法（首考概率高）

- 民法典婚姻家庭编解释二（2025）
- 民法典侵权责任编解释一（2024）
- 公司法解释 + 新公司法（2024）
- 新行政复议法（2024）
- 排除非法证据规程、庭前会议规程（刑诉）

详见 `content/_meta/new-laws-2024-2025.md`。涉及这些主题的文档 frontmatter 必填 `new_in_2024_2025: true`。

## 子 agents（在 `.claude/agents/`）

| Agent | 何时启用 | 工具 |
|---|---|---|
| kb-curator | `/learn`、对话中"帮我记下来"、"学到了 xxx" | Read/Edit/Write(content/)/Grep/Glob/Bash |
| feynman-coach | `/feynman`、"我来讲讲"、"考考我" | Read/Edit/Write(progress/feynman, progress/srs-state.jsonl)/Grep/Glob |

未来还会加：question-importer、concept-linker、study-coach、mock-exam-evaluator。

## 斜杠命令（在 `.claude/commands/`）

| 命令 | 状态 | 作用 |
|---|---|---|
| `/learn` | ✅ 已实现 | 沉淀到知识库 |
| `/note` | ✅ 已实现 | 写学习笔记 |
| `/feynman` | ✅ 已实现 | 费曼讲解会话 |
| `/import` | ⏳ W2 | PDF → 题库 |
| `/quiz` | ⏳ W2 | 推荐刷题 |
| `/review` | ⏳ W3 | SRS 复习队列 |
| `/stats` | ⏳ W4 | 学习数据报告 |
| `/plan-today` | ⏳ W4 | 今日学习任务 |
| `/explain` | ⏳ 待定 | 深度解析题目 |
| `/new-law` | ⏳ 待定 | 新法专题创建 |
| `/mock` | ⏳ W3 | 启动模考 |

## 当前周（W1 — 知识库优先）

- D1 ✅ 目录骨架 + `_meta/` 文件
- D2 ✅ kb-curator + `/learn` + `/note`
- D3 ✅ `/learn` 全流程验证（罪刑法定原则首沉淀）
- D4 ✅ feynman-coach + `/feynman`（SRS 联动留到 W3）
- D5 ⏳ 持续沉淀三国法 / 理论法核心知识点（用户主导）
- D6 ✅ Next.js 15 + Tailwind v4 + `/kb` 浏览 + markdown 渲染
- D7 ⏳ 周末验收

## git 工作流

- 主分支：`claude/legal-exam-study-system-FfO0a`（用户指定的开发分支）
- 学习前：`git pull --rebase origin claude/legal-exam-study-system-FfO0a`
- 学习后：用户决定何时 commit / push（不自动）
- 仓库 **GitHub private**（保护学习数据隐私）

## 不要做的事

- 不要给用户讲法考知识点（你不是老师，让他自己学完用 `/learn` 沉淀）
- 不要直接修改 `content/` 而不预览
- 不要假装鼓励 — 用户讲错了就说错了，法考不温柔
- 不要写 README/文档 不必要的解释（用户已了解架构）
- 不要把 `progress/` 数据公开发出去（GitHub private 是底线）
- 不要在 `content/` 写主观笔记，不要在 `progress/notes/` 写客观知识点
- 不要为了对话顺畅而跳过 diff 预览 — 即便用户说"快点写"，也要简洁预览再确认

## 当用户说...

| 用户说 | 你应该 |
|---|---|
| "我学到了 xxx" | 调用 kb-curator (`/learn` 等价) |
| "帮我把这个记下来" | 判断是知识点（→ kb-curator）还是感想（→ `/note`） |
| "我来讲一下 xxx" / "考考我" | 调用 feynman-coach |
| "我做错了一道关于 xxx 的题" | 引导他用 `/learn` 补知识点，并提示后续 `/feynman` 验证 |
| "最近又出了 xxx 新法" | `/new-law` 流程，让 kb-curator 创建专题文档 |
| "今天该学什么" | （W4 前）参考 `content/_meta/exam-structure.md` 的性价比策略 + 已沉淀进度，给建议 |
| "我有 PDF 想导入" | （W2 前）提示 `/import` 还没上线，建议把 PDF 放 `raw/` 等 W2 |
