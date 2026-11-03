import os,json,time,requests
B="https://generativelanguage.googleapis.com/v1beta/";H={"x-goog-api-key":os.environ['GEMINI_API_KEY'],"Content-Type":"application/json"}
rep="\n".join(f"L{i+1}: {l}" for i,l in enumerate(open("report_v1b.md").read().split("\n")))
p="""The report has been revised to report_v1b.md (below, line-numbered; this version supersedes v1). Re-review it, focusing on the new §4b (post-Q3'26 stock drop). Using google_search/url_context, independently verify and judge:
1) price reaction: after-hours -7.3%, T+1 close -2.26% (S&P +0.58%), T+5 +1.8%;
2) cause ranking: main = 3-5% I&A per-procedure price cut + US procedure growth slowing to 10%; secondary = $450M antitrust settlement (GAAP EPS $1.49); guidance narrowed same midpoint = weak; tariffs = not supported (gross margin guide raised). Do you agree with the ranking and the tariff dismissal?
3) the $171-285M/yr impact estimate in §4b.3 and its comparison vs Case Insights ~$40k/system;
4) whether downgrading conclusion from 'moderate beneficiary' to 'moderate-to-low: moat holds share but pricing power weakening' is justified by evidence;
5) any remaining errors/logic holes vs your prior review. Cite file:Lnn and URLs; mark UNVERIFIED where you cannot source. Give verdict per item.

"""+rep
iid=open("run_gai.log").read().split("iid ")[1].split()[0]
r=requests.post(B+"interactions",headers=H,json={"agent":"isrg-surgical-robot-reviewer","input":p,"environment":"6898496e634eb79f120e9ae782c9c667","background":True,"previous_interaction_id":iid}).json()
i=r.get("id");print("iid2",i,flush=True)
if not i: print(r);raise SystemExit
while True:
  time.sleep(20);d=requests.get(B+"interactions/"+i,headers=H).json()
  if d.get("status") not in("in_progress","queued","pending"):break
print("status",d.get("status"),flush=True)
json.dump(d,open("gai_raw_2.json","w"),ensure_ascii=False,indent=1)
t=[s for s in d.get("steps",[]) if s.get("type")=="model_output"]
txt="\n".join(c.get("text","") for c in t[-1]["content"]) if t else json.dumps(d)[:3000]
open("googleai_review_r1_raw.md","a").write("\n\n---\n# Round 1b (report_v1b.md, §4b focus)\n\n"+txt)
