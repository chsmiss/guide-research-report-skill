# 四份历史原件与旧评估存档

本目录保留四份原始报告、文件哈希、当时的评估记录与证据快照。当前五份比较请看[仓库 README](../../../README.md)和[2026-10-29 排名原文](../comparison-20261029/RANKING.md)。

此处历史评分采用旧协议（单维 0–5、加权 100 分制），与新排名的单维 0–10、十维等权和用途分不兼容。请勿混合排序或价格口径。旧评分并未改写为新分数。

旧 `research-report-evaluator` skill 已按要求从当前分支删除；`evaluation/skill_snapshot.json` 只保留历史溯源，不代表这些文件仍可用。

从仓库根目录运行：

```sh
python3 examples/ai-pharma/no-skill-2026/scripts/replay.py
```

脚本核对四份报告哈希、12 份历史评分中保存的权重及贡献算术、临床注册快照的入组人数和保存的计算。它不再调用旧 skill，不重演完整门槛规则，也不核验事实真伪、来源时效、可读性或新五份排名。

[旧评估正文](EVALUATION.md) · [原件清单](manifest.json)
