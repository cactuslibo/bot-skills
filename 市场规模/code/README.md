# scripts
- `bass_fit.py`：Bass(m,p,q) / Logistic(K,r,t0) 拟合与外推。原创编写（公式依据 Bass 1969），离线运行、只读输入 CSV、只打印到 stdout，无网络、无 shell 调用。依赖 numpy、scipy。适用说明见 market-forecast-growth.md 第 5 节。
- 未复制原仓库脚本。已审阅（只读，未运行）：AlphaMao1 market-sizing/scripts（data_fetcher.py 用 urllib 访问 World Bank/DBnomics 公开 API，FRED 需 FRED_API_KEY 环境变量，可选 pytrends；report_generator.py 等仅本地生成 Excel/Markdown；未发现 subprocess/eval/删除操作）和 deanpeters tam-sam-som-calculator/scripts/market-sizing.py（95 行纯算术）。需要时可直接从原仓库取用。
