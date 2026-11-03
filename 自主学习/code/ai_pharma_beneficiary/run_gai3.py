import re,time,json,urllib.request,urllib.error,os
os.chdir("/workspace/ai_pharma")
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
os.chdir("/workspace/ai_pharma_beneficiary")
AID=open("/workspace/ai_pharma/gai_agent_id.txt").read().strip()
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""New, independent red-team review (new topic): entry barriers in life-science tools, sequencing and CRO. Report entry_barrier_v2.md pasted with line numbers; cite entry_barrier_v2.md:Lnn. The user's (Taz's) thesis: these industries have far lower technical barriers than TSMC; TMO/DHR dominate only because profits are low and nobody wants to enter. Answer in English; use google_search to verify; give URLs; mark UNVERIFIED; never invent numbers.
For each of the 6 claims in section 9, give AGREE/DISAGREE + sources:
1) Tools companies' gross margins are in the same range as TSMC (so 'low profit' is false) - check GAAP figures.
2) TMO/DHR low ROIC is caused by acquisition goodwill - compute ROIC with and without goodwill (and intangibles) for TMO, DHR vs TSMC from latest 10-K/annual report figures (show NOPAT, invested capital, goodwill, formula).
3) Sequencing entrants 'can get in but cannot make money' - Element, Ultima, MGI overseas installs/margins, Illumina share source.
4) CRO low margins come from buyer bargaining power.
5) Bundling / aftermarket (razor-blade) mechanisms apply to tools and sequencing.
6) AI demand gets diluted by price wars in low-barrier segments.
Also verify: ROIC figures in L15-17 (TSMC ~44%, TMO ~7.6%, DHR ~5.7%); Illumina short-read share ~84% -> ~77%; Ultima (~25 installs, ~50% cheaper consumables) and MGI (gross margin 52.9%) data; the 2022 settlement direction (report says Illumina paid Complete Genomics US$325M - confirm who paid whom).
Output: overall verdict (AGREE / CONDITIONAL AGREE / DISAGREE), numbered MUST-FIX list with line refs and concrete edits, SUGGESTED list.

=====entry_barrier_v2.md=====
"""+num("entry_barrier_v2.md")
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
json.dump(r,open("gai_raw_eb1.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("googleai_review_r1_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
