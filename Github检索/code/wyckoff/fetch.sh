r=$1; shift; d=sources/${r/\//__}; mkdir -p $d
for p in "$@"; do f=$d/$(echo $p|tr / _); gh api repos/$r/contents/$p -H "Accept: application/vnd.github.raw" > "$f" 2>/dev/null || { echo "FAIL $r $p"; rm -f "$f"; }; done
