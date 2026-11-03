#!/usr/bin/env python3
"""用 Crossref 核验文献元数据（标题/年份/第一作者）。
输入 CSV 列: id,doi,title,year,first_author ；输出 crossref_check.csv
用法: python crossref_verify.py refs.csv --email YOUR_EMAIL
"""
import argparse, csv, difflib, json, re, time, urllib.parse, urllib.request

def norm(s): return re.sub(r'\W', '', (s or '').lower())

def crossref(doi, email):
    url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi) + '?mailto=' + urllib.parse.quote(email)
    return json.load(urllib.request.urlopen(url, timeout=30))['message']

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('csv'); ap.add_argument('--email', default='YOUR_EMAIL')
    ap.add_argument('--out', default='crossref_check.csv'); a = ap.parse_args()
    rows = list(csv.DictReader(open(a.csv, encoding='utf-8')))
    out = []
    for r in rows:
        doi = (r.get('doi') or '').strip()
        rec = {'id': r.get('id'), 'doi': doi, 'status': '', 'flags': ''}
        if not doi: rec['status'] = 'no_doi'; out.append(rec); continue
        try: m = crossref(doi, a.email)
        except Exception as e: rec['status'] = 'error: ' + str(e)[:60]; out.append(rec); continue
        ti = (m.get('title') or [''])[0]
        yr = (m.get('issued', {}).get('date-parts') or [[None]])[0][0]
        au = m.get('author') or []; fa = au[0].get('family', '') if au else ''
        sim = difflib.SequenceMatcher(None, norm(ti), norm(r.get('title'))).ratio()
        flags = []
        if sim < 0.85: flags.append('TITLE')
        if r.get('year') and str(yr) != str(r['year']).strip(): flags.append('YEAR')
        ufa = (r.get('first_author') or '').lower()
        if ufa and ufa not in fa.lower() and fa.lower() not in ufa: flags.append('AUTHOR')
        rec.update(status='ok', flags='|'.join(flags), cr_title=ti, cr_year=yr, cr_first=fa,
                   journal=(m.get('container-title') or [''])[0], volume=m.get('volume'),
                   page=m.get('page') or m.get('article-number'), sim=round(sim, 2))
        out.append(rec); print(rec['id'], rec['flags'] or 'OK'); time.sleep(0.15)
    keys = sorted({k for o in out for k in o})
    w = csv.DictWriter(open(a.out, 'w', newline='', encoding='utf-8'), fieldnames=keys); w.writeheader(); w.writerows(out)

if __name__ == '__main__': main()
