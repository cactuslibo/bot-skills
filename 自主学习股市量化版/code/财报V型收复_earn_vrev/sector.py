import yfinance as yf,pandas as pd,os
from concurrent.futures import ThreadPoolExecutor
E=pd.read_csv('events_all.csv'); T=E.ticker.unique()
def f(t):
    try: return t,yf.Ticker(t.replace('.','-')).info.get('sector')
    except: return t,None
with ThreadPoolExecutor(6) as ex: r=list(ex.map(f,T))
pd.DataFrame(r,columns=['ticker','sector']).to_csv('sectors.csv',index=False)
