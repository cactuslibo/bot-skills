import os,json,time,urllib.request,urllib.error
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    return json.load(urllib.request.urlopen(req,timeout=600))
AID="tv-shortcrash-reviewer"
try: print("exists",call("agents/"+AID).get("name"))
except urllib.error.HTTPError as e:
    body={"id":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"你是量化金融与统计方法学审稿专家。始终用中文回答；绝不编造数据、数字或来源；所有统计数字必须用 code_execution 从用户提供的数据计算得出；无法从数据或可靠来源核实的内容必须明确标注“无法核实”。",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
    print("created",call("agents",body))
rep=open("../tv_independent_short.md").read();csv=open("slim.csv").read()
q1=f"""请审阅一份TradingView复权日线的形态研究（另一个bot所写）。形态：急涨→高位平台→后期跌破平台下沿→快速收复并创新高→随后短期暴跌。样本105个品种（美股ETF、市值>100亿美元美股、A股大盘股、主要指数）。暴跌定义：新高后63个交易日内ETF/指数跌≥25%、个股≥35%（dd63_pct，正例从新高日最高价newhigh_price起算；反例/基准从收盘价起算）。声称：689个去重完整事件，44个暴跌(6.4%)；反例3.7%；全品种基准5.2%；个股7.4%对4.5%；ETF 5.1%对6.4%；暴跌组收复日量比1.42对1.26、新高日1.22对1.09、新高高于平台顶15%对11%；新高前美联储降息期暴跌率13.3%（195事件）、其他3.6%、加息期2.6%；暴跌集中于2020初和2015 A股。
下附报告全文和事件CSV（dup=True为被去重剔除；分析样本= dup==False 且 complete_63d==True）。CSV不含利率周期列。请用 code_execution 从CSV计算并回答：
(1) 去重规则是否合理：重叠事件、同日跨品种重复（如指数与跟踪它的ETF、同一冲击下多只股票），按新高日期/月份聚类后有效独立样本量；
(2) 正例用新高日盘中最高价、基准用收盘价对命中率的抬高程度——CSV无新高日收盘价，请用可用数据（如把回撤阈值平移2/3/5个百分点、或用recovery_close等）给出敏感性估计，并说明能否精确重算；
(3) 13.3%降息期结果是否由2020聚类驱动：CSV无利率周期列，请计算剔除2020年后的总体暴跌率、按日期聚类的置信区间，并评估在缺乏周期列时能否核实13.3%；
另外：多重比较、n=44小样本、聚类标准误的显著性检验（如正例6.4% vs 基准5.2%、个股 vs ETF、量比差异）、形态识别中的前视偏差（新高定义为收复后60日内最高点）、105品种幸存者偏差、利率周期分类来源。最后给出该形态是否有预警价值的结论。
=====报告=====
{rep}
=====CSV=====
{csv}"""
q2="第二轮：请挑战上一轮中仍薄弱的论点和本报告最弱的结论：每个数字说明是否由代码从CSV算出；对无法核实的标注“无法核实”；做一个按日期聚类的bootstrap或置换检验比较正例暴跌率与5.2%基准（考虑基准口径差异），并给出最终中文审稿结论与报告应修改的具体措辞清单。"
prev=None;out=open("../tv_short_review_transcript.md","w");out.write(f"# {AID} 对话记录\n\n")
for i,q in enumerate([q1,q2],1):
    body={"agent":AID,"input":q,"environment":"remote","background":True}
    if prev: body["previous_interaction_id"]=prev
    r=call("interactions",body);print("created",i,r["id"],flush=True)
    while r.get("status") in ("in_progress","queued","pending"):
        time.sleep(20)
        try: r=call("interactions/"+r["id"])
        except Exception as e: print("poll err",e,flush=True);continue
    print(i,r.get("status"),flush=True);prev=r["id"]
    json.dump(r,open(f"raw_{i}.json","w"),ensure_ascii=False)
    txt="\n".join(s.get("text","") or "".join(c.get("text","") for c in s.get("content",[]) if isinstance(c,dict)) for s in r.get("steps",[]) if s.get("type")=="model_output")
    open(f"r{i}.txt","w").write(txt)
    qq=q if i==2 else q.split("=====报告=====")[0]+"[附报告全文与slim CSV，略]"
    out.write(f"## 第 {i} 轮\n**问：** {qq}\n\n**interaction id:** {r['id']} status={r.get('status')}\n\n**答：**\n\n{txt}\n\n---\n\n");out.flush()
