# 引导生成研报skill 1.1.0

独立技能名：`guided-research-report`；界面名称：**引导生成研报skill**。源自 `deep-tech-research-report` 2.6.0，创建日期2026-10-28。原技能继续保留。

使用：`请用 $guided-research-report 引导我完成一份AI制药行业研报。`

启动后先选定研报类型与主要用途，再确认研究范围和论证大纲。用户已给出选择、获批大纲或授权自主完成时沿用该依据。详情见 [SKILL.md](SKILL.md) 和 [类型与确认流程](references/report-intake.md)。

入口及全部研究指导文档采用以期望行动为主的表达，保留证据、反证、定量与交付标准。继承脚本、数值模板和CSV接口保持兼容；测试样例中的失败事实、逻辑否定、状态枚举和合成数据标识按原意保留。

1.1版把读者理解、出版一致性和最终页面分别验收：实际重建结论、处理重复限定、安排附录与资料包，并检查连续引用和数字展示。[出版一致性工具](references/publication-checks.md) 提供编号生成、Decimal舍入与导出文字检查；审读和逐页渲染按 [编辑与交付](references/editorial-design.md) 执行。

[用途质量映射](references/generation-quality.md) 将Bohrium和Codex评估要求转为生成目标。正式评分另按选定评估协议执行。2.6的八维评分保留为兼容选项，另可衔接独立十维评估技能；每次正式评分明确选定协议。

验证命令：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/analyse_outlook.py --input templates/outlook.synthetic.json --output /a/new/path/calculations.json
```

脚本负责结构、声明和算术，来源真实性、推理质量和读者理解分别核查。完整改写与继承范围见 [迁移核对](references/migration-review.md)。
