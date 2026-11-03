import sys,json,re
K=re.compile(r'wyckoff|威科夫|维科夫|vikoff|筑底|吸筹',re.I)
for f in sys.argv[1:]:
  for line in open(f):
    line=line.strip()
    if not line.startswith('{'): continue
    try: o=json.loads(line)
    except: continue
    for c in o.get('message',{}).get('content',[]):
      t=c.get('text') or json.dumps(c.get('input',''),ensure_ascii=False) if c.get('type') in('text','tool_use') else ''
      if t and K.search(t) and (o['role']=='user' or c.get('name')=='SendToUser' or c.get('type')=='text'):
        print('---',o['role'],c.get('name',''));print(t[:2500])
