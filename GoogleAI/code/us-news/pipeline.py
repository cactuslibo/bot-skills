#!/usr/bin/env python3
"""US stock news pipeline: fetch (key-free) -> dedup -> SQLite -> JSON/Markdown -> optional AI summary."""
import calendar, json, os, re, sqlite3, sys, time, datetime as dt, argparse
from difflib import SequenceMatcher
from urllib.parse import urlsplit, urlunsplit, quote_plus
import requests, feedparser
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
def iso(ts): return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat()

# ---------- sources ----------
def src_tickertick(t, c):
    r = requests.get(f"https://api.tickertick.com/feed?q=z:{t.lower()}&n={c['per_source_limit']}", headers=UA, timeout=20); r.raise_for_status()
    return [dict(title=s["title"], url=s["url"], publisher=s.get("site"), published=iso(s["time"]/1000), snippet=s.get("description","")) for s in r.json().get("stories", [])]

def _rss(url, limit, headers=UA, retries=3):
    for k in range(retries):
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 429: break
        time.sleep(2 * (k + 1))
    r.raise_for_status()
    out = []
    for e in feedparser.parse(r.content).entries[:limit]:
        p = e.get("published_parsed"); src = e.get("source", {}).get("title") if e.get("source") else None
        out.append(dict(title=e.title, url=e.link, publisher=src, published=iso(calendar.timegm(p)) if p else None,
                        snippet=BeautifulSoup(e.get("summary",""), "html.parser").get_text(" ", strip=True)[:300]))
    return out

def src_yahoo_rss(t, c): return _rss(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={t}&region=US&lang=en-US", c["per_source_limit"], headers={"User-Agent": "Mozilla/5.0"})

def src_google_news(t, c):
    q = quote_plus(f"{t} stock when:{c.get('google_news_window','2d')}")
    items = _rss(f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en", c["per_source_limit"])
    for i in items:  # Google titles end with " - Publisher"
        if i["publisher"] and i["title"].endswith(" - " + i["publisher"]): i["title"] = i["title"][: -len(i["publisher"]) - 3]
        i["snippet"] = ""
    return items

def src_finviz(t, c):
    r = requests.get(f"https://finviz.com/quote.ashx?t={t}&p=d", headers=UA, timeout=20); r.raise_for_status()
    tbl = BeautifulSoup(r.text, "html.parser").find(id="news-table"); out = []; day = None
    for tr in (tbl.find_all("tr") if tbl else [])[: c["per_source_limit"]]:
        a = tr.find("a", class_="tab-link-news")
        if not a: continue
        stamp = tr.td.get_text(" ", strip=True).split()
        if len(stamp) == 2: day = stamp[0]
        pub = tr.find("span"); out.append(dict(title=a.get_text(strip=True), url=a["href"], publisher=pub.get_text(strip=True).strip("()") if pub else None,
                    published=f"{day} {stamp[-1]} ET (finviz local)", snippet=""))
    return out

SOURCES = dict(tickertick=src_tickertick, yahoo_rss=src_yahoo_rss, google_news=src_google_news, finviz=src_finviz)

# ---------- dedup ----------
def norm_url(u):
    s = urlsplit(u); return urlunsplit((s.scheme.lower(), s.netloc.lower().removeprefix("www."), s.path.rstrip("/"), "", ""))
def norm_title(t): return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()
def dedup(items, thr):
    kept, urls = [], set()
    for it in items:
        u = norm_url(it["url"]); nt = norm_title(it["title"])
        if u in urls or any(SequenceMatcher(None, nt, k["_nt"]).ratio() >= thr for k in kept):
            for k in kept:
                if norm_url(k["url"]) == u or SequenceMatcher(None, nt, k["_nt"]).ratio() >= thr:
                    k["also_in"] = sorted(set(k.get("also_in", [])) | {it["source"]}); break
            continue
        urls.add(u); it["_nt"] = nt; kept.append(it)
    for k in kept: k.pop("_nt", None)
    return kept

# ---------- storage ----------
def db_init(p):
    con = sqlite3.connect(p)
    con.execute("""CREATE TABLE IF NOT EXISTS news(id INTEGER PRIMARY KEY, ticker TEXT, source TEXT, title TEXT, url TEXT,
      norm_url TEXT, publisher TEXT, published TEXT, snippet TEXT, fetched_at TEXT, UNIQUE(ticker, norm_url))""")
    return con

# ---------- link check ----------
def filter_links(text, allowed_urls):
    """Remove markdown links whose URL is not in allowed_urls. Returns (text, removed_list)."""
    if not text: return text, []
    allowed = set(allowed_urls); removed = []
    def rep(m):
        if m.group(2) in allowed: return m.group(0)
        removed.append(m.group(2)); return ""
    out = re.sub(r"\[([^\]]*)\]\((https?://[^)\s]+)\)", rep, text)
    return re.sub(r"[ \t]+\n", "\n", out), removed

# ---------- AI summary hook ----------
def summarize(ticker, items, prompt=None):
    """Returns summary text or None if no key. Keys are read from env only."""
    if not items: return None
    if prompt is None:
      news = "\n".join(f"[{n}] {i['title']} | {i.get('publisher') or i['source']} | {i.get('published') or ''} | {i['url']}"
                     for n, i in enumerate(items[:40], 1))
      prompt = (f"你是美股新闻分析助手。以下是美股 {ticker} 的最新新闻（编号、标题、来源、时间、链接）。\n"
              "请用中文输出 Markdown：\n1. 先写 3-5 条要点（以 '- ' 开头），合并同一事件，每条末尾用 Markdown 链接注明来源，如 [来源名](URL)，URL 必须原样取自下方列表，不得编造；\n"
              "2. 最后单独一行写：**整体情绪：** 偏多/中性/偏空 + 一句理由。\n不要输出其他内容。\n\n" + news)
    try:
        if os.environ.get('GEMINI_API_KEY'):  # highest priority; official REST, key sent in header (never in URL/logs)
            models = [os.getenv("GEMINI_MODEL", "gemini-3.5-flash")] + [m for m in ("gemini-flash-latest", "gemini-3.5-flash-lite") if m != os.getenv("GEMINI_MODEL")]
            r, used = None, None
            for model in dict.fromkeys(models):
                for k in range(3):
                    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", timeout=int(os.getenv("LLM_TIMEOUT", "300")),
                         headers={"x-goog-api-key": os.environ['GEMINI_API_KEY'], "content-type": "application/json"},
                         json={"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.3}})
                    if r.status_code not in (429, 500, 503): break
                    time.sleep(3 * (k + 1))
                if r.ok: used = model; break
            if not r.ok: return f"(Gemini summary failed: HTTP {r.status_code} {r.text[:300]})"
            print(f"  [gemini] {ticker} model={used}")
            parts = r.json()["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
        if os.getenv("ANTHROPIC_API_KEY"):
            r = requests.post("https://api.anthropic.com/v1/messages", timeout=60, headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01", "content-type": "application/json"},
                 json={"model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5"), "max_tokens": 800, "messages": [{"role": "user", "content": prompt}]})
            r.raise_for_status(); return r.json()["content"][0]["text"]
        if os.getenv("OPENAI_API_KEY"):
            r = requests.post(os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions", timeout=60,
                 headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                 json={"model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"), "messages": [{"role": "user", "content": prompt}]})
            r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"(summary failed: " + type(e).__name__ + ")"
    return None

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("-c", "--config", default="config.json"); ap.add_argument("--tickers")
    a = ap.parse_args(); os.chdir(os.path.dirname(os.path.abspath(__file__)))
    c = json.load(open(a.config)); tickers = a.tickers.split(",") if a.tickers else c["tickers"]
    os.makedirs(c["output_dir"], exist_ok=True); con = db_init(c["db_path"]); now = dt.datetime.now(dt.timezone.utc).isoformat()
    report = {}
    for t in [x.upper() for x in tickers]:
        raw, stats = [], {}
        for s in c["sources"]:
            try: got = SOURCES[s](t, c); stats[s] = len(got)
            except Exception as e: got = []; stats[s] = f"ERROR {e}"
            raw += [dict(i, source=s) for i in got]
        items = dedup(raw, c["title_similarity_threshold"]); new = 0
        for i in items:
            cur = con.execute("INSERT OR IGNORE INTO news(ticker,source,title,url,norm_url,publisher,published,snippet,fetched_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (t, i["source"], i["title"], i["url"], norm_url(i["url"]), i.get("publisher"), i.get("published"), i.get("snippet"), now)); new += cur.rowcount
        con.commit()
        summ = summarize(t, items)
        summ, removed = filter_links(summ, [i["url"] for i in items])
        if removed: print(f"  [linkcheck] {t} removed {len(removed)} link(s) not in fetched list")
        out = dict(ticker=t, generated_at=now, source_counts=stats, raw=len(raw), deduped=len(items), new_in_db=new, ai_summary=summ, removed_links=removed, items=items)
        json.dump(out, open(f"{c['output_dir']}/{t}.json", "w"), ensure_ascii=False, indent=2)
        md = [f"# {t} 新闻汇总", f"生成时间(UTC): {now}", f"来源计数: {stats} | 原始 {len(raw)} → 去重 {len(items)} | 新入库 {new}", ""]
        md += ["## AI 摘要", summ, ""] if summ else ["_未配置 GEMINI_API_KEY / ANTHROPIC_API_KEY / OPENAI_API_KEY，跳过摘要_", ""]
        md += ["## 标题列表"] + [f"- [{i['title']}]({i['url']}) — {i.get('publisher') or ''} · {i['source']}{(' +'+','.join(i['also_in'])) if i.get('also_in') else ''} · {i.get('published') or ''}" for i in items]
        open(f"{c['output_dir']}/{t}.md", "w").write("\n".join(md) + "\n")
        report[t] = dict(stats=stats, raw=len(raw), deduped=len(items), new=new); print(t, report[t])
    return report

if __name__ == "__main__": main()
