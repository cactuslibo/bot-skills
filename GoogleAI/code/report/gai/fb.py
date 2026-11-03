import os,json,time,urllib.request,urllib.error,sys
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    return json.load(urllib.request.urlopen(req,timeout=600))
AID="fakebreak-crash-analyst"
try: print("exists",call("agents/"+AID).get("name"))
except urllib.error.HTTPError as e:
    body={"id":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"你是独立的量化市场研究分析师。始终用中文回答；绝不编造数字、事实或引用；所有统计必须用 code_execution 基于用户提供的数据计算并展示代码与结果；美联储政策、利率、宏观等事实须用 google_search / url_context 查证并附URL；无法核实的内容必须明确标注“无法核实”。",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
    print("created",call("agents",body))
u=open("u_slim.csv").read();c=open("c_summary.txt").read()
q1=f"""任务：独立分析“高位平台整理→跌破平台下沿（假跌破）→收复→创新高”形态之后发生崩盘的案例为何形成这一路径。
数据说明：
- universe.csv（754 条，全文如下）：经典ETF/指数，以及平台期市值>100亿美元的美股与A股个股；每条为一次完整形态。crash 定义：创新高后 12 个月内，ETF/指数回撤≥30%、个股≥40%（crash_thr_pct 列，dd_from_high_12m_pct 为新高后12月最大回撤）。complete_12m=False 表示后续12个月数据不完整。crash=False 的 613 条即“有形态无崩盘”组。plat_width_pct=平台高低点宽度%（我方由plat_high/plat_low计算）；break_depth_pct=跌破平台下沿深度；vol_* 为相对成交量；newhigh_vs_plattop_pct=新高超出平台顶幅度；plat_mcap_usd_bn 市值（mcap_status 标注是否核验）。
- counter（3324 条，因输入限额仅提供汇总统计）：反例——跌破平台下沿后未收复/未创新高（真跌破），mdd12m_from_flush 为跌破后12月最大回撤。
请先在 code_execution 中把下面 universe CSV 文本写入文件再用 pandas 分析（若无法读取请明确说明）。
请从以下维度比较 崩盘组 vs 无崩盘组 vs 反例组，并给出你自己计算的统计（基准率、条件概率、显著性检验，如 Fisher/卡方/Mann-Whitney、logistic 回归）：
1) 形态特征：平台长度/宽度、跌破深度、收复速度（flush→recovery 天数）、新高超出幅度、新高距收复天数；
2) 成交量（跌破、收复、新高相对量）；
3) 利率与美联储政策（加息/降息阶段、收益率曲线倒挂）——须查证并附来源URL；
4) 宏观环境（衰退、估值、信用利差）——须查证并附来源；
5) 年份分布与聚集（如2000、2007-08、2021-22、A股2015）。
务必处理：同一时期多案例聚集/重叠导致的非独立性（例如按月份或事件聚类、去重后重算、聚类稳健标准误或按年份块自助法），市场(US/CN)与类型(stock/ETF/index)分层，complete_12m=False 的处理。
输出：数字均须来自代码；区分“统计支持”“仅描述性”“无法核实”。

=====universe.csv=====
{u}

=====counter 汇总（原始3324行因API限额无法全文上传）=====
{c}
"""
q2="""第二轮：请自我挑战：(1) 逐条列出上轮所有未附可核查来源的美联储/宏观/估值论断，补充URL或标注“无法核实”并改写；(2) 对样本量小、受聚类影响（同一危机期大量案例）、多重比较的结论，做聚类调整（如按崩盘事件/年份去重）后重新检验，说明哪些结论站不住；(3) 给出最终结构化中文报告：摘要；数据与定义；基准率与条件概率表（列出精确计数 n/N）；形态特征；成交量；利率与美联储；宏观；年份聚集；稳健性与局限；结论（按证据强度分级）；来源列表。"""
prev=None;out=open("/workspace/report/gai_independent_transcript.md","w");out.write(f"# Agent {AID} 对话记录\n\n")
for i,q in enumerate([q1,q2],1):
    body={"agent":AID,"input":q,"environment":"remote","background":True}
    if prev: body["previous_interaction_id"]=prev
    try: r=call("interactions",body)
    except urllib.error.HTTPError as e: print("ERR",e.code,e.read().decode()[:1500]);sys.exit(2)
    print("created",i,r["id"],flush=True)
    while r.get("status") in ("in_progress","queued","pending"):
        time.sleep(30)
        try: r=call("interactions/"+r["id"])
        except Exception as e: print("poll err",e,flush=True)
    print(i,r.get("status"),flush=True);prev=r["id"]
    json.dump(r,open(f"fb_raw_{i}.json","w"),ensure_ascii=False)
    txt=r.get("output_text") or "\n".join(o.get("text","") for o in r.get("outputs",[]) if isinstance(o,dict))
    open(f"fb_r{i}.txt","w").write(txt)
    out.write(f"## 第 {i} 轮\n**问：**\n\n{q[:3000]}{'…(CSV 全文略，见 gai/u_slim.csv、gai/c_slim.csv)' if i==1 else ''}\n\n**interaction id:** {r['id']} status={r.get('status')}\n\n**答：**\n\n{txt}\n\n---\n\n");out.flush()
