import os,json,time,requests
B="https://generativelanguage.googleapis.com/v1beta/";H={"x-goog-api-key":os.environ['GEMINI_API_KEY'],"Content-Type":"application/json"}
rep="\n".join(f"L{i+1}: {l}" for i,l in enumerate(open("report_v2.md").read().split("\n")))
p="""Round 2. The report is revised to report_v2.md (below, line-numbered) with a changelog (also below). 1) Check whether each of your 7 must-fixes and 3 detail items from the previous round are implemented, item by item, citing file:Lnn. 2) Find any NEW errors or internal inconsistencies (e.g. L71 vs L7/L118 Case Insights figures; L36 'already charged' vs first-year-free). 3) Recompute Case Insights: 2,023 dV5 x $40k x 20-30%, and confirm it is labeled as an assumption. 4) MicroPort MedBot (2252.HK) FY2025: verify via HKEX annual results announcement which number is 'loss for the year' vs 'loss attributable to owners of the parent' (RMB 254.1M vs 249.7M?). Cite URLs, mark UNVERIFIED if not found. 5) Final verdict: can it be finalized (AGREE) or not, plus remaining must-fix list.

CHANGELOG:
"""+open("report_v2_changelog.md").read()+"""

REPORT:
"""+rep

iid=open("run_gai2.log").read().split("iid2 ")[1].split()[0]
r=requests.post(B+"interactions",headers=H,json={"agent":"isrg-surgical-robot-reviewer","input":p,"environment":"6898496e634eb79f120e9ae782c9c667","background":True,"previous_interaction_id":iid}).json()
i=r.get("id");print("iid2",i,flush=True)
if not i: print(r);raise SystemExit
while True:
  time.sleep(20);d=requests.get(B+"interactions/"+i,headers=H).json()
  if d.get("status") not in("in_progress","queued","pending"):break
print("status",d.get("status"),flush=True)
json.dump(d,open("gai_raw_3.json","w"),ensure_ascii=False,indent=1)
t=[s for s in d.get("steps",[]) if s.get("type")=="model_output"]
txt="\n".join(c.get("text","") for c in t[-1]["content"]) if t else json.dumps(d)[:3000]
open("googleai_review_r1_raw.md","a").write("\n\n---\n# Round 1b (report_v2.md, §4b focus)\n\n"+txt)
