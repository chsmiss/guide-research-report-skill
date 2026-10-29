# 写作方法出处与评估

需要追溯方法或比较技能改写时读取。实际写作遵循 [editorial-design.md](editorial-design.md)。以下公开方法链接和检查日期继承自2.6的出处记录，本次创建完成本地内容改写，公开链接的当前状态可另行查证。

## 固定输入比较

比较新旧技能时，固定任务、读者、证据和输出约束，保持模型、工具与预算可比，保留审阅前草稿。评价者可接收随机标签版本，分别判断理解、证据保真、机制清晰与重复。评分权重在结果出现前固定。普通报告按任务交付一份成稿。

记录样例、缺陷和任务数量，结论限于实际观察范围。一个片段的偏好提供局部证据，检索质量需要相同预算的端到端任务。本次改写的结构与兼容性验证按真实执行记录报告。

## 继承的方法参考

- STORM，MIT：[研究后提纲](https://github.com/stanford-oval/storm/blob/fb951af7744dab086e34962e9bc6fe878e145f83/knowledge_storm/storm_wiki/modules/outline_generation.py)、[分节生成](https://github.com/stanford-oval/storm/blob/fb951af7744dab086e34962e9bc6fe878e145f83/knowledge_storm/storm_wiki/modules/article_generation.py)、[摘要与去重](https://github.com/stanford-oval/storm/blob/fb951af7744dab086e34962e9bc6fe878e145f83/knowledge_storm/storm_wiki/modules/article_polish.py)；[论文](https://arxiv.org/html/2402.14207v2) 的组织收益对应小规模英文百科任务，中文研报表现需单独评估。
- [Co-STORM §5.4](https://arxiv.org/html/2408.15232v1)：借助已检索但尚待讨论的材料提出问题，用于启发问题协调；团队数量按授权与实际需要选择。
- DeerFlow，MIT：[consulting-analysis](https://github.com/bytedance/deer-flow/blob/fb553747d1d6fa9fd0d5f55729895cfe2e8d15f7/skills/public/consulting-analysis/SKILL.md)：借鉴章节目标与分析意图，篇幅和图表按读者问题配置。
- [199-biotechnologies deep-research](https://github.com/199-biotechnologies/claude-deep-research-skill/blob/main/SKILL.md)：参考提纲细化及分节证据循环，保留本技能自身质量标准。源记录显示README声明MIT，独立许可可按实际需要进一步核对。
- [DeepResearch Bench](https://deepresearch-bench.github.io/)：分别评估报告质量和引用准确性；系统排名限于公开测试版本与设置。

本技能对上述方法独立转述，所保留的脚本与资产来自本地2.6技能的兼容资源。
