import re,json
recs={}
for f in ["info1.txt","info2.txt"]:
    t=open(f).read()
    for blk in re.split(r"\n(?=\[[A-Za-z]+\d+[a-z]?\] )",t):
        m=re.match(r"\[(\w+)\] (.*?) \((\d{4}|Unknown Year)\)\n",blk)
        if not m: continue
        k=m.group(1); d={"key":k,"title":m.group(2),"year":m.group(3)}
        lines=blk.split("\n")
        d["venue"]=lines[1].strip() if len(lines)>1 else ""
        a=re.search(r"\nBy (.*?)(?: - (\d+) citations.*)?\n",blk); d["authors"]=a.group(1) if a else ""; d["cites"]=a.group(2) if a and a.group(2) else ""
        doi=re.search(r"\nDOI: (\S+)",blk); d["doi"]=doi.group(1) if doi else ""
        ln=re.search(r"\nLink: (\S+)",blk); d["link"]=ln.group(1) if ln else ""
        d["pdf"]="✓" in blk.split("\n\n")[0]
        parts=blk.split("\n\n",1); d["abstract"]=parts[1].strip() if len(parts)>1 else ""
        recs[k]=d
json.dump(recs,open("cands.json","w"),ensure_ascii=False,indent=1)
print(len(recs))
