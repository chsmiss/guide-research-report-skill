# 评分记录与计算

脚本用标准库运行，从同版本 `profiles.json` 读取维度与权重。先运行 init，再用实际评估填写；初始 null 不代表零分。

```bash
python3 scripts/score_report.py init --profile technical --output /absolute/path/evaluation.json
python3 scripts/score_report.py score /absolute/path/evaluation.json --output /absolute/path/score.json
```

JSON 主要字段：

- `protocol_version`、`profile`：版本和用途。锁定同批比较条件。
- `report`：至少填写 title、version、publication_date、evidence_cutoff；不知道的日期说明未知，不编造。
- `assessment`：purpose、assessed_at、materials_received、checks_performed、limitations、confidence、confidence_basis。confidence 为 high/medium/low，说明的是本次评估把握。
- `gate`：status 为 pass/restricted/reject/undetermined；basis 记录实际核查定位与判断；affected_scope、remediation 说明使用范围及解除限制条件。
- `ratings`：十维，每维 `rating` 为 null 或 0–5 的 0.5 步长，`observations` 为事实观察与理由，`locators` 指向报告页码、章节、表格和／或核查记录。定位是可追溯入口，不是自动验证。
- `ratings.communication`：主要评价论证能否被目标读者理解，记录入口、解释、推理衔接、重复或图表引导的具体表现。不能只给字体、配色或页数理由；评分不高于2时，评语须保留“需要实质改写后交付”的限制。脚本不自动识别文本是否易读。
- `issues`：重要问题列表，含 id、description、primary_dimension、severity、scope、locators、checks、consequence、repair。severity 为 minor/major/critical；scope 为 conclusion/report。脚本不会根据这些标签自行判断底线真假，但会拦截与 pass/reject 声明明显不一致的记录。
- 可选 `custom_weights`：十维全量权重、非负、合计 100；同时填写 `weight_rationale`。仍保留原 profile 为基准说明，输出标记 custom。

无底线问题可不填 issues，但 pass 也需提供已检查什么的依据。restricted 需明确影响范围和修复条件；reject 需至少一项 critical/report 问题及检查依据。对单个结论的 critical 问题使用 restricted，不自动否决整份报告。

## 输出解释

完整评分：`diagnostic_total` 为 Σ(权重×分数/5)，只取一位小数。`headline_total` 只有在全部正权重维度已评估且底线是 pass/restricted 时存在；restricted 必须连同限制展示，不能与 pass 无条件混排。

不完整评分：`headline_total` 和 `diagnostic_total` 均为 null；输出 `assessed_contribution`、`unassessed_weight` 和 `possible_range`。范围仅把未知项分别取 0 和 5，是数学边界，不是置信区间。不把已评部分按比例放大到 100。

reject 或 undetermined 即使十维已填，也不产生可排名的 headline_total。可以保留诊断分数供修复，但不能把它作为推荐依据。

`comparison_key` 包含协议版本、实际权重和底线类别；相同 key 是数学比较的必要条件，仍需核查读者、任务、材料和评审深度是否一致。脚本不自动排名，也不判断比较的实质合理性。

结构、算术通过不证明事实正确或作者分析有效。对短评可直接给表格，但沿用相同的未知处理、底线和可追溯原则。

## 协议更新与旧记录

v1.1.0 提高可读性权重并扩充其判据。旧记录仍属于旧版本；当前计算器会拒绝版本不匹配的输入。若只测试权重变化，在副本中记录原版本、原评分、采用新权重的目的与可读性尚未重评的限制；不要把该敏感性结果称作新协议下的完整复评。实际复评应重新阅读、更新具体段落依据，保留旧文件。
