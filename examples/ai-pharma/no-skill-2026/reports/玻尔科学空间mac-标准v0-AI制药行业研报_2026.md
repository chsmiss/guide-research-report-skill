# AI 制药行业研究报告（2026 年更新）

**综合研报：技术 · 市场 · 公司 · 投资（全球与中国对比）**

更新时间：2026 年 10 月

---

## 摘要

AI 制药正处在"技术加速、商业化兑现尚未完成"的临界阶段。经过过去几年生成式 AI 的快速渗透，人工智能已经覆盖从靶点发现到临床试验优化的新药研发全链条；但截至 2026 年年中，全球还没有一款"全流程由生成式 AI 设计"的新药获得美国 FDA 的完全批准，首个此类里程碑被普遍预测落在 2026–2028 年。[Clinical Trial Vanguard，2026](https://www.clinicaltrialvanguard.com/opinion/ai-drug-discovery-has-8-9-billion-in-hype-and-zero-fda-approvals-when-does-the-bill-come-due/) [Drug Target Review，2026](https://www.drugtargetreview.com/ai-in-drug-discovery-predictions-for-2026/1865962.article)

这份研报的核心结论如下：

1. **技术主线已经清晰。** 蛋白质结构预测与设计（AlphaFold 3 及 Chai-1、Boltz-1 等开源生态）、流匹配生成模型（逐步取代扩散模型成为小分子生成主流）、以及蛋白/基因组基础模型（ESM-3、Evo 2）是 2024–2026 年最实质性的进展，正在从论文进入产业工具链。

2. **市场规模是一个被口径撕裂的数字。** 狭义"AI in drug discovery"市场 2025 年约 23–69 亿美元、2030 年代初预测 130–250 亿美元（多数机构给 25% 左右 CAGR）；而中国机构的广义"AI 制药"口径 2025 年约 240–300 亿美元，相差 4–10 倍。引用和比较时必须先定口径。[Grand View Research，2026](https://www.grandviewresearch.com/industry-analysis/artificial-intelligence-drug-discovery-market)

3. **竞争格局呈"海外巨头 + 中国平台公司"双轨。** 海外以 Isomorphic Labs（Alphabet 系）、Recursion（已整合 Exscientia）、Schrödinger、Relay、Absci 为代表；中国以晶泰科技、英矽智能、深势科技、剂泰医药、百图生科、华深智药等为代表，普遍采用"平台授权 + 自研管线 + 海外 license-out"的混合货币化路径。

4. **资本端在 2025–2026 明显回暖，但高度头部集中。** 2025 年全球 AI 制药融资约 110 亿美元（DealForma 口径）；中国 2026 年前三季度融资额已超 2023–2025 三年总和，港股成为主要上市通道。

5. **临床端最接近"证明点"的是英矽智能的 rentosertib（ISM001-055）。** 其特发性肺纤维化 IIa 期结果于 2025 年发表于 *Nature Medicine*，是首个进入随机对照 IIa 期、靶点和分子均由生成式 AI 发现的管线，但仍是小样本、探索性次要终点，属于"概念验证"而非"疗效证明"。[Xu 等，2025](https://doi.org/10.1038/s41591-025-03743-2)

6. **政策与监管正从"观望"转向"主动规范"。** 中国在 2025–2026 年密集出台"人工智能+医药/监管"文件，明确 AI 的辅助定位、算法备案与模型验证要求；美国 FDA 则以"风险为基础的可信度框架"推进对 AI 支持监管决策的规范。

---

## 一、什么是 AI 制药，为什么现在需要它

AI 制药（AI for drug discovery / AI-driven pharma）指用机器学习、深度学习及大模型，辅助或部分替代新药研发中的关键环节，包括靶点发现、分子生成与设计、虚拟筛选、成药性（ADMET）预测、逆合成规划、以及临床试验的入组与分层。它兴起于一个长期困扰制药业的现实：新药研发投入持续攀升、回报却在下降。

这一现象常被概括为"Eroom 定律"（Eroom 是 Moore 的反写）——即每十亿美元研发投入带来的获批新药数量大约每九年减半。成本端最常引用的估计来自 DiMasi 等人：每个获批新药的平均自付研发成本约 13.95 亿美元（2013 年美元），资本化后约 26 亿美元。[DiMasi 等，2016](https://pubmed.ncbi.nlm.nih.gov/26928437/) [Applied Clinical Trials，2014](https://www.appliedclinicaltrialsonline.com/view/tufts-center-study-drug-development-cost-developing-new-drugs) 需要说明的是，这一数字本身存在争议：有研究以 2020 年数据给出中位数约 9.85 亿美元、均值约 13 亿美元，也有批评者认为 26 亿美元的资本化口径夸大了实际现金支出。[Wikipedia，无日期](https://en.wikipedia.org/wiki/Cost_of_drug_development) 但无论取哪个口径，结论方向一致：新药研发周期长（通常 10–15 年）、成功率低、成本高，这正是 AI 制药的核心价值主张——用数据与计算缩短周期、提高命中率、降低失败成本。

需要强调的是，AI 制药目前主要价值仍在**研发端提效**，而非替代临床验证。行业普遍承认：AI 可以提高候选分子的质量与产出速度，但一个分子能否获批，最终仍取决于人体内的安全性与有效性，这部分无法被计算模型跳过。

---

## 二、技术图谱：AI 正在改变哪些环节

### 1. 靶点发现与验证

这一环节用多组学数据整合、知识图谱、网络医学和因果推断从海量生物数据中筛选疾病相关靶点。代表工作包括单细胞多组学基础模型 scGPT、用于扰动效应因果识别的 CINEMA-OT（*Nature Methods*, 2024），以及多组学整合方向的综述与工具。需要强调，这类方法给出的多为相关性或预测性线索，真正的靶点"验证"仍依赖扰动实验和功能学证据。

### 2. 分子生成与设计

这是 AI 制药技术迭代最快的领域。成熟方法包括扩散模型、SE(3) 等变图神经网络（几何 GNN）、以及强化学习（如 REINVENT 4）。2024–2026 年的显著趋势是**流匹配（flow matching）取代扩散成为小分子生成的主流范式**：FlowMol（ICML 2024）、MolFORM、PAFlow（NeurIPS 2025）、FlowMol3（2026）以及"流匹配 + 强化学习微调"（*Nature Communications*, 2026）相继出现。[FlowMol，2024](https://icml.cc/virtual/2024/36820) [PAFlow，2025](https://neurips.cc/virtual/2025/poster/115118) 这些方法主要在计算机指标（in silico metrics）上验证，湿实验的成功率仍偏低，是当前公认的瓶颈之一。

### 3. 蛋白质结构预测与设计

这是 AI 制药最扎实、也最被验证的一环。**AlphaFold 3**（*Nature*, 2024）将预测范围从单条蛋白链扩展到蛋白质—小分子、蛋白质—核酸等全原子相互作用，并在 2024 年 11 月开源权重；其衍生开源模型 **Chai-1**（2024-10）与 **Boltz-1**（MIT, 2024）使全原子相互作用预测"民主化"。[AlphaFold 3，2024](https://www.nature.com/articles/s41586-024-07487-w) 在蛋白**设计**端，RFdiffusion 及其小分子 binder 设计版本 RFdiffusionAA（*Science*, 2024）支撑了从头设计。[RFdiffusionAA，2024](https://www.science.org/doi/10.1126/science.adl2528) 静态结构预测接近成熟，但柔性、构象系综和绝对结合亲和力预测仍是短板。

### 4. ADMET 性质预测

吸收、分布、代谢、排泄、毒性（ADMET）预测以图神经网络为主流。ADMET-AI（基于 Chemprop-RDKit，覆盖 41 项性质）、ADMETlab 3.0 是常用工具；TDC 作为基准平台暴露过排行榜模型的**可复现性**问题，提示该领域存在数据泄漏与评估标准不统一的隐患。[ADMET-AI，2024](https://academic.oup.com/bioinformatics/article/40/7/btae416/7698030)

### 5. 逆合成与合成可及性

模板型、半模板与模板自由（GPT 类）方法并行，RSGPT（*Nature Communications*, 2025）在百亿分子上预训练。[RSGPT，2025](https://www.nature.com/articles/s41467-025-62308-6) 但合成可及性评分（RAscore、SYBA、SCScore）与真实化学家规划的一致性有限——生成模型产出的分子"好看但难合成"是现实痛点。

### 6. 临床试验优化

用 AI 做患者分层、入组优化、终点与结果预测。代表性工作包括 TrialBench（23 个数据集、8 个任务，*Scientific Data*, 2025）、用于 II 期结果预测的 inClinico（回顾性准确率约 79%）、以及阿尔茨海默病试验中的 AI 患者分层（AMARANTH，*Nature Communications*, 2025）。[TrialBench，2025](https://www.nature.com/articles/s41597-025-05680-8) 这一环节的模型多缺乏前瞻性验证。

### 7. 大语言模型与基础模型

Tx-LLM（Google，2024，709 数据集、66 个任务）、ESM-3（980 亿参数，序列—结构—功能生成）、Evo 2（Arc Institute 的跨 DNA/RNA/蛋白基因组模型）把生成式 AI 扩展到蛋白工程与基因组设计。[Tx-LLM，2024](https://arxiv.org/abs/2406.06316) [ESM-3，2024](https://www.evolutionaryscale.ai/blog/esm3-release) [Evo 2，2025](https://arcinstitute.org/tools/evo)

**综合判断**：静态结构预测与生成模型已在产业中可用，但"模型预测—湿实验验证—人体临床"的闭环仍未完全打通。核心瓶颈集中在高质量标注数据稀缺、湿实验闭环成本高、基准标准化与前瞻验证缺失三件事上。

---

## 三、市场规模：一个被口径撕裂的数字

AI 制药市场数据最大的问题不是"不知道多大"，而是**各机构定义不同、口径互不可比**。全球主要咨询机构的估算如下（2025 年基期，单位：亿美元）：

| 机构 | 口径 | 基准年数值 | 预测年数值 | CAGR |
|---|---|---|---|---|
| Grand View Research | AI in drug discovery | 2025 年 23 亿 | 2033 年 138 亿 | 24.8%（2026–2033） |
| Mordor Intelligence | AI in drug discovery | 2026 年 25.8 亿 | 2032 年 129.6 亿 | 25.94%（2027–2032） |
| MarketsandMarkets | AI in drug discovery | 2026 年 50.9 亿 | 2031 年 175.6 亿 | 约 28% |
| Precedence Research | AI in drug discovery | 2025 年 69.3 亿 | 2035 年约 178 亿 | 9.9%（2026–2035） |
| Roots Analysis | AI-based drug discovery | 2025 年 60 亿 | 2035 年 250 亿 | 约 15% |

数据来源：[Grand View Research](https://www.grandviewresearch.com/industry-analysis/artificial-intelligence-drug-discovery-market)、[Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/artificial-intelligence-in-drug-discovery-market)、[MarketsandMarkets](https://www.marketsandmarkets.com/PressReleases/ai-in-drug-discovery.asp)、[Precedence Research](https://www.precedenceresearch.com/artificial-intelligence-in-drug-discovery-market)、[Roots Analysis](https://www.rootsanalysis.com/reports/ai-based-drug-discovery-market.html)

同一细分市场，2025 年的估值从 23 亿到 69 亿美元不等，差距约 3 倍；到 2030 年代初的预测更是横跨 130–250 亿美元。差异主要来自：统计的环节范围（是否含软件、服务、自动化实验室、临床试验优化）、地域口径，以及是否把 AI 公司拿到的合作/授权里程碑算作"市场规模"。

一个更具误导性的口径是"AI 制药"的广义统计。中国机构（如丁香园 Insight、中研普华）给出的全球"AI 制药"市场 2025 年约为 **241 亿—298 亿美元**，2035 年预测可到 460 亿美元以上，这一口径通常把 AI 在药物研发全链条的软硬件、数据、服务与相关交易都纳入。[21 经济网，2026](https://www.21jingji.com/article/20260918/herald/f10c933797e2a875c7f46af198ab0647.html) [中研普华，2026](https://www.chinairn.com/news/20260706/172609533.shtml) 与狭义口径相差 4–10 倍，跨口径直接比较没有意义。

**中国本土市场**（狭义，人民币口径）体量很小：华经/Wind/艾媒口径 2024 年约 5.6 亿元（同比 +36.6%）、2025 年突破 6 亿元；中研普华口径 2024 年 7.3 亿元、2025 年 12.1 亿元（+65.8%）、2028 年预测超 58.6 亿元。[艾媒咨询，2025](https://www.iimedia.cn/c1020/109755.html) [华经产业研究院，2025](https://www.huaon.com/channel/yzsb/1181281.html) 两者对 2025 年的判断（6.2 亿 vs 12.1 亿）也相差近一倍。这说明中国 AI 制药的**软件/服务收入盘子仍小**，行业价值更多体现在公司股权估值、BD 交易与管线权益，而非当期市场收入。

**融资端**的规模更能反映行业热度：

- 全球：DealForma 统计 2025 年 AI/ML 药物发现融资 **348 轮、约 110 亿美元**（2024 年为 264 轮、89 亿美元）。[DealForma，2026](https://dealforma.com/ai-ml-drug-discovery-and-licensing-rd-ma-ventures-and-ipos-2025-review/) CB Insights 仅统计股权口径时 2024 年约 38 亿美元，口径差异同样显著。[CB Insights，2024](https://www.cbinsights.com/research/ai-drug-research-development-market-map/)
- 中国：医药魔方统计 2025 年 **32 笔、67.54 亿元人民币（+130.5%）**，2024 年为 40 笔、29.3 亿元。[医药魔方，2026](https://www.pharmcube.com/newsLibrary/detail?id=108a3767c1dc14abb8ae3d96c66f10b8) 投中嘉川 CVSource 统计 2026 年前 9 个月已达 **57 笔、157.65 亿元**，超过 2023–2025 三年总和，但前 4 笔即占六成，头部集中度极高。[新浪财经，2026](https://finance.sina.com.cn/tech/roll/2026-09-20/doc-inisnhay9248573.shtml)

---

## 四、竞争格局：海外与中国的两条路线

### 1. 海外代表公司

| 公司 | 定位/技术平台 | 2024–2026 关键进展 |
|---|---|---|
| Isomorphic Labs | Alphabet/DeepMind 系，AI-first 药物设计（IsoDDE 引擎） | 2024 年初与礼来、诺华签近 30 亿美元合作；2025 年 3 月融资 6 亿美元，2026 年 5 月 B 轮再融 21 亿美元 |
| Recursion（RXRX） | 湿实验+干实验闭环（Recursion OS/LOWE） | 2024-11 完成对 Exscientia 的全股票收购；收缩早期管线，聚焦 REC-4881/617/7735 |
| Schrödinger（SDGR） | 物理计算平台 + 软件/SaaS + 自研管线 | SGR-1505（MALT1）I 期 ORR 22%；SGR-2921（CDC7）2025-08 因安全性终止 |
| Relay（RLAY） | Dynamo 平台（蛋白运动/别构位点） | lirafugratinib（FGFR2）2026-09 获 FDA 批准；RLY-2608（PI3Kα）进入关键期 |
| Absci（ABSI） | 生成式抗体设计 + 高通量湿实验室 | ABS-101（抗 TL1A）临床中；与阿斯利康等合作 |
| Insilico Medicine（3696.HK） | Pharma.AI 平台 + 自研管线 | 2025-12 港交所上市；rentosertib IIa 期发表于 Nature Medicine |

**Isomorphic Labs** 是当前最受关注的海外标的：背靠 Alphabet/DeepMind，2024 年 1 月与礼来（首付 4500 万美元 + 最高 17 亿美元里程碑）和诺华（首付 3750 万美元 + 最高 12 亿美元里程碑）达成合计近 30 亿美元合作，此后与诺华扩容并新增 J&J 合作；2026 年 5 月完成 21 亿美元 B 轮融资（Thrive 领投，Alphabet、GV、CapitalG、淡马锡等参与）。[Fierce Biotech，2024](https://www.fiercebiotech.com/biotech/alphabets-isomorphic-stacks-two-new-deals-lilly-novartis-worth-nearly-3b-ahead-buzzy-jpm) [Isomorphic Labs，2026](https://www.isomorphiclabs.com/articles/isomorphic-labs-announces-series-b-investment-round) 值得注意的是，其自营管线的靶点、适应症与阶段尚未公开披露，外界对"估值与兑现"的判断仍依赖合作交易而非临床数据。

**Recursion** 于 2024 年 8 月宣布以约 6.88 亿美元全股票收购 Exscientia、11 月完成整合，成为 AI 制药领域最具标志性的并购。[Reuters，2024](https://www.reuters.com/markets/deals/biotech-firm-recursion-buy-smaller-peer-exscientia-688-million-2024-08-08/) 整合后公司收缩了多个早期管线（停产 REC-2282、REC-3964，去优先 REC-994），聚焦 REC-4881（家族性腺瘤性息肉病）、REC-617（原 Exscientia 的 CDK7 抑制剂）等，2025 财年营收 7470 万美元，显示平台型公司仍在"以合作收入养研发"的阶段。

### 2. 中国代表公司

| 公司 | 定位/技术平台 | 关键进展（2024–2026） |
|---|---|---|
| 晶泰科技（2228.HK） | AI-CRO + 自动化湿实验室 | 2024-06 港股 18C 首股；与辉瑞、礼来（累计约 6 亿美元）合作 |
| 英矽智能（3696.HK） | Pharma.AI 平台 + 自研管线 | 2025-12 港股上市；rentosertib IIa 期；与 Exelixis、美纳里尼 3 项授权（最高 21 亿美元） |
| 深势科技 | AI4S 基础模型（Uni-Mol/Uni-Fold）+ Hermite 平台 | 2025-12 完成超 8 亿元 C 轮；服务 70+ 生命科学企业 |
| 剂泰医药（7666.HK） | AI 递送/制剂 + 药物发现（NanoForge） | 2026-05 港股上市；2026-10 与礼来签组织特异性 LNP 合作（里程碑最高约 11 亿美元） |
| 百图生科 | 蛋白质大模型 xTrimo（2680 亿参数） | 2023-10 与赛诺菲合作；2026 被曝递表港交所 |
| 华深智药 | AI 抗体/双抗设计（Earendil Labs） | 2026-03 完成 7.87 亿美元 B 轮；与赛诺菲、基因泰克多项合作 |

**晶泰科技**是"AI + 自动化湿实验"的代表，2024 年 6 月成为港交所 18C 规则下首家上市的 AI 制药企业，2024 年营收 2.664 亿元（+52.8%），业务以 AI-CRO 和平台服务为主，与辉瑞（晶型/多晶筛选、Paxlovid 相关）和礼来（2023 年 2.5 亿美元小分子合作）绑定。[晶泰科技，2024](https://ir.xtalpi.com/media/hmtn0mw1/2024060400065.pdf)

**英矽智能**是"生成式 AI + 自研管线"路线的全球标杆，2025 年 12 月 30 日登陆港交所，募资 22.77 亿港元，为 2025 年香港最大生物医药 IPO，上市后现金及银行存款达 3.93 亿美元。[英矽智能，2025](https://insilico.com/news/p010170up1-insilico-medicine-lists-on-hong-kong-sto) 其商业模式是"平台 + 管线"双轮：Pharma.AI 软件平台服务全球前二十大药企中的 13 家，2025 年软件收入同比 +23.8%；同时推进自研管线（8 个处于临床开发，含 2 个 II 期、4 个 I 期），并通过对外授权/合作（Exelixis、美纳里尼、TaiGen 等）获取首付与里程碑付款。2025 年全年总收入 5624 万美元。[英矽智能，2026](https://insilico.com/news/ohz9ozx0t1-insilico-medicine-announces-2025-annual)

**华深智药（Helixon/Earendil Labs）**是 2026 年的资本亮点：3 月完成 7.87 亿美元 B 轮（据称创下当年全球生物技术融资纪录），并先后与赛诺菲（2025-04 双抗 18.45 亿美元、2026-01 自身免疫 25.6 亿美元）和基因泰克（最高超 15 亿美元）达成合作，凸显"AI 抗体设计 + 大厂背书"的融资逻辑。

### 3. 三种商业模式

把上述公司归拢，AI 制药主要存在三种变现路径，现实中多为混合：

1. **平台/工具授权（AI-CRO 或 SaaS）**：卖软件、卖计算服务或研发服务，如晶泰、深势（Hermite）、Schrödinger 的软件许可。现金流相对确定，但天花板取决于客户预算。
2. **自研管线（AI-Biotech）**：自己推进候选药物、走临床，如英矽智能、Relay、Recursion 的部分资产。潜在回报最高，但临床风险与烧钱速度也最高。
3. **对外授权/合作（license-out / 里程碑）**：把 AI 发现的资产或平台能力卖给大药企，收首付+里程碑+销售分成，如华深智药、百图生科、剂泰与礼来的合作。这是当前中国公司快速货币化最常用的路径。

三条路线的共同难点是：**平台能力需要"湿实验闭环 + 临床验证"背书，而这两样恰好最烧钱、最慢**。这是理解 AI 制药公司高融资额与普遍亏损并存的关键。

---

## 五、临床进展与标志性成果：从"能用"到"获批"的距离

### 标志性案例：rentosertib（ISM001-055）

英矽智能的 **rentosertib**（原 ISM001-055）是目前 AI 制药最接近"概念验证完成"的管线，其靶点 TNIK 和分子都由生成式 AI 平台发现，且 TNIK 是特发性肺纤维化（IPF）领域的 first-in-class 靶点。2025 年 6 月发表于 *Nature Medicine* 的 IIa 期试验（GENESIS-IPF）共入组 71 例患者，随机分至 30 mg QD、30 mg BID、60 mg QD 或安慰剂，治疗 12 周。[Xu 等，2025](https://doi.org/10.1038/s41591-025-03743-2)

关键结果：主要终点为安全性（至少发生一例治疗相关不良事件的患者比例），各剂量组与安慰剂相似（72.2%–83.3% vs 70.6%）；有效性为探索性次要终点，其中 **60 mg QD 组的用力肺活量（FVC）平均 +98.4 mL，而安慰剂组为 −20.3 mL**，同时观察到胶原相关生物标志物（COL1A1、MMP10、FAP）下降。论文结论是"安全可耐受，值得更大规模、更长周期的验证"。

这个案例值得逐层理解，它同时说明 AI 制药的**突破与局限**：

- **突破**：一个靶点（TNIK）和一个分子都由生成式 AI 发现的管线，走完了 IIa 期随机对照，并在 FVC 上出现方向性改善信号——这是 AI-first 药物研发迄今最扎实的临床证据。
- **局限**：样本量小（n=71）、单国（中国）、周期短（12 周）、有效性是探索性终点，且主要终点是安全性而非疗效。它证明的是"AI 管线能走到临床并显示早期信号"，**不是**"AI 设计的药有效"。作者本人在论文中也强调需更大规模验证。

### 其他代表性临床数据

| 资产 | 公司 | 适应症 | 阶段 | 关键结果 |
|---|---|---|---|---|
| rentosertib（ISM001-055） | 英矽智能 | IPF | IIa | 60 mg QD 组 FVC +98.4 mL vs 安慰剂 −20.3 mL（Nature Medicine） |
| REC-4881 | Recursion | 家族性腺瘤性息肉病 | 1b/2 | 75% 可评估患者息肉负荷下降，12 周中位降 43%（公司自报） |
| SGR-1505 | Schrödinger | R/R B 细胞淋巴瘤 | I | ORR 22%（10/45）；WM 5/5 缓解（EHA 2025） |
| RLY-2608（zovegalisib）+ 氟维司群 | Relay | PIK3CA 突变乳腺癌 | 1/2 | mPFS 10.3 个月，ORR 38.7%（ASCO 2026） |
| lirafugratinib | Relay（授权 Elevar） | FGFR2 胆管癌 | 获批 | 2026-09-23 获 FDA 批准 |

除 rentosertib 经同行评议外，上表多数数据来自公司新闻稿或会议摘要，尚未独立发表，需谨慎对待。[CancerNetwork，2026](https://www.cancernetwork.com/)

### 关键判断：为什么"零批准"不能简单理解为"失败"

截至 2026 年年中，尚无一款"全流程生成式 AI 设计"的新药获得 FDA 完全批准，多个追踪机构预计首个此类批准出现在 2026–2028 年。[Clinical Trial Vanguard，2026](https://www.clinicaltrialvanguard.com/opinion/ai-drug-discovery-has-8-9-billion-in-hype-and-zero-fda-approvals-when-does-the-bill-come-due/) 但这有两点需要注意：

1. **"AI 参与"与"AI 全程设计"是两回事。** 现实中大量获批或在研药物都用了计算辅助（分子对接、结构优化、理化性质预测），只是没有被打上"AI 药物"标签。边界模糊使得"第一款 AI 药物"的统计口径本身就有争议。
2. **一个近似的边界案例是 Relay 的 lirafugratinib**：它 2026 年 9 月获 FDA 批准用于 FGFR2 融合/重排胆管癌，其发现过程深度依赖计算蛋白动力学（Relay 的 Dynamo 平台），属于"计算/结构驱动"而非"生成式 AI 驱动"的药物。它提示行业正从"结构计算辅助"滑向"生成式 AI 全程设计"，真正的分水岭尚未到来。

因此，更准确的判断是：**AI 制药的临床转化仍处于早期但已跨过"能否进入人体"的门槛，尚未跨过"能否成为获批药物"的门槛**。

---

## 六、政策与监管：中国密集加码，美国以风险为基础

### 中国：从产业鼓励到监管规范化

中国在 2025–2026 年密集出台政策，形成"产业激励 + 监管规范 + 数据合规"的三层框架：

- **顶层设计**：国务院 2025 年 8 月印发《关于深入实施"人工智能+"行动的意见》（国发〔2025〕11 号），把"人工智能+科学技术"（加速科学发现）列为六大行动之一。[国务院，2025](https://www.gov.cn/zhengce/content/202508/content_7037861.htm)
- **行业落地**：国家卫健委、发改委、工信部、中医药局、疾控局五部门 2025 年 11 月发布《关于促进和规范"人工智能+医疗卫生"应用发展的实施意见》，设 2027/2030 目标。[中新网，2025](https://m.chinanews.com/wap/detail/cht/zw/10509546.shtml)
- **监管侧**：国家药监局 2026 年 4 月发布《关于"人工智能+药品监管"的实施意见》（国药监综〔2026〕6 号），提出"人机协同智能审评审批"等七大方向，设定 2030/2035 目标，并**明确 AI 的辅助型定位、算法备案与模型验证要求**。[国家药监局，2026](https://www.nmpa.gov.cn/xxgk/fgwj/gzwj/gzwjzh/20260402091552114.html)

在数据合规层面，**《人类遗传资源管理条例实施细则》**（科技部令第 21 号，2023）把受管控的"人遗信息"限定为基因/基因组数据（不含临床、影像、蛋白质、代谢数据），并对外方单位与 500 例以上外显子/基因组测序信息的出境设置安全审查。[科技部，2023](https://www.most.gov.cn/xxgk/xinxifenlei/fdzdgknr/fgzc/bmgz/202306/t20230601_186416.html) 叠加《数据安全法》《个人信息保护法》与生成式 AI/算法备案要求，AI 制药公司面临"数据可用性"与"合规成本"的持续权衡。

### 美国：以风险为基础的渐进规范

美国 FDA 于 2025 年 1 月发布 AI 支持监管决策的指南草案，采用"以风险为基础的可信度框架"，即 AI 用于监管决策时的验证强度应与其风险等级匹配。这与中国的"AI 辅助定位"思路方向相近，但美国更强调风险分级与灵活性，中国更强调系统建设与全生命周期监管。

### 中美差异要点

| 维度 | 中国 | 美国 |
|---|---|---|
| 数据 | 统一的人遗/健康数据管控；本土公司可借政策整合临床数据，但跨境受限 | 数据分散（EHR/保险/隐私 HIPAA），人遗跨境限制少 |
| 监管 | "AI+药品监管"实施意见推进监管智能化；申报沿用 ICH+个案监管科学 | FDA 以风险为基础的可信度框架草案 |
| 资本 | 港股为主要上市通道，融资回暖但头部集中 | 生物科技资本成熟、一级市场体量大 |
| 商业化 | 平台授权 + 自研管线 + 海外 license-out | 平台/权益金模式成熟，AI 工具公司多被收购 |

---

## 七、挑战与风险

1. **数据稀缺、质量与泄漏**：高质量、标准化、可互操作的训练数据不足，且多个基准暴露过数据泄漏与可复现性问题，导致"榜单性能"与实际能力脱节。
2. **湿实验验证率低**：生成分子的合成可及性差、实验命中率低，"模型产出的分子好看但难合成、难验证"是普遍痛点。
3. **临床转化风险**：从计算机指标到人体有效，中间隔着 ADMET、毒理、给药、患者分层等多重关卡；rentosertib 的 IIa 期也只是早期信号。
4. **盈利模式未跑通**：多数公司长期亏损、收入依赖少数大客户或合作里程碑，自研管线烧钱快，平台业务天花板有限。
5. **估值与泡沫风险**：2025–2026 融资回暖、大额 BD 频现，但"AI 制药"标签溢价明显；若首个 AI 药物获批一再推迟，估值可能再次回调。
6. **监管与伦理不确定**：AI 的辅助边界、算法备案、数据出境、责任归属（AI 推荐失误谁负责）等规则仍在演化中。

---

## 八、展望与判断

综合以上证据，我们给出三点判断：

**第一，技术已具备产业可用性，但"AI 价值"的兑现取决于闭环而非单点指标。** 结构预测、生成模型、基础模型已经从论文变成工具；下一个竞争焦点是"模型—湿实验—临床"的数据闭环能力，单纯比拼分子生成指标的意义正在下降。

**第二，2026–2028 年将出现决定行业叙事的里程碑。** 若首个全流程 AI 设计的药物获批（或 rentosertib 在更大 III 期验证有效），行业叙事将从"技术演示"转向"疗效证明"；若一再推迟，估值可能承压。市场对 Isomorphic、英矽智能、Relay 等公司的定价，本质上是在押注这一时间点。

**第三，中国公司的机会在于"工程化落地 + 出海 BD"，而非纯技术原创。** 中国在算力成本、工程人才、临床试验执行效率和 license-out 变现上有相对优势，头部公司已形成"平台+管线+授权"的组合打法；但数据合规、监管细化与盈利兑现仍是不确定因素。相对而言，海外巨头在基础模型和与大型药企的深度绑定上仍占优势。

**对关注者的实用提示**：评估一家 AI 制药公司的价值，建议优先看三件事——①有没有进入人体的临床资产及其结果（而非仅管线数量和计算机指标）；②有没有能持续产生现金流的合作/授权（而非一次性大额 BD）；③湿实验能力与数据闭环是否真实（而非只有模型）。这三者比"用了多先进的生成模型"更能预测商业兑现。

---

## 免责声明

本报告基于截至 2026 年 10 月的公开信息撰写，仅供研究与参考，不构成任何投资建议。市场规模的预测来自各咨询机构，口径不一、且多为付费报告摘要数字，请以原始报告为准；融资与交易金额多转引自第三方数据库或公司自报，未经独立审计；临床数据除注明同行评议外，多为公司新闻稿或会议摘要，未经独立验证。部分 2026 年事件（如融资、股价、上市）会随时间更新。

---

## 参考来源

- Grand View Research（2026）。[Artificial Intelligence In Drug Discovery Market Report, 2033](https://www.grandviewresearch.com/industry-analysis/artificial-intelligence-drug-discovery-market)
- Mordor Intelligence（2026）。[Artificial Intelligence in Drug Discovery Market](https://www.mordorintelligence.com/industry-reports/artificial-intelligence-in-drug-discovery-market)
- MarketsandMarkets（2026）。[AI in Drug Discovery Market](https://www.marketsandmarkets.com/PressReleases/ai-in-drug-discovery.asp)
- Precedence Research（2026）。[Artificial Intelligence in Drug Discovery Market](https://www.precedenceresearch.com/artificial-intelligence-in-drug-discovery-market)
- Roots Analysis（2026）。[AI-based Drug Discovery Market](https://www.rootsanalysis.com/reports/ai-based-drug-discovery-market.html)
- DealForma（2026）。[AI/ML Drug Discovery and Licensing: R&D, M&A, Ventures and IPOs 2025 Review](https://dealforma.com/ai-ml-drug-discovery-and-licensing-rd-ma-ventures-and-ipos-2025-review/)
- CB Insights（2024）。[AI Drug Research & Development Market Map](https://www.cbinsights.com/research/ai-drug-research-development-market-map/)
- 21 经济网（2026）。[AI 制药市场相关报道](https://www.21jingji.com/article/20260918/herald/f10c933797e2a875c7f46af198ab0647.html)
- 中研普华（2026）。[AI 制药市场分析](https://www.chinairn.com/news/20260706/172609533.shtml)
- 艾媒咨询（2025）。[AI 制药市场规模](https://www.iimedia.cn/c1020/109755.html)
- 华经产业研究院（2025）。[AI 制药行业研究](https://www.huaon.com/channel/yzsb/1181281.html)
- 医药魔方（2026）。[AI 制药融资统计](https://www.pharmcube.com/newsLibrary/detail?id=108a3767c1dc14abb8ae3d96c66f10b8)
- 新浪财经（2026）。[AI 制药融资报道](https://finance.sina.com.cn/tech/roll/2026-09-20/doc-inisnhay9248573.shtml)
- Xu 等（2025）。[A generative AI-discovered TNIK inhibitor for idiopathic pulmonary fibrosis: a randomized phase 2a trial](https://doi.org/10.1038/s41591-025-03743-2)（*Nature Medicine*）
- Clinical Trial Vanguard（2026）。[AI Drug Discovery Has $8.9 Billion in Hype and Zero FDA Approvals](https://www.clinicaltrialvanguard.com/opinion/ai-drug-discovery-has-8-9-billion-in-hype-and-zero-fda-approvals-when-does-the-bill-come-due/)
- Drug Target Review（2026）。[AI in drug discovery: predictions for 2026](https://www.drugtargetreview.com/ai-in-drug-discovery-predictions-for-2026/1865962.article)
- DiMasi 等（2016）。[Innovation in the pharmaceutical industry: New estimates of R&D costs](https://pubmed.ncbi.nlm.nih.gov/26928437/)
- Applied Clinical Trials（2014）。[Tufts CSDD: Cost to Develop a New Drug Is $2.6 Billion](https://www.appliedclinicaltrialsonline.com/view/tufts-center-study-drug-development-cost-developing-new-drugs)
- Wikipedia（无日期）。[Cost of drug development](https://en.wikipedia.org/wiki/Cost_of_drug_development)
- Isomorphic Labs（2026）。[Isomorphic Labs announces Series B investment round](https://www.isomorphiclabs.com/articles/isomorphic-labs-announces-series-b-investment-round)
- Fierce Biotech（2024）。[Alphabet's Isomorphic stacks two deals with Lilly, Novartis](https://www.fiercebiotech.com/biotech/alphabets-isomorphic-stacks-two-new-deals-lilly-novartis-worth-nearly-3b-ahead-buzzy-jpm)
- Reuters（2024）。[Recursion to buy Exscientia for $688 million](https://www.reuters.com/markets/deals/biotech-firm-recursion-buy-smaller-peer-exscientia-688-million-2024-08-08/)
- 英矽智能（2025）。[Insilico Medicine Lists on Hong Kong Stock Exchange](https://insilico.com/news/p010170up1-insilico-medicine-lists-on-hong-kong-sto)
- 英矽智能（2026）。[Insilico Medicine Announces 2025 Annual Results](https://insilico.com/news/ohz9ozx0t1-insilico-medicine-announces-2025-annual)
- 晶泰科技（2024）。[上市招股相关文件](https://ir.xtalpi.com/media/hmtn0mw1/2024060400065.pdf)
- CancerNetwork（2026）。[RLY-2608 相关报道](https://www.cancernetwork.com/)
- 国务院（2025）。[关于深入实施"人工智能+"行动的意见](https://www.gov.cn/zhengce/content/202508/content_7037861.htm)
- 中新网（2025）。[五部门促进规范"人工智能+医疗卫生"应用发展的实施意见](https://m.chinanews.com/wap/detail/cht/zw/10509546.shtml)
- 国家药监局（2026）。[关于"人工智能+药品监管"的实施意见](https://www.nmpa.gov.cn/xxgk/fgwj/gzwj/gzwjzh/20260402091552114.html)
- 科技部（2023）。[人类遗传资源管理条例实施细则](https://www.most.gov.cn/xxgk/xinxifenlei/fdzdgknr/fgzc/bmgz/202306/t20230601_186416.html)
- AlphaFold 3（2024）。[Accurate structure prediction of biomolecular interactions with AlphaFold 3](https://www.nature.com/articles/s41586-024-07487-w)
- RFdiffusionAA（2024）。[De novo design of protein structure and function with RFdiffusion](https://www.science.org/doi/10.1126/science.adl2528)
- FlowMol（2024）。[ICML 2024](https://icml.cc/virtual/2024/36820)
- PAFlow（2025）。[NeurIPS 2025](https://neurips.cc/virtual/2025/poster/115118)
- RSGPT（2025）。[*Nature Communications*](https://www.nature.com/articles/s41467-025-62308-6)
- ADMET-AI（2024）。[*Bioinformatics*](https://academic.oup.com/bioinformatics/article/40/7/btae416/7698030)
- TrialBench（2025）。[*Scientific Data*](https://www.nature.com/articles/s41597-025-05680-8)
- Tx-LLM（2024）。[arXiv](https://arxiv.org/abs/2406.06316)
- ESM-3（2024）。[EvolutionaryScale](https://www.evolutionaryscale.ai/blog/esm3-release)
- Evo 2（2025）。[Arc Institute](https://arcinstitute.org/tools/evo)
