# 量化指标汇总：代码

## indicator_correlation/
指标类内相关性分析（yfinance 日线，10 个标的，2011–2026）：
- `indicators.py`：计算各指标并做平稳化处理。
- `analyze.py`：Spearman、距离相关、分市场状态检验、bootstrap、层次聚类、VIF 和 PCA。
- `subcluster.py`：大簇的子聚类，并用 ARI 对比 Ward 聚类。
- `make_report.py`：生成报告。

## ndx_top_study/
QQQ 逃顶组合的事件研究：
- `study.py`：计算信号触发后 20 日和 60 日的前向收益与回撤。
- `gen_doc*.py`：生成指标清单文档。

## 说明
- 依赖：python3、pandas、numpy、scipy、yfinance、dcor（距离相关）。
- 不含数据文件，也不含任何密钥。
