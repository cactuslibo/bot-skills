import yfinance as yf,pandas as pd,os
from concurrent.futures import ThreadPoolExecutor
E=pd.read_csv('events_all.csv'); E=E[(E.grpB.isin(['V','CTRL']))|(E.grpA.isin(['V','CTRL']))]
os.makedirs('ud',exist_ok=True)
def f(t):
    p=f'ud/{t}.csv'
    if os.path.exists(p): return
    try: yf.Ticker(t.replace('.','-')).upgrades_downgrades.to_csv(p)
    except Exception as e: open(p,'w').write('')
with ThreadPoolExecutor(4) as ex: list(ex.map(f,E.ticker.unique()))
