import os,json,urllib.request,sys
B='/workspace/qqq_hourly_rl/'
def rd(f): return f"\n===== {f} =====\n"+"".join(f"{i+1:4d}| {l}" for i,l in enumerate(open(B+f)))
def summ(f):
    d=json.load(open(B+f)); return f"\n===== {f} (摘要：best/res/oos_p2) =====\n"+json.dumps(dict(best=d['best'],oos_p2=d['oos_p2'],res=d['res']),ensure_ascii=False,default=str)[:15000]
ctx="".join(rd(f) for f in ['r5.py','r6.py','r7.py','winrun.py','ROUND_6.md','ROUND_7.md','SUMMARY.md','WIN_CRITERIA.md','OOS_LOG.md'])+summ('r6_results.json')+summ('r7_results.json')
ctx+="\n===== 审核者独立复算 indep.py =====\n"+open('indep.py').read()+"\n输出:\n"+open('indep_out.txt').read()
ctx+="""\n审核者补充事实：VIX_1h 时间戳为 ET bar 开始时间，常规时段 09:30..15:30 各一根，另有 03:15-09:15 的盘前 bar；VIX3M_1h、ADV_DECL_1h 为 09:30..15:30。r6_results.json 的 OOS 结果没有 avgw 字段（只有 expo）。用 r6.py 重算 F2 的 OOS avgw=0.2304。DSR 的 N=10670 来自 ROUND_5.md（600+400+5600+4000+70），第 6、7 轮各有 67 个候选。"""
Q="""你是独立的量化审计员。请审核下面这个 QQQ 小时线研究（第 6–7 轮），目标是找出幻觉、编造的数字、前视偏差和未来数据泄漏。请逐项回答，每项给出文件名和行号证据，并给出 确认/可疑/无问题 的判断：
1) 15:30 决策是否只用了已收盘的 K 线（PX、rsi2_px、sum_prev、VIX 14:30 bar、VIX 盘中高点、涨跌家数）；
2) 盘中 VIX/VIX3M 与涨跌家数的时间戳是否和 QQQ 对齐（时区、bar 开始还是结束）；
3) MOC 成交价是否可实现（15:30 决策 vs 15:50 MOC 截止时间、半日交易日）；
4) 资金占用是否按新口径（平均权重 avgw）计算，r6 的表格是否混用了口径；
5) DSR/SPA 是否计入了第 6–7 轮的试验，N=10670 是否已过时；
6) 样本外已被查看 7 次，污染程度如何、该怎么处理；
7) G1 的恐慌规则在训练段从未触发意味着什么，冻结 G1 做前推验证是否合理；
8) 文中数字和 json 结果、复算结果是否一致（逐个列出差异）；
9) 你发现的其他 bug。
最后给出整改清单。用中文回答。"""
key=os.environ['GEMINI_API_KEY']; body=json.dumps({"contents":[{"parts":[{"text":Q+"\n\n"+ctx}]}],"generationConfig":{"temperature":0.2}}).encode()
for model in ['gemini-3.8-flash','gemini-3-flash-preview']:
    try:
        r=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=body,headers={'Content-Type':'application/json','x-goog-api-key':key})
        j=json.load(urllib.request.urlopen(r,timeout=600)); txt="".join(p.get('text','') for p in j['candidates'][0]['content']['parts'])
        open(B+'gemini_audit_r6_7.md','w').write(f"# Gemini 原始回复（模型 {model}，2026-10-30 ET）\n\n"+txt); print('OK',model,len(txt)); break
    except urllib.error.HTTPError as e: print(model,e.code,e.read()[:300])
