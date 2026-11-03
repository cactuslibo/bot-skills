# 企业估值分析 代码

- `tem/yf.py`：用 yfinance 拉取 Tempus AI (TEM) 行情与财务数据，保存为 yf.json
- `tem/model.py`：TEM 估值模型（DCF + 可比公司，全面摊薄股本）
- `tem/model_boom.py`：TEM 在 AI 制药繁荣情景下的估值（熊/基/牛三情景，分有约束和无约束两个版本），并反推现价隐含的情景概率
- `fvrr/model.py`：Fiverr (FVRR) 估值（DCF 三情景、WACC×g 敏感性、反向 DCF）

依赖：Python 3、yfinance、numpy。只用免费公开数据，不含任何密钥。
