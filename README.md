# 传染病传播动力学的可预测视界、极限机制与实证研究 (Epidemic Predictability Limits)

本工作目录为论文研究与正式投稿的**唯一核心权威工作区** (`final_clean_submission/`)，所有历史草稿、冗余副本及中间构建垃圾已全面剔除。

> **工作目录与稿件规范说明：**
> 1. 本目录即为论文主稿的根目录，核心 LaTeX 文档为根目录下的 **`main.tex`**，编译输出为 **`main.pdf`**（与根目录 **`流行病传播动力学可预测视界_最终稿.pdf`** 完全一致）。
> 2. 根目录下的 `流行病传播动力学的可预测视界、极限机制与实证研究_期刊模版版.docx` 及对应导出的 PDF 为期刊双栏格式排版衍生副本。
> 3. `Response_to_Reviewers.md` 为针对审稿意见（含 19 项问题）的官方逐条修改落实说明（唯一官方外送回复信）；`审稿意见.txt` 为内部留存之专家审查意见。

---

## 一、目录结构与核心清单

```text
.
├── main.tex                                        # 最终修订版 LaTeX 论文主文档源码（0 错误、0 溢出）
├── main.pdf                                        # Tectonic 编译产物 (42 页完整期刊论文)
├── references.bib                                  # 净化后的参考文献库（57 篇，0 未引项）
├── fig1_framework.png                              # 理论原理与双层基准框架图高清矢量渲染图
├── 流行病传播动力学可预测视界_最终稿.pdf              # 唯一官方权威终稿 PDF（与 main.pdf 字节哈希完全相同，即开即读）
├── 流行病传播动力学的可预测视界、极限机制与实证研究_期刊模版版.docx  # 按期刊双栏模版排版的 Word 终稿（衍生副本）
├── 流行病传播动力学的可预测视界、极限机制与实证研究_期刊模版版.pdf  # Word 版对应导出版（27 页，衍生副本）
├── Response_to_Reviewers.md                           # 针对终审意见（19 项问题）的官方逐条修改落实说明（外送回复信）
├── 审稿意见.txt                                     # 内部留存：原始终审专家审查报告与修改意见
├── README.md                                       # 本说明文件：项目架构、自洽规范与复现指南
├── MANIFEST.md                                     # 全量有效交付文件与磁盘真实路径全量对照表
├── environment.yml                                 # Conda 运行环境配置文件
├── LICENSE                                         # 开源学术授权协议
├── derivations/                                    # 数学定理严格推导与证明手册
│   ├── derivations_manual.tex                      # 逐行数学证明源码（统一 C >= 1,429）
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
│   └── hub/                                        # COVID-19 Forecast Hub 官方顶级集成模型预测与评估
│       ├── *-COVIDhub-ensemble.csv.gz              # 12 个代表性预测原点的官方集成模型原始预测归档 (逐周点位与分位数)
│       └── forecast_hub_operational_evaluation.json# 预测枢纽 12 个原点 1--4 周技能衰减与持续性基线对比评估结果
├── scripts_v2/                                     # 生产级可复现分析、制表与检验代码集
│   ├── make_all.py                                 # 全流程一键复现主入口
│   ├── check_consistency.py                       # 核心数理与实证断言自动化一致性检验脚本 (九大类断言)
│   ├── emit_v3.py                                  # 表格 LaTeX 片段全自动生成脚本
│   ├── state_panel_v3.py                           # 州级面板分析与滚动回测主脚本
│   ├── ingest_and_aggregate.py                     # 数据溯源与数据锁定检验脚本
│   ├── make_figures_v3.py                          # 实证图件高清渲染脚本
│   ├── make_all_figures_v2.py                      # 理论推导图件高清渲染脚本
│   ├── sim_verify_t1.py                            # 定理 1/2 分支过程模拟验证脚本
│   ├── sim_verify_t3.py                            # 定理 3 拟平稳分布数值验证脚本
│   ├── sim_verify_t4.py                            # 定理 4 Cramér–Rao 下界数值验证脚本
│   └── verify_suite.py                             # 定理 5R 与推论 1 验证脚本
├── reports/                                        # 基础理论数值模拟输出与图件
│   ├── *.json                                      # 数值模拟输出结果
│   └── figures_v2/                                 # 理论推导与下界验证图件 (图 2, 图 3, 图 4)
├── reports_v3/                                     # 经验实证分析产物与图件
│   ├── *.json                                      # 州级视界、四项误差记账与预测枢纽实证结果
│   └── figures/                                    # 实证结果高清图件 (微观拟合, 州级视界, Hub 技能衰减)
└── tables_v3/                                      # 导出的独立 LaTeX 表格源码片段
    ├── table7_micro.tex                            # 正文表 2: 微观极大似然与 CRB 检验
    ├── table2_state.tex                            # 正文表 3: 51 州可预测视界空间分布
    ├── table4_budget.tex                           # 正文表 4: 四项描述性误差记账分解
    ├── table3_rolling.tex                          # 正文表 5: 伪实时滚动业务时效双层对照
    ├── table5_hub.tex                              # 正文表 6: 预测枢纽集成预测技能衰减
    └── table6_tiers.tex                            # 正文表 7: 分级预警响应策略推荐
```

---

## 二、快速复现与一致性验证

### 1. 执行全量自动化一致性检验套件
在本项目根目录下：
```bash
python scripts_v2/check_consistency.py
```
该脚本全量执行针对表格碎片、引用图件、退役短语黑名单、摘要数值区间、CRB 比例、量纲对齐、双侧穿越、数据锁定及**文档声明路径存在性**等 **9 大类断言** 实施自动化检查。

### 2. 重新编译 LaTeX 主稿
直接在根目录下执行：
```bash
tectonic main.tex
```
当前指标：**0 Errors, 0 Overfull hboxes, 0 Undefined References**。\n