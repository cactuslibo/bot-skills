import os,json,urllib.request,sys
B='/workspace/qqq_hourly_rl/'
def rd(f): return f"\n===== {f} =====\n"+"".join(f"{i+1:4d}| {l}" for i,l in enumerate(open(B+f)))
def summ8(f):
    d=json.load(open(B+f)); return f'\n===== {f} 摘要 =====\n'+json.dumps(dict(NT=d['NT'],spa_all=d['spa_all'],best=d['best'],res=d['res'],val_p2=d['val_p2']),ensure_ascii=False,default=str)[:15000]
def summ(f):
    d=json.load(open(B+f)); return f"\n===== {f} (摘要：best/res/oos_p2) =====\n"+json.dumps(dict(best=d['best'],oos_p2=d['oos_p2'],res=d['res']),ensure_ascii=False,default=str)[:15000]
ctx="".join(rd(f) for f in ['REVIEW_REQUEST_R8.md','AUDIT_FIX_R6_7.md','r5.py','r6.py','r7.py','r8.py','r9.py','winrun2.py','forward_track.py','ROUND_8.md','ROUND_9.md','WIN_CRITERIA.md','OOS_LOG.md'])+summ8('r8_results.json')+summ8('r9_results.json')
ctx+="\n===== 审核者独立复算 indep.py =====\n"+open('indep.py').read()+open('indep8.py').read()+"\n输出:\n"+open('indep8_out.txt').read()
ctx+='''
审核者补充事实：/workspace/data/QQQ_1h.csv 最后一行是 2026-10-29 11:30（当日只有 3 根 bar）；VIX.csv 日线最后一行是 2026-10-30（盘中未收盘的值）；VIX_1h 最后一根是 2026-10-30 13:30。forward_log.csv 目前只有表头。'''
Q="""你是独立的量化审计员。请复审下面这个 QQQ 小时线研究的审计整改情况以及第 8–9 轮工作，目标是找出幻觉、编造数据、前视偏差和未来数据泄漏。请逐项回答，并给出文件名和行号作为证据，判断为 确认/可疑/无问题：
1) r8.py 的 sigH2/sigH3/sigH4 是否只用了 15:30 前已经收盘的 K 线（lo1530、bull1430、br1330、vix1330、hrsi1430、smaL）；
2) r8.ladder 的权重构造是否正确；
3) winrun2.py 与 r5.rc_spa、r5.dsr 的 SPA/DSR 实现是否正确，是否真的覆盖了全部候选，试验数 N 是否正确（10804/10909/10945）；
4) forward_track.py 是否存在前视、重复记录或数据不完整的问题；
5) 上次的整改是否已落实：半日交易日 PX=NaN、avgw 口径、训练段触发≥5（A1）、"验证集"改称；
6) 文中数字与 json 结果、独立复算是否一致；
7) 其他 bug。
最后给出整改清单，用中文回答。"""
key=os.environ['GEMINI_API_KEY']; body=json.dumps({"contents":[{"parts":[{"text":Q+"\n\n"+ctx}]}],"generationConfig":{"temperature":0.2}}).encode()
for model in ['gemini-3.8-flash','gemini-3-flash-preview']:
    try:
        r=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=body,headers={'Content-Type':'application/json','x-goog-api-key':key})
        j=json.load(urllib.request.urlopen(r,timeout=600)); txt="".join(p.get('text','') for p in j['candidates'][0]['content']['parts'])
        open(B+'gemini_audit_r8_9.md','w').write(f"# Gemini 原始回复（模型 {model}，2026-10-30 ET）\n\n"+txt); print('OK',model,len(txt)); break
    except urllib.error.HTTPError as e: print(model,e.code,e.read()[:300])
