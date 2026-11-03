#!/usr/bin/env python3
"""QQQ 小时线 Gemini 第三方审核：持续对话。
用法:
  python3 gemini_chat.py "问题"            # 发送并追加到 history.json（先备份）
  python3 gemini_chat.py -f q.md           # 从文件读问题
  --model M        默认 gemini-3.8-flash；503 时自动换 gemini-3-flash-preview
  --no-save        不写历史（测试用）
  --cache          历史较长时（>= --cache-min-tokens 估算）用 cachedContents 缓存旧历史
  --compress N     把最早 N 条压缩成摘要（调用 Gemini，保留已确认问题与结论），写回前备份
"""
import argparse, json, os, re, shutil, sys, time, urllib.request, urllib.error, pathlib
D = pathlib.Path(__file__).resolve().parent
HIST, SYS, CACHE = D/'history.json', D/'system_instruction.txt', D/'cache_state.json'
BASE = 'https://generativelanguage.googleapis.com/v1beta'
FALLBACK = 'gemini-3-flash-preview'

def est_tokens(h):  # 粗估：中文约 1 字≈1 token，其他约 4 字符≈1 token
    t = ''.join(p.get('text','') for c in h for p in c['parts'])
    cjk = len(re.findall(r'[\u4e00-\u9fff]', t)); return cjk + (len(t)-cjk)//4

def post(url, body, method='POST'):
    key = os.environ.get('GEMINI_API_KEY')
    if not key: sys.exit('GEMINI_API_KEY 未设置')
    sep = '&' if '?' in url else '?'
    req = urllib.request.Request(f'{url}{sep}key={key}', data=None if body is None else json.dumps(body).encode(),
                                 headers={'Content-Type':'application/json'}, method=method)
    with urllib.request.urlopen(req, timeout=300) as r: return json.loads(r.read() or b'{}')

def merge(h):  # 保证 user/model 交替：合并连续同角色
    out = []
    for c in h:
        if out and out[-1]['role'] == c['role']: out[-1]['parts'] += c['parts']
        else: out.append({'role':c['role'],'parts':list(c['parts'])})
    return out

def backup():
    if HIST.exists(): shutil.copy(HIST, D/f'history.{time.strftime("%Y%m%d_%H%M%S")}.bak.json')

def get_cache(model, h, sysi, ttl):
    """缓存除最后一条外的历史；历史前缀未变且未过期则复用。"""
    prefix = h[:-1]
    if len(prefix) < 2 or prefix[-1]['role'] != 'model': return None, h
    sig = f'{model}:{len(prefix)}:{hash(json.dumps(prefix, ensure_ascii=False))}'
    if CACHE.exists():
        st = json.loads(CACHE.read_text())
        if st.get('sig') == sig and st.get('expire', 0) > time.time() + 60: return st['name'], h[-1:]
    try:
        r = post(f'{BASE}/cachedContents', {'model': f'models/{model}', 'contents': prefix,
                 'systemInstruction': {'parts':[{'text':sysi}]}, 'ttl': f'{ttl}s'})
    except urllib.error.HTTPError as e:
        print(f'[cache] 创建失败 HTTP {e.code}，改为不使用缓存', file=sys.stderr); return None, h
    CACHE.write_text(json.dumps({'sig':sig,'name':r['name'],'expire':time.time()+ttl}))
    return r['name'], h[-1:]

def generate(model, contents, sysi, cache_name=None):
    body = {'contents': contents}
    if cache_name: body['cachedContent'] = cache_name
    else: body['systemInstruction'] = {'parts':[{'text':sysi}]}
    r = post(f'{BASE}/models/{model}:generateContent', body)
    parts = r['candidates'][0]['content']['parts']
    return ''.join(p.get('text','') for p in parts if not p.get('thought')), r.get('usageMetadata', {})

def ask(model, h, sysi, use_cache, ttl, min_tok):
    for m in [model] + ([FALLBACK] if model != FALLBACK else []):
        cname, contents = (get_cache(m, h, sysi, ttl) if use_cache and est_tokens(h) >= min_tok else (None, h))
        try: return m, *generate(m, contents, sysi, cname)
        except urllib.error.HTTPError as e:
            if e.code in (503, 429) and m != FALLBACK: print(f'[{m}] HTTP {e.code}，改用 {FALLBACK}', file=sys.stderr); continue
            sys.exit(f'HTTP {e.code}: {e.read()[:500].decode(errors="replace")}')

COMPRESS_PROMPT = ('请把以上对话压缩成一份审计摘要，供后续继续审核使用。必须完整保留：'
 '1) 每个已确认（属实/已核实）的问题及其文件:行号、影响和整改状态；2) 被我方核实为不成立或夸大的说法及理由；'
 '3) 关键数字（年化、exS、MDD、笔数、胜率、avgw、DSR、N、SPA 覆盖等）与口径；4) 仍未解决/未核实的事项。'
 '不得新增任何结论，不确定的标注"未核实"。用中文，分条列出。')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('q', nargs='?'); ap.add_argument('-f')
    ap.add_argument('--model', default='gemini-3.8-flash'); ap.add_argument('--no-save', action='store_true')
    ap.add_argument('--cache', action='store_true'); ap.add_argument('--cache-ttl', type=int, default=3600)
    ap.add_argument('--cache-min-tokens', type=int, default=4096); ap.add_argument('--compress', type=int)
    a = ap.parse_args()
    h, sysi = json.loads(HIST.read_text()), SYS.read_text().strip()
    if a.compress:
        old, rest = h[:a.compress], h[a.compress:]
        if old and old[-1]['role'] == 'user': old, rest = old[:-1], [old[-1]] + rest  # 压缩段以 model 结尾
        m, summ, _ = ask(a.model, merge(old + [{'role':'user','parts':[{'text':COMPRESS_PROMPT}]}]), sysi, False, 0, 0)
        new = [{'role':'user','parts':[{'text':f'【此前 {len(old)} 条对话的压缩摘要（由 {m} 生成，原文见备份）】\n'+summ}]},
               {'role':'model','parts':[{'text':'已收到摘要，后续审核以此为准，未核实事项继续标注"未核实"。'}]}] + rest
        backup(); HIST.write_text(json.dumps(merge(new), ensure_ascii=False, indent=1))
        print(f'已压缩：{len(h)} → {len(merge(new))} 条，约 {est_tokens(h)} → {est_tokens(new)} token'); return
    q = open(a.f).read() if a.f else a.q
    if not q: ap.error('需要问题文本或 -f')
    convo = merge(h + [{'role':'user','parts':[{'text':q}]}])
    m, ans, usage = ask(a.model, convo, sysi, a.cache, a.cache_ttl, a.cache_min_tokens)
    print(ans); print(f'\n[model={m} usage={usage}]', file=sys.stderr)
    if not a.no_save:
        backup(); HIST.write_text(json.dumps(convo + [{'role':'model','parts':[{'text':ans}]}], ensure_ascii=False, indent=1))
if __name__ == '__main__': main()
