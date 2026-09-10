# 有效交付文件清单与磁盘映射对照表 (MANIFEST)

本清单完整记录 `final_clean_submission/` 归档包中全部有效文件及其与正文论文章节、图表的严格对应关系。

---

## 1. 核心文书与手稿
| 磁盘文件路径 | 文件类型 | 说明与用途 |
|---|---|---|
| `流行病传播动力学可预测视界_最终稿.pdf` | PDF 文档 | 最终排版生成的完整期刊论文（即开即读） |
| `流行病传播动力学的可预测视界、极限机制与实证研究_期刊模版版.docx` | Word 文档 | 按中文核心/卓越期刊模版排版的 Word 终稿 |
| `Response_to_Reviewers_审稿逐条回复.md` | Markdown | 针对最新终审意见（含 19 项问题）的详尽逐条修改说明 |
| `审稿意见.txt` | 纯文本 | 原始终审专家对抗性审查报告 |
| `README.md` | Markdown | 项目自洽指南、架构说明与复现指南 |
| `MANIFEST.md` | Markdown | 本文件：全量有效交付文件与磁盘真实路径对照表 |
| `environment.yml` | YAML | Conda 运行环境依赖定义 |
| `LICENSE` | 文本 | 开源学术授权协议 |

---

## 2. 中文期刊模版源码 (`paper_cn_journal_template/`)
| 磁盘文件路径 | 说明 |
|---|---|
| `paper_cn_journal_template/main.tex` | 最终修订版 LaTeX 主文档（含定理 1--5R、四项描述性误差记账与完整实证分析） |
| `paper_cn_journal_template/references.bib` | 净化后的参考文献库（57 篇，0 未引项，0 格式冲突） |
| `paper_cn_journal_template/main.pdf` | Tectonic / XeLaTeX 编译输出 (1.35 MiB) |
| `paper_cn_journal_template/Response_to_Reviewers.md` | 审稿意见修改说明（LaTeX 模版内备份） |
| `paper_cn_journal_template/审稿意见.txt` | 原始审稿意见备份 |

---

## 3. 数学推导手册 (`derivations/`)
| 磁盘文件路径 | 说明 |
|---|---|
| `derivations/derivations_manual.tex` | 数学定理“显微镜式”逐行代数证明源码（已统一 C >= 1,429） |
| `derivations/derivations_manual.pdf` | 数学推导手册编译就绪 PDF |

---

## 4. 表格源码片段与正文表号对应 (`tables_v3/`)
正文中的表格采用 `\input{../tables_v3/...}` 动态加载，磁盘文件编号与正文表序号映射关系如下：

| 磁盘文件名 | 正文表序与标题 | 对应数据来源 / 生成脚本 |
|---|---|---|
| `tables_v3/table7_micro.tex` | **表 2**：微观传播链层的子代分布极大似然拟合与信息论下界检验 | `scripts_v2/emit_v3.py` <- `data/micro/micro_branching_fit_results.json` |
| `tables_v3/table2_state.tex` | **表 3**：州级面板各阶段动力学参数与理论可预测视界分布 | `scripts_v2/emit_v3.py` <- `reports_v3/state_phases.json` |
| `tables_v3/table4_budget.tex` | **表 4**：四项预测误差记账的州级分解 | `scripts_v2/emit_v3.py` <- `reports_v3/budget_national.json` |
| `tables_v3/table3_rolling.tex` | **表 5**：理论机制视界与伪实时滚动业务时效的州级双层对照 | `scripts_v2/emit_v3.py` <- `reports_v3/state_rolling.json` |
| `tables_v3/table5_hub.tex` | **表 6**：COVIDhub-ensemble 集成预测的州级技能衰减 | `scripts_v2/emit_v3.py` <- `data/hub/verify_forecast_hub.json` |
| `tables_v3/table6_tiers.tex` | **表 7**：公共卫生决策分级场景、理论可预测视界与风控策略推荐 | `scripts_v2/emit_v3.py` <- `reports_v3/scenarios.json` |

---

## 5. 高清矢量图件清单
| 磁盘文件路径 | 正文图序与内容说明 |
|---|---|
| `reports/figures_v2/fig2_cv_verify.png` | **图 2**：负二项分支过程单代及全代变异系数平方 CV²(h) 理论曲线与模拟验证 |
| `reports/figures_v2/fig_t3_quasistationary.png` | **图 3**：反射正则化辅助扩散平稳密度与首达建群概率模拟对比 |
| `reports/figures_v2/fig_t4_fisher_bound.png` | **图 4**：Fisher 信息量与 Cramér–Rao 样本量基准 (C >= 1,429) 验证 |
| `reports_v3/figures/fig_micro.png` | **图 5**：三组真实个体传播链数据集负二项生成假设似然检验 |
| `reports_v3/figures/fig_state_horizons.png` | **图 6**：全美 51 个州级辖区在七个流行阶段下的理论可预测视界空间分布 |
| `reports_v3/figures/fig_hub_skill.png` | **图 7**：COVID-19 预测枢纽顶级集成模型在 12 个真实预测原点下的技能衰减 |

---

## 6. 实证原始与清洗后数据集 (`data/`)
| 磁盘文件/目录路径 | 说明 |
|---|---|
| `data/micro/guinea_ebola_faye2015/` | 2014--2015 年几内亚科纳克里埃博拉传播链数据与流调队列 |
| `data/micro/hong_kong_adam2020/` | 2020 年香港 COVID-19 本地聚集性病例接触追踪集群数据 |
| `data/micro/lloyd_smith_2005/` | 超级传播历史基准参数集与文献对比数据 |
| `data/micro/micro_branching_fit_results.json` | 个体层负二项极大似然拟合参数 (R, k) 与 50,000 次 Bootstrap 抽样检验结果 |
| `data/panels/covid_weekly_hospitalizations.csv.gz` | 全美 51 个州周度 COVID-19 新增住院面板 (Delta, Omicron, JN.1) |
| `data/panels/flu_weekly_hospitalizations.csv.gz` | 全美 51 个州周度流感新增住院面板 (2022--23, 2024--25) |
| `data/panels/rsv_weekly_hospitalizations.csv.gz` | 全美 51 个州周度 RSV 新增住院面板 (2024--25, 2025--26) |
| `data/hub/hub_forecasts_with_baseline.csv.gz` | COVID-19 Forecast Hub 官方集成模型每周点位及分位数预测与持续性基线数据 |
| `data/hub/verify_forecast_hub.json` | 预测枢纽 12 个原点 1--4 周技能衰减统计结果 |

---

## 7. 汇报与演示成果 (`presentation/`)
| 磁盘文件路径 | 说明 |
|---|---|
| `presentation/epidemic_predictability_masterclass.pptx` | 面向公共卫生管理者与学术同行的 Masterclass 完整汇报幻灯片 |
| `presentation/index.html` | 交互式研究成果全景可视化与论文导读单页网页 |
