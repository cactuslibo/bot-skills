#!/usr/bin/env python3
"""AI healthcare news, last ~30 days: Google News RSS + TickerTick -> dedup -> SQLite -> Gemini topic summary (link-checked)."""
import json, os, re, sqlite3, requests, urllib.parse as u, datetime as dt
import pipeline as p
SINCE = os.getenv("SINCE", "2026-09-29")
GN_QUERIES = ["AI healthcare", "AI drug discovery", "AI medical", "AI diagnostics", "AI radiology imaging", "FDA artificial intelligence medical device",
              "FDA AI guidance", "healthcare AI startup funding", "AI biotech acquisition", "pharma AI partnership", "LLM clinical", "OpenAI health",
              "Anthropic Claude healthcare", "Google AI medicine", "Nvidia healthcare AI", "AI pathology", "AI clinical trials"]
TT_TICKERS = ["rxrx", "sdgr", "tem", "absi", "abcl", "isrg", "veev", "doc", "hims", "gh"]
AI_RE = re.compile(r"\b(AI|A\.I\.|artificial intelligence|machine learning|LLM|generative|GPT|chatbot|Claude|Gemini|deep learning|algorithm)\b", re.I)
HEALTH_RE = re.compile(r"health|medic|drug|pharma|biotech|clinic|hospital|patient|FDA|diagnos|radiolog|imaging|cancer|disease|therap|doctor|physician|care|genom|pathology|trial", re.I)

def fetch():
    raw = []
    for q in GN_QUERIES:
        try:
            raw += [dict(i, source="google_news", query=q) for i in p._rss(f"https://news.google.com/rss/search?q={u.quote_plus(q + ' when:30d')}&hl=en-US&gl=US&ceid=US:en", 100)]
        except Exception as e: print("GN", q, e)
    tq = "(and (or " + " ".join(f"tt:{t}" for t in TT_TICKERS) + ") (or T:curated T:market T:sec))"
    for q in [tq, "(or " + " ".join(f"z:{t}" for t in TT_TICKERS) + ")"]:
        try:
            r = requests.get("https://api.tickertick.com/feed", params={"q": q, "n": 200}, headers=p.UA, timeout=20); r.raise_for_status()
            raw += [dict(title=s["title"], url=s["url"], publisher=s.get("site"), published=p.iso(s["time"]/1000), snippet=s.get("description", ""), source="tickertick", query=q)
                    for s in r.json().get("stories", [])]
        except Exception as e: print("TT", q, e)
    return raw

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if os.getenv("CACHED"):
        items = json.load(open("output/ai_health_items.json")); raw = rel = items
    else:
      raw = fetch(); print("raw", len(raw), {s: sum(1 for i in raw if i["source"] == s) for s in ("google_news", "tickertick")})
      rel = [i for i in raw if (i.get("published") or "") >= SINCE and AI_RE.search(i["title"] + " " + (i.get("snippet") or "")) and HEALTH_RE.search(i["title"] + " " + (i.get("snippet") or "") + " " + i.get("query", ""))]
      rel.sort(key=lambda i: i.get("published") or "", reverse=True)
      items = p.dedup(rel, 0.8); print("relevant", len(rel), "dedup", len(items))
    con = sqlite3.connect("news.db"); con.execute("CREATE TABLE IF NOT EXISTS ai_health(id INTEGER PRIMARY KEY, source TEXT, query TEXT, title TEXT, url TEXT UNIQUE, publisher TEXT, published TEXT)")
    for i in items: con.execute("INSERT OR IGNORE INTO ai_health(source,query,title,url,publisher,published) VALUES(?,?,?,?,?,?)", (i["source"], i.get("query"), i["title"], i["url"], i.get("publisher"), i.get("published")))
    con.commit()
    json.dump(items, open("output/ai_health_items.json", "w"), ensure_ascii=False, indent=1)
    lst = "\n".join(f"[{n}] {i['published'][:10]} | {i['title']} | {i.get('publisher') or ''}" for n, i in enumerate(items, 1))
    prompt = ("以下是过去一个月（%s 至 2026-10-29）抓取的 AI 医疗相关新闻列表（编号|日期|标题|来源）。请用中文写一份分主题月度总结，主题依次为："
              "1 药物研发；2 诊断与医学影像；3 大模型/生成式AI医疗应用；4 监管与FDA；5 融资与并购；6 药企与AI公司合作；7 其他值得关注。"
              "每个主题用 '## ' 标题，下列 4-8 条要点（'- ' 开头），每条合并同一事件、写清公司/事件/数字（公司名、数字、期刊名等只能来自所引编号的标题原文，标题里没有的细节一律不写，不得推测）；要点需覆盖整个月份（含10月上旬），不要只写最近几天，末尾用 [#编号] 格式标注 1-2 个来源编号（如 [#12][#40]），编号必须来自列表，不要输出任何 URL。"
              "最后写 '## 本月趋势' 3 句话。只输出 Markdown。\n\n" % SINCE) + lst
    os.environ.setdefault("GEMINI_MODEL", "gemini-3.5-flash")
    summ = p.summarize("__custom__", items, prompt=prompt)
    used = items; bad = []
    def cite(m):
        n = int(m.group(1))
        if 1 <= n <= len(used): return f"[{used[n-1].get('publisher') or 'link'}]({used[n-1]['url']})"
        bad.append(n); return ""
    summ = re.sub(r"\[#(\d+)\]", cite, summ or ""); print("invalid ids:", bad)
    summ, removed = p.filter_links(summ, [i["url"] for i in items]); print("removed links:", len(removed))
    open("output/ai_health_summary.md", "w").write(f"# AI 医疗月度新闻总结（{SINCE} — 2026-10-29）\n\n去重后 {len(items)} 条（全部送入摘要）\n\n{summ}\n")
if __name__ == "__main__": main()
