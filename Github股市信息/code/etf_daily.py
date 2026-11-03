import json, os, re, datetime as dt, requests, urllib.parse as u, concurrent.futures as cf, pipeline as p, yfinance as yf
os.environ.setdefault("GEMINI_MODEL", "gemini-3.5-flash")
DAY=os.environ.get("DAY","2026-10-29"); import zoneinfo; ET=zoneinfo.ZoneInfo("America/New_York")
ETFS="QQQ XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY ARKK ARKQ ARKW ARKG ARKF ARKX ARKB IZRL PRNT".split()
perf=json.load(open("output/etf_perf.json"))
def top(e):
    if e in perf: return perf[e]["top"][:4]
    try: return [s for s in yf.Ticker(e).funds_data.top_holdings.index[:4]]
    except Exception: return []
def ret1(e):
    try:
        h=yf.Ticker(e).history(start=str(dt.date.fromisoformat(DAY)-dt.timedelta(days=6)),end=str(dt.date.fromisoformat(DAY)+dt.timedelta(days=1)))["Close"]
        if str(h.index[-1].date())!=DAY: return None
        return round((h.iloc[-1]/h.iloc[-2]-1)*100,2)
    except Exception: return None
def today(i):
    s=i.get("published") or ""
    try: return dt.datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(ET).date().isoformat()==DAY
    except Exception: return False
def gn(q,n=25):
    try: return [dict(i,source="google_news") for i in p._rss(f"https://news.google.com/rss/search?q={u.quote_plus(q)}+when:2d&hl=en-US&gl=US&ceid=US:en",n)]
    except Exception: return []
def tt(q,n=40):
    try:
        r=requests.get("https://api.tickertick.com/feed",params={"q":q,"n":n},headers=p.UA,timeout=20)
        return [dict(title=s["title"],url=s["url"],publisher=s.get("site"),published=p.iso(s["time"]/1000),source="tickertick") for s in r.json().get("stories",[])]
    except Exception: return []
def yh(t):
    try: return [dict(i,source="yahoo") for i in p.src_yahoo_rss(t,{"per_source_limit":30})]
    except Exception: return []
cache={}
def hn(h):
    if h not in cache:
        s=h.split(".")[0]; cache[h]=tt(f"z:{s.lower()}")+gn(f"{s} stock")+(yh(s) if "." not in h else [])
    return cache[h]
data={}
for e in ETFS:
    t=top(e); raw=[dict(i,about=e) for i in gn(f'"{e}" ETF')+tt(f"z:{e.lower()}")+yh(e)]
    for h in t: raw+=[dict(i,about=h) for i in hn(h)]
    if e=="ARKB": raw+=[dict(i,about="BTC") for i in gn("bitcoin price")+gn("bitcoin ETF flows")]
    items=p.dedup([i for i in raw if today(i)],0.85)
    data[e]=dict(top=t,r=ret1(e),items=items); print(e,t,data[e]["r"],len(raw),"->",len(items),flush=True)
MQ=["Federal Reserve","Fed rate","PCE inflation","economic data report","Treasury yields","stock market today","jobs report","tariffs trade policy","White House economy","consumer sentiment"]
mraw=[]
for q in MQ: mraw+=[dict(i,about="MACRO") for i in gn(q,30)]
data["MACRO"]=dict(top=[],r=None,items=p.dedup([i for i in mraw if today(i)],0.85)); print("MACRO",len(mraw),"->",len(data["MACRO"]["items"]),flush=True)
json.dump(data,open(f"output/etf_daily_news_{DAY}.json","w"),ensure_ascii=False,indent=1)
def one(e):
    d=data[e]; items=d["items"][:150]
    if e=="MACRO":
        lst="\n".join(f"[{n}] {i['title']} | {i.get('publisher') or i['source']}" for n,i in enumerate(items,1))
        prompt=(f"下面是 {DAY}（美东）当天抓取的美国宏观新闻标题。用中文写 4～6 条要点（“- ”开头），涵盖美联储、经济数据、政策、美债与大盘。每条末尾用 [#编号] 标注 1～3 个来源，只用标题中的事实和数字，不得编造；证据不足写“（未核实）”。只输出要点。\n\n"+lst)
    if not items: return e,"今日未抓到相关新闻（原因不确定）。"
    if e!="MACRO":
     lst="\n".join(f"[{n}] {i.get('about')} | {i['title']} | {i.get('publisher') or i['source']}" for n,i in enumerate(items,1))
     rt=f"今日收盘涨跌 {d['r']}%（yfinance）" if d["r"] is not None else "今日涨跌幅未取到（写“未核实”）"
     prompt=(f"ETF {e}（主要持仓：{', '.join(d['top'])}）。{rt}。下面是 {DAY}（美东）当天抓取的新闻标题（编号|相关代码|标题|来源）。"
       "用中文写 2～4 条要点（每条以“- ”开头），说明今天影响这只 ETF 的公司层面原因（财报、指引、政策、经营）。每条末尾用 [#编号] 标注 1～3 个来源，编号必须来自列表；只用标题中出现的事实和数字，不得编造；证据不足写“（未核实）”。只输出要点。\n\n"+lst)
    s=""
    for _ in range(3):
        s=p.summarize(e,items,prompt=prompt) or ""
        if s and not s.startswith("(") and "[#" in s: break
    def cite(m):
        o=[]
        for n in map(int,re.findall(r"\d+",m.group(1))):
            if 1<=n<=len(items): i=items[n-1]; o.append(f"[{(i.get('publisher') or i['source'])[:30]}]({i['url']})")
        return " ".join(o)
    s=re.sub(r"\[(#?\d+(?:\s*[,，、]\s*#?\d+)*)\]",cite,s).replace("](/news/","](https://finviz.com/news/")
    s,_=p.filter_links(s,[i["url"].replace("/news/","https://finviz.com/news/") if i["url"].startswith("/news/") else i["url"] for i in items])
    return e,s.strip()
res={}
with cf.ThreadPoolExecutor(3) as ex:
    for e,s in ex.map(one,["MACRO"]+ETFS): res[e]=s; print("done",e,len(s),flush=True)
G=[("宏观（美联储/经济数据/政策）",["MACRO"]),("宽基/科技",["QQQ","XLK","XLC"]),("周期与金融",["XLB","XLE","XLF","XLI"]),("防御",["XLP","XLRE","XLU","XLV"]),("可选消费",["XLY"]),("ARK 主题",["ARKK","ARKQ","ARKW","ARKG","ARKF","ARKX","ARKB"]),("其他主题",["IZRL","PRNT"])]
md=[f"## {DAY} 增量（美东时间当日新闻）","",f"只收录美东 {DAY[5:]} 发布的新闻（TickerTick、Yahoo RSS、Google News），由 Gemini 根据标题汇总，链接经 filter_links 校验；当日涨跌幅取自 yfinance 收盘价。",""]
for g,es in G:
    md+=[f"### {g}",""]
    for e in es:
        d=data[e]
        if e=="MACRO": md+=[res[e],""]; continue
        r=f"{d['r']:+.2f}%" if d["r"] is not None else "未取到"
        md+=[f"#### {e}（今日 {r}；持仓 {', '.join(d['top']) or '未取到'}）","",res[e],""]
txt="\n".join(md)
open(f"output/etf_daily_{DAY}.md","w").write("# ETF 当日归因 "+DAY+"\n\n"+txt)
open("output/etf_drivers.md","a").write("\n\n"+txt)
