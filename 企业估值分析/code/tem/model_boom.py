# AI 制药爆发情景 DCF（独立于 model.py）
import json
WACC0=0.1234; G0=0.03; FD=195.984756; NC=581.8
DX0=1600*550.4/730.6; DA0=1600-DX0   # 2026 segment split by 1H26 mix
YEARS=range(2027,2037)
def fade(a,b,i,n=10): return a+(b-a)*i/(n-1)
SC={ # assumptions
 'mild':   dict(da_g=0.35,dx_g=0.22,da_end=0.06,dx_end=0.05,mult=1.5,opex_lt=0.45),
 'base':   dict(da_g=0.45,dx_g=0.26,da_end=0.07,dx_end=0.05,mult=2.0,opex_lt=0.42),
 'extreme':dict(da_g=0.60,dx_g=0.32,da_end=0.08,dx_end=0.06,mult=3.0,opex_lt=0.40),
}
CON=dict(share_cap=0.15,price_eros=0.03,gm_da=0.75,gm_dx=0.65)   # constraints
UNC=dict(share_cap=None,price_eros=0.0,gm_da=0.85,gm_dx=0.70)
TAX=0.18; CAPEX=0.025; OPEX26=0.66
def run(s,c,wacc=WACC0,g=G0,detail=False):
    p=SC[s]; da,dx=DA0,DX0; rows=[]; pv=0
    rwe=5430*1.149  # RWE market 2026 (MarketsandMarkets)
    for i,y in enumerate(YEARS):
        da*=1+fade(p['da_g'],p['da_end'],i); dx*=1+fade(p['dx_g'],p['dx_end'],i)
        rwe*=1.149 if y<=2031 else 1.08
        boom_mult=1+(p['mult']-1)*min(i+1,5)/5
        da_eff=da*(1-c['price_eros'])**(i+1)
        if c['share_cap']: da_eff=min(da_eff,rwe*boom_mult*c['share_cap'])
        gmda=fade(0.707,c['gm_da'],min(i,6),7); gmdx=fade(0.62,c['gm_dx'],min(i,6),7)
        rev=da_eff+dx; gp=da_eff*gmda+dx*gmdx
        opex=fade(OPEX26,p['opex_lt'],min(i,6),7)*rev
        ebit=gp-opex; fcf=ebit-max(ebit,0)*TAX-CAPEX*rev*0.5  # D&A≈capex, net capex half
        pv+=fcf/(1+wacc)**(i+1)
        rows.append(dict(y=y,da=da_eff,dx=dx,rev=rev,gm=gp/rev,m=fcf/rev,fcf=fcf,cap=rwe*boom_mult*(c['share_cap'] or 0)))
    tv=rows[-1]['fcf']*(1+g)/(wacc-g)/(1+wacc)**10
    ev=pv+tv; px=(ev+NC)/FD
    return (px,ev,tv/ev,rows) if detail else px
out={}
for s in SC:
  for lab,c in [('con',CON),('unc',UNC)]:
    px,ev,tvs,rows=run(s,c,detail=True); out[f'{s}_{lab}']=px
    print(f'== {s} {lab}: px {px:.1f} EV {ev:.0f} TV% {tvs:.2f}')
    for r in rows:
      if r['y'] in (2027,2028,2029,2031,2033,2036): print(r['y'],{k:round(v,3) if isinstance(v,float) else v for k,v in r.items() if k!='y'})
print('sens (constrained)')
for s in SC:
  print(s)
  for W in [0.10,0.11,0.1234,0.13,0.14]: print(W,[round(run(s,CON,W,G),1) for G in [0.02,0.03,0.04]])
# single-constraint attribution (base)
for k in ['share_cap','price_eros','gm_da','gm_dx']:
  c=dict(UNC); c[k]=CON[k]; print('only',k,round(run('base',c),1))
for k in ['share_cap','price_eros','gm_da','gm_dx']:
  c=dict(CON); c[k]=UNC[k]; print('relax',k,round(run('base',c),1))
json.dump(out,open('boom_out.json','w'),indent=1)
