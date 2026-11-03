"""FVRR valuation model (2026-11-02). Sources noted inline. Run: python model.py"""
import json, numpy as np, warnings; warnings.filterwarnings("ignore")
import yfinance as yf
# --- Inputs: Q3'26 press release (GlobeNewswire 2026-10-29) ---
CASH = 125.471+25.997+90.0+74.754   # cash+ST MS+bank deposits+LT MS = 316.2 $M; user funds excluded (offset by user accounts)
DEBT = 0.0                           # converts repaid 2025 (no amortization in 2026 per PR); only ~$1.75M leases
SHARES = 37.236                      # Q3'26 diluted weighted avg, M (PR)
FCF_9M26 = 21.017+13.635+9.373       # PR FCF reconciliation
FY26_REV = 377.0                     # guidance midpoint $374-380M (PR)
FY26_EBITDA = 63.0                   # guidance midpoint $61-65M
FY26_FCF = FCF_9M26 + 5.0            # ASSUMPTION Q4 FCF ~ $5M (Q4 EBITDA guide $6-10M)
PRICE = float(yf.Ticker("FVRR").history(period="1d",interval="5m")["Close"].iloc[-1])
RF = float(yf.Ticker("^TNX").history(period="5d")["Close"].iloc[-1])/100  # 10y UST
ERP = 0.042                          # Damodaran implied ERP 2026-10-01
SC = {  # rev growth 2027-2031, FCFF margin 2027-2031, terminal g, beta
 "bear":dict(g=[-.28,-.15,-.08,-.05,-.03], m=[.05,.06,.07,.08,.08], tg=-.02, beta=1.55),
 "base":dict(g=[-.21,-.08,-.02,.01,.02],  m=[.08,.10,.11,.12,.12], tg=.01,  beta=1.38),
 "bull":dict(g=[-.15,.00,.05,.06,.06],    m=[.12,.14,.16,.17,.18], tg=.025, beta=1.22),
}
def dcf(g,m,tg,wacc,rev0=FY26_REV):
    r=rev0; pv=0; f=None
    for t,(gi,mi) in enumerate(zip(g,m),1):
        r*=1+gi; f=r*mi; pv+=f/(1+wacc)**(t-0.5+ (2/12))  # mid-year, valuation date ~Nov-26
    tv=f*(1+tg)/(wacc-tg); pv_tv=tv/(1+wacc)**(len(g)+2/12)
    ev=pv+pv_tv; return ev,(ev+CASH-DEBT)/SHARES, pv_tv/ev
out={"price":PRICE,"rf":RF,"cash":CASH,"shares":SHARES,"fy26_fcf_est":FY26_FCF}
for k,s in SC.items():
    w=RF+s["beta"]*ERP; ev,ps,tvs=dcf(s["g"],s["m"],s["tg"],w)
    out[k]=dict(wacc=round(w,4),ev=round(ev,1),per_share=round(ps,2),tv_share=round(tvs,2))
b=SC["base"]; sens={}
for w in [.09,.10,.11,.12,.13]:
    sens[w]={tg:round(dcf(b["g"],b["m"],tg,w)[1],2) for tg in [-.02,0,.01,.02,.03]}
out["sens_base"]=sens
# Reverse DCF: flat perpetuity FCFF needed / constant-decline
mcap=PRICE*SHARES; ev_mkt=mcap-CASH; out["mkt_cap"]=mcap; out["ev_mkt"]=ev_mkt
wb=out["base"]["wacc"]
for tg in [-.05,-.10,0.0]:
    out[f"implied_FCFF_next_at_g{tg}"]=round(ev_mkt*(wb-tg),1)
# implied terminal decline rate if FCFF stays ~FY26 level
def brentq(f,a,b):
    for _ in range(200):
        c=(a+b)/2
        if f(a)*f(c)<=0: b=c
        else: a=c
    return c
f0=FY26_FCF-8.0  # ASSUMPTION: strip ~$8M/yr financial income (9M26 fin. income $6.6M, PR) to get operating FCFF
out["ops_fcf_fy26"]=f0
out["implied_perp_g_if_fcf_holds"]=round(brentq(lambda g: f0*(1+g)/(wb-g)-ev_mkt,-0.9,wb-1e-4),3)
# Comps
comps={}
for t in ["FVRR","UPWK","ETSY","EBAY"]:
    i=yf.Ticker(t).info
    comps[t]={k:i.get(k) for k in ["currentPrice","marketCap","enterpriseValue","totalRevenue","ebitda","freeCashflow","revenueGrowth"]}
    c=comps[t]; c["EV/S"]=c["enterpriseValue"]/c["totalRevenue"]; c["EV/EBITDA"]=c["enterpriseValue"]/c["ebitda"]; c["P/FCF"]=c["marketCap"]/c["freeCashflow"]
# FVRR on own verified EV
comps["FVRR_verified"]={"EV":ev_mkt,"EV/S_FY26":ev_mkt/FY26_REV,"EV/EBITDA_FY26":ev_mkt/FY26_EBITDA,"P/FCF_FY26":mcap/FY26_FCF,"EV/EBITDA_annQ3":ev_mkt/(14.542*4),"P/FCF_annQ3":mcap/(9.373*4)}
# Comps-implied FVRR value using UPWK multiples (most direct peer) with discounts
u=comps["UPWK"]
for name,mult,metric in [("EV/S",u["EV/S"],FY26_REV),("EV/EBITDA",u["EV/EBITDA"],FY26_EBITDA)]:
    for d in [0.0,0.3,0.5]:
        out[f"comp_{name}_disc{d}"]=round((mult*(1-d)*metric+CASH)/SHARES,2)
out["comp_PFCF_disc0"]=round(u["P/FCF"]*FY26_FCF/SHARES,2)
out["comp_PFCF_disc0.5"]=round(u["P/FCF"]*0.5*FY26_FCF/SHARES,2)
out["comps"]=comps
print(json.dumps(out,indent=1,default=float))
# --- SBC-adjusted variant: treat SBC (Q3'26 $6.7M = 7.4% of rev, PR) as cash cost; subtract 6pp from FCFF margins
adj={}
for k,s in SC.items():
    w=RF+s["beta"]*ERP; m=[max(x-.06,-.05) for x in s["m"]]
    adj[k]=round(dcf(s["g"],m,s["tg"],w)[1],2)
print("SBC_ADJ", adj, "net_cash_per_share", round(CASH/SHARES,2))
