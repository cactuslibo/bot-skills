import os,json,time,requests
B="https://generativelanguage.googleapis.com/v1beta/";H={"x-goog-api-key":os.environ["GEMINI_API_KEY"],"Content-Type":"application/json"}
num=lambda f:"\n".join(f"L{i+1}: {l}" for i,l in enumerate(open(f).read().split("\n")))
AID=open("gai_agent_id.txt").read().strip()
prev=json.load(open("gai_raw_1.json"))["id"]
p="""第二轮复核（全程用中文）。产业研究已提交 report_v2.md（附行号）和改动记录 report_v2_changelog.md，声称上一轮 4 项必须修改、5 项细节修改已全部落实，且上一轮被我方核查否定的说法（MTurk 07-30 停止注册、Upwork AI GSV 年化 $300M+、Upwork 活跃客户 -6%/811K、Fiverr 2025 GMV 用总营收推算）均未写入。注意：上一轮我方核查更正：Upwork 活跃客户同比 -4%（796K→763K）；Fiverr 2025 GMV ≈ Marketplace 营收 $297.5M ÷ 27.7% ≈ $1.07B，份额约 7.0%。
任务：
1. 逐条核对 9 项是否改到位（引用 report_v2.md:Lnn）。
2. 检查是否引入新错误或内部不一致。
3. 用 google_search 核实 Upwork 2026 Q3 财报（原定 2026-11-02 美东盘后）截至现在是否已发布；正文继续用 Q2 数据并注明是否合理。
4. 输出：“必须修改”与“细节修改”分开列，带行号、改法、来源；若没有必须修改，明确写“同意”。查不到的标 UNVERIFIED，不得编造。

=====report_v2_changelog.md=====
"""+open("report_v2_changelog.md").read()+"\n\n=====report_v2.md=====\n"+num("report_v2.md")
body={"agent":AID,"input":p,"environment":"6898496e634eb79f120e9ae782c9c667","background":True,"previous_interaction_id":prev}
r=requests.post(B+"interactions",headers=H,json=body).json(); i=r.get("id"); print("iid",i,flush=True)
if not i: print(r); raise SystemExit
while True:
  time.sleep(20); d=requests.get(B+"interactions/"+i,headers=H).json()
  if d.get("status") not in("in_progress","queued","pending"): break
print("status",d.get("status"),flush=True)
json.dump(d,open("gai_raw_2.json","w"),ensure_ascii=False,indent=1)
t=[s for s in d.get("steps",[]) if s.get("type")=="model_output"]
open("googleai_review_r2_raw.md","w").write("\n".join(c.get("text","") for c in t[-1]["content"]) if t else json.dumps(d)[:3000])
