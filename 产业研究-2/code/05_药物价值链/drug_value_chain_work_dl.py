import json,subprocess,os,sys
def fetch(key,url,tag=''):
    fn=f'/workspace/drug_value_chain/pdfs/{key}.pdf'
    if os.path.exists(fn): return True
    tmp=fn+'.tmp'
    subprocess.run(['curl','-sL','--max-time','60','-A','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36','-o',tmp,url])
    if os.path.exists(tmp):
        t=open(tmp,'rb').read(5).decode('latin1'); ok=subprocess.run(['pdfinfo',tmp],capture_output=True).returncode==0
        if t.startswith('%PDF') and ok:
            os.rename(tmp,fn); return True
        os.remove(tmp)
    return False
if __name__=='__main__':
    R=json.load(open('um_links.json'))
    for r in R:
        print(r['cite_key'],fetch(r['cite_key'],r['url']))
