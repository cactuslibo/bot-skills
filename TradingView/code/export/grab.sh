#!/bin/bash
cd ~/Downloads
for t in "$@"; do f=$(find . -maxdepth 1 -name "*_${t}, 1D*.csv" -mmin -60 -printf '%T@ %p\n'|sort -n|tail -1|cut -d' ' -f2-)
if [ -n "$f" ]; then cp "$f" /workspace/tv_db/daily/$t.csv; echo $t $(sed -n 2p /workspace/tv_db/daily/$t.csv|cut -c1-10) $(wc -l </workspace/tv_db/daily/$t.csv) "$f"; else echo $t MISSING; fi; done
