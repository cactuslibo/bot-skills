import os,json,urllib.request
key=os.environ['GEMINI_API_KEY']
body={"id":"quant-indicator-auditor","base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
"system_instruction":"你是量化技术指标审计专家。始终用中文回答；绝不编造指标、作者、年份或文献；不确定时明确说明；为关键结论引用可核查的来源（原始文献或权威资料，给出URL）。",
"base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/agents",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":key})
try: print(urllib.request.urlopen(req,timeout=120).read().decode()[:2000])
except urllib.error.HTTPError as e: print(e.code,e.read().decode()[:2000])
