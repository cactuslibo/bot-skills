import os,json,time,urllib.request,urllib.error
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    return json.load(urllib.request.urlopen(req,timeout=600))
AID="search-method-reviewer"
try: print("exists",call("agents/"+AID).get("name"))
except urllib.error.HTTPError as e:
    body={"id":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"你是信息检索、系统综述方法学与信息素养研究审稿专家。始终用中文回答；绝不编造文献、作者、年份、期刊、DOI或URL；所有事实、数字和引用都要用 google_search / url_context 核实；无法核实的内容必须明确标注“无法核实”。",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
    print("created",call("agents",body))
draft=open("draft.md").read()
qs=["请审阅下面这份供AI机器人做网络调研时使用的《如何在网上找到最完整信息》方法论草案（来自另一个bot）。任务：\n1) 逐条（第1-7步及反“乱搜”规则）指出：哪些不合理、有遗漏、或AI bot难以执行；\n2) 逐条核实每条引用：作者、年份、期刊/出处，以及草案引用它支持的论断是否与原文一致（例如 Greenhalgh & Peacock 2005 BMJ 是否真的说“数据库只覆盖约30%”，具体数字和含义是什么）；附URL；\n3) 给出具体修改建议，至少考虑：来源独立性/循环报道、搜索引擎个性化与地区差异、付费墙、非英语来源、LLM特有失败模式（幻觉URL、伪造引用、过度自信）、时效性与缓存结果、预算/调用次数限制、查询日志。\n\n=====草案=====\n"+draft,
"第二轮：请逐条挑战草案中（以及你上一轮回答中）所有没有给出可核查来源的论断：能找到支持/反驳证据的附URL，不能核实的标注“无法核实”并建议改措辞。最后输出一份修订后的完整最终版方法论（中文，可直接给AI bot使用，保留经核实的引用并附正确出处），以及引用更正表（原引用→核实后信息→来源）。"]
prev=None;out=open("agent_transcript.md","w");out.write(f"# {AID} 对话记录\n\n")
for i,q in enumerate(qs,1):
    body={"agent":AID,"input":q,"environment":"remote","background":True}
    if prev: body["previous_interaction_id"]=prev
    r=call("interactions",body);print("created",i,r["id"],flush=True)
    while r.get("status") in ("in_progress","queued","pending"):
        time.sleep(20)
        try: r=call("interactions/"+r["id"])
        except Exception as e: print("poll err",e,flush=True);continue
    print(i,r.get("status"),flush=True);prev=r["id"]
    json.dump(r,open(f"raw_{i}.json","w"),ensure_ascii=False)
    txt=r.get("output_text") or "\n".join(o.get("text","") for o in r.get("outputs",[]) if isinstance(o,dict))
    open(f"r{i}.txt","w").write(txt)
    out.write(f"## 第 {i} 轮\n**问：** {q}\n\n**interaction id:** {r['id']} status={r.get('status')}\n\n**答：**\n\n{txt}\n\n---\n\n");out.flush()
