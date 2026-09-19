# 传染病预测视界的机制基准与实证校准差距

本工作目录为论文研究与正式投稿的**唯一核心权威工作区**，所有历史草稿、冗余副本及中间构建垃圾已全面剔除。

## 论文手稿与复现包说明

根目录下的 **`main.tex`** 为正式提交稿（35 页全文，标题《传染病预测视界的机制基准与实证校准差距》；本稿按中文期刊体例排版，不含英文题名与英文摘要），经由 Tectonic 编译生成 **`main.pdf`**（35 页；0 错误、0 未定义引用、0 Overfull、0 Underfull）。

推导手册位于 `derivations/derivations_manual.tex`（编译生成 `derivations/derivations_manual.pdf`，10 页），提供全文核心定理的逐行数学证明。补充材料位于 `supplementary/supplementary_tables.tex`（编译生成 `supplementary/supplementary_tables.pdf`），收录正文引用的全部支持表格 S1--S9。
`archive/` 目录存放早期的探索稿（如 `archive/main_reframed.tex` 及 `archive/REWRITE_REPORT.md`）。

本包提供全流程一键复现与自动化一致性核验：
```bash
python scripts_v2/check_consistency.py        # 执行 21 大类严格数理、实证与路径一致性断言
tectonic main.tex                             # 编译主稿
tectonic derivations/derivations_manual.tex   # 编译推导手册
tectonic supplementary/supplementary_tables.tex # 编译补充材料 S1--S9
```

FluSight **三个锁定 release**（v1.0.0 / v1.1.0 / v1.2.0）的 final-vintage 严格外部审计已完成，证据文件为 `reports_v3/flusight_v1.0_strict.json`、`flusight_v1.1_strict.json`、`flusight_v1.2_strict.json`（逐单元 CSV 见同名 `.csv`），三者均可从原始文件逐字节复现。扩展评分面板见 `reports_v3/flusight_v1.*_extended.json`：它在同一批预测单元上追加 WIS 分解（离散度、低估惩罚、过度预测惩罚）、50/80/95% 覆盖率、区间宽度与随机化 PIT，按流行阶段分层，并把本稿的启发式插件式机制预测器作为同批单元对照评分。实证报告见 `reports_v3/EMPIRICAL_EXTENSION_REPORT.md`；协议、锁定 commit 与逐文件 SHA-256 见 `data/flusight/README.md` 与 `data/input_hashes.json`（覆盖全部 237 个输入文件的 SHA-256 清单，由门禁逐条复核）。

> **工作目录与稿件规范说明：**
> 1. 本目录即为论文主稿的根目录，核心 LaTeX 文档为根目录下的 **`main.tex`**，编译输出为 **`main.pdf`**（35 页，Tectonic 编译）。
> 2. 内部评审材料（审稿意见、评审报告与作者回复信）均不纳入本公开复现包，以避免双盲匿名性泄漏。

---

## 一、目录结构与核心清单

```text
.
├── main.tex                                        # 精炼重构版 LaTeX 论文主文档源码（0 错误、0 溢出）
├── main.pdf                                        # 精炼重构版 Tectonic 编译产物 (35 页)
├── archive/main_reframed.tex                               # 重构稿 LaTeX 源码（条件锐风险 + 版本化外部审计）
├── archive/main_reframed.pdf                               # 重构稿 Tectonic 编译产物 (10 页, 0 未定义引用/0 溢出)
├── references.bib                                  # 净化后的参考文献库（46 篇，双向完全闭合：0 缺失、0 未引项）
├── README.md                                       # 本说明文件：项目架构、自洽规范与复现指南
├── MANIFEST.md                                     # 全量有效交付文件与磁盘真实路径全量对照表
├── environment.yml                                 # Conda 运行环境配置文件
├── LICENSE                                         # 开源学术授权协议
├── derivations/                                    # 数学定理严格推导与证明手册
│   ├── derivations_manual.tex                      # 逐行数学证明源码（统一 C >= 1,300）
│   └── derivations_manual.pdf                      # 推导手册编译就绪 PDF
├── presentation/                                   # 成果报告与展示材料
│   ├── epidemic_predictability_masterclass.pptx    # Masterclass 汇报幻灯片
│   └── index.html                                  # 交互式结果全景展示网页
├── data/                                           # 实证研究原始与清洗后核心数据集
│   ├── micro/                                      # 个体传播链微观数据
│   │   ├── guinea_ebola_faye2015/                  # 几内亚科纳克里埃博拉传播网络数据
│   │   ├── hong_kong_adam2020/                     # 香港 COVID-19 接触追踪集群数据
│   │   ├── lloyd_smith_2005/                       # 超级传播文献基准
│   │   └── micro_branching_fit_results.json        # 微观似然拟合参数结果
│   ├── panels/                                     # 51 个州级面板数据 (Delta, Omicron, Flu, RSV)
│   │   ├── covid_weekly_hospitalizations.csv.gz    # COVID-19 州级周度住院序列
│   │   ├── flu_weekly_hospitalizations.csv.gz      # 流感州级周度住院序列
│   │   ├── rsv_weekly_hospitalizations.csv.gz      # RSV 州级周度住院序列
│   │   └── us_state_daily_hospitalizations.csv     # 州级逐日住院基础序列
│   ├── hub/                                        # COVID-19 Forecast Hub 官方顶级集成模型预测与评估
│   │   ├── *-COVIDhub-ensemble.csv.gz              # 12 个代表性预测原点的官方集成模型原始预测归档 (逐周点位与分位数)
│   │   └── forecast_hub_operational_evaluation.json# 预测枢纽 12 个原点 1--4 周技能衰减与持续性基线对比评估结果
│   └── flusight/                                   # FluSight 版本化外部审计输入与协议
│       ├── README.md                               # 锁定 release、评分协议与逐文件 SHA-256 说明
│       ├── file_hashes.json                        # 全部下载文件的 SHA-256 清单
│       ├── upstream_sources/                       # 锁定的 release README / LICENSE / 模型元数据
│       ├── v1.0.0/                                 # v1.0.0 冻结真值 + ensemble/baseline 预测
│       └── v1.1.0/                                 # v1.1.0 冻结真值 + ensemble/baseline 预测
├── scripts_v2/                                     # 生产级可复现分析、制表与检验代码集
│   ├── make_all.py                                 # 全流程一键复现主入口
│   ├── check_consistency.py                       # 核心数理与实证断言自动化一致性检验脚本 (九大类断言)
│   ├── emit_v3.py                                  # 表格 LaTeX 片段全自动生成脚本
│   ├── macro_model.py                             # 固定 k_agg 宏观负二项更新模型（主口径唯一来源）
│   ├── reframed_model.py                           # 重构稿理论接口：宏观矩、对数正态参数混合、视界集合、条件 AR(1)
│   ├── reframed_statistics.py                      # WIS 评分、moving-block 自助与区间工具
│   ├── reframed_analysis.py                        # 重构分析：宏观精确条件根、同口径配对损失与州块自助
│   ├── verify_reframed.py                          # 理论接口的 7 项独立数值核验
│   ├── score_flusight.py                           # FluSight final-vintage WIS 与点损失评分脚本
│   ├── state_panel_v3.py                           # 州级面板分析与滚动回测主脚本（宏观精确主口径）
│   ├── ingest_and_aggregate.py                     # 数据溯源与数据锁定检验脚本
│   ├── make_figures_v3.py                          # 实证图件高清渲染脚本
│   ├── make_all_figures_v2.py                      # 理论推导图件高清渲染脚本
│   ├── sim_verify_t1.py                            # 定理 1/2 分支过程模拟验证脚本
│   ├── sim_verify_t3.py                            # 定理 3 拟平稳分布数值验证脚本
│   ├── sim_verify_t4.py                            # 定理 4 Cramér–Rao 下界数值验证脚本
│   ├── micro_reanalysis.py                         # 微观层再分析：自助CI、拟合优度、零膨胀敏感性、非参数自助
│   ├── sensitivity_v4.py                           # 视界方程敏感性（k_agg 窗口/截断、个体 k、口径对照）
│   ├── predictor_sensitivity.py                    # 预测规则依赖（插入式 vs 偏差修正，含 MC 核验）
│   ├── caliber_table.py                           # 七阶段多口径视界对照
│   ├── macro_cv_check.py                          # 宏观固定 k_agg 模型的 CV² 方差律核验
│   ├── coarsegrain_check.py                        # 个体 k → 宏观 k_agg 粗粒化核验
│   ├── rolling_bootstrap.py                        # 滚动穿越点的原点级自助区间
│   └── verify_suite.py                             # 定理 5R 与推论 1 验证脚本
├── reports/                                        # 基础理论数值模拟输出与图件
│   ├── *.json                                      # 数值模拟输出结果
│   └── figures_v2/                                 # 理论推导与下界验证图件 (图 2, 图 3, 图 4)
├── reports_v3/                                     # 经验实证分析产物与图件
│   ├── reframed_summary.json                       # 重构稿：七阶段条件机制根与配对损失审计
│   ├── theory_verification.json                    # 理论接口 7 项独立数值核验结果
│   ├── flusight_v1.0_strict.json / .csv            # FluSight v1.0.0 严格 final-vintage 外部审计
│   ├── flusight_v1.1_strict.json / .csv            # FluSight v1.1.0 严格 final-vintage 外部审计
│   ├── *.json                                      # 州级视界、误差记账与预测枢纽实证结果
│   └── figures/                                    # 实证结果高清图件 (微观拟合, 州级视界, Hub 技能衰减)
└── tables_v3/                                      # 导出的独立 LaTeX 表格源码片段
    ├── table2_micro.tex                            # 正文表 2: 微观极大似然与 CRB 检验
    ├── table3_state.tex                            # 正文表 3: 51 辖区宏观机制视界空间分布
    ├── table4_budget.tex                           # 正文表 4: 启发式模型方差与模型—观测代数差额分解
    ├── table5_rolling.tex                          # 正文表 5: 伪实时滚动业务时效双层对照
    ├── table8_flusight_audit.tex                   # 正文表 6: CDC FluSight 外部审计三赛季总体表现
    ├── table9_phase_stratification.tex             # 正文表 7: CDC FluSight 流行阶段分层校准评估
    ├── table6_hub.tex                              # 补充表: COVIDhub 集成预测技能衰减
    ├── table7_tiers.tex                            # 补充表: 分级预警响应策略映射
    └── tab_sensitivity.tex                        # 补充表: k_agg 敏感性表格片段
```

---

## 二、快速复现与一致性验证

### 1. 执行全量自动化一致性检验套件
在本项目根目录下：
```bash
python scripts_v2/check_consistency.py
```
该脚本全量执行针对表格碎片、引用图件、退役短语黑名单、摘要数值区间、CRB 比例、量纲对齐、双侧穿越、数据锁定、文档声明路径存在性、阶段分类协议、Poisson 极限单调性、WIS 惩罚方向以及相交单元样本量一致性等 **15 大类断言** 实施自动化检查。

### 2. 重新编译 LaTeX 主稿
直接在根目录下执行：
```bash
tectonic main.tex
```
当前指标：**0 Errors、0 Undefined References、0 Overfull hbox**（仅余若干 \sloppy 段落内的 Underfull 松紧提示，视觉不可见）。
