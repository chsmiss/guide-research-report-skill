# 兼容2.6的研究包与工具

按任务需要采用CSV或等价结构笔记。脚本负责字段、声明关系及相应算术，来源、推理和内容充分性由单独核查支持。

## 模式与范围

传统模式：`python scripts/check_research_pack.py --claims claims.csv --evidence evidence.csv`

严格模式：`python scripts/check_research_pack.py --claims claims.csv --evidence evidence.csv --judgments judgments.csv --challenges challenges.csv --strict --review-output review_summary.json`

相对路径以工作目录解析。严格模式按需启用，保留旧包兼容，要求Tier1挑战和推断判断覆盖、原始核实声明所需已检查证据、独立证据所声明的依据。挑战可采用反例、替代机制、缺失检验或有限搜索，预测按任务需要提供。

广泛行业和概率展望验收另外对照 [industry-framework.md](industry-framework.md)、[scenarios-and-diligence.md](scenarios-and-diligence.md) 及模板。登记检查的结构PASS、数值模型的算术PASS与覆盖质量、概率依据各自记录。

`--review-output`在全部记录检查通过后向新文件写摘要，输入保持原样。`structural_check_only`始终为true。报告汇总与登记ID保持可对应，人可读引用在编辑阶段形成。

出版阶段保持研究登记ID稳定，用单独的连续编号映射生成读者引用与来源列表，见 [出版一致性工具](publication-checks.md)。脚本、运行命令、依赖与QA日志放在研究包使用说明；报告附录承载读者复核结论需要的公式、口径、假设和来源。报告以工程实现为研究对象时，保留解释对象所需的技术内容。

## 基础登记

- `claims.csv`：窄命题ID、tier、类型、期间、分母、状态、置信度、限制及决策影响。测量用fact/observation或calculation，作者推断用interpretation/inference、hypothesis、forecast或recommendation；各自依据各自核查。
- `evidence.csv`：来源、日期、定位、链、支持关系；可选 `observation_path`、`independence_basis`。严格模式下 `independently_generated=yes` 需两项均有内容，真实独立性另检查。
- `decision_map.csv`：优先级及判别检验，保留初始假说并更新最终状态。
- `peer_sets.csv`：纳入目的及可比较内容，估值组按实际任务选用。

## 判断登记

列：`judgment_id,claim_ids,judgment_type,judgment_text,basis_evidence_ids,strongest_alternative,decision_implication,horizon,update_trigger,confidence,limitations`。

多ID用分号。类型为 `interpretation`、`conditional_forecast`、`recommendation`。依据证据需连接该判断列明的命题。必要内容为判断、依据ID、替代解释、决策后果、更新条件、置信度；预测另给期限。假设主导与待解决部分写入limitations。

严格模式要求Tier1推断关联判断，事实型Tier1按事实核查。缺少已检查支持/背景证据时保留警告并说明条件身份。

## 挑战登记

列：`challenge_id,claim_id,challenge_type,challenge_text,evidence_ids,search_scope,search_date,disposition,effect_on_judgment,independence_check,remaining_gap`。

类型：`adverse_observation`、`alternative_mechanism`、`missing_test`、`search_no_result`。

处置：`retained_with_limits`、`revised`、`downgraded`、`withdrawn`、`unresolved`。

反例连接已检查证据；替代机制和待做检验可以是推理，明确其观察缺口。`search_no_result`填写有限来源/查询范围、日期及剩余缺口，evidence_ids留空，结果只描述该范围搜索。每条有内容、处置、对判断影响及独立性检查状态和理由。

挑战证据需登记到同一命题，适合时添加contextualizes关系，底层链保持一致。导出保留真实支持关系，警告作为检查提示，按实际含义修复记录。

## 需要另行检查的内容

来源真伪、真实独立性、搜索充分性、数字计算、推断合理性和出版质量分别检查。结构字段齐备的记录仍需回到原始材料。准确的背景关系按其含义保留。

## 可选决策底稿

可选证据字段 `evidence_domain`、`validation_design`、`evidence_scope`描述具体命题的证据属性。

```bash
python scripts/build_decision_brief.py --claims claims.csv --evidence evidence.csv --judgments judgments.csv --challenges challenges.csv --strict --output decision_brief.md
python scripts/build_decision_brief.py --claims claims.csv --evidence evidence.csv --judgments judgments.csv --challenges challenges.csv --decision-tests decision_tests.csv --strict --format json --output decision_brief.json
```

brief连接真实支持/背景证据、反例、缺口和更新条件，用于内部审阅。出版时按 [editorial-design.md](editorial-design.md) 选择发现与组织论证。缺失领域、设计和计划状态原样呈现，原始核查与推断独立性分别保留。文件以新路径创建，记录和链接通过后才写入。

`decision_tests.csv`列：`test_id,judgment_id,test_type,question_or_event,held_fixed,changed_factor,observable_source,review_window,update_direction,affected_scope,status,result_or_remaining_gap,evidence_ids`。

类型：`causal_identification`、`sensitivity`、`cash_stress`、`falsification_event`、`scenario`。状态：`planned`、`observed`、`calculated_scenario`、`unavailable`。方向：`up`、`down`、`both`、`confidence_only`、`no_change`。

情景报告假设条件下的计算；observed需已检查且关联受影响命题的证据。因果/敏感性/现金/情景填固定与变化因素，更新事件填来源与窗口。每行给范围、方向和结果/缺口。短任务可把这些字段并入已有笔记，实际事件、判别能力、更新方向和来源支持范围仍由内容检查负责。
