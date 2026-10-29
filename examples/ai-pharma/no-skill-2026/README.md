# 四份未使用 skill 的 AI 制药研报

此目录保存四份原始输出、评价记录与离线复算脚本。生成时均未使用研报生成 skill，由文件提供者说明。

- [仓库总览、评分和价值估计](../../../README.md)
- [逐份十维评审与修复建议](EVALUATION.md)
- [四份原件](reports/)
- [文件清单与 SHA-256](manifest.json)
- [核查台账](evaluation/evidence/source_checks.json)
- [评分记录](evaluation/records/)
- [价格假设](evaluation/valuations.json)

从仓库根目录执行：

```bash
python3 examples/ai-pharma/no-skill-2026/scripts/replay.py
```

评价日期为 2026-10-29，中国时间；主协议为 research-report-evaluator v1.1.0 / balanced。其他用途结果仅为权重敏感性。原件未修改，评审批注另存。
