import yfinance as yf, pandas as pd
for t in ['^NDX','^IXIC','QQQ','^VIX','^IRX','HYG','LQD','RSP']:
    d=yf.download(t,start='1985-01-01',end='2026-11-03',auto_adjust=True,progress=False)
    d.columns=[c[0] if isinstance(c,tuple) else c for c in d.columns]
    d.to_csv(t.replace('^','')+'.csv'); print(t,d.index[0].date(),d.index[-1].date(),len(d))
