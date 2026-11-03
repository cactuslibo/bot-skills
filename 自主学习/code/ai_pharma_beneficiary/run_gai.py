import re,time,json,urllib.request,urllib.error,os
os.chdir("/workspace/ai_pharma")
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
os.chdir("/workspace/ai_pharma_beneficiary")
AID=open("/workspace/ai_pharma/gai_agent_id.txt").read().strip()
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""Adversarial (red-team) review of a new research report. Premise: AI speeds up target/drug/protein screening ~10x and cuts cost sharply; who across the industry chain benefits most? Core conclusions: bottleneck shifts in order to wet-lab validation, clinical trial capacity, proprietary data linked to clinical outcomes; top-3 beneficiary types: wet-lab & preclinical CRO, life-science tools/consumables, clinical-outcome data platforms; top-5 names: WuXi AppTec, Pharmaron, TMO, MEDP, TEM; squeezed: pure dry-lab outsourcing, animal safety-assessment.
Answer in English. Use google_search to verify. Give URLs for external facts; mark UNVERIFIED what you cannot verify; never invent numbers. Cite report_v1.md:Lnn / thesis.md:Lnn.
Review three points from the opposing side:
1) Does the bottleneck-shift logic and beneficiary ranking hold? E.g. does faster screening actually translate into more wet-lab orders; if clinical success rates are unchanged, is clinical capacity a real bottleneck; impact of FDA's plan to reduce animal testing on safety assessment (CRL etc.).
2) Are numbers and sources correct? Verify each key number with google_search; list each as Correct / Wrong (with correct value + URL) / Unverified.
3) Missing beneficiaries and risks, especially the US BIOSECURE Act — verify its LATEST legislative status (e.g. whether enacted via the NDAA, its provisions, transition/grandfather periods, whether WuXi AppTec is named or how entities are designated) and impact on WuXi entities; also TEM valuation/loss/dilution risk (prior verified facts: Q2'26 GAAP net income +$5.64M, 1H26 GAAP net loss -$120.3M, shares outstanding 180,434,756).
Output: Overall verdict (AGREE / CONDITIONAL AGREE / DISAGREE); numbered MUST-FIX list with concrete edit suggestions and line refs; SUGGESTED (nice-to-have) list.

=====thesis.md=====
"""+num("thesis.md")+"\n\n=====report_v1.md=====\n"+num("report_v1.md")
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
json.dump(r,open("gai_raw_1.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("review_googleai_v1_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
