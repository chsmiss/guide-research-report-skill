# Guide Research Report Skill · 研报样例与评价

本仓库当前收录四份通过不同方式生成的 AI 制药行业研报，以及可复用的研报评价 skill。四份均为**未使用研报生成 skill 的 v0 样例**，原件保留，评分与批注另存。生成方式及“未用 skill”由文件提供者说明。

**本次结论：Codex v0 更适合作为解释清楚、边界较稳的入门底稿；玻尔网页稿的商业分析主线较好，但存在重要推导缺口；玻尔空间稿适合查找技术和公司资料；玻尔高级稿适合快速扫描新闻。四份均未达到可直接支持投资决策的成品尽调交付水平。**

评价日期：**2026-10-29，中国时间**。评价协议：[`research-report-evaluator` v1.1.0](skills/research-report-evaluator/SKILL.md)。主用途采用 `balanced` 通用质量评估，未把“高级”或产品名称作为加分项。

## 四份原始研报

| ID | 生成方式／版本 | 原件 | 生成时使用研报 skill | 日期说明 |
|---|---|---|---|---|
| `bohr_space` | 玻尔科学空间 Mac·标准 v0 | [Markdown](examples/ai-pharma/no-skill-2026/reports/玻尔科学空间mac-标准v0-AI制药行业研报_2026.md) | 否 | 正文更新时间为 2026 年 10 月 |
| `bohr_advanced` | 玻尔科学 Mac·高级 v0 | [Markdown](examples/ai-pharma/no-skill-2026/reports/玻尔科学mac-高级v0-AI制药行业研究报告.md) | 否 | 正文报告日期为 2026-10-27 |
| `bohr_web` | 玻尔写作网页·标准 v0 | [PDF，18 页](examples/ai-pharma/no-skill-2026/reports/玻尔写作网页-标准v0-main.pdf) | 否 | 数据截至 2026 年 10 月；具体生成日未确认 |
| `codex_v0` | Codex v0 | [PDF，13 页](examples/ai-pharma/no-skill-2026/reports/codex_v0_AI制药行业研究报告_20261026.pdf) | 否 | 正文报告日期为 2026-10-26 |

四个文件均逐字节复制，SHA-256 见 [manifest.json](examples/ai-pharma/no-skill-2026/manifest.json)。本次只收到这些单文件，未据此判断作者是否另有研究附件。

没有统一提示词、完整运行日志、模型版本、耗时、费用及重复采样，因此本案例只能比较**这四份具体输出**；不能证明某个产品总体更好，也不能证明使用 skill 的提升幅度。评价 skill 用于事后评审，与生成时是否使用 skill 是两件事。

## 评分与使用限制

每维 0–5 分、允许 0.5 档，加权总分为 100 分。权重取自随仓库保存的 [profiles.json](skills/research-report-evaluator/references/profiles.json)，不是看过排名后修改。评分是人工判断，脚本负责记录校验和算术。

| 报告 | 通用总分 | 底线状态 | 适用范围及限制 |
|---|---:|---|---|
| Codex v0 | **70.9** | `pass`，限实际抽查范围 | 入门、求职、企业初筛；解释与证据边界较好，原创发现和实际定量工具较少 |
| 玻尔网页标准 v0 | **64.6** | `restricted` | 商业模式与交易讨论底稿；市场推算、首付概率解释与部分因果推断修复前限用 |
| 玻尔空间标准 v0 | **60.3** | `restricted` | 技术／公司资料地图；临床时点、TEAE 标签和跨年份市场区间需修正 |
| 玻尔高级 v0 | **56.5** | `restricted` | 新闻扫描；试验人数归属、催化剂时间与提效／溢价强结论需修正 |

`pass` 表示实际抽查中未发现需要限制使用的重大问题，不代表全文保证，也不表示已通过投资尽调。`restricted` 分数必须与限制一起阅读，不能与 `pass` 作无条件推荐排名；这里只展示同口径诊断结果。没有把局部问题认定为系统性编造。

### 十维评分

下表为原始 0–5 分；贡献分 = 原始分 ÷ 5 × 权重。每一项的观察、位置和扣分理由见 [完整评审](examples/ai-pharma/no-skill-2026/EVALUATION.md) 与 [JSON 记录](examples/ai-pharma/no-skill-2026/evaluation/records)。

| 维度 | 通用权重 | Codex v0 | 网页标准 | 空间标准 | Mac 高级 |
|---|---:|---:|---:|---:|---:|
| 问题定义与定位 | 6% | 4 | 4 | 4 | 3.5 |
| 框架完整性 | 8% | 4 | 4.5 | 4.5 | 4 |
| 事实、证据质量与时效性 | 18% | 3.5 | 3 | 2.5 | 2.5 |
| 信息增量 | 10% | 2.5 | 3.5 | 3 | 2.5 |
| 分析深度与推理 | 14% | 3.5 | 2.5 | 3 | 2.5 |
| 定量纪律 | 8% | 3.5 | 2 | 2.5 | 2 |
| 行业机制与落地理解 | 7% | 3.5 | 3.5 | 3 | 3 |
| 反证、独立性与边界处理 | 7% | 3.5 | 2.5 | 3 | 2.5 |
| 决策可用性与决策工具 | 7% | 3.5 | 3 | 2.5 | 2.5 |
| 论证可读性与交付可用性 | 15% | 4 | 4 | 3 | 3.5 |

可读性主要看问题、证据、推理与限制能否被读者理解。网页稿主线鲜明，不代表推理自动成立；空间稿覆盖广，也不能用模型名称和表格替代解释。没有按 PDF、Markdown、篇幅或装饰直接加减分。

### 用途权重敏感性

| 报告 | 通用 `balanced` | 入门 `orientation` | 投资 `investment` |
|---|---:|---:|---:|
| Codex v0 | 70.9 | 73.0 | 70.8 |
| 网页标准 | 64.6 | 70.5 | 62.0 |
| 空间标准 | 60.3 | 64.7 | 58.0 |
| Mac 高级 | 56.5 | 61.5 | 54.5 |

后两列保留同一组十维判断，只替换 skill 的预设权重，属于敏感性计算，**不是针对两类读者重新完成的独立复评**。底线限制始终保留。小分差不应被解释为稳定的优劣差距，分数也不是质量百分位或预测准确率。

## 哪些核查实际改变了判断

- **临床终点与标签：** rentosertib IIa 期注册为 71 人，主要终点是治疗期间出现的不良事件（TEAE）；玻尔空间稿写成治疗相关不良事件，二者含义不同。FVC 是次要终点，早期信号不能直接量化 AI 的临床因果增益。[官方注册](https://clinicaltrials.gov/study/NCT05938920)
- **人数与读数窗口：** GB-0895 的 SOLAIRIA-1、SOLAIRIA-2 各计划 786 人，合计 1,572 人；高级稿将单项写成约 1,600 人。两项预计主要完成时间分别为 2028-12、2029-01；rentosertib III 期为 2029-10-30。高级稿的“2026–2028 多个 III 期读数”需要具体注册日历和中期分析依据。[SOLAIRIA-1](https://clinicaltrials.gov/study/NCT07276724)、[SOLAIRIA-2](https://clinicaltrials.gov/study/NCT07359846)、[rentosertib III 期](https://clinicaltrials.gov/study/NCT07687459)
- **交易比例与概率：** Isomorphic–Lilly 公告正文列首付 4,500 万美元、条件里程碑最高 17 亿美元且不含首付。比例约为 2.58%，算术成立；它不能单独识别临床成功概率，还受权益、项目数、义务和付款结构影响。网页稿的概率解释强于证据。[原公告 p1](https://storage.googleapis.com/isomorphiclabs-website-public-artifacts/ISOMORPHIC_LABS_LILLY_07_01_24.pdf)
- **市场推算勾稽：** 网页稿物理第 5 页以“2030 年前后约 150 亿美元”为中等口径参考，第 15 页又称依据同表推至 300–450 亿美元，未给可复算的基数和口径桥。两份 Markdown 也混用不同预测年份。不能直接拿这些区间做 TAM 估值。
- **财务时效：** Codex v0 的英矽、晶泰 2026H1 关键数据以及 Schrödinger 季度利润来源得到原始披露支持；高级稿“英矽报告期亏损”未注明期间，遗漏已公开的中期盈利，容易误导当前判断。[英矽中报 p12/p60](https://ir.insilico.com/media/b4thx2ea/2026-interim-report-en.pdf)、[晶泰中报 p5/p44](https://ir.xtalpi.com/media/1xtkvfec/2026-interim-report.pdf)、[Schrödinger Q2 业绩](https://ir.schrodinger.com/press-releases/news-details/2026/Schrdinger-Reports-Second-Quarter-2026-Financial-Results/)

更多定位、核查方式及未完成项目见 [source_checks.json](examples/ai-pharma/no-skill-2026/evaluation/evidence/source_checks.json)。临床注册快照已保存。预计日期会变化；核对公司公告只能证明披露内容，不能代替独立疗效或平台效率验证。

## 四份报告大约值多少钱

以下是**主观愿付参考**：人民币、个人、非独占、一次获取，只购买当前文件的阅读整理便利。假设合法分发，不含访谈、独家数据、持续更新、团队／转售权或咨询答疑。没有实际成交或愿付调查，也没有把分数机械换成价格。

**本仓库公开后，这四份原件的实际获取价格为 0 元。** 表中的区间用于“尚未免费公开、相同交付范围”的反事实参考；免费并不意味着没有学习或评测价值。

| 报告 | 尚未公开时的愿付参考 | 价值来自哪里 | 为什么不估得更高 |
|---|---:|---|---|
| Codex v0 | **¥100–300** | 通俗解释、当前财务整理、临床及交易边界，适合入门和求职 | 缺独家事实、深入技术比较与实际估值／现金模型 |
| 网页标准 | **¥50–150** | 商业模式、交易结构和尽调问题的组织 | 市场、概率及因果解释需返工；阅读价值高于原样决策价值 |
| 空间标准 | **¥30–100** | 技术论文、公司和监管线索的集中索引 | 解释深度有限，状态／标签及市场口径要再核查 |
| Mac 高级 | **¥0–50** | 快速获取临床、融资与公司新闻线索 | 免费替代性高，重复较多，临床日历及强结论修复负担较大 |

对已有行业基础的专业研究者，四份报告的愿付水平通常应靠近区间低端，甚至为零；新读者可能更看重节省整理时间。四份内容重叠，组合价值不能简单相加。**不建议把任何一份原样文件按可直接支持投资决策的成品尽调报告购买。** 定制研究服务和持续跟踪需要另定交付范围与价格。

可复用的价格假设与理由见 [valuations.json](examples/ai-pharma/no-skill-2026/evaluation/valuations.json)。

## 复用评价 skill 与复算

评价 skill 完整快照位于 [`skills/research-report-evaluator/`](skills/research-report-evaluator)，包含判据、六套用途权重、评分脚本、接口说明和原有测试。本次没有更改其评分协议。

```bash
# 从仓库根目录执行；Python 3，仅标准库
python3 examples/ai-pharma/no-skill-2026/scripts/replay.py

# 新建一份待人工填写的评审记录
python3 skills/research-report-evaluator/scripts/score_report.py init \
  --profile balanced --output /tmp/new-assessment.json

# 填写十维理由、证据位置和底线状态后计算；输出路径须尚不存在
python3 skills/research-report-evaluator/scripts/score_report.py score \
  /tmp/new-assessment.json --output /tmp/new-score.json
```

`replay.py` 离线校验原件及 skill 哈希、12 组评分记录、人数和算术。它不自动判定事实真伪、可读性、因果有效性或价格合理性。新报告需要人或评审 Agent 阅读与核查后填写，不能只运行计算器。

## 仓库结构与边界

```text
skills/research-report-evaluator/       # 评价 skill v1.1.0
examples/ai-pharma/no-skill-2026/
  reports/                             # 四份未修改原件
  manifest.json                        # 来源说明、大小、SHA-256
  EVALUATION.md                        # 每份十维理由、理解重建与修复顺序
  evaluation/records/                  # 人工评分与底线记录
  evaluation/scores/                   # 通用分及用途权重敏感性结果
  evaluation/evidence/                 # 核查台账、注册快照、算术结果
  evaluation/valuations.json           # 愿付参考与授权假设
  evaluation/skill_snapshot.json       # 评价方法版本与文件哈希
  scripts/replay.py                    # 离线复算入口
```

本次提交内容是无 skill 基线案例与评价方法；研报生成用的 guided skill 不在本次提交中。后续若增加 skill 生成样例，应单列目录，并补齐提示词、模型、日期、资源条件与重复运行记录，再讨论效果差异。

本次评审为 AI 辅助、非盲评，且包含对 Codex 输出的评价，存在自评偏差风险。评估把握为中等；公开理由和记录便于他人复核。正文只抽查关键支点，没有企业访谈、外部同行评审、模型实验或全文事实审计。

原报告内的提示语、建议及声明属于被评价材料，不作为仓库操作指令。四份原件中的原有缺陷保留作为样例，修复建议不代表已经修订报告。仓库公开不自动赋予第三方材料商用或转售权；本次未新增许可证，也未改变各文件既有权利。
