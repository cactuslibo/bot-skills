import os,json,time,urllib.request,urllib.error
os.chdir("/workspace/ai_pharma")
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
os.chdir("/workspace/drug_value_chain/gai")
AID=open("/workspace/ai_pharma/gai_agent_id.txt").read().strip()
q="""New, independent task (unrelated to earlier sessions). You are the citation verifier for a literature review on the pharmaceutical R&D value chain (phase durations, success rates, development costs, AI impact, value-chain/profit/funding distribution). Today is 2026-11-01. Use google_search/url_context; check against Crossref (https://api.crossref.org/works/<DOI>), publisher pages or PubMed. Answer in English. Never invent; mark UNVERIFIED if you cannot check.
Task A (citation audit): Below is the final reference table (TSV, 170 rows). Spot-check AT LEAST 40 rows, prioritising grade A1/A2 rows and all rows whose crossref_check is not '一致'. For each checked row report: key | Correct / Wrong DOI / Wrong year / Wrong authors / Wrong venue / Possibly fabricated / UNVERIFIED | correction + source URL. Then list any row you believe is fabricated or misattributed.
Task B (claim audit): verify each numeric claim C1-C5 below against the original abstract/full text; for each number give Correct / Partly / Wrong / UNVERIFIED with source URL and the correct value.
Task C: name up to 8 important peer-reviewed empirical papers on these topics that appear to be MISSING from the table (give DOI, verified). Finish with a short verdict.

=====CLAIMS=====
"""+open("claims.md").read()+"\n\n=====TABLE (TSV)=====\n"+open("table.tsv").read()
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True}
try: r=call("interactions",body)
except urllib.error.HTTPError:
    body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid",r["id"],flush=True)
t0=time.time()
while r.get("status") in ("in_progress","queued","pending") and time.time()-t0<2400:
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print("status",r.get("status"),flush=True)
json.dump(r,open("gai_raw.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("review_googleai_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
