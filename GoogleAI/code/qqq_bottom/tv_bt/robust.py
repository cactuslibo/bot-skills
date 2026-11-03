from bt import *
q=pd.read_csv('/workspace/data/QQQ_daily.csv',parse_dates=['date']).set_index('date'); O,H,L,C=q.open,q.high,q.low,q.close
r2=rsi(C,2); s5=sma(C,5); s200=sma(C,200); g=wvf(C,L)[4]; b=boo(C)
S={'bench RSI2<10/SMA5/200':((C>s200)&(r2<10),C>s5),'P1 RSI2<15/RSI2>70/200':((C>s200)&(r2<15),r2>70),
   'P3 WVF green/RSI2>70':(g,r2>70),'P4 boo<0&C>200/SMA5':((b<0)&(C>s200),C>s5)}
for k,(e,x) in S.items():
    tr,ret,inp,_,_=run(q,e,x)
    for a,bb in [('2000-01-01','2026-12-31'),('2000-01-01','2015-12-31')]: print(k,a[:4],bb[:4],{kk:round(v,3) for kk,v in stats(q,tr,ret,inp,a,bb).items()})
df=load('2015-01-01'); C=df.close
print(df.tail(1).T); print('RSI2',rsi(C,2).iloc[-3:].round(1).tolist(),'SMA200',sma(C,200).iat[-1].round(2),'SMA5',sma(C,5).iat[-1].round(2),
 'VIX/VIX3M',(df.vix/df.vix3m).iat[-1].round(3),'WVF',[round(v.iat[-1],2) for v in wvf(C,df.low)[:4]],'boo',boo(C).iat[-1].round(1),'MO',mcclellan(df.adv,df.dec).iat[-1].round(1))
