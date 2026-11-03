# v2: 依据量化指标汇总事件研究预先设定（未看测试年）：VXN替代VIX(缺失回退VIX)；只用强预警档；深回撤+波动扩张=再入场
exec(open('bt.py').read().split("TRAIN=")[0].replace("vix=L('VIX').Close.reindex(c.index).ffill()","vix=L('VXN').Close.reindex(c.index).combine_first(L('VIX').Close.reindex(c.index)).ffill()"))
dh=c/c.rolling(252).max()-1; volexp=(rv/sma(rv,50)>1.2)|(vix/sma(vix,50)>1.25)
def position2(lo,hi):
    s20=sma(c,20); w=1.0; out=[]
    for i in range(len(c)):
        sc=score.iloc[i]; tgt=1.0 if sc<lo else (0.5 if sc<hi else 0.0)
        if tgt<w: w=tgt
        elif tgt>w and sc<(lo if w==0.5 else hi)-10 and c.iloc[i]>s20.iloc[i]: w=min(1.0,w+0.5)
        if newhi.iloc[i] or (dh.iloc[i]<-0.08 and volexp.iloc[i]): w=1.0
        out.append(w)
    return pd.Series(out,index=c.index)
TRAIN=[y for y in range(1990,2015) if y not in (1999,2003,2004,2005,2006,2007)]
res={}
for lo,hi in [(60,80),(50,70),(70,90)]:
    w=position2(lo,hi); r=pd.concat([run(w,y)[0] for y in TRAIN]); res[(lo,hi)]=(stats(r),w)
    print(lo,hi,{k:round(v,3) for k,v in stats(r).items()})
bh=pd.concat([ret[c.index.year==y] for y in TRAIN]); print('BH',stats(bh))
best=max(res,key=lambda k:res[k][0]['sharpe']); W2=res[best][1]; print('best',best)
TEST=[2018,1999,2005,2004,2006,2025,2007,2003,2021,2026]; rows=[]
for y in TEST:
    r,ws=run(W2,y); b=ret[c.index.year==y]; s=stats(r); sb=stats(b); cu,fl=sellfly(ws,y)
    rows.append(dict(year=y,ret=s['ret'],bh=sb['ret'],mdd=s['mdd'],bmdd=sb['mdd'],sh=s['sharpe'],bsh=sb['sharpe'],trades=int((ws.diff().abs()>0).sum()),cuts=cu,fly=fl))
d=pd.DataFrame(rows); print(d.round(3).to_string()); t=d[d.year!=2026]
print(t.mean(numeric_only=True).round(4).to_dict(),'wins',(t.ret>t.bh).sum(),(t.mdd>t.bmdd).sum(),(t.sh>t.bsh).sum(),'cum',(1+t.ret).prod()-1)
for lo,hi in res: 
  ex=[stats(run(res[(lo,hi)][1],y)[0])['ret']-stats(ret[c.index.year==y])['ret'] for y in TEST[:-1]]; print('sens',lo,hi,round(np.mean(ex),4),sum(e>0 for e in ex))
print('now',score.iloc[-1],W2.iloc[-1],vix.iloc[-1],dh.iloc[-1])
