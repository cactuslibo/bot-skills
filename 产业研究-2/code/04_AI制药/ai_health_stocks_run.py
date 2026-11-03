import os,json,time,urllib.request,urllib.error,sys
H={"Content-Type":"application/json","x-goog-api-key":os.environ["GEMINI_API_KEY"]}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H),timeout=600))
def text(r):
    mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
    return "\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else []) if isinstance(c,dict))
rep=open("report.md").read()
q1="今天是 2026-10-31。请审阅下面这份报告：《AI医疗股近期大涨背后的新闻汇总（2026-08-03 至 2026-10-30）》，覆盖礼来 LLY、默沙东 MRK，以及 ARKG 中的 AI 医疗持仓 TEM、ABSI、SDGR、RXRX、GENB、IAM。报告中 2026 年的数据都是真实发生的历史数据，不是“未来”，请不要这样标注。只使用英文来源。请：\n1) 逐条核实关键数字、日期和当日股价涨跌，对照一手来源（公司新闻稿、SEC EDGAR、ARK 官方持仓 CSV、权威媒体原文）；每条给出：正确/部分正确/错误/无法核实、正确值、来源URL；\n2) 检查每条引用是否准确：链接是否真实存在，是否支持报告中的论断，来源等级是否标对；\n3) 列出 2026-08 至 2026-10 期间被遗漏的重要新闻（附一手来源）；\n4) 绝不编造来源或URL；没有实际打开过的页面请标“未打开”。\n\n=====报告全文=====\n"+rep
q2="第二轮（挑战）：请逐条挑战你上一轮回答中以及报告中所有没有可核查一手来源的论断。对你上一轮给出的每个URL，说明是否在本会话中实际打开过；没打开过的请删除或标“未核实”。凡是把 2026 年数据称为“未来/假设”的地方请改正。最后给出一份最终核查表（逐条：结论、正确值、来源URL），以及最终的遗漏新闻清单。"
envs=[l.strip() for l in open("envs.txt")]
prev=None;out=open("agent_transcript.md","w");out.write("# ai-pharma-factchecker：AI医疗股报告复核对话记录\n\n");env_ok=None
for i,q in ((1,q1),(2,q2)):
    cands=[env_ok] if env_ok else envs
    r=None
    for env in cands:
        body={"agent":"ai-pharma-factchecker","input":q,"environment":env,"background":True}
        if prev: body["previous_interaction_id"]=prev
        try: r=call("interactions",body); env_ok=env; print("round",i,"env",env,"id",r["id"],flush=True); break
        except urllib.error.HTTPError as e: print("env",env,"ERR",e.code,e.read().decode()[:200].replace("\n"," "),flush=True)
    if not r: print("NO ENV WORKS");sys.exit(3)
    while r.get("status") in ("in_progress","queued","pending"):
        time.sleep(20)
        try: r=call("interactions/"+r["id"])
        except Exception as e: print("poll err",e,flush=True)
    print(i,r.get("status"),flush=True);prev=r["id"]
    json.dump(r,open(f"raw_gai_{i}.json","w"),ensure_ascii=False)
    t=text(r);open(f"r{i}.txt","w").write(t)
    out.write(f"## 第 {i} 轮\n**environment:** {env_ok}\n\n**interaction id:** {r['id']} status={r.get('status')}\n\n**问：** {q[:1200]}{'…（报告全文略）' if i==1 else ''}\n\n**答：**\n\n{t}\n\n---\n\n");out.flush()
