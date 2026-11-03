# 小时策略 代码

Python 回测脚本（依赖 pandas、numpy、matplotlib），基于 MyRSI 指标。仓库里不含数据，需要自备 `/workspace/data/<TICKER>_1h.csv` 格式的小时线 OHLCV 文件。

- `bt_hourly.py`：QQQ 小时线 MyRSI 策略变种的网格搜索，以及与买入持有的对比。
- `etf_bt.py`：对 XL 系列和 ARK 系列共 20 只 ETF 逐一搜索最优变种，用 60/40 划分样本内外，每边成本 0.05%。
- `etf_bear.py`：剔除 2018Q4、2020-02~03、2021-11~2022-12 三段熊市区间后重跑。
