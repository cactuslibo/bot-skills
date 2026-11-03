import json
from r5 import *
PRE=('2015-01-01','2022-01-01'); OOS=('2022-01-01','2026-10-30')
mk=Mkt('QQQ'); cands=candidates()
m_pre=(mk.days>=pd.Timestamp(PRE[0]))&(mk.days<pd.Timestamp(PRE[1]))
rf=np.array([EFFR.get(d.year,0)/100/252 for d in mk.days])
b=build(mk,'P2',None); bdr=mk.returns(*b,True); bpre=full_report(mk,*b,*PRE)
rows=[];Rm=[];Dm=[]
for fam,p in cands:
    w=build(mk,fam,p); dr=mk.returns(*w,True); s=full_report(mk,*w,*PRE)
    R=(s['exSharpe']-bpre['exSharpe'])+(s['win']-bpre['win'])+0.5*(s['cagr']-bpre['cagr'])
    rows.append(dict(fam=fam,p=p,pre=s,R=R)); Rm.append(dr[m_pre]-rf[m_pre]); Dm.append(dr[m_pre]-bdr[m_pre])
Rm=np.array(Rm).T; Dm=np.array(Dm).T
fams=sorted(set(r['fam'] for r in rows)); best_f={}
for f in fams:
    ii=[i for i,r in enumerate(rows) if r['fam']==f]; k=max(ii,key=lambda i:rows[i]['R']); best_f[f]=k
    prc,pspa=rc_spa(Dm[:,ii]); best_f[f]=(k,prc,pspa)
prc_all,pspa_all=rc_spa(Dm); pb,ncomb=pbo(np.column_stack([Rm,(bdr-rf)[m_pre]]))
chosen=max(range(len(rows)),key=lambda i:rows[i]['R'])
# DSR：五轮全部试验数（R1 600 + R2 400 + R3 14×400 + R4 8×500 + R5 70）
NT=600+400+14*400+8*500+len(cands); srs=Rm.mean(0)/Rm.std(0)
ds=dsr(Rm[:,chosen],NT,srs.var()); ds_p2=dsr((bdr-rf)[m_pre],NT,srs.var())
print('P2 pre',{k:round(v,4) for k,v in bpre.items()})
for f,(k,prc,pspa) in best_f.items(): print(f,'best',rows[k]['p'],'R=%.3f'%rows[k]['R'],{a:round(v,4) for a,v in rows[k]['pre'].items()},'RC p=%.3f SPA p=%.3f'%(prc,pspa))
print('ALL RC p=%.3f SPA p=%.3f'%(prc_all,pspa_all),'PBO=%.3f (%d combos)'%(pb,ncomb),'chosen',rows[chosen]['fam'],rows[chosen]['p'],'DSR',ds,'P2 DSR',ds_p2,'NT',NT)
# 跨 ETF 验证（预样本外 + 样本外；同一冻结参数）
ETF=['XLK','XLY','XLF','XLI','XLV','XLP','XLE','XLB','XLU']; xv={}
sel=[best_f[f][0] for f in fams]
for tk in ETF:
    e=Mkt(tk); eb=build(e,'P2',None); xv[tk]={}
    for seg,(lo,hi) in {'pre':PRE,'oos':OOS}.items():
        sb=full_report(e,*eb,lo,hi)
        for k in sel:
            s=full_report(e,*build(e,rows[k]['fam'],rows[k]['p']),lo,hi)
            xv[tk][f"{rows[k]['fam']}_{seg}"]=dict(dExS=s['exSharpe']-sb['exSharpe'],dWin=s['win']-sb['win'],dCagr=s['cagr']-sb['cagr'])
for k in sel:
    f=rows[k]['fam']
    for seg in ('pre','oos'):
        v=[xv[t][f'{f}_{seg}'] for t in ETF]
        print('XETF',f,seg,'dExSharpe>0: %d/9'%sum(x['dExS']>0 for x in v),'dWin>0: %d/9'%sum(x['dWin']>0 for x in v),'mean dExS %.3f mean dCAGR %.4f'%(np.mean([x['dExS'] for x in v]),np.mean([x['dCagr'] for x in v])))
# QQQ 样本外：一次（预先声明 chosen；各族最佳作为参考一并列出）
oos={'P2':full_report(mk,*b,*OOS)}
for k in sel: oos[rows[k]['fam']]=full_report(mk,*build(mk,rows[k]['fam'],rows[k]['p']),*OOS)
for n,s in oos.items(): print('OOS',n,{a:round(v,4) for a,v in s.items()})
json.dump(dict(rows=rows,best_f={f:dict(idx=k,p=rows[k]['p'],p_rc=a,p_spa=c) for f,(k,a,c) in best_f.items()},rc_all=prc_all,spa_all=pspa_all,pbo=pb,
  chosen=dict(fam=rows[chosen]['fam'],p=rows[chosen]['p']),dsr=ds,dsr_p2=ds_p2,ntrials=NT,xetf=xv,oos=oos),open('r5_results.json','w'),indent=1,default=float)
