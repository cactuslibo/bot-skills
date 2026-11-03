import os,json,time,urllib.request,urllib.error,sys
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    return json.load(urllib.request.urlopen(req,timeout=600))
v2=open("/workspace/method/plan_v2.md").read()
q="第三轮（二审）：原作者已按你前两轮意见把方法论修订为 v2，并接受了全部引用更正。主要改动：先做意图分类；三档预算（注明数值无文献依据）；明确“独立来源”定义；网页追踪限 1 跳；SIFT 改写为 bot 可执行步骤；三级信源并合并转载；停止规则为三条件任一满足、删除重捕法；JSON 日志 + 异构红队复核；只输出本会话实际访问且返回 HTTP 200 的 URL。作者保留一点：二手来源默认仍需追溯原始出处，但允许使用权威综述，须标注。\n请：\n1) 逐条核查你第 1、2 轮提出的问题在 v2 中是否解决（已解决/部分解决/未解决 + 理由）；\n2) 评估关于二手来源的保留意见是否可接受；\n3) 指出仍存在的异议或错误，包括 v2 新增的任何引用（逐条核实作者/年份/出处/论断，附URL）；\n4) 给出明确结论：“同意”，或列出具体的剩余修改清单（按优先级）。\n\n=====plan_v2.md 全文=====\n"+v2
prev=sys.argv[1]
body={"agent":"search-method-reviewer","input":q,"environment":"remote","background":True}
if prev!="none": body["previous_interaction_id"]=prev
else: body["input"]="（新会话。前两轮要点：Greenhalgh 30%含手工翻检、纯数据库25%且限复杂证据；Booth 2010 无两轮即停规则；重捕法前提不成立；PRESS 只审检索式；需防循环报道、幻觉URL、个性化、付费墙、预算等。）\n\n"+q
r=call("interactions",body);print("created",r["id"],flush=True)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=call("interactions/"+r["id"])
    except Exception as e: print("poll err",e,flush=True)
print(r.get("status"),flush=True)
json.dump(r,open("raw_3.json","w"),ensure_ascii=False)
mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
txt="\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else []))
open("r3.txt","w").write(txt)
