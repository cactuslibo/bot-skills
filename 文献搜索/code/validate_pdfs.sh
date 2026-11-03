#!/usr/bin/env bash
# 校验目录下所有 PDF：文件头 %PDF + pdfinfo 可解析，坏文件移到 bad/ 子目录
# 用法: bash validate_pdfs.sh <pdf_dir>
set -u
D="${1:-pdfs}"; mkdir -p "$D/bad"; ok=0; bad=0
for f in "$D"/*.pdf; do
  [ -e "$f" ] || continue
  if [ "$(head -c 4 "$f")" = "%PDF" ] && pdfinfo "$f" >/dev/null 2>&1; then
    ok=$((ok+1)); echo "OK   $(pdfinfo "$f" | awk '/^Pages:/{print $2}')p  $f"
  else
    bad=$((bad+1)); echo "BAD  $f"; mv "$f" "$D/bad/"
  fi
done
echo "合格: $ok  损坏/非PDF: $bad"
