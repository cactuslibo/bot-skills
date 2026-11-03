#!/usr/bin/env python3
"""通过合法开放获取渠道（Unpaywall / OpenAlex / Semantic Scholar / Europe PMC / arXiv）查找并下载 PDF，
并校验文件头 %PDF、大小及首页标题匹配。
输入 CSV 列: id,doi,title ；PDF 存到 --outdir/<id>.pdf；结果写 oa_results.csv
用法: python oa_download.py refs.csv --outdir pdfs --email YOUR_EMAIL [--workers 4]
依赖: curl, pdftotext (poppler-utils)
"""
import argparse, csv, json, os, re, subprocess, urllib.parse
from concurrent.futures import ThreadPoolExecutor

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
BAD = re.compile(r'sci-hub|scihub|libgen|library\.lol|annas-archive|z-lib', re.I)  # 只用合法 OA 来源
EMAIL = 'YOUR_EMAIL'

def get(u, t=25): return subprocess.run(['curl', '-sL', '-m', str(t), '-A', UA, u], capture_output=True).stdout
def js(u):
    try: return json.loads(get(u))
    except Exception: return {}
def norm(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def candidates(doi, title):
    c = []
    if doi:
        for l in js(f'https://api.unpaywall.org/v2/{doi}?email={EMAIL}').get('oa_locations') or []:
            for k in ('url_for_pdf', 'url'):
                if l.get(k): c.append(l[k])
        for l in js(f'https://api.openalex.org/works/doi:{doi}?mailto={EMAIL}').get('locations') or []:
            for k in ('pdf_url', 'landing_page_url'):
                if l.get(k): c.append(l[k])
        s = js(f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,externalIds')
        if (s.get('openAccessPdf') or {}).get('url'): c.append(s['openAccessPdf']['url'])
        ax = (s.get('externalIds') or {}).get('ArXiv')
        if ax: c.append(f'https://arxiv.org/pdf/{ax}')
        e = js(f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%22{doi}%22&format=json&resultType=core')
        for r in (e.get('resultList') or {}).get('result', []):
            if r.get('pmcid'):
                c.append(f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={r['pmcid']}&blobtype=pdf")
        if doi.startswith('10.1101/'):
            c += [f'https://www.biorxiv.org/content/{doi}v1.full.pdf', f'https://www.medrxiv.org/content/{doi}v1.full.pdf']
    if title:
        q = urllib.parse.quote(title[:150])
        for w in js(f'https://api.openalex.org/works?search={q}&per-page=5&mailto={EMAIL}').get('results') or []:
            if norm(w.get('title')) == norm(title):
                c += [l['pdf_url'] for l in w.get('locations') or [] if l.get('pdf_url')]
    seen = []
    for u in c:
        if u not in seen and not BAD.search(u): seen.append(u)
    return seen

def valid_pdf(fn, title):
    if not os.path.exists(fn) or os.path.getsize(fn) < 30000: return False
    with open(fn, 'rb') as f:
        if f.read(4) != b'%PDF': return False
    if subprocess.run(['pdfinfo', fn], capture_output=True).returncode != 0: return False
    if not title: return True
    t = norm(subprocess.run(['pdftotext', '-l', '3', fn, '-'], capture_output=True).stdout.decode('utf8', 'ignore'))
    return norm(title)[:40] in t

def pdf_from_html(u):
    h = get(u).decode('utf8', 'ignore')
    m = re.search(r'citation_pdf_url"\s+content="([^"]+)', h)
    return m.group(1) if m else None

def run(row, outdir):
    i, doi, title = row['id'], (row.get('doi') or '').strip(), row.get('title') or ''
    fn = os.path.join(outdir, f'{i}.pdf')
    if os.path.exists(fn): return {'id': i, 'status': 'EXISTS', 'url': ''}
    for u in candidates(doi, title):
        for uu in (u, pdf_from_html(u)):
            if not uu or BAD.search(uu): continue
            subprocess.run(['curl', '-sL', '-m', '60', '-A', UA, '-o', fn + '.tmp', uu])
            if valid_pdf(fn + '.tmp', title): os.rename(fn + '.tmp', fn); return {'id': i, 'status': 'OK', 'url': uu}
            if os.path.exists(fn + '.tmp'): os.remove(fn + '.tmp')
    return {'id': i, 'status': 'MISSING', 'url': ''}

def main():
    global EMAIL
    ap = argparse.ArgumentParser(); ap.add_argument('csv'); ap.add_argument('--outdir', default='pdfs')
    ap.add_argument('--email', default='YOUR_EMAIL'); ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--out', default='oa_results.csv'); a = ap.parse_args(); EMAIL = a.email
    os.makedirs(a.outdir, exist_ok=True)
    rows = list(csv.DictReader(open(a.csv, encoding='utf-8')))
    with ThreadPoolExecutor(a.workers) as ex: res = list(ex.map(lambda r: run(r, a.outdir), rows))
    for r in res: print(r['id'], r['status'])
    w = csv.DictWriter(open(a.out, 'w', newline='', encoding='utf-8'), fieldnames=['id', 'status', 'url']); w.writeheader(); w.writerows(res)

if __name__ == '__main__': main()
