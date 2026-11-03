import re,time,json,urllib.request,urllib.error,os
os.chdir("/workspace/ai_pharma")
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
os.chdir("/workspace/ai_pharma_beneficiary")
AID=open("/workspace/ai_pharma/gai_agent_id.txt").read().strip()
prev=re.findall(r"iid (\S+)",open("run_gai.log").read())[0]
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""Follow-up round on the same AI-pharma beneficiary review. The author revised into report_v2.md (pasted with line numbers; cite report_v2.md:Lnn) and logged changes in changes_v2.md. Round-1 review (Chinese, with fact-checker corrections marked 【核查】 — note: Insilico reports in USD, TTM ~US$135M is correct, so your round-1 fix #4 was overruled; WuXi AppTec's 1260H designation was preliminarily enjoined on 2026-08-07) is pasted below. Answer in English; use google_search; give URLs; mark UNVERIFIED what you cannot verify; never invent numbers.
Tasks:
1. For each must-fix 1-8 and suggestions 1-4: Handled correctly / Partly / Not handled / Handled incorrectly, with line refs.
2. Author keeps a dissent on fix #2: tools/consumables now #1, WuXi/Pharmaron in a separate 'geopolitical discount' tier ranked #5/#6, arguing that during the injunction restrictions only concern federal funds, commercial customers are not legally bound, and capacity/cost advantages are hard to replace short-term. Is this acceptable? Check whether these claims are accurate (e.g. BIOSECURE scope, injunction status).
3. Verify Medpace GAAP gross margin ~30.1% (state formula/definition used, from 10-K or latest 10-Q) and the premise that biopharma R&D budgets grow ~3-5% per year (find sources, e.g. Evaluate Pharma, IQVIA, Deloitte).
4. Any new errors introduced in v2.
5. Verdict: AGREE TO FINALIZE, or list remaining must-fix items. Items labeled 待核实 are acceptable if clearly labeled.

=====round-1 review=====
"""+open("review_googleai_v1.md").read()+"\n\n=====changes_v2.md=====\n"+open("changes_v2.md").read()+"\n\n=====report_v2.md=====\n"+num("report_v2.md")
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True,"previous_interaction_id":prev}
try: r=call("interactions",body)
except urllib.error.HTTPError as e:
    print("env1 fail",e,flush=True); body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid",r["id"],body["environment"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print("status",r.get("status"),flush=True)
json.dump(r,open("gai_raw_2.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("review_googleai_v2_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
