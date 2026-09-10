# 有效交付文件清单与磁盘映射对照表 (MANIFEST)

本清单完整记录 `final_clean_submission/` 论文核心工作目录中全部有效文件及其与正文论文章节、图表的严格对应关系。

---

## 1. 核心文书与手稿
| 磁盘文件路径 | 文件类型 | 说明与用途 |
|---|---|---|
| `main.tex` | LaTeX 源码 | 论文主文档源码：含定理 1--5R、四项描述性误差记账与完整实证分析（0 错误、0 溢出） |
| `main.pdf` | PDF 文档 | 论文编译主产物（42 页，与 `流行病传播动力学可预测视界_最终稿.pdf` 哈希完全一致） |
| `references.bib` | BibTeX | 净化后的参考文献库（57 篇，0 未引项，0 格式冲突） |
| `fig1_framework.png` | 图像 | 理论原理与双层基准框架图高清矢量渲染图 |
| `流行病传播动力学可预测视界_最终稿.pdf` | PDF 文档 | 唯一官方权威终稿：基于最新 `main.tex` 编译生成之完整期刊论文（42 页，即开即读） |
| `流行病传播动力学的可预测视界、极限机制与实证研究_期刊模版版.docx` | Word 文档 | 期刊双栏排版衍生副本（按期刊 Word 双栏模版排版） |
| `流行病传播动力学的可预测视界、极限机制与实证研究_期刊模版版.pdf` | PDF 文档 | Word 衍生版对应高清导出版（27 页） |
| `Response_to_Reviewers.md` | Markdown | 针对最新终审意见（含 19 项问题）的官方详尽逐条修改说明与落实报告（唯一官方外送回复信） |
| `审稿意见.txt` | 纯文本 | 内部留存：原始终审专家对抗性审查报告与修改意见（外送编辑部时可从包内剔除） |
| `README.md` | Markdown | 项目自洽指南、架构说明与复现指南 |
| `MANIFEST.md` | Markdown | 本文件：全量有效交付文件与磁盘真实路径对照表 |
| `environment.yml` | YAML | Conda 运行环境依赖定义 |
| `LICENSE` | 文本 | 开源学术授权协议 |

---

## 2. 数学推导手册 (`derivations/`)
| 磁盘文件路径 | 说明 |
|---|---|
| `derivations/derivations_manual.tex` | 数学定理“显微镜式”逐行代数证明源码（已统一 C >= 1,429） |
| `derivations/derivations_manual.pdf` | 数学推导手册编译就绪 PDF |

---

## 3. 表格源码片段与正文表号对应 (`tables_v3/`)
正文中的表格采用 `\input{tables_v3/...}` 动态加载，磁盘文件编号与正文表序号映射关系如下：

| 磁盘文件名 | 正文表序与标题 | 对应数据来源 / 生成脚本 |
|---|---|---|
| `tables_v3/table7_micro.tex` | **表 2**：微观传播链层的子代分布极大似然拟合与信息论下界检验 | `scripts_v2/emit_v3.py` <- `data/micro/micro_branching_fit_results.json` |
| `tables_v3/table2_state.tex` | **表 3**：州级面板各阶段动力学参数与理论可预测视界分布 | `scripts_v2/emit_v3.py` <- `reports_v3/state_phases.json` |
| `tables_v3/table4_budget.tex` | **表 4**：四项预测误差记账的州级分解 | `scripts_v2/emit_v3.py` <- `reports_v3/budget_national.json` |
| `tables_v3/table3_rolling.tex` | **表 5**：理论机制视界与伪实时滚动业务时效的州级双层对照 | `scripts_v2/emit_v3.py` <- `reports_v3/state_rolling.json` |
| `tables_v3/table5_hub.tex` | **表 6**：COVIDhub-ensemble 集成预测的州级技能衰减 | `scripts_v2/emit_v3.py` <- `data/hub/forecast_hub_operational_evaluation.json` |
| `tables_v3/table6_tiers.tex` | **表 7**：公共卫生决策分级场景、理论可预测视界与风控策略推荐 | `scripts_v2/emit_v3.py` <- `reports_v3/scenarios.json` |

---

## 4. 高清矢量图件清单
| 磁盘文件路径 | 正文图序与内容说明 |
|---|---|
| `reports/figures_v2/fig2_cv_verify.png` | **图 2**：负二项分支过程单代及全代变异系数平方 CV²(h) 理论曲线与模拟验证 |
| `reports/figures_v2/fig_t3_quasistationary.png` | **图 3**：反射正则化辅助扩散平稳密度与首达建群概率模拟对比 |
| `reports/figures_v2/fig_t4_fisher_bound.png` | **图 4**：Fisher 信息量与 Cramér–Rao 样本量基准 (C >= 1,429) 验证 |
| `reports_v3/figures/fig_micro.png` | **图 5**：三组真实个体传播链数据集负二项生成假设似然检验 |
| `reports_v3/figures/fig_state_horizons.png` | **图 6**：全美 51 个州级辖区在七个流行阶段下的理论可预测视界空间分布 |
| `reports_v3/figures/fig_hub_skill.png` | **图 7**：COVID-19 预测枢纽顶级集成模型在 12 个真实预测原点下的技能衰减 |

---

## 5. 实证原始与清洗后数据集 (`data/`)
| 磁盘文件/目录路径 | 说明 |
|---|---|
| `data/micro/guinea_ebola_faye2015/` | 2014--2015 年几内亚科纳克里埃博拉传播链数据与流调队列 |
| `data/micro/hong_kong_adam2020/` | 2020 年香港 COVID-19 本地聚集性病例接触追踪集群数据 |
| `data/micro/lloyd_smith_2005/` | 超级传播历史基准参数集与文献对比数据 |
| `data/micro/micro_branching_fit_results.json` | 个体层负二项极大似然拟合参数 (R, k) 与 50,000 次 Bootstrap 抽样检验结果 |
| `data/panels/covid_weekly_hospitalizations.csv.gz` | 全美 51 个州周度 COVID-19 新增住院面板 (Delta, Omicron, JN.1) |
| `data/panels/flu_weekly_hospitalizations.csv.gz` | 全美 51 个州周度流感新增住院面板 (2022--23, 2024--25) |
| `data/panels/rsv_weekly_hospitalizations.csv.gz` | 全美 51 个州周度 RSV 新增住院面板 (2024--25, 2025--26) |
| `data/panels/us_state_daily_hospitalizations.csv` | 州级逐日住院基础序列 |
| `data/hub/` | COVID-19 Forecast Hub 官方顶级集成模型预测与评估目录 (含 12 个原点原始预测归档) |
| `data/hub/forecast_hub_operational_evaluation.json` | 预测枢纽 12 个原点 1--4 周技能衰减与持续性基线对比统计结果 |

---

## 6. 生产级分析与自动化验证套件 (`scripts_v2/`)
| 磁盘文件路径 | 说明与功能 |
|---|---|
| `scripts_v2/make_all.py` | 全流程一键复现主入口：数据溯源 -> 面板估计 -> 制表画图 -> 定理模拟 -> 一致性检验 |
| `scripts_v2/check_consistency.py` | 9 大类核心数理、实证断言及文档路径存在性自动化一致性检验脚本 |
| `scripts_v2/ingest_and_aggregate.py` | 数据溯源与完整性校验脚本（含国家级窗口和校验断言） |
| `scripts_v2/state_panel_v3.py` | 州级面板分析、动力学参数拟合与滚动回测主脚本 |
| `scripts_v2/emit_v3.py` | 四项描述性误差记账与 LaTeX 表格片段全自动生成脚本 |
| `scripts_v2/make_figures_v3.py` | 经验实证高清图件渲染脚本（图 5, 图 6, 图 7） |
| `scripts_v2/make_all_figures_v2.py` | 理论推导与数值下界高清图件渲染脚本（图 2, 图 3, 图 4） |
| `scripts_v2/sim_verify_t1.py` | 定理 1（分支过程两阶段递推）与定理 2（单调性极限）蒙特卡洛数值验证 |
| `scripts_v2/sim_verify_t3.py` | 定理 3（拟平稳分布与定殖概率尺度）数值模拟验证 |
| `scripts_v2/sim_verify_t4.py` | 定理 4（Fisher 信息量与 Cramér–Rao 下界）数值模拟验证 |
| `scripts_v2/verify_suite.py` | 定理 5R（环境噪声自回归）与推论 1 验证套件 |

---

## 7. 分析中间结果与报告数据 (`reports/` & `reports_v3/`)
| 磁盘文件路径 | 说明 |
|---|---|
| `reports_v3/state_phases.json` | 51 州在七个流行阶段下的动力学参数与理论视界汇总结果 |
| `reports_v3/state_rolling.json` | 51 州逐周滚动外推回测与业务穿越点逐州明细 |
| `reports_v3/national_rolling.json` | 国家级聚合序列逐周滚动外推回测评估结果 |
| `reports_v3/budget_national.json` | 四项描述性预测误差记账的国家级与州级分解数据 |
| `reports_v3/scenarios.json` | 公共卫生分级响应场景、理论视界与运筹策略配置结果 |
| `reports/verify_t1.json` | 定理 1/2 分支过程模拟数值检验结果 |
| `reports/verify_t3.json` | 定理 3 拟平稳分布检验结果 |
| `reports/verify_t4.json` | 定理 4 Fisher 信息量与 Cramér–Rao 下界检验结果 |
| `reports/verify_t5R_v2.json` | 定理 5R 环境噪声检验结果 |
| `reports/verify_t5R_renewal_v2.json` | 定理 5R Renewal 形式检验结果 |
| `reports/corollary1_grid.json` | 推论 1 二次方程正根网格求解结果 |

---

## 8. 汇报与演示成果 (`presentation/`)
| 磁盘文件路径 | 说明 |
|---|---|
| `presentation/epidemic_predictability_masterclass.pptx` | 面向公共卫生管理者与学术同行的 Masterclass 完整汇报幻灯片 |
| `presentation/index.html` | 交互式研究成果全景可视化与论文导读单页网页 |

---

## 9. 历史归档与参考材料 (`docs/`)
| 磁盘文件路径 | 说明 |
|---|---|
| `docs/Response_to_Reviewers_round16_archive.md` | 早期英文 Round 16 审稿回复历史归档（供内部查阅参考） |
| `docs/流行病传播动力学的可预测视界、极限机制与实证研究_期刊模版版.docx` | 期刊 Word 模版排版原稿存档 |\n