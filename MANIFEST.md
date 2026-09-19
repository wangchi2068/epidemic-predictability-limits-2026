# 有效交付文件清单与磁盘映射对照表 (MANIFEST)

本清单完整记录 `final_clean_submission/` 论文核心工作目录中全部有效文件及其与正文论文章节、图表的严格对应关系。

---

## 1. 核心文书与手稿
| 磁盘文件路径 | 文件类型 | 说明与用途 |
|---|---|---|
| `main.tex` | LaTeX 源码 | **正式提交稿**论文主文档源码：32 页紧凑精炼稿，含定理 1--5、引理 1--4、命题 1--4、推论 1--4，四层证据架构（0 错误、0 溢出、0 未定义引用） |
| `main.pdf` | PDF 文档 | 正式提交稿编译产物（严格 32 页，由 Tectonic 从 `main.tex` 编译生成） |
| `archive/main_reframed.tex` | LaTeX 源码 | [历史存档] 重构探索稿源码（12 页，曾用作独立审计验证测试） |
| `archive/main_reframed.pdf` | PDF 文档 | [历史存档] 重构探索稿编译产物（12 页） |
| `references.bib` | BibTeX | 净化后的参考文献库（46 篇，双向完全闭合：0 缺失、0 未引项） |
| `README.md` | Markdown | 项目自洽指南、架构说明与复现指南 |
| `MANIFEST.md` | Markdown | 本文件：全量有效交付文件与磁盘真实路径对照表 |
| `environment.yml` | YAML | Conda 运行环境依赖定义 |
| `archive/REWRITE_REPORT.md` | Markdown | [历史存档] 重构探索阶段决策与修改记录 |
| `LICENSE` | 文本 | 开源学术授权协议 |

---

## 2. 数学推导手册 (`derivations/`)
| 磁盘文件路径 | 说明 |
|---|---|
| `derivations/derivations_manual.tex` | 数学定理“显微镜式”逐行代数证明源码（已统一 C >= 1,300） |
| `derivations/derivations_manual.pdf` | 数学推导手册编译就绪 PDF |

---

## 3. 表格清单与对应关系

### 3.1 正式提交稿 (`main.tex`, 32 页) 正文表格清单
| 正文表序 | 标题与说明 | 对应数据来源 / 生成脚本 |
|---|---|---|
| **表 1** | 证据架构与跨尺度层级界定（确定性分支与随机范围） | 正文内嵌排版 (`main.tex`) |
| **表 2** | 微观传播链子代分布极大似然拟合与信息论下界检验 | `tables_v3/table2_micro.tex` <- `data/micro/micro_branching_fit_results.json` |
| **表 3** | 州级七阶段动力学参数与固定离散度 NB2 模型内机制视界分布 | `tables_v3/table3_state.tex` <- `reports_v3/state_phases.json` |
| **表 4** | 启发式模型方差与模型—观测代数差额的州级分解 | `tables_v3/table4_budget.tex` <- `reports_v3/budget_national.json` |
| **表 5** | 宏观机制视界与伪实时滚动业务时效的州级双层对照 | `tables_v3/table5_rolling.tex` <- `reports_v3/state_rolling.json` |
| **表 6** | CDC FluSight 外部审计：三历史赛季严格四向相交单元总体表现与配对差异 | `tables_v3/table8_flusight_audit.tex` <- `reports_v3/flusight_v1.*_extended.json` |
| **表 7** | CDC FluSight 外部审计按流行病学阶段分层的校准评估 | `tables_v3/table9_phase_stratification.tex` <- `reports_v3/flusight_v1.*_extended.json` |
| **表 8** | 全文核心定理证明推导索引全景目录 | 正文内嵌排版 (`main.tex`) |

### 3.2 补充与备用表格片段 (`tables_v3/`)
| 磁盘文件名 | 标题与说明 | 对应数据来源 / 生成脚本 |
|---|---|---|
| `tables_v3/table6_hub.tex` | COVIDhub-ensemble 集成预测技能衰减汇总表 | `scripts_v2/emit_v3.py` <- `data/hub/forecast_hub_operational_evaluation.json` |
| `tables_v3/table7_tiers.tex` | 公共卫生分级响应场景与机制视界策略映射表 | `scripts_v2/emit_v3.py` <- `reports_v3/scenarios.json` |
| `tables_v3/tab_sensitivity.tex` | 视界方程 $k_{\text{agg}}$ 敏感性表格片段 | `scripts_v2/emit_v3.py` <- `reports_v3/sensitivity_v4.json` |

---

## 4. 高清矢量图件清单

### 4.1 正式提交稿 (`main.tex`, 32 页) 正文图件清单
| 磁盘文件路径 | 正文图序与内容说明 |
|---|---|
| `reports_v3/figures/fig1_framework.png` | **图 1**：传染病预测视界机制基准与实证外部审计架构全景图 |
| `reports/figures_v2/fig2_cv_verify.png` | **图 2**：微观分支方差饱和与宏观 NB2 线下递推几何增长的跨尺度理论与数值对比 |
| `reports_v3/figures/fig_micro.png` | **图 3**：个体传播链子代分布负二项极大似然拟合与 Cramér--Rao 下界验证 |
| `reports_v3/figures/fig_state_horizons.png` | **图 4**：宏观机制视界州级空间分布、国家级聚合对照与方差占比 |
| `reports_v3/figures/fig_flusight_audit.png` | **图 5**：CDC FluSight 外部审计流行动力学阶段分层加权区间评分与经验覆盖率衰减 |
| `reports_v3/figures/fig_hub_skill.png` | **图 6**：COVIDhub-ensemble 预测技能州级衰减与 WIS 随前瞻步长耗散 |

### 4.2 推导手册与补充图件 (`derivations/` & `reports/`)
| 磁盘文件路径 | 正文图序与内容说明 |
|---|---|
| `reports/figures_v2/fig_t3_quasistationary.png` | 反射正则化辅助扩散平稳密度与首达建群概率模拟对比（推导手册收录） |
| `reports/figures_v2/fig_t4_fisher_bound.png` | Fisher 信息量与 Cramér–Rao 样本量基准 ($C \ge 1,300$) 验证（推导手册收录） |

---

## 5. 实证原始与清洗后数据集 (`data/`)
| 磁盘文件/目录路径 | 说明 |
|---|---|
| `data/micro/guinea_ebola_faye2015/` | 2014--2015 年几内亚科纳克里埃博拉传播链数据与流调队列 |
| `data/micro/hong_kong_adam2020/` | 2020 年香港 COVID-19 本地聚集性病例接触追踪集群数据 |
| `data/micro/lloyd_smith_2005/` | 超级传播历史基准参数集与文献对比数据 |
| `data/micro/micro_branching_fit_results.json` | 个体层负二项极大似然拟合参数 (R, k) 与 50,000 次 Bootstrap 抽样检验结果 |
| `data/panels/covid_weekly_hospitalizations.csv.gz` | 美国 51 个州级辖区周度 COVID-19 新增住院面板 (Delta, Omicron, JN.1) |
| `data/panels/flu_weekly_hospitalizations.csv.gz` | 美国 51 个州级辖区周度流感新增住院面板 (2022--23, 2024--25) |
| `data/panels/rsv_weekly_hospitalizations.csv.gz` | 美国 51 个州级辖区周度 RSV 新增住院面板 (2024--25, 2025--26) |
| `data/panels/us_state_daily_hospitalizations.csv` | 州级逐日住院基础序列 |
| `data/hub/` | [历史存盘/已废弃] COVID-19 Forecast Hub 早期集成预测目录 (含 12 个原点原始预测归档) |
| `data/hub/forecast_hub_operational_evaluation.json` | [历史存盘/已废弃] 早期旧工作包旧 Hub 汇总指标（无法由随附 CSV 以误差容忍度重建，已移出重构稿主证据链，仅保留作复现性审计阴性对照记录在 `reports_v3/hub_pooled_metric_NOTE.md`） |
| `data/flusight/README.md` | 外部审计协议：锁定 release 与 commit、评分口径与边界、输入哈希与复现命令 |
| `data/flusight/v1.0.0/target-hospital-admissions.csv` | FluSight v1.0.0 frozen target file (SHA-256 recorded in `data/flusight/README.md`) |
| `data/flusight/v1.0.0/ensemble/` | FluSight v1.0.0 30 frozen ensemble forecast origins |
| `data/flusight/v1.0.0/baseline/` | FluSight v1.0.0 30 frozen official-baseline forecast origins |
| `data/flusight/v1.0.0/2024-01-06-FluSight-ensemble.csv` | v1.0.0 first-origin download verification copy; not used by the scorer |
| `data/flusight/v1.1.0/target-hospital-admissions.csv` | FluSight v1.1.0 frozen target file (SHA-256 recorded in `data/flusight/README.md`) |
| `data/flusight/v1.1.0/ensemble/` | FluSight v1.1.0 57 frozen ensemble forecast origins |
| `data/flusight/v1.1.0/baseline/` | FluSight v1.1.0 27 frozen official-baseline forecast origins |
| `data/flusight/v1.2.0/` | FluSight v1.2.0（2025--26）冻结真值 + 28 ensemble + 28 baseline 预测 origin |
| `data/flusight/file_hashes.json` | SHA-256 manifest for all 204 downloaded FluSight release files |
| `data/flusight/upstream_sources/` | Release-pinned README, LICENSE, and model metadata for v1.0.0 and v1.1.0 |

---

## 6. 生产级分析与自动化验证套件 (`scripts_v2/`)
| 磁盘文件路径 | 说明与功能 |
|---|---|
| `scripts_v2/make_reframed_all.py` | 重构探索稿一键复现主入口：分析运行 -> 理论核验 -> 严格四向相交单元核验 -> Tectonic 编译 12 页 PDF -> 0 错误检验 |
| `scripts_v2/make_all.py` | 全流程一键复现主入口：数据溯源 -> 面板估计 -> 制表画图 -> 定理模拟 -> 一致性检验 |
| `scripts_v2/check_consistency.py` | 15 大类核心数理、实证断言及文档路径存在性自动化一致性检验脚本 |
| `scripts_v2/ingest_and_aggregate.py` | 数据溯源与完整性校验脚本（含国家级窗口和校验断言） |
| `scripts_v2/macro_model.py` | 固定 $k_{\text{agg}}$ 宏观负二项更新模型的精确方差闭式（州级主口径的唯一来源，被 state_panel_v3 / emit_v3 / caliber_table 共用） |
| `scripts_v2/state_panel_v3.py` | 州级面板分析、动力学参数拟合与滚动回测主脚本 |
| `scripts_v2/reframed_model.py` | 理论接口：`macro_moments`、`lognormal_predictive_moments`、`horizon_set`、条件/无条件 AR(1) 求和方差 |
| `scripts_v2/reframed_statistics.py` | WIS 评分（23 分位数）、moving-block 自助与可信区间工具 |
| `scripts_v2/reframed_analysis.py` | 宏观精确条件根、同口径配对损失和州块自助区间分析 |
| `scripts_v2/score_flusight.py` | FluSight final-vintage WIS 与原点归一化平方损失评分脚本 |
| `scripts_v2/flusight_audit_extended.py` | 扩展评分面板：WIS 分解、50/80/95\% 覆盖率、区间宽度、随机化 PIT、按阶段分层，并把插件机制预测器在同一批单元评分 |
| `scripts_v2/fetch_flusight_release.py` | FluSight 锁定 release 的下载与 SHA-256 登记脚本 |
| `scripts_v2/verify_reframed.py` | Independent numerical checks for macro recursion, parameter mixtures, WIS and moving-block bootstrap |
| `scripts_v2/emit_v3.py` | 描述性误差记账与 LaTeX 表格片段全自动生成脚本 |
| `scripts_v2/make_figures_v3.py` | 经验实证高清图件渲染脚本（图 3, 图 4, 图 5, 图 6） |
| `scripts_v2/make_all_figures_v2.py` | 理论推导与数值下界高清图件渲染脚本（图 2 及推导手册图件） |
| `scripts_v2/sim_verify_t1.py` | 定理 1（分支过程两阶段递推）与定理 2（单调性极限）蒙特卡洛数值验证 |
| `scripts_v2/sim_verify_t3.py` | 定理 3（拟平稳分布与定殖概率尺度）数值模拟验证 |
| `scripts_v2/sim_verify_t4.py` | 定理 4（Fisher 信息量与 Cramér–Rao 下界）数值模拟验证 |
| `scripts_v2/micro_reanalysis.py` | 微观传播链层再分析：$\hat R$、$\hat k$ 自助置信区间、负二项拟合优度检验、零膨胀敏感性、非参数自助对照 |
| `scripts_v2/sensitivity_v4.py` | k_agg 窗口/截断敏感性、个体级 k 替换敏感性、周度-代际求根差异量化 |
| `scripts_v2/rolling_bootstrap.py` | 滚动回测穿越点的原点级自助置信区间（B=2000） |
| `scripts_v2/coarsegrain_check.py` | 个体级 k 到宏观 k_agg 的粗粒化机制数值核验 |
| `scripts_v2/macro_cv_check.py` | 固定 k_agg 宏观模型与引理闭式的方差律差异核验 |
| `scripts_v2/predictor_sensitivity.py` | 预测规则依赖：插入式预测与均值偏差修正预测的视界对照（含 $2\times10^6$ 次蒙特卡洛核验） |
| `scripts_v2/caliber_table.py` | 七阶段五口径视界与实测时效的逐阶段对照（含包络失效判定） |
| `scripts_v2/verify_suite.py` | 定理 5R（环境噪声自回归）与推论 1 验证套件 |

---

## 7. 分析中间结果与报告数据 (`reports/` & `reports_v3/`)
| 磁盘文件路径 | 说明 |
|---|---|
| `reports_v3/state_phases.json` | 美国 51 个州级辖区在七个流行阶段下的动力学参数与理论视界汇总结果 |
| `reports_v3/reframed_summary.json` | 七阶段条件机制根与配对损失审计结果 |
| `reports_v3/flusight_v1.0.0_scores.json` | FluSight v1.0.0 final-vintage origin-normalized loss and WIS audit |
| `reports_v3/flusight_v1.1.0_scores.json` | FluSight v1.1.0 final-vintage origin-normalized loss and WIS audit |
| `reports_v3/flusight_v1.0_strict.json` | FluSight v1.0.0 ensemble versus official baseline strict audit |
| `reports_v3/flusight_v1.1_strict.json` | FluSight v1.1.0 ensemble versus official baseline strict cross-season audit |
| `reports_v3/flusight_v1.2_strict.json` | FluSight v1.2.0（2025--26）ensemble versus official baseline strict audit |
| `reports_v3/flusight_v1.*_extended.json` | 三个赛季的扩展评分面板（含机制基准同单元评分、阶段分层） |
| `reports_v3/EMPIRICAL_EXTENSION_REPORT.md` | 三赛季外部审计与扩展面板的实证报告 |
| `reports_v3/reframed_verification.json` | Independent verification results for the rewritten analysis |
| `reports_v3/theory_verification.json` | 重构稿理论接口的 7 项独立数值核验结果（宏观递推、可去极限、对数正态混合、视界集合、AR(1)、WIS、moving-block 自助） |
| `reports_v3/state_rolling.json` | 美国 51 个州级辖区逐周滚动外推回测与业务穿越点明细 |
| `reports_v3/national_rolling.json` | 国家级聚合序列逐周滚动外推回测评估结果 |
| `reports_v3/budget_national.json` | 描述性预测误差记账的国家级与州级分解数据 |
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
| COVIDhub-ensemble 预测归档 | reichlab/covid19-forecast-hub（`data-processed/COVIDhub-ensemble/`，历史存盘/已废弃） | 逐周 12 个预测原点 | 2026-09 |
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
| `data/hub/forecast_hub_operational_evaluation.json` | `4f6deb0852da027d699fa3512227a1a222b29344d9827eceff2e289abf953ac6`（历史存盘/已废弃） |

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
