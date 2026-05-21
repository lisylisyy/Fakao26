# progress/

个人学习状态。**入 git，但仓库必须是 GitHub private**。

## 文件

| 文件 | 写入方 | 说明 |
|---|---|---|
| `attempts.jsonl` | Web app `/api/attempt`（W2 起） | 答题记录，append-only |
| `srs-state.jsonl` | Web app `/api/srs` + feynman-coach（W3 起接入） | FSRS 调度事件流，append-only |
| `srs-snapshot.json` | `scripts/fold-srs.ts` 生成 | 折叠产物，**不入 git**（已 .gitignore） |
| `notes/<subject>/<date>-<slug>.md` | `/note` 命令 → kb-curator | 个人学习笔记 |
| `feynman/<date>-<concept>.md` | `/feynman` → feynman-coach | 费曼讲解会话记录 |
| `sessions/<date>.md` | `/plan-today` 命令（W4 起） | 每日学习日志 |
| `mock-reports/<exam_id>.md` | mock-exam-evaluator（W3 起） | 模考报告 |

## 为什么 append-only？

多设备 git 同步时，如果两台设备都全量改写同一份 jsonl，会 merge conflict。
append-only 模式下，两边各自往末尾追加几行，git 合并 = 简单拼接，无冲突。

折叠逻辑（`fold-srs.ts`）只读不写源数据：

```
srs-state.jsonl（事件流）
  → 按 card_id 取最新事件
  → srs-snapshot.json（构建产物，可重生，不入 git）
```

## 隐私

`progress/` 暴露你的薄弱点 / 学习习惯 / 错题历史。**仓库必须 private**。
如果未来想分享代码而不分享数据，可以把 `progress/` 拆到另一个 private repo（plan 文件第 8 节列了这个选项）。
