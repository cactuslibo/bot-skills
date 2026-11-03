import pandas as pd; R=pd.read_csv('all_results.csv',keep_default_na=False,dtype=str)
q=[('CM RSI-2 lime','RSI2<15','RSI2>70','C>SMA200'),('RSI2+breadth','RSI2<15','C>SMA5','VIX/VIX3M<1'),('WVF','WVF green','RSI2>70','none'),('MyRSI boo','boo<0','C>SMA5','C>SMA200'),('Twiggs MF','TMF<-0.1 & RSI2<10','C>SMA5','none'),('MyRSI rule3','green x red','C<SMA200 (rule3)','C>SMA200'),('RSI2 benchmark','RSI2<10','C>SMA5','C>SMA200')]
for f,e,x,fi in q:
  s=R[(R['family']==f)&(R['entry']==e)&(R['exit']==x)&(R['filter']==fi)&(R['maxd']=='-')]
  r=s.iloc[0]; print(f,'|',e,'|',x,'|',fi,'pos',r.pos_now,'sig',r.signal_1029,'pend',r.entry_pending)
  for p in ['FULL','IS','OOS']: print('  ',p,[round(float(r[p+'_'+k]),3) for k in ['trades','win','CAGR','sharpe','MDD','exposure']])
