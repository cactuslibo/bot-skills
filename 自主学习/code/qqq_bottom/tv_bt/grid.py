import itertools, pandas as pd, numpy as np, json, sys
from bt import *
df=load('2015-01-01'); O,H,L,C,V=df.open,df.high,df.low,df.close,df.volume
s5,s10,s200=sma(C,5),sma(C,10),sma(C,200); r2=rsi(C,2); up=C>s200
w,wmid,wup,wrh,wgreen=wvf(C,L); b=boo(C); g12,b26,r120=ema(b,12),ema(b,26),ema(b,120)
mo=mcclellan(df.adv,df.dec); tm=tmf(C,H,L,V); mrs,k=mfi_rsi_stoch(H,L,C,V,20); mrs30,_=mfi_rsi_stoch(H,L,C,V,30)
w1,w2=wavetrend(H,L,C); ptz,tz=tz_low(L); ts=df.vix/df.vix3m; nd=df.ndfi
cu=lambda a,bb:(a>bb)&(a.shift()<=bb.shift())
EX={'C>SMA5':C>s5,'RSI2>70':r2>70,'C>SMA10':C>s10}
filt={'none':pd.Series(True,df.index),'C>SMA200':up,'VIX/VIX3M<1':ts<1,'NDFI<30':nd<30,'MO<0':mo<0}
fams={}
def fam(name,src,entries,exits,filters,maxds=(None,)):
    fams[name]=dict(src=src,combos=[(en,ex,fi,md) for en in entries for ex in exits for fi in filters for md in maxds],E=entries)
fam('RSI2 benchmark','CM_RSI-2_Strategy_Lower_Indicator.pine',{'RSI2<10':r2<10},['C>SMA5'],['C>SMA200'])
fam('CM RSI-2 lime','CM_RSI-2_Strategy_Lower_Indicator.pine',{'lime(C>200&C<5&RSI2<10)':cm_rsi2_buy(C),'RSI2<5':r2<5,'RSI2<15':r2<15},['C>SMA5','RSI2>70'],['C>SMA200','none'])
fam('WVF','CM_Williams_Vix_Fix_Finds_Market_Bottoms.pine',{'WVF green':wgreen,'WVF green ends':wgreen.shift().fillna(False)&~wgreen},['C>SMA5','RSI2>70','C>SMA10'],['none','C>SMA200'],(None,10))
fam('WVF+RSI2','CM_Williams_Vix_Fix + CM_RSI-2',{'WVF green & RSI2<10':wgreen&(r2<10),'WVF green & RSI2<20':wgreen&(r2<20)},['C>SMA5','RSI2>70'],['none','C>SMA200','VIX/VIX3M<1'])
fam('MyRSI boo','MyRSI.pine / CCT_Bollinger_Band_Oscillator',{'boo<0':b<0,'boo<-10':b<-10,'boo crosses up 0':cu(b,pd.Series(0,df.index))},['C>SMA5','RSI2>70'],['none','C>SMA200','VIX/VIX3M<1'])
fam('MyRSI rule3','MyRSI.pine (rule3)',{'green x red':cu(g12,r120)},['C<SMA200 (rule3)'],['C>SMA200'])
fam('MyRSI green<-40','MyRSI.pine',{'green<-40 turns up':(g12<-40)&(g12>g12.shift()),'green<-20 turns up':(g12<-20)&(g12>g12.shift())},['C>SMA5','RSI2>70','C>SMA10'],['none','C>SMA200'])
fam('MFI+RSI+StochRSI','My_MFI_RSI_STOCH_RSI.pine',{'all<20':mrs,'all<30':mrs30},['C>SMA5','RSI2>70','C>SMA10'],['none','C>SMA200'])
fam('WaveTrend','WaveTrend_with_Crosses_LazyBear.pine',{'wt1 x wt2 & wt1<-53':cu(w1,w2)&(w1<-53),'wt1 x wt2 & wt1<-60':cu(w1,w2)&(w1<-60)},['C>SMA5','RSI2>70','C>SMA10'],['none','C>SMA200','VIX/VIX3M<1'])
fam('McClellan','McClellan_Oscillator_LazyBear.pine',{'MO x up -50':cu(mo,pd.Series(-50,df.index)),'MO<-75 & RSI2<10':(mo<-75)&(r2<10),'MO turns up <-50':(mo<-50)&(mo>mo.shift())},['C>SMA5','RSI2>70','C>SMA10'],['none','C>SMA200'])
fam('Twiggs MF','CM_Twiggs_Money_Flow.pine',{'TMF<-0.1 & RSI2<10':(tm<-0.1)&(r2<10),'TMF x up -0.1':cu(tm,pd.Series(-0.1,df.index))},['C>SMA5','RSI2>70'],['none','C>SMA200'])
fam('Transient Zones','Transient_Zones_v1_1.pine',{'PTZ low & RSI2<10':ptz&(r2<10),'TZ low confirmed':tz},['C>SMA5','RSI2>70','C>SMA10'],['none','C>SMA200'])
fam('VIX term (roll-yield proxy)','vix_roll_yield.pine (proxy VIX/VIX3M)',{'VIX/VIX3M>1 & RSI2<10':(ts>1)&(r2<10),'VIX/VIX3M x down 1':cu(1/ts,pd.Series(1,df.index))},['C>SMA5','RSI2>70','C>SMA10'],['none'])
fam('RSI2+breadth','CM_RSI-2 + NDFI/McClellan',{'RSI2<10':r2<10,'RSI2<15':r2<15},['C>SMA5'],['NDFI<30','MO<0','VIX/VIX3M<1'],(None,))
fam('3-way RSI2+WVF/boo+filter','CM_RSI-2 + MyRSI/WVF + VIX/breadth',{'RSI2<10 & boo<0':(r2<10)&(b<0),'RSI2<10 & WT1<-53':(r2<10)&(w1<-53)},['C>SMA5','RSI2>70'],['C>SMA200','VIX/VIX3M<1','none'])
EX['C<SMA200 (rule3)']=C<s200
rows=[];sel=[];ntot=0;RETS=[]
for fn,f in fams.items():
    best=None
    for en,ex,fi,md in f['combos']:
        ntot+=1; ent=f['E'][en]&filt[fi]
        tr,ret,inp,op,pin=run(df,ent,EX[ex],md); RETS.append(ret[df.index>=pd.Timestamp('2016-01-22')])
        st={p:stats(df,tr,ret,inp,*P[p]) for p in P}
        r=dict(family=fn,src=f['src'],entry=en,exit=ex,filter=fi,maxd=md or '-',n_combos=len(f['combos']),
               pos_now=op, signal_1029=bool(ent.iat[-1]), entry_pending=pin)
        for p in P:
            for kk,v in st[p].items(): r[p+'_'+kk]=v
        rows.append(r)
        if r['IS_trades']>=15 and (best is None or r['IS_sharpe']>best['IS_sharpe']): best=r
    if best: sel.append(best)
R=pd.DataFrame(rows); S=pd.DataFrame(sel)
R.to_csv('all_results.csv',index=False); np.save('round1_rets.npy',np.array(RETS)); S.to_csv('selected_IS.csv',index=False)
pd.set_option('display.width',300); pd.set_option('display.max_columns',40); pd.set_option('display.max_colwidth',30)
cols=['family','entry','exit','filter','maxd','n_combos','FULL_trades','FULL_win','FULL_CAGR','FULL_sharpe','FULL_MDD','FULL_exposure','IS_sharpe','IS_trades','OOS_trades','OOS_sharpe','OOS_MDD','pos_now','signal_1029']
print(S[cols].round(3).to_string()); print('total combos',ntot)
print(R.sort_values('FULL_sharpe',ascending=False)[cols].head(25).round(2).to_string())
