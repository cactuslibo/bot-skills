import os,json,time,urllib.request
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key};B="https://generativelanguage.googleapis.com/v1beta/interactions"
q=json.load(open("qs_corr.json"))[1]+"\n\n补充：你上一条回答是第1轮评审，现在请执行这一轮质疑。另请特别核对：(1) 平均连接(average linkage)是否真的要求度量满足三角不等式；(2) bb_ci 对全样本秩重抽样是否真的“严重低估”方差，可用 code_execution 做模拟验证；(3) 把 OBV 等差分后的单日序列与累积形态之间的取舍，在“平稳化防伪相关”的目标下是否仍应判为必须改；(4) GAPO 原式 ln(range)/ln(n) 依赖价格量纲，你的修复是否与平稳化要求冲突；(5) RWI 标准定义是否为 i∈[2,N] 取最大值，引用来源。"
prev=json.load(open("raw_corr_2.json"))["id"]
r=json.load(urllib.request.urlopen(urllib.request.Request(B,data=json.dumps({"agent":"quant-indicator-auditor","input":q,"environment":"remote","background":True,"previous_interaction_id":prev}).encode(),headers=H),timeout=300))
print("created",r["id"],flush=True); open("q3.txt","w").write(q)
while r.get("status") in ("in_progress","queued","pending"):
    time.sleep(20)
    try: r=json.load(urllib.request.urlopen(urllib.request.Request(B+"/"+r["id"],headers=H),timeout=300))
    except Exception as e: print("poll err",e,flush=True)
json.dump(r,open("raw_corr_3.json","w"),ensure_ascii=False); print("DONE",r.get("status"),flush=True)
