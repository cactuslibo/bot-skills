import os,json,time,urllib.request,urllib.error
key=os.environ["GEMINI_API_KEY"];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    return json.load(urllib.request.urlopen(req,timeout=600))
AID="ai-pharma-factchecker"
try: print("exists",call("agents/"+AID).get("name"))
except urllib.error.HTTPError:
    body={"id":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"你是生物医药与AI制药领域的独立事实核查员。始终用中文回答；每一条事实（日期、金额、编号、数字）都必须用 google_search / url_context 对照一手来源（监管机构、登记库、交易所/SEC公告、公司新闻稿、期刊DOI页）核实并附URL；绝不编造事实、数字、链接或引用；无法核实的内容必须明确标注“无法核实”；不要把被核查报告的结论当作事实。",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
    print("created",call("agents",body))
rep=open("report.md").read()
qs=["请对下面这份“过去一年（2025-11-01 至 2026-10-31，今天是 2026-10-31）AI 制药重要新闻”报告做独立事实核查。报告由另一个 bot 生成，其结论不能当作事实，请你自行对照一手来源核实。\n1) 逐条核实第 1–16 条的日期、金额/数字和来源（链接是否支持该论断），每条给出：正确/部分正确/错误/无法核实、正确值、你的来源URL；\n2) 以下几项请重点核查：礼来-英矽智能 27.5 亿美元交易（首付款 1.15 亿美元，港交所公告）；Isomorphic 21 亿美元 B 轮（日期、领投方）；Rentosertib III 期及 NCT07687459（状态、入组人数、中心数）；Recursion REC-4881 数据（47%/55%、REC-1245 91.7%、2 亿美元增发）；国药监综〔2026〕6号（名称、发布日期）；FDA-EMA 联合 10 条原则（发布日期、正式名称）；AIntibody 的 Nature Biotechnology 论文（DOI、日期、511 个抗体/29 家机构、主要结论）；\n3) 列出报告遗漏的重大新闻（附一手来源）；\n4) 评价报告末尾的方法改进建议（报告写有 6 条，实际列了 7 条），逐条说明是否合理并给出修改意见。\n\n=====报告全文=====\n"+rep,
"第二轮：请逐条挑战你上一轮回答以及报告中所有没有给出可核查一手来源的论断：能证实的附URL，不能证实的标“无法核实”并改措辞。最后给出一张最终核查表（第 1–16 条：结论、正确值、来源URL），以及最终的遗漏新闻清单。"]
prev=None;out=open("agent_transcript.md","w");out.write(f"# {AID} 对话记录\n\n")
for i,q in enumerate(qs,1):
    body={"agent":AID,"input":q,"environment":"remote","background":True}
    if prev: body["previous_interaction_id"]=prev
    r=call("interactions",body);print("created",i,r["id"],flush=True)
    while r.get("status") in ("in_progress","queued","pending"):
        time.sleep(20)
        try: r=call("interactions/"+r["id"])
        except Exception as e: print("poll err",e,flush=True)
    print(i,r.get("status"),flush=True);prev=r["id"]
    json.dump(r,open(f"raw_{i}.json","w"),ensure_ascii=False)
    mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
    txt="\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else []))
    open(f"r{i}.txt","w").write(txt)
    out.write(f"## 第 {i} 轮\n**interaction id:** {r['id']} status={r.get('status')}\n\n**问：** {q[:1500]}{'…（报告全文略）' if i==1 else ''}\n\n**答：**\n\n{txt}\n\n---\n\n");out.flush()
