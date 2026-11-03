#!/usr/bin/env python3
"""把 PDF 目录打包成 zip；超过 --max-mb 自动分卷（part1, part2…），便于邮件/上传。
用法: python package_zip.py pdfs --name papers --max-mb 20
"""
import argparse, os, zipfile

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('--name', default='papers')
    ap.add_argument('--max-mb', type=float, default=20); a = ap.parse_args()
    files = sorted(f for f in os.listdir(a.dir) if f.lower().endswith('.pdf'))
    lim = a.max_mb * 1024 * 1024; parts, cur, size = [], [], 0
    for f in files:
        s = os.path.getsize(os.path.join(a.dir, f))
        if cur and size + s > lim: parts.append(cur); cur, size = [], 0
        cur.append(f); size += s
    if cur: parts.append(cur)
    for n, p in enumerate(parts, 1):
        zn = f'{a.name}.zip' if len(parts) == 1 else f'{a.name}_part{n}.zip'
        with zipfile.ZipFile(zn, 'w', zipfile.ZIP_DEFLATED) as z:
            for f in p: z.write(os.path.join(a.dir, f), f)
        print(zn, len(p), 'files', round(os.path.getsize(zn) / 1e6, 1), 'MB')

if __name__ == '__main__': main()
