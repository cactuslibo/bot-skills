import re,time,json,urllib.request,urllib.error,os
os.chdir("/workspace/ai_pharma")
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
os.chdir("/workspace/drug_value_chain")
AID=open("/workspace/ai_pharma/gai_agent_id.txt").read().strip()
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""Independent red-team review of a market-sizing report (no stocks): market size of each stage of the drug value chain from idea to patient, incl. AI drug discovery. Report pasted with line numbers; cite report_v1.md:Lnn. Answer in English; use google_search to verify each item; give URLs; mark UNVERIFIED what you cannot verify; never invent numbers; for each item give AGREE/DISAGREE + source.
Items:
1) Evaluate: 2024 global pharma R&D spend ~US$288B.
2) AI-discovered molecules Phase II success ~40% (Jayatunga et al. 2024) vs 19.5% (Haque 2026) — do these papers exist, what exactly do they say, are they comparable?
3) Clinical CRO market US$45.3-92.3B and CDMO US$166-215B ranges: definitions/scope consistent?
4) Can Sood et al. 2017 41/41/17 split be extrapolated globally? IQVIA US$1.8T vs 1.5T global spending — definitional difference (invoice vs net, year)?
5) Commercialization US$300-400B and total clinical trial spend US$130-170B — is there an original source?
6) Is the framework that stage sizes are nested/overlapping and cannot be summed correct?
7) Any other errors.
Output: overall verdict (AGREE / CONDITIONAL AGREE / DISAGREE), numbered MUST-FIX list with line refs and concrete edits, SUGGESTED list.

=====report_v1.md=====
"""+num("report_v1.md")
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True}
try: r=call("interactions",body)
except urllib.error.HTTPError as e:
    print("env1 fail",e,flush=True); body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid",r["id"],body["environment"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print("status",r.get("status"),flush=True)
json.dump(r,open("gai_raw_r1.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("googleai_review_r1_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
