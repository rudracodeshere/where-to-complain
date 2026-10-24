#!/usr/bin/env python3
"""Read-only page checker for Where to Complain. Stdlib only, no network unless --external or --live.

    python3 tools/check_pages.py                 # check docs/ as built
    python3 tools/check_pages.py --live          # mirror nothing; fetch the live pages listed in docs/sitemap.xml
    python3 tools/check_pages.py --external      # also HEAD/GET every outbound link (slow, polite: 1 req/sec)
    python3 tools/check_pages.py --json          # machine-readable output

Exit code 1 if any FAIL. WARN never fails the run.

Rules come from BUILD-PLAYBOOK.md (claude-seo, web-quality-skills seo/a11y, seo-audit-skill,
claude-blog blog-seo-check, geo-seo-claude citability, humanizer). Not wired into build.py.
"""
import argparse, json, re, sys, time, urllib.request, urllib.error, xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BASE = "https://rudracodeshere.github.io/where-to-complain/"
UA = "Mozilla/5.0 (where-to-complain page checker)"

AI_WORDS = ["additionally", "align with", "bolstered", "crucial", "deep dive", "delve", "enduring", "enhance",
            "garner", "interplay", "intricate", "meticulous", "pivotal", "showcase", "tapestry", "testament",
            "underscore", "vibrant", "seamless", "navigate the", "landscape", "in today's", "rest assured",
            "it's important to note", "it is important to note", "game-changer", "unlock"]
HUB_SLUGS = {"", "about", "insurance", "banks", "regulators", "credit-cards", "telecom", "404.html"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""; self.meta = {}; self.links = []; self.canon = None; self.lang = None
        self.headings = []; self.jsonld = []; self.imgs = []; self.text = []; self.icons = 0
        self._in = None; self._buf = ""; self._skip = 0; self.ids = []; self.has_main = False
        self.anchors = []  # (href, text)
        self._a = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.append(a["id"])
        if tag == "html": self.lang = a.get("lang")
        elif tag == "main": self.has_main = True
        elif tag == "title": self._in, self._buf = "title", ""
        elif tag == "meta":
            k = a.get("name") or a.get("property")
            if k: self.meta[k.lower()] = a.get("content", "")
        elif tag == "link":
            rel = (a.get("rel") or "").lower()
            if rel == "canonical": self.canon = a.get("href")
            if "icon" in rel: self.icons += 1
            if a.get("href"): self.links.append(("link", a["href"]))
        elif tag == "a":
            self.links.append(("a", a.get("href")))
            self._a = [a.get("href"), ""]
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"): self._in, self._buf = tag, ""
        elif tag == "script":
            if a.get("type") == "application/ld+json": self._in, self._buf = "ld", ""
            else: self._skip += 1
            if a.get("src"): self.links.append(("script", a["src"]))
        elif tag == "style": self._skip += 1
        elif tag == "img": self.imgs.append(a)

    def handle_endtag(self, tag):
        if tag == "title" and self._in == "title": self.title = self._buf.strip(); self._in = None
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._in == tag:
            self.headings.append((tag, re.sub(r"\s+", " ", self._buf).strip())); self._in = None
        elif tag == "script":
            if self._in == "ld": self.jsonld.append(self._buf); self._in = None
            elif self._skip: self._skip -= 1
        elif tag == "style" and self._skip: self._skip -= 1
        elif tag == "a" and self._a is not None:
            self.anchors.append((self._a[0], self._a[1].strip())); self._a = None

    def handle_data(self, d):
        if self._in: self._buf += d
        if self._a is not None: self._a[1] += d
        if not self._skip and self._in != "ld": self.text.append(d)


def load_local():
    pages = {}
    for f in sorted(DOCS.rglob("*.html")):
        rel = f.relative_to(DOCS).as_posix()
        if rel.startswith("google") : continue
        url = BASE + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
        pages[url] = f.read_text("utf-8")
    return pages


def fetch(url, method="GET"):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode("utf-8", "ignore") if method == "GET" else ""
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return f"ERR {type(e).__name__}", ""


def load_live():
    st, sm = fetch(BASE + "sitemap.xml")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    pages = {}
    for u in locs:
        st, body = fetch(u)
        pages[u] = body if st == 200 else ""
        time.sleep(0.5)
    return pages


def check(pages, external=False, local=True):
    out = []  # (level, url, rule, detail)
    add = lambda lvl, u, r, d="": out.append((lvl, u.replace(BASE, "/") or "/", r, d))
    parsed = {u: Page() for u in pages}
    for u, h in pages.items(): parsed[u].feed(h)
    inbound = {u: 0 for u in pages}
    titles, descs = {}, {}
    sitemap = set()
    if local and (DOCS / "sitemap.xml").exists():
        sitemap = set(re.findall(r"<loc>([^<]+)</loc>", (DOCS / "sitemap.xml").read_text()))
    llms = (DOCS / "llms.txt").read_text() if local and (DOCS / "llms.txt").exists() else ""
    ext_links = set()

    for u, p in parsed.items():
        slug = u.replace(BASE, "").strip("/")
        is404 = slug == "404.html"
        is_guide = slug not in HUB_SLUGS
        text = re.sub(r"\s+", " ", " ".join(p.text))
        words = len(text.split())
        # head basics (web-quality best-practices / seo)
        if not p.lang: add("FAIL", u, "html-lang missing")
        if "viewport" not in p.meta: add("FAIL", u, "viewport meta missing")
        if not p.icons: add("WARN", u, "no <link rel=icon>", "browser requests /favicon.ico at the user-site root, which 404s (Lighthouse console error)")
        t = p.title
        if not t: add("FAIL", u, "title missing")
        else:
            titles.setdefault(t, []).append(u)
            if len(t) > 65: add("WARN", u, "title long", f"{len(t)} chars: {t}")
            if len(t) < 25 and not is404: add("WARN", u, "title short", f"{len(t)} chars")
        d = p.meta.get("description", "")
        if not d: add("FAIL", u, "meta description missing")
        else:
            descs.setdefault(d, []).append(u)
            if not is404 and not (110 <= len(d) <= 165): add("WARN", u, "description length", f"{len(d)} chars")
        if is404:
            if p.canon: add("WARN", u, "404 page has a canonical", "drop canonical, keep noindex")
            if "noindex" not in p.meta.get("robots", ""): add("WARN", u, "404 page not noindex")
        else:
            if p.canon != u: add("FAIL", u, "canonical mismatch", f"{p.canon}")
            for k in ("og:title", "og:description", "og:url"):
                if k not in p.meta: add("WARN", u, f"{k} missing")
            if "og:image" not in p.meta: add("WARN", u, "og:image missing", "no share preview on WhatsApp/X")
        # headings
        h1 = [h for h in p.headings if h[0] == "h1"]
        if len(h1) != 1: add("FAIL", u, "h1 count", str(len(h1)))
        prev = 1
        for tag, txt in p.headings:
            lvl = int(tag[1])
            if lvl > prev + 1: add("WARN", u, "heading level skipped", f"{tag}: {txt[:60]}")
            prev = lvl
        if not p.has_main: add("FAIL", u, "no <main> landmark")
        dup_ids = {i for i in p.ids if p.ids.count(i) > 1}
        if dup_ids: add("FAIL", u, "duplicate ids", ", ".join(sorted(dup_ids)))
        for img in p.imgs:
            if "alt" not in img: add("FAIL", u, "img without alt", img.get("src", ""))
            if not (img.get("width") and img.get("height")): add("WARN", u, "img without width/height (CLS)", img.get("src", ""))
        # structured data (claude-seo seo-schema)
        types = []
        for raw in p.jsonld:
            try:
                data = json.loads(raw)
            except Exception as e:
                add("FAIL", u, "JSON-LD does not parse", str(e)[:80]); continue
            items = data if isinstance(data, list) else data.get("@graph", [data])
            for it in items:
                ty = it.get("@type"); types.append(ty)
                if ty in ("HowTo", "SpecialAnnouncement", "ClaimReview"): add("WARN", u, f"deprecated schema {ty}")
                if ty == "Article":
                    for k in ("headline", "datePublished", "dateModified", "author", "publisher"):
                        if k not in it: add("WARN", u, f"Article.{k} missing")
                    if len(it.get("headline", "")) > 110: add("WARN", u, "Article.headline > 110 chars")
                if ty == "FAQPage":
                    vis = text.lower()
                    for q in it.get("mainEntity", []):
                        if q.get("name", "").lower()[:40] not in vis: add("FAIL", u, "FAQ schema question not visible on page", q.get("name", "")[:60])
        if not is404 and slug and "BreadcrumbList" not in types: add("WARN", u, "no BreadcrumbList")
        if isinstance(p.jsonld, list) and p.jsonld and all(r.strip().startswith("[") for r in p.jsonld):
            add("INFO", u, "JSON-LD is a top-level array", "valid for Google; some audit tools (seomator) miss @type. @graph is safer")
        # YMYL trust + freshness (eeat, claude-blog decay, geo)
        if is_guide and not is404:
            if not re.search(r"last checked", text, re.I): add("FAIL", u, "no 'Last checked' date")
            if not re.search(r"not (legal|financial)[^.]{0,40}advice", text, re.I): add("FAIL", u, "no not-legal-advice disclaimer")
            gov = [h for k, h in p.links if h and re.search(r"\.(gov|nic)\.in|rbi\.org\.in|irdai|cioins|consumerhelpline|edaakhil|pgportal", h)]
            if len(gov) < 2: add("FAIL", u, "fewer than 2 official-source links", str(len(gov)))
            qh = [h for h in p.headings if h[0] == "h2" and h[1].endswith("?")]
            if not qh: add("WARN", u, "no question-style H2 (GEO answer block)")
            if words < 600: add("WARN", u, "thin guide", f"{words} words")
        # copy rules (humanizer)
        dashes = text.count("\u2014") + text.count("\u2013")
        if dashes: add("WARN", u, "em/en dashes in copy", f"{dashes} (humanizer rule 8)")
        low = text.lower()
        hits = sorted({w for w in AI_WORDS if re.search(r"\b" + re.escape(w) + r"\b", low)})
        if hits: add("WARN", u, "AI-tell words", ", ".join(hits))
        if re.search(r"official source linked below", low) and low.rfind("official source linked below") > low.rfind("all official sources used"):
            add("WARN", u, "disclaimer says 'official source linked below' but nothing official follows it")
        # links
        for href, atext in p.anchors:
            if href is None: continue
            if href == "": add("WARN", u, "empty href", f"anchor '{atext[:30]}'")
            if atext.lower() in ("click here", "here", "read more", "this", "link"): add("WARN", u, "vague anchor text", atext)
        for kind, href in p.links:
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")): continue
            absu = urljoin(u, href).split("#")[0]
            if absu.startswith(BASE):
                key = absu if absu.endswith("/") or "." in absu.rsplit("/", 1)[-1] else absu + "/"
                if key in inbound and key != u and kind == "a": inbound[key] += 1
                if local:
                    path = DOCS / absu[len(BASE):]
                    if absu.endswith("/"): path = path / "index.html"
                    if not path.exists(): add("FAIL", u, "broken internal link", href)
            elif absu.startswith("http"):
                if absu.startswith("http://"): add("WARN", u, "non-HTTPS link", absu)
                ext_links.add((absu, u))
        if sitemap and not is404 and u not in sitemap: add("FAIL", u, "page not in sitemap.xml")
        if llms and is_guide and not is404 and u not in llms: add("WARN", u, "guide not listed in llms.txt")

    for t, us in titles.items():
        if len(us) > 1: add("FAIL", us[0], "duplicate title", f"{len(us)} pages: {t}")
    for d, us in descs.items():
        if len(us) > 1: add("FAIL", us[0], "duplicate description", f"{len(us)} pages")
    for u, n in inbound.items():
        slug = u.replace(BASE, "").strip("/")
        if slug and slug != "404.html":
            if n == 0: add("FAIL", u, "orphan page (no inbound internal links)")
            elif slug not in HUB_SLUGS and n < 3: add("WARN", u, "weak inbound links", f"{n} pages link here (target 3+)")
    for s in sitemap:
        if s not in pages: add("FAIL", s, "sitemap URL has no built page")

    if external:
        seen = {}
        for absu, src in sorted(ext_links):
            if absu not in seen:
                st, _ = fetch(absu, "HEAD")
                if st in (403, 405, 501) or isinstance(st, str): st, _ = fetch(absu, "GET")
                seen[absu] = st; time.sleep(1)
            st = seen[absu]
            if st != 200 and not (isinstance(st, int) and 300 <= st < 400):
                add("WARN" if st in (403, 429) or isinstance(st, str) or st >= 500 else "FAIL", src, "outbound link not 200", f"{st} {absu}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true"); ap.add_argument("--external", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    pages = load_live() if a.live else load_local()
    res = check(pages, external=a.external, local=not a.live)
    if a.json:
        print(json.dumps([dict(level=l, page=p, rule=r, detail=d) for l, p, r, d in res], indent=1))
    else:
        order = {"FAIL": 0, "WARN": 1, "INFO": 2}
        for l, p, r, d in sorted(res, key=lambda x: (order[x[0]], x[2], x[1])):
            print(f"{l:4} {p:45} {r}" + (f"  [{d}]" if d else ""))
        c = {k: sum(1 for x in res if x[0] == k) for k in order}
        print(f"\n{len(pages)} pages: {c['FAIL']} FAIL, {c['WARN']} WARN, {c['INFO']} INFO")
    sys.exit(1 if any(x[0] == "FAIL" for x in res) else 0)


if __name__ == "__main__":
    main()
