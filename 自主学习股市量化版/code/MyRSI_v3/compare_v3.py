# 对照组 + 2024 一次性查看（须记入 VAL_LOG）。交易口径统一用 v3.daily/position 与 run_v3.tst。
import json,sys,numpy as np
import v3; P=v3.P; from run_v3 import tst,TRN
sys.path.insert(0,'/workspace/myrsi_top'); import myr as Q
assert (Q.lab==P.lab).all() and (Q.ok==P.ok).all()
O=json.load(open('main_results.json')); OM=json.load(open('/workspace/myrsi_top/main_results.json')); OT=json.load(open('/workspace/quant_topdiv/MyRSI/main_results.json'))
EXT=dict(trig=0,thr=50.0,tf=0,tN=200,kc=0,buf=0.0,nb=1)
def cnt(sig,years):
    s=sig[np.isin(P.yr[sig],years)]; N=len(s); k=int(P.lab[s].sum()); pb=float(np.mean([P.BR[y] for y in P.yr[s]])) if N else None
    cid=np.full(P.n,-1); m=P.lab&P.ok&np.isin(P.yr,years); idx=np.flatnonzero(m); g=np.r_[0,np.cumsum(np.diff(idx)>1)]; cid[idx]=g
    return dict(n=N,prec=k/N if N else None,base=pb,cp_lo=P.cp_lo(k,N) if N else None,binom_p=P.binomtest(k,N,pb,'greater').pvalue if N else None,
                recall_cluster=len(set(cid[s][cid[s]>=0]))/(g.max()+1),missed=v3.missed(s))
def trade(w,years): d,ex=v3.daily(w); return tst(d,ex,np.isin(v3.DY,years))[0]
R={}
f,vt=O['size_train'][1],O['size_train'][2]; vb=O['volbase_train'][1]
groups={'new_v3':lambda yrs:P.signals(O['best'],yrs),'orig_myrsi_v2':lambda yrs:Q.signals(OM['best'],yrs),'topdiv_prev':lambda yrs:P.signals({**OT['best'],**EXT},yrs)}
for nm,fn in groups.items():
    for tag,yrs in (('train',TRN),('2024',[2024])):
        s=fn(yrs); R[f'{nm}_{tag}']=dict(**cnt(s,yrs),trade_full_exit=trade(v3.position(s,1,0),yrs))
R['new_v3_2024']['trade_sized']=trade(v3.position(groups['new_v3']([2024]),f,vt),[2024])
R['new_v3_train']['trade_sized']=trade(v3.position(groups['new_v3'](TRN),f,vt),TRN)
# 对照 LOYO（原代码各折参数）
lo_o=np.array(sorted(sum([list(Q.signals(v['p'],[int(y)])) for y,v in OM['loyo'].items()],[])),int)
lo_t=np.array(sorted(sum([list(P.signals({**v['p'],**EXT},[int(y)])) for y,v in OT['loyo'].items()],[])),int)
lo_n=np.array(sorted(sum([list(P.signals(v['p'],[int(y)])) for y,v in O['loyo'].items()],[])),int)
for nm,s in (('orig_myrsi_v2',lo_o),('topdiv_prev',lo_t),('new_v3',lo_n)): R[f'{nm}_loyo']=dict(**cnt(s,TRN),trade_full_exit=trade(v3.position(s,1,0),TRN))
R['volbase_train']=dict(vt=vb,trade=trade(v3.position([],0,vb),TRN)); R['volbase_2024']=dict(vt=vb,trade=trade(v3.position([],0,vb),[2024]))
R['size_train']=dict(f=f,vt=vt)
# 邻域边界
ps=[r['p'] for r in O['top5']]+[v['p'] for v in O['loyo'].values()]; R['boundary']={}
for k,(lo,hi) in [(k,v) for k,v in P.SPACE.items() if isinstance(v,tuple)]:
    x=np.array([p[k] for p in ps],float); R['boundary'][k]=dict(frac=float(np.mean((x-lo<=0.05*(hi-lo))|(hi-x<=0.05*(hi-lo)))),best=ps[0][k],loyo=[round(p[k],3) for p in ps[5:]])
json.dump(R,open('compare.json','w'),indent=1,default=lambda o:o.item() if hasattr(o,'item') else str(o)); print('ok')
