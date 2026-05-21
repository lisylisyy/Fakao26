# raw/

存放原始法考资料 PDF / 扫描件 / 视频字幕 txt 等。**这个目录不入 git**（除本 README 和 .gitignore），靠云盘（iCloud / 坚果云 / OneDrive）同步到各设备。

工作流：
1. 把 PDF/资料丢到这里
2. 在 Claude Code 里跑 `/import raw/<文件名>`
3. question-importer agent 解析为题目 / 知识点，预览 → 确认 → 写入 `data/` 或 `content/`
4. 原 PDF 留在云盘，结构化产物入 git
