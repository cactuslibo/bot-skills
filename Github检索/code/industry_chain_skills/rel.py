import json,re
K=r'chain|supply|value|bom|产业|链|pharm|drug|industry|sourc|procure|vendor|mineral|上下游'
def rel(v):
  if v['paths']: return any(re.search(K,p,re.I) for p in v['paths'])
  return bool(re.search(r'(supply|value|industry)[ -]?chain|产业链|供应链|上下游|bill of materials',v.get('desc',''),re.I)) and bool(re.search(r'skill|agent|claude|mcp|llm|gpt|codex|cursor|ai',v.get('desc','')+' ',re.I))
