import re,time,json,urllib.request,urllib.error,os
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
AID="ai-pharma-chain-reviewer"
while not re.search(r"^5 \w+",open("run4.log").read(),re.M): time.sleep(20)
prev=re.findall(r"iid 5 (\S+)",open("run4.log").read())[0]
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""FINAL task (same review): audit draft_v2.md below (the second draft; line numbers; cite draft_v2.md:Lnn). Use the findings from ALL your previous audits in this conversation (draft_v1, market.md, chain.md, chain_r2.md, news.md) plus these checker notes on round 1: FDA Jan 2025 draft guidance excludes discovery-only AI uses; Jayatunga 2024 (Drug Discovery Today, DOI 10.1016/j.drudis.2024.104009) phase II ~40% rests on ~10 molecules; many margin ranges in your round 1 were unsourced proposals.
Tasks (English; URLs for any new external fact; mark UNVERIFIED):
1. Check every factual claim in draft_v2 for consistency with the audited sources/your earlier verdicts; table: line, claim, status (Consistent/Inconsistent/Unsourced/UNVERIFIED), fix.
2. The three flagged inferences: Insilico 2025 revenue ~$56M; Recursion negative gross margin; Lilly as an XtalPi customer — final verdicts.
3. XtalPi-DoveTree payments: reconcile first payment $51M, second payment $19M (May 2026) vs the $49M figure; state the precise total received to date with sources and currency.
4. Is the bottleneck ranking and are the four theses supported by evidence? For hypothesis 3, audit the 'third round' non-AI baseline section of market.md (pasted below): check DealForma 2023 figures (discovery/platform deals ~2.4% upfront over 176 deals; preclinical ~3.1% over 69 deals); the deal sample with non-AI 1.3-5.6% vs AI 2.1-6.8%; late-stage deals 10-21%; XtalPi cumulative received $70M ~1.2% of total and the unexplained $30M gap vs the '$100M upfront+near-term' figure. Flag: the 2023-vs-2025 year mismatch against the DealForma 2025 AI figures; that most of the sample is China out-licensing deals (selection bias); and that 'similar ratio' does not prove 'not a bottleneck' — the real issue may be deal-stage concentration (AI deals mostly discovery-stage) and absolute cash received. Keep DealForma scopes separate.
5. Verdict: PASS / CONDITIONAL PASS / FAIL, then a numbered list of required fixes (must-fix vs nice-to-have).

=====draft_v2.md=====
"""+num("draft_v2.md")+"\n\n=====market.md (third-round baseline section; full file with line numbers)=====\n"+num("market.md")
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True,"previous_interaction_id":prev}
try: r=call("interactions",body)
except urllib.error.HTTPError:
    body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid 6",r["id"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print(6,r.get("status"),flush=True)
json.dump(r,open("gai_raw_6.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("review_googleai_draft_v2_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
