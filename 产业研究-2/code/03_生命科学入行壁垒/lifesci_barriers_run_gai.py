import re,time,json,urllib.request,urllib.error,os
os.chdir("/workspace/ai_pharma")
exec(open("run2.py").read().split("prev=")[0].split("try: a=call")[0])
os.chdir("/workspace/lifesci_barriers")
AID=open("/workspace/ai_pharma/gai_agent_id.txt").read().strip()
q="""New independent task (unrelated to earlier ones): citation verification for a literature table on entry barriers in the life-science tools / DNA sequencing / CRO (contract research organization) industries. Today is 2026-11-01.
Below are 87 entries (ID | title | authors | year | DOI or link | the author's one-line summary of the claimed finding, in Chinese). Using google_search/url_context (Crossref, DOI landing pages, PubMed/PMC, publisher pages, SSRN, NBER, Semantic Scholar), check for each entry:
(1) Does the work exist with this title/authors/year? (2) Does the DOI resolve to THIS work (flag wrong attribution)? (3) Is the claimed finding consistent with the abstract (flag misattribution or overstatement, esp. numbers)?
Output in English a table: ID | Exists (Y/N/UNVERIFIED) | DOI correct (Y/N/NA/UNVERIFIED) | Claim consistent (Y/Partly/N/UNVERIFIED) | Correction/note with source URL.
Prioritize thorough checks on: B13, B16, B17, B21, B23, B26, B29, B30, B31, B36, B38, B46, B47, B49, B50, B57, B58, B62, B64, B65, B67, B73, B78, B80, B86. For the rest, at least check existence and DOI. Never fabricate; mark UNVERIFIED when you cannot check. End with a short list of must-fix items.

=====table=====
"""+open("verify_list.txt").read()
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True}
try: r=call("interactions",body)
except urllib.error.HTTPError:
    body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid",r["id"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print("status",r.get("status"),flush=True)
json.dump(r,open("gai_raw_verify.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("googleai_verify_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
