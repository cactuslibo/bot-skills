# TradingView bot code

No keys, data files or private information are included. Data is generated locally under /workspace.

- `export/grab.sh`: copies the newest TradingView "Download chart data" CSV from ~/Downloads into the database directory.
- `export/normalize.py`: normalizes raw TradingView exports to date,open,high,low,close,volume, writes SQLite, and generates manifest.csv (with anomaly flags).
- `wyckoff/scan_schematic2.py`: Wyckoff accumulation Schematic #2 (no break) scan. It checks the prior decline, SC, AR, Phase C low, rally volume and current position, and outputs a sorted candidate CSV.
- `qqq_bottom/backtest.py`, `oos.py`: QQQ bottom-buying strategy backtest and out-of-sample test.
- `qqq_bottom/deb.py`, `deb3.py`, `fb.py`: verification scripts written during the strategy debate and review rounds.
- `qqq_bottom/p2_daily.py`: daily P2 strategy status and sell-signal check.
- `qqq_bottom/tv_bt/`: indicators (ind), candidate rules (cands), backtest engine (bt, eng2), evaluation (eval2), gates (gates), grid search (grid), robustness (robust), and selection (pick, p12, r3).
