import json,os,requests
K=os.environ['GEMINI_API_KEY'];B='https://generativelanguage.googleapis.com/v1beta'
body={"id":"rsi-top-reviewer","base_agent":"antigravity-preview-09-2026","agent_config":{"type":"antigravity","model":"gemini-3.8-flash"},
"system_instruction":"You are a rigorous quantitative-finance reviewer. Every claim must cite the specific file and line number from the provided materials (or a real, verifiable published source). Never invent sources, line numbers, or numbers; if unsure, say so. Separate must-fix from suggested items.",
"base_environment":"remote","tools":[{"type":"google_search"},{"type":"url_context"},{"type":"code_execution"}]}
r=requests.post(f'{B}/agents',headers={'x-goog-api-key':K},json=body,timeout=300)
print(r.status_code);open('01_create_agent.json','w').write(r.text);print(r.text[:2000])
