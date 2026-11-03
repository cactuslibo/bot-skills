import os,json,time,sys,urllib.request
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key};B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    try: return json.load(urllib.request.urlopen(req,timeout=300))
    except urllib.error.HTTPError as e: return {"_err":e.code,"_body":e.read().decode()[:2000]}
AID="market-analog-reviewer"
if sys.argv[1]=="create":
    print(call("agents/"+AID))
    print(call("agents",{"id":AID,"base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
     "system_instruction":"你是严谨的宏观与股市历史类比研究审稿人。始终用中文回答；绝不编造数字、日期或事实；不确定或无法核实时明确说明；关键结论必须引用可核查来源（给出URL）；使用 google_search 核实事实，必要时用 code_execution 基于真实数据计算。",
     "base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}))
else:
    n=int(sys.argv[1]); q=open(f"q{n}.txt").read()
    body={"agent":AID,"input":q,"environment":"remote","background":True}
    if n>1: body["previous_interaction_id"]=json.load(open(f"raw_{n-1}.json"))["id"]
    r=call("interactions",body); print("created",str(r)[:300],flush=True)
    while r.get("status") in ("in_progress","queued","pending"):
        time.sleep(20); x=call("interactions/"+r["id"])
        if "_err" in x: print("poll err",x,flush=True); continue
        r=x; print(r.get("status"),flush=True)
    json.dump(r,open(f"raw_{n}.json","w"),ensure_ascii=False); print("DONE",r.get("status"))
