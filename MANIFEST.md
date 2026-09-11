# 有效交付文件清单与磁盘映射对照表 (MANIFEST)

本清单完整记录 `final_clean_submission/` 论文核心工作目录中全部有效文件及其与正文论文章节、图表的严格对应关系。

---

## 1. 核心文书与手稿
| 磁盘文件路径 | 文件类型 | 说明与用途 |
|---|---|---|
| `main.tex` | LaTeX 源码 | 论文主文档源码：含定理 1、2、4、5、5R、命题 3 与推论 1--3、四项描述性误差记账与完整实证分析（0 错误、0 溢出） |
| `main.pdf` | PDF 文档 | 论文编译主产物（48 页，由 Tectonic 从当前 `main.tex` 编译生成） |
| `references.bib` | BibTeX | 净化后的参考文献库（60 篇，双向完全闭合：0 缺失、0 未引项） |
| `README.md` | Markdown | 项目自洽指南、架构说明与复现指南 |
| `MANIFEST.md` | Markdown | 本文件：全量有效交付文件与磁盘真实路径对照表 |
| `environment.yml` | YAML | Conda 运行环境依赖定义 |
| `LICENSE` | 文本 | 开源学术授权协议 |

---

## 2. 数学推导手册 (`derivations/`)
| 磁盘文件路径 | 说明 |
|---|---|
| `derivations/derivations_manual.tex` | 数学定理“显微镜式”逐行代数证明源码（已统一 C >= 1,300） |
| `derivations/derivations_manual.pdf` | 数学推导手册编译就绪 PDF |

---

## 3. 表格源码片段与正文表号对应 (`tables_v3/`)
正文中的表格采用 `\input{tables_v3/...}` 动态加载，磁盘文件编号与正文表序号映射关系如下：

| 磁盘文件名 | 正文表序与标题 | 对应数据来源 / 生成脚本 |
|---|---|---|
| `tables_v3/table2_micro.tex` | **表 2**：微观传播链层的子代分布极大似然拟合与信息论下界检验 | `scripts_v2/emit_v3.py` <- `data/micro/micro_branching_fit_results.json` |
| `tables_v3/table3_state.tex` | **表 3**：州级面板各阶段动力学参数与理论可预测视界分布 | `scripts_v2/emit_v3.py` <- `reports_v3/state_phases.json` |
| `tables_v3/table4_budget.tex` | **表 4**：四项预测误差记账的州级分解 | `scripts_v2/emit_v3.py` <- `reports_v3/budget_national.json` |
| `tables_v3/table5_rolling.tex` | **表 5**：理论机制视界与伪实时滚动业务时效的州级双层对照 | `scripts_v2/emit_v3.py` <- `reports_v3/state_rolling.json` |
| `reports_v3/sensitivity_v4.json` | 视界方程的三项补充敏感性结果（k_agg 窗口/截断、个体级 k、周代求根） |
| `reports_v3/rolling_bootstrap.json` | 滚动穿越点的原点级自助区间 |
| `reports_v3/coarsegrain_check.json` | 粗粒化核验：微观分支模拟反解 k_agg 与隐含聚合因子 M |
| `reports_v3/macro_cv_check.json` | 宏观固定离散度模型的 CV²(h) 模拟（相对引理闭式的低估倍数） |
| `reports_v3/caliber_table.json` | 七阶段多口径视界与实测时效对照结果 |
| `tables_v3/table6_hub.tex` | **表 6**：COVIDhub-ensemble 集成预测的州级技能衰减 | `scripts_v2/emit_v3.py` <- `data/hub/forecast_hub_operational_evaluation.json` |
| `tables_v3/table7_tiers.tex` | **表 7**：公共卫生决策分级场景、理论可预测视界与风控策略推荐 | `scripts_v2/emit_v3.py` <- `reports_v3/scenarios.json` |

---

## 4. 高清矢量图件清单
| 磁盘文件路径 | 正文图序与内容说明 |
|---|---|
| `reports/figures_v2/fig2_cv_verify.png` | **图 2**：负二项分支过程单代及全代变异系数平方 CV²(h) 理论曲线与模拟验证 |
| `reports/figures_v2/fig_t3_quasistationary.png` | **图 3**：反射正则化辅助扩散平稳密度与首达建群概率模拟对比 |
| `reports/figures_v2/fig_t4_fisher_bound.png` | **图 4**：Fisher 信息量与 Cramér–Rao 样本量基准 (C >= 1,300) 验证 |
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
| `scripts_v2/micro_reanalysis.py` | 微观传播链层再分析：$\hat R$、$\hat k$ 自助置信区间、负二项拟合优度检验、零膨胀敏感性、非参数自助对照 |
| `scripts_v2/sensitivity_v4.py` | k_agg 窗口/截断敏感性、个体级 k 替换敏感性、周度-代际求根差异量化 |
| `scripts_v2/rolling_bootstrap.py` | 滚动回测穿越点的原点级自助置信区间（B=2000） |
| `scripts_v2/coarsegrain_check.py` | 个体级 k 到宏观 k_agg 的粗粒化机制数值核验 |
| `scripts_v2/macro_cv_check.py` | 固定 k_agg 宏观模型与引理闭式的方差律差异核验 |
| `scripts_v2/caliber_table.py` | 七阶段五口径视界与实测时效的逐阶段对照（含包络失效判定） |
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

## 10. 数据溯源、上游来源与 SHA-256 完整性校验

本节登记论文实证分析所用的冻结输入及其上游来源，供第三方核验手中数据与本文所用是否为同一份。

### 10.1 上游数据来源与检索信息

| 数据层 | 上游来源 | 版本 / release | 检索日期 |
|---|---|---|---|
| COVID-19 州级住院面板 | reichlab/covid19-forecast-hub（目标数据 `target-data`，NHSN 周度住院口径） | 终版 release 2024-04-28 | 2024-04-28 |
| 季节性流感州级住院面板 | cdcepi/FluSight-forecast-hub（目标数据，NHSN 周度住院口径） | 终版归档 | 2026-09 |
| RSV 州级住院面板 | cdcepi/RSV-forecast-hub（目标数据，NHSN 周度住院口径） | 终版归档 | 2026-09 |
| COVIDhub-ensemble 预测归档 | reichlab/covid19-forecast-hub（`data-processed/COVIDhub-ensemble/`） | 逐周 12 个预测原点 | 2026-09 |
| 香港 COVID-19 传播链 | Adam 等 (2020) 补充材料（接触追踪队列） | 公开发表版 | 2026-09 |
| 几内亚埃博拉传播链 | Faye 等 (2015) 补充材料（Conakry 传播网络） | 公开发表版 | 2026-09 |

### 10.2 SHA-256 校验和（分析输入）

| 文件 | SHA-256 |
|---|---|
| `data/panels/covid_weekly_hospitalizations.csv.gz` | `4ee61b27d547f8dbee3db139705316a951e2b431d45585a4bdd530c67e88476a` |
| `data/panels/flu_weekly_hospitalizations.csv.gz` | `05e7fc87a3362efcb0afb05b9a33d0579eda86f90e56319d18d63a782657048f` |
| `data/panels/rsv_weekly_hospitalizations.csv.gz` | `22c0f0fa1f38a551cf2ab880bb306b2cad7f5d1d8777d46ceaa9ae1627cdc5f8` |
| `data/panels/us_state_daily_hospitalizations.csv` | `90c9d057b9561c4ce26ac591a61c0e174df52acfbd3a695d35b09fac963ae338` |
| `data/micro/micro_branching_fit_results.json` | `2369cf1cce28be1c1e7f7cdc304098df06e682f081a94626fec4656fdce51977` |
| `data/hub/forecast_hub_operational_evaluation.json` | `4f6deb0852da027d699fa3512227a1a222b29344d9827eceff2e289abf953ac6` |

### 10.3 SHA-256 校验和（COVIDhub-ensemble 逐文件）

| 文件 | SHA-256 |
|---|---|
| `data/hub/2021-08-02-COVIDhub-ensemble.csv.gz` | `9dcbd1bee254c5235455aef93ba39a1fb8a3d6f0da83f9ae5d4451d367f13ebe` |
| `data/hub/2021-08-09-COVIDhub-ensemble.csv.gz` | `7ea25fd5a883bd5c5023b8ede07a20075881164285ae7547468010b13a02f6bb` |
| `data/hub/2021-08-16-COVIDhub-ensemble.csv.gz` | `95af3305e95ad4819cb2086672b58c29267e50c14a353b0faad50257541737ae` |
| `data/hub/2021-08-23-COVIDhub-ensemble.csv.gz` | `25d81de69d82672bfa4370a47519214b96f7a1758bad6d4fe65bf35fed32bdc3` |
| `data/hub/2021-08-30-COVIDhub-ensemble.csv.gz` | `4546e4d52de90b1549e8acb982f6a758e3f5f0cac2b7c8b316c7685f7e2f71e1` |
| `data/hub/2021-09-06-COVIDhub-ensemble.csv.gz` | `a7ba1f34d3deacc553b2e871a5c09e7560ef7c4257d28783d93c3278c644b2a1` |
| `data/hub/2021-12-06-COVIDhub-ensemble.csv.gz` | `ef5a7bb8d67c6b4081d8486dde24c48eecbd32c6b059a290b538aead31f391d8` |
| `data/hub/2021-12-13-COVIDhub-ensemble.csv.gz` | `efd6378c85df167333c517385ffe2edc692d45bcfc5ee8d9f2b3ea05a48f76a8` |
| `data/hub/2021-12-20-COVIDhub-ensemble.csv.gz` | `07b1e9cf35331c87c947b56c1a968644783d7c856423787fd1f4d77b7da2c0d2` |
| `data/hub/2021-12-27-COVIDhub-ensemble.csv.gz` | `ce4f660b8a4ab9380a4abe8946ad9c0e1dda3169514da94df1a75ec6dcee17e9` |
| `data/hub/2022-01-03-COVIDhub-ensemble.csv.gz` | `10874eb918fd471be524ec50dc9be70b01047127ef100a540cfb3368f5c70a84` |
| `data/hub/2022-01-10-COVIDhub-ensemble.csv.gz` | `c0949b3719c237d4bc0f53db5242e24d9a372fed7559c8846d5ccd6ae71d6a2b` |

### 10.4 校验方式

`scripts_v2/ingest_and_aggregate.py` 为输入完整性校验脚本：它从逐日住院文件重导出周度 COVID 面板并与冻结副本比对，断言三个面板的结构不变量与国家级窗口合计锚点，并在标准输出打印上述各文件的 SHA-256 摘要以供回填核验。上游原始快照到冻结面板之间的整理链路不可在离线环境重放（三个预测枢纽的历史目标数据版本不可重建逐日快照），故本包以冻结面板加校验和的方式固化输入身份。
