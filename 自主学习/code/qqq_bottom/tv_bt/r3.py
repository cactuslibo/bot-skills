"""Round 3: Gemini R1/R2/R3 + fallback P2. 2008-01-02..2026-10-29, 5bp/side, borrow EFFR+1% (EFFR = hard-coded annual averages in eng2.py)."""
import itertools, pickle
from cands import *
from statistics import NormalDist; N_=NormalDist()
ts=ts_real.values; s50s={n:sma(C,n).values for n in (40,50,60)}; S={n:sma(C,n).values for n in (4,5,6)}
def engine(base_fn,sat_fn,exit_fn,cost=5,cash=False):
    """base_fn(i)->base weight; sat_fn(i)->desired sat size (0 if none); exit_fn(i)->bool. Sizes decided at close, applied next open."""
    N=len(df); tgt=np.zeros(N); tr=[]; sz=0.0; ei=None
    for i in range(N):
        if np.isnan(ts[i]) or np.isnan(s200[i]): tgt[i]=0; continue
        if sz>0 and exit_fn(i): tr.append((ei,i+1 if i+1<N else i,o[ei],o[i+1] if i+1<N else c[i],'t')); sz=0.0
        else:
            n=sat_fn(i)
            if n>sz:
                if sz==0: ei=i+1 if i+1<N else i
                sz=n
        tgt[i]=base_fn(i)+sz
    if sz>0: tr.append((ei,N-1,o[ei],c[-1],'t'))
    r,w=returns(df,tgt,cost,borrow=True,cash_yield=cash)
    return dict(tr=tr,r=r,w=w,tgt=tgt,open=sz>0,pend=None)
def R1(fast=50,rsi_t=15,exs=5,**k):
    f=s50s[fast]
    return engine(lambda i:1.0 if (f[i]>s200[i] and c[i]>f[i]) else 0.0, lambda i:0.5 if (r2[i]<rsi_t and ts[i]<1) else 0, lambda i:c[i]>S[exs][i],**k)
def R2(sm=5,vt=0.95,rsi_t=15,**k):
    tsm=pd.Series(ts).rolling(sm).mean().values
    return engine(lambda i:1.0 if (c[i]>s200[i] and tsm[i]<0.98) else 0.0, lambda i:0.5 if (r2[i]<rsi_t and ts[i]<vt) else 0, lambda i:c[i]>S[5][i] or ts[i]>=1,**k)
def R3(deep=0.90,rsi_t=15,exs=5,**k):
    return engine(lambda i:0.0, lambda i:(1.0 if ts[i]<deep else 0.5 if ts[i]<1 else 0) if r2[i]<rsi_t else 0, lambda i:c[i]>S[exs][i],**k)
def P2f(**k): return engine(lambda i:0.0, lambda i:1.0 if (r2[i]<15 and ts[i]<1) else 0, lambda i:c[i]>S[5][i],**k)
F=('2008-01-02','2026-10-29')
BASE={'R1':dict(fast=50,rsi_t=15,exs=5),'R2':dict(sm=5,vt=0.95,rsi_t=15),'R3':dict(deep=0.90,rsi_t=15,exs=5)}
GR={'R1':dict(fast=[40,50,60],rsi_t=[10,15,20],exs=[4,5,6]),'R2':dict(sm=[3,5,10],vt=[0.92,0.95,0.98],rsi_t=[12,15,18]),'R3':dict(deep=[0.88,0.90,0.92],rsi_t=[12,15,18],exs=[4,5,6])}
FN={'R1':R1,'R2':R2,'R3':R3}
prev=pickle.load(open('round2_out.pkl','rb')); V=(prev['meta']['Vsr_ann']/np.sqrt(252))**2
NT=prev['meta']['Ntot']+sum(27 for _ in GR)+4   # +81 grid + fallback variants
def dsr(st):
    g=0.5772156649; sr0=np.sqrt(V)*((1-g)*N_.inv_cdf(1-1/NT)+g*N_.inv_cdf(1-1/(NT*np.e)))
    return N_.cdf((st['srd']-sr0)*np.sqrt(st['T']-1)/np.sqrt(1-st['skew']*st['srd']+(st['kurt']-1)/4*st['srd']**2))
B=bh(); bmdd=stats(df,B,*F,0)['MDD']
def S_(R,a,b): return stats(df,R,a,b,5)
res={}
for k,f in FN.items():
    R=f(**BASE[k]); st=S_(R,*F); oo=S_(R,'2022-01-01','2026-10-29'); y8=S_(R,'2008-01-01','2008-12-31'); y22=S_(R,'2022-01-01','2022-12-31')
    grid=[]
    for combo in itertools.product(*GR[k].values()):
        kw=dict(zip(GR[k].keys(),combo)); grid.append((kw,S_(f(**kw),*F)['sharpe']))
    nb=[sh for kw,sh in grid if sum(kw[p]!=BASE[k][p] for p in kw)==1]
    drop=max((st['sharpe']-x)/st['sharpe'] for x in nb)
    ov=(k!='R3'); Rc=f(**BASE[k],cash=True); cy=S_(Rc,*F)['CAGR']
    G=[('交易≥100',st['trades'],st['trades']>=100),('DSR≥0.90',dsr(st),dsr(st)>=0.90),('PF≥1.7',st['PF'],st['PF']>=1.7),
       ('全期Sharpe≥%.2f'%(0.80 if ov else 0.75),st['sharpe'],st['sharpe']>=(0.80 if ov else 0.75)),('OOS Sharpe≥0.80',oo['sharpe'],oo['sharpe']>=0.8),
       ('Calmar≥%.2f'%(0.85 if ov else 0.65),st['calmar'],st['calmar']>=(0.85 if ov else 0.65)),
       ('MDD '+('≤50%%×B&H(%.1f%%)'%(bmdd*50) if ov else '优于-15%'),st['MDD'],st['MDD']>=(bmdd*0.5 if ov else -0.15)),
       ('回撤期≤24月',st['dd_days'],st['dd_days']<=731),('胜率≥70%',st['win'],st['win']>=0.7),('盈亏比≥0.85',st['WL'],st['WL']>=0.85),
       ('邻域降幅≤25%',drop,drop<=0.25 and min(nb)>0),('2008 MDD优于-12%',y8['MDD'],y8['MDD']>=-0.12),('2022 Sharpe≥0.6',y22['sharpe'],(y22['sharpe']>=0.6) if y22['sharpe']==y22['sharpe'] else False)]
    if ov: G.append(('同时胜B&H CAGR/Sharpe/MDD',f"{st['CAGR']:.3f}/{st['sharpe']:.2f}/{st['MDD']:.3f}",st['CAGR']>stats(df,B,*F,0)['CAGR'] and st['sharpe']>stats(df,B,*F,0)['sharpe'] and st['MDD']>bmdd))
    tg={'R1':[('目标:2022 Sharpe≥0.20',y22['sharpe'],y22['sharpe']>=0.2),('目标:全期Sharpe≥0.80',st['sharpe'],st['sharpe']>=0.8),('目标:MDD优于-22%',st['MDD'],st['MDD']>=-0.22)],
        'R2':[('目标:2008 MDD优于-15%',y8['MDD'],y8['MDD']>=-0.15),('目标:2022 Sharpe≥0',y22['sharpe'],y22['sharpe']>=0),('目标:全期Sharpe≥0.85',st['sharpe'],st['sharpe']>=0.85)],
        'R3':[('目标:全期Sharpe≥0.75',st['sharpe'],st['sharpe']>=0.75),('目标:MDD优于-12%',st['MDD'],st['MDD']>=-0.12),('目标:2022 Sharpe≥0.70',y22['sharpe'],y22['sharpe']>=0.7),('目标:Calmar≥0.65',st['calmar'],st['calmar']>=0.65)]}[k]
    res[k]=dict(G=G+tg,st=st,o=oo,y8=y8,y22=y22,grid=grid,cy=cy,last=R['tgt'][-1],exp22=S_(R,'2022-01-01','2022-12-31')['avgw'])
    print(f"\n== {k} base {BASE[k]}  CAGR {st['CAGR']:.1%} (cash@EFFR {cy:.1%}) Sharpe {st['sharpe']:.2f} MDD {st['MDD']:.1%} exp {st['avgw']:.2f} | OOS {oo['sharpe']:.2f} | 2008 tot {y8['tot']:.1%} MDD {y8['MDD']:.1%} | 2022 Sharpe {y22['sharpe']:.2f} tot {y22['tot']:.1%} avgw {res[k]['exp22']:.2f} | last tgt {R['tgt'][-1]}")
    for g,v,ok in G+tg: print(f"   {g:28s} {v if isinstance(v,str) else round(float(v),3)} {'✅' if ok else '❌'}")
    gs=[x[1] for x in grid]; print('   grid Sharpe min/med/max',round(min(gs),2),round(np.median(gs),2),round(max(gs),2),'passes',sum(ok for _,_,ok in G+tg),'/',len(G+tg))
print('NT',NT,'B&H 2008+ MDD',round(bmdd,3),stats(df,B,*F,0)['CAGR'],stats(df,B,*F,0)['sharpe'])
# --- verification
p0=P2f(cost=5); 
for lab,(a,b) in {'2022':('2022-01-01','2022-12-31'),'2008':('2008-01-01','2008-12-31')}.items():
    s=S_(p0,a,b); print('P2',lab,'sharpe',round(s['sharpe'],3),'tot',round(s['tot'],4),'MDD',round(s['MDD'],4))
s50=sma(C,50); s2=sma(C,200); x=(s50<s2)&(s50.shift()>=s2.shift()); y=(s50>s2)&(s50.shift()<=s2.shift())
print('death cross',[d.date() for d in x[x].index if '2021-06'<=str(d.date())<='2023-12'],'golden',[d.date() for d in y[y].index if '2021-06'<=str(d.date())<='2023-12'])
for a,b in [F,('2016-01-22','2026-10-29'),('2022-01-01','2026-10-29'),('2023-01-01','2026-10-29')]:
    for cost in (0,5):
        for cash in (False,True):
            s=stats(df,P2f(cost=cost,cash=cash),a,b,cost); print(f'P2 {a}~{b} {cost}bp cash={cash}: CAGR {s["CAGR"]:.2%} Sharpe {s["sharpe"]:.2f} MDD {s["MDD"]:.1%}')
sf=S_(P2f(),*F); print('P2 fallback 2008+ stats',{k:round(float(v),3) for k,v in sf.items()},'DSR',round(dsr(sf),3))
print('state 10-29: RSI2',round(r2[-1],1),'VIX/VIX3M',round(ts[-1],3),'C',c[-1],'SMA5',round(S[5][-1],2),'SMA50',round(s50s[50][-1],2),'SMA200',round(s200[-1],2),'SMA5(ts)',round(pd.Series(ts).rolling(5).mean().iat[-1],3), df.index[-1].date())
pickle.dump(res,open('round3_out.pkl','wb'))
