import pandas as pd, json, sys, os
D='/workspace/exports_1102' if len(sys.argv)<2 else sys.argv[1]
def load(p):
    df=pd.read_csv(p); c=df.columns[0]
    t=df[c]
    if pd.api.types.is_numeric_dtype(t): df['date']=pd.to_datetime(t,unit='s',utc=True).dt.tz_convert('America/New_York').dt.date.astype(str)
    else: df['date']=t.astype(str).str[:10]
    return df.set_index('date')
q=load(f'{D}/QQQ.csv'); v=load(f'{D}/VIX.csv'); v3=load(f'{D}/VIX3M.csv')
c=q['close']
sma5=c.rolling(5).mean()
d=c.diff(); up=d.clip(lower=0); dn=-d.clip(upper=0)
au=up.ewm(alpha=0.5,adjust=False).mean(); ad=dn.ewm(alpha=0.5,adjust=False).mean()
rsi=100-100/(1+au/ad)
out=pd.DataFrame({'close':c,'open':q['open'],'sma5':sma5,'rsi2':rsi,'vix':v['close'],'vix3m':v3['close']})
out['ratio']=out.vix/out.vix3m
print(out.tail(8).round(4).to_string())
