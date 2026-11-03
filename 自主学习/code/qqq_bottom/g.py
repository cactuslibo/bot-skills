import os,json,time,urllib.request,urllib.error,sys
K=os.environ['GEMINI_API_KEY'];B="https://generativelanguage.googleapis.com/v1beta/models"
def call(m,prompt,json_mode=False,tries=1):
  body={"contents":[{"parts":[{"text":prompt}]}]}
  if json_mode: body["generationConfig"]={"responseMimeType":"application/json"}
  for i in range(tries):
    try:
      r=urllib.request.urlopen(urllib.request.Request(f"{B}/{m}:generateContent?key={K}",json.dumps(body).encode(),{"Content-Type":"application/json"}),timeout=300)
      d=json.load(r);return d["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
      c=getattr(e,"code",0)
      if c and c not in(429,500,503):print(m,c,file=sys.stderr);return None
      print(m,i,repr(e)[:80],file=sys.stderr);time.sleep(min(60,10*2**i));continue
      print(m,i,e.code,file=sys.stderr)
      if e.code not in(429,500,503):return None
      time.sleep(min(60,10*2**i))
  return None
P1="""You are a quantitative trading researcher. Compile a comprehensive list of 8-15 established quantitative models / rules (from literature, practitioners, and widely used trading systems) for detecting market BOTTOM formation in QQQ (Nasdaq-100 ETF). Prioritize models computable from daily OHLCV price/volume plus the VIX index; include at most a few needing breadth data and flag them. For each model give: 1) name and source/origin, 2) logic, 3) EXACT entry rule for 'bottom confirmed' with specific numeric parameters (unambiguous, codable on daily bars, signal at close, entry next open), 4) exit rule for backtesting (specific), 5) parameter list, 6) exact data/indicators required (e.g. QQQ daily OHLCV, RSI(14), MACD(12,26,9), SMA200, VIX daily close, VIX3M, % stocks above 50DMA, etc.). Be concrete."""
m=sys.argv[1]; t=sys.argv[2:] and int(sys.argv[2]) or 1
r1=call(m,P1,tries=t)
if not r1: sys.exit(2)
P2="Convert the following model list into a JSON array. Each element must have keys: name, logic, entry_rule, exit_rule, params (object of parameter name->value), required_data (array of strings). Keep the content faithful; make rules fully concrete with numbers where the text is vague.\n\n"+r1
r2=call(m,P2,True,3)
open("gemini_models_raw.md","w").write(f"# Gemini raw responses\nModel: {m}\n\n## Prompt 1\n{P1}\n\n## Response 1\n{r1}\n\n## Prompt 2 (JSON structuring)\n{P2[:300]}...\n\n## Response 2\n{r2}\n")
json.dump(json.loads(r2),open("models.json","w"),indent=2,ensure_ascii=False);print("OK",m)
