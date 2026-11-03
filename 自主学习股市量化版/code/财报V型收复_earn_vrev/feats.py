import pandas as pd, numpy as np
from scipy import stats
E=pd.read_csv('events_all.csv'); E['date']=pd.to_datetime(E.date)
feats={'gap':'缺口(开盘/前收)','volx_D':'D日量倍数','volx_D1':'D+1量倍数','clv_D':'D日收盘位置','clv_D1':'D+1收盘位置','pre60':'财报前60日涨幅','pre250':'财报前250日涨幅','drop_sig':'跌幅/σ','surprise':'EPS超预期%','above_ma200':'前收>MA200'}
res=[];trials=0
for g in 'AB':
  V=E[E['grp'+g]=='V'].copy()
  tr=V[V.year<=2015]; te=V[V.year>=2016]
  for f,name in feats.items():
    trials+=1
    if f=='above_ma200': hi=lambda d:d[f].astype(bool)
    else:
      th=tr[f].median(); hi=lambda d,th=th:d[f]>th
    row=dict(定义=g,特征=name,阈值='True' if f=='above_ma200' else round(float(tr[f].median()),3))
    for nm,d in (('训练',tr),('测试',te)):
      a=d[hi(d)].x120.dropna(); b=d[~hi(d)].x120.dropna()
      t,p=stats.ttest_ind(a,b,equal_var=False)
      row[f'{nm}_高组超额120']=a.mean(); row[f'{nm}_低组超额120']=b.mean(); row[f'{nm}_差']=a.mean()-b.mean(); row[f'{nm}_p']=p
      ta=d[hi(d)].trend120.dropna().astype(bool).mean(); tb=d[~hi(d)].trend120.dropna().astype(bool).mean(); row[f'{nm}_趋势率差']=ta-tb
    row['方向一致']=np.sign(row['训练_差'])==np.sign(row['测试_差'])
    res.append(row)
R=pd.DataFrame(res); R.to_csv('features_oos.csv',index=False)
pd.set_option('display.width',250); print(R.round(3).to_string()); print('trials',trials)
# combined rule pre-registered: above MA200 & pre60>0 & clv_D1>0.7 & volx_D>3
for g in 'AB':
  V=E[E['grp'+g]=='V']; m=V.above_ma200.astype(bool)&(V.pre60>0)&(V.clv_D1>0.7)&(V.volx_D>3)
  for nm,d in (('训练',V.year<=2015),('测试',V.year>=2016)):
    a=V[m&d].x120.dropna(); b=V[~m&d].x120.dropna()
    print(g,nm,'rule N',len(a),round(a.mean(),4),'rest',round(b.mean(),4),'p',round(stats.ttest_ind(a,b,equal_var=False)[1],3),'trend',round(V[m&d].trend120.dropna().astype(bool).mean(),3))
# industry: need sector; trend base rate
C={}
import glob,random
random.seed(0)
rows=[]
for p in random.sample(glob.glob('/workspace/tv_db/daily/*.csv'),300):
  t=p.split('/')[-1][:-4]
  if t in set(pd.read_csv('/workspace/tv_db/universe_10B.csv').query("type!='stock'").Symbol): continue
  c=pd.read_csv(p).close.values
  for i in range(260,len(c)-121,40):
    y=np.log(c[i:i+121]); s,_,r,_,_=stats.linregress(np.arange(121),y); rows.append((s>0)&(r*r>=0.6))
print('base trend120 rate',np.mean(rows),len(rows))
