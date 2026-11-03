# 每日量化策略检测 —— 代码说明

所有数据文件（csv/json/pkl/图片/日志/state）均未上传；运行前需自行准备 TradingView 导出或用 yfinance 下载日线数据，并按脚本内路径放置（默认在 `/workspace/...`，可自行修改）。

| 脚本 | 作用 |
|---|---|
| strategy_compare/framework.py | 通用回测/信号框架（数据加载、持仓与绩效计算） |
| strategy_compare/strategies_daily.py | 五个策略（MyRSI、园园1x、v1、v2、P2）的日线信号实现 |
| strategy_compare/matrix.py | 生成各标的×策略的当日状态矩阵与变动 |
| ndx_escape/bt.py | 纳指逃顶策略 v1 回测 |
| ndx_escape/v2.py | 纳指逃顶策略 v2 回测 |
| myrsi/daily.py | MyRSI 规则三每日信号（20 只 ETF 持有/空仓及当日买卖） |
| nazhi_siji/siji_1x.py | 园园策略（纳指四季 V22.3）单一 1x ETF+现金版 |
| nazhi_siji/backtest.py | 园园AI 策略回测（QQQ 信号，持 TQQQ） |
| nazhi_siji/backtest_tv.py | 同上，使用 TradingView 数据版本 |
| qqq_bottom/p2_daily.py | P2 抄底模型每日信号（RSI2 + VIX/VIX3M） |
| qqq_bottom/backtest.py, oos.py | P2 等抄底模型回测与样本外检验 |
| qqq_bottom/deb*.py, fb.py, g.py | 调用 Gemini 做模型辩论/反馈的辅助脚本（需环境变量 `GEMINI_API_KEY`） |

## 运行
```bash
pip install pandas numpy yfinance
python myrsi/daily.py
python qqq_bottom/p2_daily.py
python strategy_compare/matrix.py
```
