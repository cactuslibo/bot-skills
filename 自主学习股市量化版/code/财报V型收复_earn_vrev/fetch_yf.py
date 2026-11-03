import yfinance as yf, pandas as pd, os, sys, time
from concurrent.futures import ThreadPoolExecutor
u=pd.read_csv('/workspace/tv_db/universe_10B.csv'); T=u[u.type=='stock'].Symbol.tolist()
def f(t):
    p=f'ed/{t}.csv'
    if os.path.exists(p): return
    for k in range(3):
        try:
            d=yf.Ticker(t.replace('.','-')).get_earnings_dates(limit=100)
            if d is not None and len(d): d.to_csv(p); return
            open(p+'.empty','w'); return
        except Exception as e:
            time.sleep(5*(k+1))
    open(p+'.err','w')
with ThreadPoolExecutor(4) as ex: list(ex.map(f,T))
