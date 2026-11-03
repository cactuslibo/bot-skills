import os,json,time,urllib.request,sys
H={"Content-Type":"application/json","x-goog-api-key":os.environ['GEMINI_API_KEY']}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H),timeout=600))
def text(r): return "\n".join(c.get("text","") for s in r.get("steps",[]) if s.get("type")=="model_output" for c in s.get("content",[]) if isinstance(c,dict))
pkg=open("us_package.txt").read()
q1="""新会话（重做）。说明：上一会话中你的 code_execution 环境无法读取提示中的 CSV 原文（你只手工录入了 192 行，结果作废）。因此本次我方用代码把数据预先整理成下列汇总表（计数、分位数、分箱列联表、年份分布、全部崩盘案例清单）。请不要尝试重录原始行；请在 code_execution 中直接录入这些汇总表/列联表进行你自己的统计检验。
范围（用户要求）：仅限美国上市标的——美国上市 ETF/指数与美国大市值个股（616 条形态案例，来自 tv_us_universe.csv；反例 tv_us_counter.csv 2505 条）。
任务：独立分析“高位平台整理→跌破平台下沿→收复→创新高”之后崩盘（新高后12个月内 ETF/指数回撤≥30%、个股≥40%）的案例为何形成这一路径。比较 崩盘组 vs 无崩盘组 vs 反例组：
1) 形态特征（平台长度/宽度、跌破深度、收复速度、新高超出幅度）；2) 成交量；3) 利率与美联储（加息/降息阶段、收益率曲线）——用 google_search/url_context 查证并附URL，可将 F 节崩盘案例的新高日期对照联储政策阶段；4) 宏观（衰退NBER日期、估值、信用利差）附URL；5) 年份分布与聚集（2000、2007-08、2020、2021-22 等）。
统计：基准率、条件概率、Fisher/卡方/趋势检验、分组 logistic、多重比较校正；务必处理同期案例聚集/重叠（按 event_id 去重结果、按年份聚集），区分 stock 与 ETF/index。数字须来自代码或下表；无法核实的标注“无法核实”。

"""+pkg
q2="""第二轮：请自我挑战：(1) 逐条列出上轮未附可核查来源的美联储/宏观/估值论断，补URL或标注“无法核实”并改写；(2) 对小样本、同期聚集、多重比较的结论，按事件/年份聚集调整后重新评估，指出哪些站不住；(3) 对 A 节中的其它崩盘定义（crash 列 43 条等）做定义敏感性讨论；(4) 输出最终结构化中文报告（仅美国）：摘要；数据与定义；基准率与条件概率表（精确 n/N）；形态特征；成交量；利率与美联储；宏观；年份聚集；定义敏感性；稳健性与局限；结论（按证据强度分级）；来源列表。"""
prev=None;out=open("/workspace/report/gai_independent_transcript.md","a")
out.write("\n\n# 新会话（仅美国，汇总数据包）\n\n注：上方第1-2轮因 code_execution 无法读取内联 CSV（agent 仅录入192行），结果作废，仅作记录。\n\n")
for i,q in enumerate([q1,q2],1):
    body={"agent":"fakebreak-crash-analyst","input":q,"environment":"remote","background":True}
    if prev: body["previous_interaction_id"]=prev
    r=call("interactions",body);print("created",i,r["id"],flush=True)
    while r.get("status") in ("in_progress","queued","pending"):
        time.sleep(30)
        try: r=call("interactions/"+r["id"])
        except Exception as e: print("poll err",e,flush=True)
    print(i,r.get("status"),flush=True);prev=r["id"]
    json.dump(r,open(f"us_raw_{i}.json","w"),ensure_ascii=False)
    t=text(r);open(f"us_r{i}.txt","w").write(t)
    out.write(f"## US 第 {i} 轮\n**问：**\n\n{q}\n\n**interaction id:** {r['id']} status={r.get('status')}\n\n**答：**\n\n{t}\n\n---\n\n");out.flush()
