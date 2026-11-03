import re,time,json,urllib.request,urllib.error,os
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
AID="ai-pharma-chain-reviewer"
while not re.search(r"^3 \w+",open("run2.log").read(),re.M): time.sleep(20)
prev=re.findall(r"iid 3 (\S+)",open("run2.log").read())[0]
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""Fourth task (same review): audit chain_r2.md below (data & pricing power; line numbers; cite chain_r2.md:Lnn). Primary sources with URLs; verdict Correct/Partly/Wrong/UNVERIFIED + correct value + URL for each:
1) The author's three flagged INFERENCES: Insilico 2025 revenue ~$56M (check HKEX prospectus/annual results); Recursion negative gross margin (check 10-K/10-Q cost of revenue vs revenue); Lilly being an XtalPi customer.
2) Tempus 2025 data (Data and services / insights) revenue $316M at ~72% gross margin; AstraZeneca/Pathos $200M data license; Recursion 2.2M experiments per week and ~50PB data; Roche $30M phenomap payment to Recursion; Lilly TuneLab 125+ members; AISB / OpenFold3 consortium (members, scope).
3) Do NOT build your own non-AI baseline (another team owns it); just note whether chain_r2.md's upfront-ratio framing is stage-matched.
4) Weak logic, currency/period mixing, secondary-only claims; prioritized fix list.

=====chain_r2.md=====
"""+num("chain_r2.md")
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True,"previous_interaction_id":prev}
try: r=call("interactions",body)
except urllib.error.HTTPError:
    body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid 4",r["id"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print(4,r.get("status"),flush=True)
json.dump(r,open("gai_raw_4.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("review_googleai_chain_r2_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
