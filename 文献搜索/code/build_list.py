#!/usr/bin/env python3
"""合并 Crossref 核验结果与下载结果，生成最终文献清单（Markdown 表格）。
用法: python build_list.py --refs refs.csv --check crossref_check.csv --dl oa_results.csv --out list.md
"""
import argparse, csv

def load(fn): return {r['id']: r for r in csv.DictReader(open(fn, encoding='utf-8'))} if fn else {}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--refs', required=True); ap.add_argument('--check')
    ap.add_argument('--dl'); ap.add_argument('--out', default='list.md'); a = ap.parse_args()
    refs = list(csv.DictReader(open(a.refs, encoding='utf-8'))); ck, dl = load(a.check), load(a.dl)
    L = ['| # | 标题 | 期刊 | 年份 | DOI | 核验 | PDF |', '|---|---|---|---|---|---|---|']
    for n, r in enumerate(refs, 1):
        c, d = ck.get(r['id'], {}), dl.get(r['id'], {})
        ver = '✅' if c.get('status') == 'ok' and not c.get('flags') else (c.get('flags') or c.get('status') or '-')
        L.append(f"| {n} | {c.get('cr_title') or r.get('title','')} | {c.get('journal','')} | {c.get('cr_year') or r.get('year','')} "
                 f"| {r.get('doi','')} | {ver} | {d.get('status','-')} |")
    open(a.out, 'w', encoding='utf-8').write('\n'.join(L) + '\n'); print('wrote', a.out, len(refs), 'rows')

if __name__ == '__main__': main()
