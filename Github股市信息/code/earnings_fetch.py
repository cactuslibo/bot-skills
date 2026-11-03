import json, sys, pipeline as p
c = json.load(open("config.json")); c["per_source_limit"] = 100; c["google_news_window"] = "1d"
qs = {"LLY": ["Eli Lilly earnings", "Lilly third quarter 2026", "Lilly stock Mounjaro Zepbound"],
      "MRK": ["Merck earnings", "Merck third quarter 2026", "Merck stock Keytruda"]}
import requests, urllib.parse as u
out = {}
for t, ql in qs.items():
    raw = []
    for s in ("tickertick", "yahoo_rss", "finviz"):
        try: raw += [dict(i, source=s) for i in p.SOURCES[s](t, c)]
        except Exception as e: print(t, s, e)
    r = requests.get(f"https://api.tickertick.com/feed?q=(and z:{t.lower()} T:earning)&n=50", headers=p.UA, timeout=20)
    raw += [dict(title=x["title"], url=x["url"], publisher=x.get("site"), published=p.iso(x["time"]/1000), snippet=x.get("description",""), source="tickertick_earning") for x in r.json().get("stories", [])]
    for q in ql:
        items = p._rss(f"https://news.google.com/rss/search?q={u.quote_plus(q + ' when:1d')}&hl=en-US&gl=US&ceid=US:en", 100)
        raw += [dict(i, source="google_news") for i in items]
    out[t] = [i for i in p.dedup(raw, 0.85) if (i.get("published") or "") >= "2026-10-28T12" or "Today" in (i.get("published") or "")]
    print(t, len(raw), "->", len(out[t]))
json.dump(out, open("output/earnings_raw.json", "w"), ensure_ascii=False, indent=1)
