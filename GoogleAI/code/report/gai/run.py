import os,json,time,urllib.request,urllib.error
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    return json.load(urllib.request.urlopen(req,timeout=300))
AID="pattern-report-reviewer"
try: print("exists",call("agents/"+AID).get("name"))
except urllib.error.HTTPError as e:
    print("get",e.code)
    body={"id":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"你是金融市场微观结构与行为金融研究审稿专家。始终用中文回答；绝不编造文献、作者、年份、期刊或DOI；所有事实、数字和引用都要用 google_search / url_context 核实（DOI 请在 doi.org 或 Crossref 查证）；无法核实的内容必须明确标注“无法核实”。",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
    try: print("created",call("agents",body))
    except urllib.error.HTTPError as e2: print("create err",e2.code,e2.read().decode()[:2000]); raise
rep=open("/workspace/report/report_v1.md").read()
qs=["请审阅下面这份完整报告（主题：指数/ETF 形态“高位整理→下沿假跌破→快速收复创新高→见顶真下跌”，聚焦参与者与资金流）。任务：\n1) 核查事实、数字，以及每一条引用的作者/年份/期刊/DOI（期刊名是凭记忆填写的，请逐条核实；DOI 请在 doi.org/Crossref 查证）；\n2) 找出逻辑与机制漏洞；\n3) 列出遗漏的重要机制、参与者或案例（例如回购静默期、被动资金流、年末再平衡、A股场外配资、做市商 gamma、CTA/波动率控制、期权到期等）。\n请逐条输出问题，每条附修改建议与来源（URL）。\n\n=====报告全文=====\n"+rep,
"第二轮：请逐条挑战报告中（以及你上一轮回答中）所有没有给出可核查来源的论断：对每条说明是否能找到支持/反驳证据（附URL），不能核实的标注“无法核实”并建议删改措辞。最后给出一份按优先级排序的完整修改清单（含引用更正表：原引用→核实后正确信息→来源）。"]
prev=None;out=open("/workspace/report/googleai_agent_transcript.md","w");out.write(f"# {AID} 对话记录\n\n")
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
    out.write(f"## 第 {i} 轮\n**问：** {q[:1500]}{'…(报告全文略)' if i==1 else ''}\n\n**interaction id:** {r['id']} status={r.get('status')}\n\n**答：**\n\n{txt}\n\n---\n\n");out.flush()
