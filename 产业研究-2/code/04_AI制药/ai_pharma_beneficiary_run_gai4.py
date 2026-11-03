import re,time,json,urllib.request,urllib.error,os
os.chdir("/workspace/ai_pharma")
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
os.chdir("/workspace/ai_pharma_beneficiary")
AID=open("/workspace/ai_pharma/gai_agent_id.txt").read().strip()
prev=json.load(open("gai_raw_eb1.json"))["id"]
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""Round 2 of the same entry-barrier review. Author revised into entry_barrier_v3.md (pasted with line numbers; revision table at the end; cite entry_barrier_v3.md:Lnn). Round-1 review (Chinese, fact-checker corrections marked 【核查】; note your MGI net loss was overstated 10x: actual attributable net loss RMB -222M, non-recurring-adjusted -390M) is pasted below. Answer in English; use google_search; give URLs; mark UNVERIFIED; never invent numbers.
Tasks:
1. For must-fix 1-6: Handled correctly / Partly / Not handled / Incorrectly, with line refs.
2. Re-verify TSMC 2025 balance-sheet items used for ROIC (~44%): equity, bonds/loans, cash, goodwill, operating income, tax; cite TSMC annual report / 20-F.
3. Verify Element Biosciences 2024 Series D US$277M.
4. Author did NOT put WuXi AppTec / Pharmaron operating margins in the main text (unverified). Is that appropriate?
5. Are these unadopted suggestions must-fix or optional: (a) TMO segment mix diluting gross margin; (b) sequencing market size two definitions (~$5B vs $15-20B); (c) BIOSECURE/1260H as a geopolitical barrier for MGI sequencing (check whether BGI/MGI entities are on the 1260H list)?
6. Any new errors in v3.
7. Verdict: AGREE TO FINALIZE, or remaining must-fix items.

=====round-1 review=====
"""+open("googleai_review_r1.md").read()+"\n\n=====entry_barrier_v3.md=====\n"+num("entry_barrier_v3.md")
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
json.dump(r,open("gai_raw_eb2.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("googleai_review_r2_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
