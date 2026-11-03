import numpy as np, itertools, r8
def old(s,rl,f,rmax):
    nd=len(s.days); w_d=np.zeros(nd+1); st=0; ivals=[]
    for d in range(6,nd):
        if st>0 and s.DC[d]>s.sma[5][d]:
            if st==1: ivals.append((e,d+1,'ladder'))
            else: ivals.append((e,d+1,'open' if not lad else 'ladder'))
            st=0; continue
        p2sig=s.rsi2[d]<15 and s.ratio[d]<1
        if st<2 and p2sig:
            if st==0: e=d+1; lad=False
            st=2
        elif st==0 and s.rsi2[d]<rl and s.ratio[d]<rmax: st=1; e=d+1; lad=True
    s._ivals=ivals; w_over=np.zeros(s.N); w_in=np.zeros(s.N)
    st=0; tg=np.zeros(nd+1)
    for d in range(6,nd):
        if st>0 and s.DC[d]>s.sma[5][d]: st=0
        elif st<2 and s.rsi2[d]<15 and s.ratio[d]<1: st=2
        elif st==0 and s.rsi2[d]<rl and s.ratio[d]<rmax: st=1
        tg[d+1]=[0,f,1][st]
    for d in range(nd):
        a,b=s.fi[d],s.li[d]+1
        w_in[a:b]=tg[d]; w_over[a+1:b]=tg[d]; w_over[a]=min(tg[d-1],1) if d>0 else 0
    return w_over,w_in
m=r8.M8('QQQ'); bad=0
for rl,f,rmax in itertools.product([20,25,30,35],[0.5,0.67],[1.0,1.05,9]):
    a=old(m,rl,f,rmax); ia=list(m._ivals); b=m.ladder(rl,f,rmax); ib=list(m._ivals)
    bad+= not(np.array_equal(a[0],b[0]) and np.array_equal(a[1],b[1]) and ia==ib)
print('ladder 24 组参数 新旧不一致:',bad)
