import os,json,time,requests
B="https://generativelanguage.googleapis.com/v1beta/";H={"x-goog-api-key":os.environ["GEMINI_API_KEY"],"Content-Type":"application/json"}
num=lambda f:"\n".join(f"L{i+1}: {l}" for i,l in enumerate(open(f).read().split("\n")))
AID=open("gai_agent_id.txt").read().strip()
prev=json.load(open("gai_raw_2.json"))["id"]
p="""新任务（全程中文回答；只用英文来源，尽量追到原始出处，给 URL；查不到标 UNVERIFIED，不得编造）。复核 Fiverr（FVRR）三份材料：earnings_report.md（财报解读）、report_final.md（产业研究定稿，前两轮已复核）、fvrr_valuation.md（估值）+ model.py + model_out.json。引用 文件名:Lnn。今天 2026-11-02。
重点：
1. 财报好坏判断：本季超预期但基本面恶化、材料判断偏负面——是否成立（核对 Q3'26 实际 vs 一致预期、Q4/FY 指引）。
2. 估值：合理价值 $9.5–15、中值约 $12.5；现价约 $8.68、每股净现金约 $8.49、可能是价值陷阱。核对 DCF 假设、可比公司（UPWK）打折是否合理、反向 DCF 推出的每年约 -84% 永续衰减。请用 code_execution 重算（DCF 三情景、扣 SBC 版本、反向 DCF）。检查现价与净现金对应的日期与口径，尤其 Fiverr 0% 可转债（2025 年 11 月到期）是否已偿还/已从现金中扣除，9/30/26 资产负债表是否还有可转债；用户资金是否正确排除；摊薄股数口径。
3. AI agent 雇人渠道结论（标准化小额线上任务→Fiverr；复杂/企业→Upwork；线下→RentAHuman/TaskRabbit）。特别核实：(a) Upwork MCP 是否已能起草职位/提案/offer；(b) Fiverr MCP 截至 2026-09-26 是否只能搜索——请找官方文档或官方公告，而非仅第三方 SynapticRelay；(c) MTurk 2026-09-30 关闭（mturk.com/help）。
每条写明“同意/不同意”、理由、英文来源链接；最后分“必须修改”“细节修改”列出（带行号）。

=====earnings_report.md=====
"""+num("earnings_report.md")+"\n\n=====report_final.md=====\n"+num("report_final.md")+"\n\n=====fvrr_valuation.md=====\n"+num("fvrr_valuation.md")+"\n\n=====model.py=====\n"+open("model.py").read()+"\n\n=====model_out.json=====\n"+open("model_out.json").read()
body={"agent":AID,"input":p,"environment":"6898496e634eb79f120e9ae782c9c667","background":True,"previous_interaction_id":prev}
r=requests.post(B+"interactions",headers=H,json=body).json(); i=r.get("id"); print("iid",i,flush=True)
if not i: print(r); raise SystemExit
while True:
  time.sleep(20); d=requests.get(B+"interactions/"+i,headers=H).json()
  if d.get("status") not in("in_progress","queued","pending"): break
print("status",d.get("status"),flush=True)
json.dump(d,open("gai_raw_full1.json","w"),ensure_ascii=False,indent=1)
t=[s for s in d.get("steps",[]) if s.get("type")=="model_output"]
open("googleai_review_full_r1_raw.md","w").write("\n".join(c.get("text","") for c in t[-1]["content"]) if t else json.dumps(d)[:3000])
