# 股市信息检索 · 代码

## yf.py
用 yfinance 批量抓取一组美股（默认 TEM、GH、CAI、NEO、NTRA 及 10 年期美债收益率 ^TNX）的关键行情与基本面：现价、市值、企业价值、营收、毛利率、增长、现金/债务、股本、beta、利润率、自由现金流、P/S、EV/Revenue、最近收盘价，以及分析师营收一致预期。结果以 JSON 输出到标准输出。

运行：
```bash
pip install yfinance
python yf.py > yf.json
```
修改脚本中的代码列表即可换股票。无需任何 API key。
