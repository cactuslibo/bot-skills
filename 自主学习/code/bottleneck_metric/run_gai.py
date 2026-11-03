import os,json,time,urllib.request,urllib.error
key=os.environ["GEMINI_API_KEY"];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    try: return json.load(urllib.request.urlopen(req,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:800],flush=True); raise
AID="bottleneck-financial-metric-reviewer"
try: a=call("agents/"+AID)
except urllib.error.HTTPError:
    a=call("agents",{"id":AID,"display_name":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"You are a skeptical, independent reviewer of financial-metric research on supply-chain bottlenecks. Cite real sources (URLs/DOIs) found via google_search/url_context for every external fact or number; never fabricate; mark anything unverifiable as UNVERIFIED.",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]})
    print("created",json.dumps(a)[:300],flush=True)
AID=a.get("id") or AID
open("gai_agent_id.txt","w").write(AID+"\n")
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""Independent review of a research conclusion on a financial metric to identify supply-chain "bottleneck" companies (pricing power). Answer in English. Use google_search/url_context to verify; give URLs for external facts; mark UNVERIFIED anything you cannot verify; never invent numbers. Cite files as final.md:Lnn etc.
Conclusion: primary metric OM_floor = min operating margin over last 10 fiscal years (window must include an industry downturn). >=20% bottleneck candidate, 10-20% grey, <10% non-bottleneck. Filters: ROIC-WACC>0, manually exclude regulated monopolies. Backup: gross margin >=40% and 10y GM std <=5pp. Test: 12 bottleneck vs 8 EMS/memory firms, 4 years data: GM, mean OM, 4y-min OM all AUC~1 (extreme hand-picked samples, optimistic); ROIC AUC 0.66; DPO-DSO reversed.
Answer each question:
1. Is 20% threshold reasonable; should it be industry-specific?
2. In the 2009 and 2001 troughs, were ASML, KLA, Lam operating margins still >=20%? Verify with financial statements, give specific values (fiscal years, sources).
3. Is there research directly linking supply-chain network centrality to profit margins? (give real citations)
4. Is contract liabilities / revenue a better replacement for DPO-DSO?
5. Operating margin vs De Loecker markup (sales/COGS): which is better?
6. Leading indicators for pre-profit early-stage bottleneck firms?
7. Check the descriptions of the four papers in evidence.md, and whether De Loecker (2020) and Mueller (1986) citations are accurate.
8. Is typical SaaS operating margin consistently below 20%?
Also: identify sample-selection bias and propose a stricter test design (full-universe sample, out-of-sample tests, etc.).
Output: Overall verdict (AGREE / CONDITIONAL AGREE / DISAGREE); answers 1-8; numbered MUST-FIX list with reasons.
"""
for f in ["final.md","evidence.md","test_results.md","candidates.md","data.csv","test.py"]:
    q+=f"\n\n====={f}=====\n"+num(f)
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True}
try: r=call("interactions",body)
except urllib.error.HTTPError as e:
    print("env1 fail",flush=True); body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid",r["id"],body["environment"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print("status",r.get("status"),flush=True)
json.dump(r,open("gai_raw.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("review_googleai_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
print("done")
