from bt import *; import bt, sys
sym=sys.argv[1] if len(sys.argv)>1 else 'QQQ'
d=load(sym); S,E='2016-10-28','2026-10-28'
c=d.Close; 
def bh(a,b):
    x=c[(c.index>=a)&(c.index<=b)]; return x.iloc[-1]/x.iloc[0]-1
print(sym,'BH full',bh(S,E),'IS',bh(S,'2021-12-31'),'OOS',bh('2022-01-01',E))
pairs=[('boo','g'),('boo','b'),('g','b'),('boo','r'),('g','r'),('b','r'),('boo','zero'),('boo','m40')]
res=[]
for L in [14,21,30]:
  I=ind(d,L)
  for p in [3,5]:
    bt.PV=pivots(I.boo,p)
    for en in pairs:
     for exn in pairs:
      for filt in ['none','sma200','br']:
       for hl in [0,1]:
        for lh,lvl in [(0,0),(1,-100),(1,0)]:
          if p==3 and not(hl or lh): continue
          k=(L,p,en,exn,filt,hl,lh,lvl)
          f=run(I,en,exn,filt,hl,lh,lvl,S,E)
          a=run(I,en,exn,filt,hl,lh,lvl,S,'2021-12-31'); b=run(I,en,exn,filt,hl,lh,lvl,'2022-01-01',E)
          res.append(dict(k=k,**f,IS=a['ret'],OOS=b['ret']))
R=pd.DataFrame(res); R.to_pickle(sym+'_grid.pkl')
pd.set_option('display.width',250);pd.set_option('display.max_colwidth',90)
print(R.sort_values('ret',ascending=False).head(25))
print(R.sort_values('sh',ascending=False).head(15))
