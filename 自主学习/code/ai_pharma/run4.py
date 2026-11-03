import re,time,json,urllib.request,urllib.error,os
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
AID="ai-pharma-chain-reviewer"
while not re.search(r"^4 \w+",open("run3.log").read(),re.M): time.sleep(20)
prev=re.findall(r"iid 4 (\S+)",open("run3.log").read())[0]
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""Fifth task (same review): audit news.md below (line numbers; cite news.md:Lnn). Primary sources with URLs (journals/DOIs, ClinicalTrials.gov, HKEX/SEC filings, company releases, FDA); verdict Correct/Partly/Wrong/UNVERIFIED + correct value + URL + date for each:
- rentosertib: Phase IIa results in Nature Medicine June 2025; Phase III first dosing September 2026
- Isomorphic: first clinical trial delayed to late 2026; $2.7B raised (check amounts/rounds)
- Recursion terminating REC-994 and REC-2282 in May 2025
- the AIntibody blind benchmark (paper, scope, results)
- Chai Discovery $3.8B valuation
- Insilico HK IPO raising HK$2.277B; Generate Biomedicines Nasdaq IPO raising $400M
- upfronts: Sanofi-Earendil $125M; AstraZeneca-CSPC $110M
- OpenAI, Anthropic and AstraZeneca each acquiring an AI-bio company (which, when, terms)
- FDA Jan 2025 AI draft guidance still a draft (not finalized?); FDA roadmap to reduce animal testing (April 2025) and its status
- XtalPi-DoveTree second payment of $19M in May 2026
Also flag missing major news, secondary-only sourcing, currency mixing.

=====news.md=====
"""+num("news.md")
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True,"previous_interaction_id":prev}
try: r=call("interactions",body)
except urllib.error.HTTPError:
    body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid 5",r["id"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print(5,r.get("status"),flush=True)
json.dump(r,open("gai_raw_5.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("review_googleai_news_r1_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
