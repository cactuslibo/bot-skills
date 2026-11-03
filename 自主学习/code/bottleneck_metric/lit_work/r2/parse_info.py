import re,json,glob
recs={}
for f in ["694a25ae-fc45-4e22-83a6-e1df9f46d8fa.txt","42faed60-c095-4e75-9d27-39c15a84369a.txt","bac4316e-ae23-4112-868f-29ca3c5ac82b.txt"]:
    t=open(f).read()
    blocks=re.split(r'\n(?=\[[A-Za-z]+\d{2}[a-z]{0,2}\] )',"\n"+t)
    for b in blocks:
        m=re.match(r'\s*\[([A-Za-z]+\d{2}[a-z]{0,2})\] (.*?) \((\d{4}|Unknown Year)\)\n',b)
        if not m: continue
        k=m.group(1); lines=b.strip().split("\n")
        r={"key":k,"title":m.group(2),"year":m.group(3),"venue":lines[1].strip()}
        for l in lines:
            if l.startswith("By "): r["authors"]=re.sub(r' - \d+ citations.*','',l[3:])
            if l.startswith("DOI: "): r["doi"]=l[5:].strip()
            if l.startswith("Link: "): r["link"]=l[6:].strip()
            if l.startswith("PDF "): r["pdf"]=l[4:].strip()
        i=[j for j,l in enumerate(lines) if l.startswith("PDF ")]
        r["abstract"]=" ".join(lines[i[0]+1:]).strip() if i else ""
        recs[k]=r
json.dump(recs,open("info_new.json","w"),ensure_ascii=False,indent=1)
print(len(recs))
