import re,time,json,urllib.request,urllib.error,os
os.chdir("/workspace/ai_pharma")
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
os.chdir("/workspace/drug_value_chain")
AID=open("/workspace/ai_pharma/gai_agent_id.txt").read().strip()
prev=re.findall(r"iid (\S+)",open("run_gai.log").read())[0]
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""Round 2 of the same market-sizing review. Author revised into report_v2.md (pasted with line numbers; section 9 has a revision table; cite report_v2.md:Lnn). Round-1 review (Chinese, with fact-checker corrections marked 【核查】 — note your round-1 claims that IQVIA $1.8T includes COVID, that $1.5T is 2022/net basis, and the Haque DOI 102789 were overruled) is pasted below. Answer in English; use google_search; give URLs; mark UNVERIFIED; never invent numbers.
Tasks:
1. For must-fix 1-6: Handled correctly / Partly / Not handled / Incorrectly, with line refs.
2. Fix #6: author computed 288B x 50-60% = 144-173B, which does not match the original 130-170B; author kept 130-170B, noted the original base is unclear, still labeled 'estimate, unverified'. Is this appropriate, or should the report switch to the newly computed range (or another)? Also find a source for the share of R&D spent on clinical development (e.g. PhRMA annual survey breakdown) if possible.
3. Any new errors in v2.
4. Verdict: AGREE TO FINALIZE, or list remaining must-fix items.

=====round-1 review=====
"""+open("googleai_review_r1.md").read()+"\n\n=====report_v2.md=====\n"+num("report_v2.md")
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
json.dump(r,open("gai_raw_r2.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("googleai_review_r2_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
