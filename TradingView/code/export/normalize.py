# 可重跑：新文件放入 daily/ 后再次运行即可（含后续10只ETF）
import pandas as pd, os, shutil, sqlite3, glob, datetime as dt
B='/workspace/tv_db'; os.makedirs(B+'/raw',exist_ok=True)
uni=pd.read_csv(B+'/universe_10B.csv'); uni['Symbol']=uni.Symbol.astype(str)
rows=[]; con=sqlite3.connect(B+'/daily.sqlite')
con.execute('create table if not exists bars(ticker text,date text,open real,high real,low real,close real,volume real,primary key(ticker,date))')
for f in sorted(glob.glob(B+'/daily/*.csv')):
    t=os.path.basename(f)[:-4]; raw=B+'/raw/'+os.path.basename(f)
    d=pd.read_csv(f)
    if 'time' in d.columns:            # 原始TV导出 -> 备份后规范化
        if not os.path.exists(raw): shutil.copy2(f,raw)
        d=d.rename(columns={'time':'date','Volume':'volume'})[['date','open','high','low','close','volume']]
        d=d.dropna(subset=['close']).drop_duplicates('date').sort_values('date'); d.to_csv(f,index=False)
    con.execute('delete from bars where ticker=?',(t,))
    d.assign(ticker=t)[['ticker','date','open','high','low','close','volume']].to_sql('bars',con,if_exists='append',index=False)
    dd=pd.to_datetime(d.date); gaps=int((dd.diff().dt.days>7).sum()); zv=int((d.volume.fillna(0)<=0).sum())
    iss=[]; 
    if gaps: iss.append(f'gaps>7d:{gaps}')
    if zv: iss.append(f'zero_vol:{zv}')
    if d.date.iloc[-1]<'2026-10-30': iss.append('stale')
    u=uni[uni.Symbol==t]
    rows.append(dict(ticker=t,type=u.type.iloc[0] if len(u) else '',exchange=u.Exchange.iloc[0] if len(u) else '',first_date=d.date.iloc[0],last_date=d.date.iloc[-1],rows=len(d),flag='ok' if not iss else 'issue',issues=';'.join(iss)))
con.commit(); con.execute('create index if not exists ix on bars(ticker)'); con.close()
m=pd.DataFrame(rows); m.to_csv(B+'/manifest.csv',index=False)
have=set(m.ticker); miss=[s for s in uni.Symbol if s not in have]
fl=pd.DataFrame([dict(ticker='TTE',reason='TradingView 仅有 Euronext 上市，无美股代码数据')]+[dict(ticker=s,reason='尚未下载') for s in miss if s!='TTE'])
fl.to_csv(B+'/failed.csv',index=False)
print(len(m),'files; issues',(m.flag=='issue').sum(),'missing',miss)
