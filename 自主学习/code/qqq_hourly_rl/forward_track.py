"""前推影子跟踪（真正样本外）。冻结策略（2026-10-30 冻结，不得修改）：P2、G1、G2、G1_rp10、G2_rp10，以及第 8 轮的 H2、H3。
只记录 2026-10-30 起"已完整收盘"的交易日。完整 = 该日最后一根 K 线是收盘 K 线（按 NYSE 日历：16:00 收盘 -> 15:30 那根；半日 13:00 收盘 -> 12:30 那根），
并且 QQQ_1h、QQQ_daily、VIX_1h、VIX3M_1h、ADV_DECL_1h 都有这一天的收盘数据，且数据已在收盘 15 分钟后导出（文件里有更晚的交易日，或文件修改时间 ≥ 收盘+15 分钟）。
计算时把数据截断在第一个不完整交易日之前（不完整的 K 线不会进入任何指标）；不完整的日子写入 forward_skips.csv 并注明原因。
用法：
  python3 forward_track.py            增量追加（已记录的日期不重写）
  python3 forward_track.py --verify   用当前数据重算全部已记录行并逐行比对，有差异则列出并以退出码 1 结束（不改日志）
  python3 forward_track.py --rebuild  先备份日志为 forward_log.bak_<时间>.csv，再从头重算重写
环境变量（测试用）：QDATA 数据目录、QVIXD 日线 VIX 目录、FT_LOG 日志路径、FT_START 起始日、FT_NOW 当前时间（ET，如 2026-11-03 17:00）。"""
import os, sys, csv, shutil, datetime, numpy as np, pandas as pd
import pandas_market_calendars as mcal
DATA=os.environ.get('QDATA','/workspace/data'); os.environ['QDATA']=DATA
VIXD=os.environ.get('QVIXD','/workspace/qqq_bottom/data/full').rstrip('/'); os.environ['QVIXD']=VIXD
HERE=os.path.dirname(os.path.abspath(__file__))
LOG=os.environ.get('FT_LOG',f'{HERE}/forward_log.csv'); SKIP=LOG.replace('forward_log','forward_skips') if 'forward_log' in LOG else LOG+'.skips.csv'
START=pd.Timestamp(os.environ.get('FT_START','2026-10-30'))
NOW=pd.Timestamp(os.environ['FT_NOW']) if os.environ.get('FT_NOW') else pd.Timestamp(datetime.datetime.now())
FROZEN={'P2':None,'H2':dict(kind='H2',rp=30,z=0.6,y=0.006),'H3':dict(kind='H3',rp=30,y=0.04,z=0.65),
        'G1':dict(kind='G1',y=0.03,z=0.6,rp=5),'G2':dict(kind='G2',y=0.005,z=0.6,rp=5),
        'G1_rp10':dict(kind='G1',y=0.03,z=0.6,rp=10),'G2_rp10':dict(kind='G2',y=0.005,z=0.6,rp=10)}
FIELDS=['date','strategy','pos_open','pos_close','ret','ret_int','rsi2','ratio','p2_signal','logged_at']
HOURLY=['QQQ_1h.csv','VIX_1h.csv','VIX3M_1h.csv','ADV_DECL_1h.csv']
def read_times(f):
    t=pd.to_datetime(pd.read_csv(f'{DATA}/{f}',usecols=['time']).time.str[:19]); return t
def check_days(days):
    """返回 {day: None(完整) 或 原因字符串}。"""
    cal=mcal.get_calendar('XNYS'); sch=cal.schedule(days.min()-pd.Timedelta(days=5),days.max()+pd.Timedelta(days=5))
    close=sch.market_close.dt.tz_convert('America/New_York').dt.tz_localize(None); close.index=close.index.normalize()
    times={f:read_times(f) for f in HOURLY}; mt={f:pd.Timestamp(datetime.datetime.fromtimestamp(os.path.getmtime(f'{DATA}/{f}'))) for f in HOURLY+['QQQ_daily.csv']}
    daily=pd.to_datetime(pd.read_csv(f'{DATA}/QQQ_daily.csv',usecols=['date']).date)
    vdaily={vf:pd.to_datetime(pd.read_csv(f'{VIXD}/{vf}',usecols=['time']).time) for vf in ('VIX.csv','VIX3M.csv')}
    vmt={vf:pd.Timestamp(datetime.datetime.fromtimestamp(os.path.getmtime(f'{VIXD}/{vf}'))) for vf in ('VIX.csv','VIX3M.csv')}
    out={}
    for d in days:
        if d not in close.index: out[d]='非交易日'; continue
        c=close[d]; lastbar=c-pd.Timedelta(minutes=30); why=[]
        if NOW<c+pd.Timedelta(minutes=15): why.append(f'当前时间早于收盘+15分钟（收盘 {c:%H:%M}）')
        for f in HOURLY:
            t=times[f]; td=t[t.dt.normalize()==d]
            if (td==lastbar).sum()==0: why.append(f'{f} 缺少收盘 K 线 {lastbar:%H:%M}（当日最后一根 {td.max():%H:%M}）' if len(td) else f'{f} 没有该日数据')
            elif t.max().normalize()<=d and mt[f]<c+pd.Timedelta(minutes=15): why.append(f'{f} 导出时间 {mt[f]:%m-%d %H:%M} 早于收盘+15分钟')
        for vf in ('VIX.csv','VIX3M.csv'):          # 日线 VIX：START 之前的日子必须有；START 起用小时线替代，但若已有当日行且导出早于收盘+15 分钟，视为不完整
            if d<START and (vdaily[vf]==d).sum()==0: why.append(f'日线 {vf} 没有该日')
            elif (vdaily[vf]==d).sum()>0 and vdaily[vf].max()<=d and vmt[vf]<c+pd.Timedelta(minutes=15): why.append(f'日线 {vf} 导出时间早于收盘+15分钟')
        if (daily==d).sum()==0: why.append('QQQ_daily.csv 没有该日')
        elif daily.max()<=d and mt['QQQ_daily.csv']<c+pd.Timedelta(minutes=15): why.append('QQQ_daily.csv 导出时间早于收盘+15分钟')
        out[d]='; '.join(why) if why else None
    return out
def compute():
    """返回 (rows 字典 {(date,strategy):row}, skips 列表)。"""
    q=read_times('QQQ_1h.csv'); alld=pd.DatetimeIndex(sorted(set(q.dt.normalize())))
    vt=read_times('VIX_1h.csv'); alld=alld.union(pd.DatetimeIndex(sorted(set(vt.dt.normalize()))))
    cand=alld[alld>=START-pd.Timedelta(days=10)]
    st=check_days(cand); bad=[d for d in cand if st[d] is not None and st[d]!='非交易日']
    cut=min(bad) if bad else None
    skips=[dict(date=d.strftime('%Y-%m-%d'),reason=st[d] if d==cut else f'{st[d] or "数据完整"}；且位于第一个不完整交易日 {cut:%Y-%m-%d} 之后，暂不计算') for d in bad+[x for x in cand if cut is not None and x>cut and st[x] is None] if d>=START or d==cut]
    if cut is not None: os.environ['QCUT']=cut.strftime('%Y-%m-%d')
    import engine
    for y in range(2027,2031): engine.EFFR.setdefault(y,engine.EFFR[2026])
    import r5; r5.EFFR=engine.EFFR
    from r8 import M8
    from r6 import VIXH, V3H
    m=M8('QQQ')
    def lastbar(df):
        x=df.groupby(df.index.normalize()).close.last(); return x       # VIXH 已只含常规时段；已截断不完整日由 cut 保证
    hr=(lastbar(VIXH)/lastbar(V3H)).reindex(m.days)
    new=m.days>=START; m.ratio=np.where(new&~np.isnan(hr.values),hr.values,m.ratio); m.ratio_prev=np.r_[np.nan,m.ratio[:-1]]
    rows={}; now=NOW.strftime('%Y-%m-%d %H:%M')
    for name,p in FROZEN.items():
        if p is None: w=m.p2()[:2]
        elif p['kind'] in ('H2','H3'):
            qq={k:v for k,v in p.items() if k!='kind'}
            with np.errstate(invalid='ignore'): sg=m.sigH2(**qq) if p['kind']=='H2' else m.sigH3(**qq)
            w=m.overlay(np.nan_to_num(sg).astype(bool))
        else: w=m.p2panic(**p)
        dr=m.returns(*w); dri=m.returns(*w,True)
        for d in np.where(new)[0]:
            key=(m.days[d].strftime('%Y-%m-%d'),name)
            rows[key]=dict(date=key[0],strategy=name,pos_open=float(w[1][m.fi[d]]),pos_close=float(w[1][m.li[d]]),ret=float(dr[d]),ret_int=float(dri[d]),
                rsi2=float(m.rsi2[d]),ratio=float(m.ratio[d]),p2_signal=bool(m.rsi2[d]<15 and m.ratio[d]<1),logged_at=now)
    return rows,skips,m.days[-1]
def read_log():
    if not os.path.exists(LOG): return []
    with open(LOG) as f: return list(csv.DictReader(f))
def write(path,rows,fields,mode):
    newf=mode=='w' or not os.path.exists(path)
    with open(path,mode,newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields)
        if newf: w.writeheader()
        w.writerows(rows)
def main(argv):
    mode='--verify' if '--verify' in argv else '--rebuild' if '--rebuild' in argv else 'append'
    rows,skips,lastday=compute(); old=read_log()
    if skips and mode!='--verify': write(SKIP,[dict(checked_at=NOW.strftime('%Y-%m-%d %H:%M'),**s) for s in skips],['checked_at','date','reason'],'a')
    for s in skips: print('跳过',s['date'],s['reason'])
    if mode=='--verify':
        diffs=[]
        for r in old:
            k=(r['date'],r['strategy'])
            if k not in rows: diffs.append(f'{k}: 当前数据下该日不完整或不存在'); continue
            n=rows[k]
            for c in ['pos_open','pos_close','ret','ret_int','rsi2','ratio']:
                if abs(float(r[c])-n[c])>1e-9: diffs.append(f'{k} {c}: 日志 {r[c]} vs 重算 {n[c]}')
            if str(n['p2_signal'])!=r['p2_signal']: diffs.append(f'{k} p2_signal: 日志 {r["p2_signal"]} vs 重算 {n["p2_signal"]}')
        print(f'校验 {len(old)} 行，差异 {len(diffs)} 处'); [print('  ',x) for x in diffs]
        return 1 if diffs else 0
    if mode=='--rebuild':
        if os.path.exists(LOG): bk=LOG.replace('.csv',f'.bak_{NOW:%Y%m%d_%H%M}.csv'); shutil.copy(LOG,bk); print('已备份',bk)
        write(LOG,list(rows.values()),FIELDS,'w'); print(f'重写 {len(rows)} 行'); return 0
    done={(r['date'],r['strategy']) for r in old}; add=[v for k,v in rows.items() if k not in done]
    write(LOG,add,FIELDS,'a'); print(f'计算截至 {lastday:%Y-%m-%d}；新增 {len(add)} 行；累计 {len(done)+len(add)} 行'); return 0
if __name__=='__main__': sys.exit(main(sys.argv[1:]))
