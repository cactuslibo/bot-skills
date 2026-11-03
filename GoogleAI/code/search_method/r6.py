import os,json,time,urllib.request,sys
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    return json.load(urllib.request.urlopen(req,timeout=600))
v2=open("/workspace/method/source_first_v2.md").read()
q="第六轮（第 0 步二审）：原作者已把第 0 步修订为 v2（全文见下），称已采纳你第 4、5 轮的全部意见，并按我们对原文的核查更正了引用。我们的核查结论是：(a) Heuer 1999 第 8 章原文写有“Note the absence of evidence as well as its presence”，紧接着引用了福尔摩斯“the dog did not bark”的典故（你上一轮说 Heuer 未使用该典故，这是错的）；原文还列出了未见证据的四种原因：未发生、通常不可观察、被隐瞒、没去找；(b) JP 2-0（2013）本身已同时定义 PIR 和 SIR；(c) Verification Handbook 第 3 章作者是 Claire Wardle，不是 Malachy Browne，核查要素是四项：Provenance/Source/Date/Location；(d) Berkeley Protocol 的出版细节和 ISO 15489-1 第 3.14 条的原文我们无法核实，应标注。\n请：\n1) 逐条确认你第 4、5 轮的意见以及上述引用更正是否在 v2 中正确体现（已体现/部分/未体现 + 理由）；\n2) 指出仍有的异议或错误；\n3) 给出明确结论：“同意”，或具体的剩余修改清单。\n\n=====source_first_v2.md=====\n"+v2
body={"agent":"search-method-reviewer","input":q,"environment":"remote","background":True,"previous_interaction_id":sys.argv[1]}
r=call("interactions",body);print("created",r["id"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print(r.get("status"),flush=True)
json.dump(r,open("raw_6.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
txt="\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else []))
open("r6.txt","w").write(txt)
open("agent_transcript.md","a").write(f"## 第 6 轮（第 0 步 v2 二审）\n**interaction id:** {r['id']} status={r.get('status')}\n\n**问：** {q[:900]}…（v2 全文略）\n\n**答：**\n\n{txt}\n\n---\n\n")
