# 规则三（基于 MyRSI，指标名无空格）
指标（myrsi.pine，Pine v3，默认 L=21）：
- 灰线 boo = 100*(close + 2*stdev(close,21) - sma(close,21)) / (4*stdev(close,21))  （stdev 为总体标准差）
- 绿线 = ema(boo,12)，蓝线 = ema(boo,26)，红线 = ema(boo,120)，水平线 -40
规则三：
- 买入：绿线上穿红线，且当日收盘价 > SMA(close,200)
- 卖出：收盘价 < SMA(close,200)（与 MyRSI 无关）
- 日线；收盘判断信号，次日开盘成交；只做多，全仓，无手续费
- 测试品种：QQQ（2016-10 至 2026-10：+449%，最大回撤 18.3%，夏普 1.15；持有 +520%/35.6%），ARKG（+193% vs 持有 +194%，回撤 42.5% vs 83.7%）
文件：myrsi.pine（指标源码），myrsi_opt_3.pine（规则三 Pine 策略，尚未在 TradingView 中运行验证），bt.py/grid.py（Python 回测）
数据：/workspace/data/QQQ_daily.csv、TQQQ_daily.csv（TradingView 上市以来日线），/workspace/tv_ARKG_1D_full.csv
