import os,json,time,requests
B="https://generativelanguage.googleapis.com/v1beta/";H={"x-goog-api-key":os.environ['GEMINI_API_KEY'],"Content-Type":"application/json"}
num=lambda f:"\n".join(f"L{i+1}: {l}" for i,l in enumerate(open(f).read().split("\n")))
AID=open("gai_agent_id.txt").read().strip()
prev="v1_Chd5MHpwYXVuUU82Njl4ZElQOV82dHNBVRIXeTB6cGF1blFPNjY5eGRJUDlfNnRzQVU"
p="""第 2 轮复核（全程中文）。对方已提交 report2-indicators-v2.md（附行号，引用 report2-indicators-v2.md:Lnn），文末「第2轮修改说明」逐条写了第 1 轮意见的采纳情况。注意第 1 轮我方核查已更正你的几处结论：Hurst 0.4/0.6 缓冲带不足以解决 R/S 小样本偏差（n=100–250 随机游走约 40% Ĥ>0.6）；N 日新高两种口径触发率接近（12.3% vs 13.0%）；冲击系数 0.1 偏乐观而非保守；最大回撤期望随 √T（零漂移）/ln T（正漂移）增长而非 √ln T；Sortino 原稿无 n/k 陷阱；波动率目标 clip 与杠杆上限不矛盾。
重点：
一、对方的分歧与部分采纳是否可接受：WQ Margin 与 PCR 阈值不收录；IC 胜率与主力资金流只留定义和陷阱；N 日新高、train→test 衰减、冲击成本三项部分采纳。
二、新补公式与参数是否正确：Hurst（零分布/E[H|n]、Anis-Lloyd-Peters 修正）、布林带（含 %b、BandWidth、1.9/2.1 规则、σ 用总体还是样本标准差）、KDJ、OBV、MACD 口径、DSR（含超额峰度换算）、GARCH(1,1)、PSI、MinTRL、半衰期、Kelly 等，请逐条用 code_execution 验算或对照原始出处（附 URL）。
三、是否引入新错误或前后不一致。
输出：若无必须修改，明确写「认同」；若有，按「同意 / 需修改 / 需补充」分类，带行号与建议文字。查不到出处标 UNVERIFIED。

=====report2-indicators-v2.md=====
"""+num("report2-indicators-v2.md")
r=requests.post(B+"interactions",headers=H,json={"agent":AID,"input":p,"environment":"6898496e634eb79f120e9ae782c9c667","background":True,"previous_interaction_id":prev}).json()
i=r.get("id");print("iid",i,flush=True)
if not i: print(r);raise SystemExit
while True:
  time.sleep(20)
  try: d=requests.get(B+"interactions/"+i,headers=H,timeout=120).json()
  except Exception as e: print("poll err",e,flush=True); continue
  if d.get("status") not in("in_progress","queued","pending"): break
print("status",d.get("status"),flush=True)
json.dump(d,open("gai_raw_2.json","w"),ensure_ascii=False,indent=1)
t=[s for s in d.get("steps",[]) if s.get("type")=="model_output"]
open("googleai-round2_raw.md","w").write("\n".join(c.get("text","") for c in t[-1]["content"]) if t else json.dumps(d)[:3000])
