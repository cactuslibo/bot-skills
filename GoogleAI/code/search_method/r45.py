import os,json,time,urllib.request,sys
key=os.environ['GEMINI_API_KEY'];H={"Content-Type":"application/json","x-goog-api-key":key}
B="https://generativelanguage.googleapis.com/v1beta/"
def call(url,body=None):
    req=urllib.request.Request(B+url,data=json.dumps(body).encode() if body else None,headers=H)
    return json.load(urllib.request.urlopen(req,timeout=600))
pf=open("/workspace/method/plan_final.md").read();s0=open("/workspace/method/source_first_v1.md").read()
qs=["第四轮（新议题）：方法论已定稿（plan_final.md，见下）。用户的核心思想是：搜索任何信息前，先想清楚这个信息会由什么样的来源产生，锁定来源，再去搜索。原作者据此起草了“第 0 步：来源建模”（source_first_v1.md，见下）。请：\n1) 指出遗漏，以及 bot 难以执行的部分；\n2) 说明第 0 步如何与第 1–8 步整合、避免重复；\n3) 推荐可借鉴的现有框架并附可核查来源（作者/机构、年份、出版方、URL），例如：情报搜集计划/搜集管理与情报周期（美军 JP 2-0、Heuer《Psychology of Intelligence Analysis》）、信息生命周期、档案/记录管理、新闻核实（Verification Handbook）、OSINT 方法（Berkeley Protocol on Digital Open Source Investigations 2022、Bellingcat 指南）、证据等级；说明每个框架具体可借鉴什么，不确定的标“无法核实”；\n4) 给出第 0 步的具体修订文本（可直接替换）。\n\n=====plan_final.md=====\n"+pf+"\n\n=====source_first_v1.md=====\n"+s0,
"第五轮：请逐条挑战你上一轮回答以及第 0 步草案中所有没有给出可核查来源的论断（包括框架的年份、版本、出版方和你归纳的具体内容）：能证实的附URL，不能证实的标“无法核实”并改措辞。最后给出第 0 步的最终修订文本，以及本轮引用的文献/框架清单（作者/机构、年份、出版方、URL）。"]
prev=sys.argv[1];out=open("agent_transcript.md","a")
for i,q in zip((4,5),qs):
    body={"agent":"search-method-reviewer","input":q,"environment":"remote","background":True,"previous_interaction_id":prev}
    r=call("interactions",body);print("created",i,r["id"],flush=True)
    while r.get("status") in ("in_progress","queued","pending"):
        time.sleep(20)
        try: r=call("interactions/"+r["id"])
        except Exception as e: print("poll err",e,flush=True)
    print(i,r.get("status"),flush=True);prev=r["id"]
    json.dump(r,open(f"raw_{i}.json","w"),ensure_ascii=False)
    mo=[s for s in r.get("steps",[]) if s.get("type")=="model_output"]
    txt="\n".join(c.get("text","") for c in (mo[-1]["content"] if mo else []))
    open(f"r{i}.txt","w").write(txt)
    out.write(f"## 第 {i} 轮（第 0 步：来源建模）\n**interaction id:** {r['id']} status={r.get('status')}\n\n**问：** {q[:700]}…（文件全文略）\n\n**答：**\n\n{txt}\n\n---\n\n");out.flush()
