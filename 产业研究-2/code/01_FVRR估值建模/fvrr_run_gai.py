import os,json,time,urllib.request,urllib.error
key=os.environ["GEMINI_API_KEY"];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    try: return json.load(urllib.request.urlopen(req,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:800],flush=True); raise
AID="fvrr-freelance-reviewer"
try: a=call("agents/"+AID); print("exists",flush=True)
except urllib.error.HTTPError:
    body={"id":AID,"display_name":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
    "system_instruction":"You are a skeptical, independent reviewer of freelance / gig-platform and AI-labor industry research. Cite real sources (URLs) found via google_search/url_context for every external fact or number; never fabricate; mark anything unverifiable as UNVERIFIED.",
    "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
    a=call("agents",body); print("created",json.dumps(a)[:300],flush=True)
open("gai_agent_id.txt","w").write((a.get("name") or AID).split("/")[-1]+"\n")
AID=open("gai_agent_id.txt").read().strip()
num=lambda f:"".join(f"{i}\t{l}" for i,l in enumerate(open(f),1))
q="""对一份中文产业研究报告做独立红队复核（附行号，引用 report_v1.md:Lnn）。今天是 2026-11-02。主题：Fiverr（FVRR）与自由职业/零工平台行业。请全程用中文回答，用 google_search/url_context 查证，给出 URL，查不到的标 UNVERIFIED，绝不编造数字。
重点挑战：
1. 行业规模区间 $5B–15.3B（SIA 口径，L62-L75）与 Fiverr 份额约 6% 的估算方法（L79-L80）：分子分母口径、年份是否一致，$5B 下限是否合理，SIA $15.3B/-2%/7% CAGR 是否可在 SIA 原文核实。
2. AI agent 雇人渠道排序 Upwork > Fiverr > RentAHuman 类 > TaskRabbit > Scale/Surge > MTurk（L131-L143）。特别核实：Amazon MTurk 是否确实于 2026-09-30 关闭（L127，查 mturk.com/help 与 AWS 公告）；Upwork Claude Connector 2026-06-17 / MCP 2026-08-10；RentAHuman、TaskRabbit Partner API 描述。排序逻辑是否自洽（L138 又说 Fiverr 可排第一）。
3. 结论“问题出在获客漏斗，不在人才供给”（L113、L147）是否成立，证据是否足够。
4. 其他关键数字（Fiverr Q3'26、Upwork 26Q2 指引等）抽查。
输出：总体结论（同意 / 有条件同意 / 不同意，若同意请明确写“同意”）；“必须修改”清单与“细节修改”清单分开列，每条带行号、具体改法和来源。

=====report_v1.md=====
"""+num("report_v1.md")
body={"agent":AID,"input":q,"environment":"6898496e634eb79f120e9ae782c9c667","background":True}
try: r=call("interactions",body)
except urllib.error.HTTPError as e:
    print("env1 fail",flush=True); body["environment"]="fe0e22b553a4741ee172e7ef3399c67b"; r=call("interactions",body)
print("iid",r["id"],body["environment"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print("status",r.get("status"),flush=True)
json.dump(r,open("gai_raw_1.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
open("googleai_review_r1_raw.md","w").write("\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else [])))
