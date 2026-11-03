import numpy as np, json
rf=0.04929; erp=0.05; beta=1.6
ke=rf+beta*erp; kd=0.07; E=13161.5; D=1444.2
wacc=E/(E+D)*ke+D/(E+D)*kd
FD=180.434756+15.55   # fully diluted shares (M)
cash=816.0; debt_nc=1444.2-1210.0  # debt excluding converts (Google note + leases etc.)
netcash=cash-debt_nc
R26=1600.0; fcf26_m=-0.03
AZ=45.0  # est annual AZ revenue
def proj(g1,gT,mT,az_renew,wacc=wacc,g=0.03,years=10,ramp=7):
    rev=[];R=R26
    for t in range(1,years+1):
        gr=g1+(gT-g1)*(t-1)/(years-1)
        R=R*(1+gr)
        if not az_renew: R_adj=R-AZ*(1+0.0)  # lost AZ rev each yr
        else: R_adj=R
        rev.append(R_adj)
    m=[fcf26_m+(mT-fcf26_m)*min(t,ramp)/ramp for t in range(1,years+1)]
    # lost AZ revenue at 70% GM reduces FCF margin implicitly: subtract 70%*AZ*(1-0.0) extra beyond margin? keep margin on adj rev and extra hit
    fcf=[r*mm - (0 if az_renew else AZ*0.70*0.5) for r,mm in zip(rev,m)]
    pv=sum(f/(1+wacc)**(t+0.0) for t,f in enumerate(fcf,1))  # end-year discounting from 2026-12-31 approx
    tv=fcf[-1]*(1+g)/(wacc-g); pvtv=tv/(1+wacc)**years
    ev=pv+pvtv; eq=ev+netcash
    return dict(ev=ev,eq=eq,px=eq/FD,pv_fcf=pv,pv_tv=pvtv,tv_share=pvtv/ev,rev27=rev[0],rev31=rev[4],rev36=rev[-1],fcf31=fcf[4],fcf36=fcf[-1],cagr5=(rev[4]/R26)**(1/5)-1)
sc={
 'bear_noAZ':dict(g1=0.14,gT=0.04,mT=0.10,az_renew=False),
 'base_noAZ':dict(g1=0.23,gT=0.05,mT=0.17,az_renew=False),
 'base_AZ':dict(g1=0.23,gT=0.05,mT=0.17,az_renew=True),
 'bull_AZ':dict(g1=0.27,gT=0.06,mT=0.24,az_renew=True),
}
res={k:proj(**v) for k,v in sc.items()}
w={'bear_noAZ':0.25,'base_noAZ':0.20,'base_AZ':0.35,'bull_AZ':0.20}
pw=sum(res[k]['px']*w[k] for k in w)
print('ke',ke,'wacc',wacc,'netcash',netcash,'FD',FD)
for k,r in res.items(): print(k,{a:round(b,3) for a,b in r.items()})
print('prob-weighted',pw)
# sensitivity base_AZ
ws=[0.10,0.11,0.12,0.13,0.14];gs=[0.02,0.025,0.03,0.035,0.04]
print('sens')
for W in ws: print(W,[round(proj(**sc['base_AZ'],wacc=W,g=G)['px'],1) for G in gs])
# reverse DCF: price 72.22 -> target equity
tgtEV=72.22*FD-netcash
print('target EV',tgtEV)
def brentq(f,a,b):
    fa=f(a)
    for _ in range(100):
        m=(a+b)/2; fm=f(m)
        if (fm>0)==(fa>0): a,fa=m,fm
        else: b=m
    return m
f=lambda g1: proj(g1=g1,gT=0.05,mT=0.17,az_renew=True)['ev']-tgtEV
g1=brentq(f,0.0,1.0); r=proj(g1=g1,gT=0.05,mT=0.17,az_renew=True); print('implied g1',g1,'cagr5',r['cagr5'],'rev36',r['rev36'])
f2=lambda m: proj(g1=0.23,gT=0.05,mT=m,az_renew=True)['ev']-tgtEV
m=brentq(f2,0.0,1.0);print('implied margin',m)
for W in [0.10,0.11,0.12,0.14]:
  print('W',W,'g1',brentq(lambda g1: proj(g1=g1,gT=0.05,mT=0.17,az_renew=True,wacc=W)['ev']-tgtEV,0,1),'m',brentq(lambda mm: proj(g1=0.23,gT=0.05,mT=mm,az_renew=True,wacc=W)['ev']-tgtEV,0,2))
