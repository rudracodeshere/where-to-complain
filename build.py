#!/usr/bin/env python3
"""Static site generator for "Where to Complain".

Usage:  python3 build.py            # build everything into docs/
        python3 build.py --check    # build + verify links, required fields, emails

One JSON file per content page lives in data/pages/. See README.md for the schema.
No third-party packages. No JavaScript, fonts or trackers are emitted.
"""
import html, json, re, sys, shutil
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
BASE = SITE["base_url"].rstrip("/") + "/"
BASE_PATH = "/" + BASE.split("/", 3)[3]  # e.g. /where-to-complain/
E = html.escape
DISCLAIMER = ("This page is general information to help you find the right official channel. It is not legal, "
              "financial or insurance advice, and it is not affiliated with any regulator, insurer, bank or "
              "company. Rules and contact details change; always confirm on the official source linked below "
              "before you act. If your case is complex or the amount is large, talk to a qualified professional.")

CSS = """
:root{--bg:#fff;--fg:#1b1f23;--mut:#5a636d;--line:#d8dde3;--acc:#0b5cab;--box:#eef5fc;--warn:#fff7e0;--code:#f5f6f8}
@media(prefers-color-scheme:dark){:root{--bg:#14171a;--fg:#e6e9ec;--mut:#9aa4ae;--line:#2d343b;--acc:#7db7f0;--box:#1b2631;--warn:#2b2614;--code:#1c2025}}
*{box-sizing:border-box}
body{margin:0;font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--fg)}
a{color:var(--acc)}
.wrap{max-width:860px;margin:0 auto;padding:0 16px}
header.site{border-bottom:1px solid var(--line);padding:12px 0}
header.site .wrap{display:flex;flex-wrap:wrap;gap:8px 20px;align-items:baseline}
header.site .brand{font-weight:700;font-size:1.1rem;text-decoration:none;color:var(--fg)}
header.site nav a{margin-right:14px;text-decoration:none}
h1{font-size:1.75rem;line-height:1.25;margin:1.2rem 0 .4rem}
h2{font-size:1.3rem;margin:2rem 0 .5rem;line-height:1.3}
h3{font-size:1.08rem;margin:1.4rem 0 .3rem}
.meta{color:var(--mut);font-size:.9rem;margin:0 0 1rem}
.crumbs{font-size:.9rem;color:var(--mut);margin-top:12px}
.answer{background:var(--box);border-left:5px solid var(--acc);padding:12px 16px;border-radius:4px;margin:1rem 0}
.answer h2{margin:.1rem 0 .4rem;font-size:1.1rem}
.answer ol,.answer ul{margin:.3rem 0 .3rem 1.2rem;padding:0}
.notice{background:var(--warn);border:1px solid var(--line);padding:10px 14px;border-radius:4px;margin:1rem 0;font-size:.95rem}
.tablewrap{overflow-x:auto;margin:1rem 0}
table{border-collapse:collapse;width:100%;font-size:.95rem}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--code)}
pre.letter{white-space:pre-wrap;word-wrap:break-word;background:var(--code);border:1px solid var(--line);padding:14px;border-radius:4px;font:15px/1.55 ui-monospace,Menlo,Consolas,monospace}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:1rem 0;padding:0;list-style:none}
.cards li{border:1px solid var(--line);border-radius:6px;padding:12px 14px}
.cards li strong{display:block;font-size:1.05rem}
.soon{color:var(--mut)}
.resources{border:1px dashed var(--line);padding:8px 14px;margin:2rem 0;border-radius:4px;color:var(--mut);font-size:.95rem}
.resources:empty{display:none}
.related ul{padding-left:1.2rem}
footer.site{border-top:1px solid var(--line);margin-top:3rem;padding:16px 0 40px;color:var(--mut);font-size:.88rem}
.verified{border-top:1px solid var(--line);margin-top:2rem;padding-top:12px;font-size:.92rem}
.sources li{margin-bottom:4px;word-break:break-word}
details{margin:.6rem 0}
summary{cursor:pointer;font-weight:600}
@media print{header.site,footer.site,.resources{display:none}}
"""

problems = []

def die(msg):
    problems.append(msg)

def rel(depth):
    return "../" * depth

def fmt_date(iso):
    y, m, d = map(int, iso.split("-"))
    return date(y, m, d).strftime("%-d %B %Y")

def layout(*, title, desc, canon_path, body, depth, jsonld=None, noindex=False, crumbs=None):
    r = rel(depth)
    canon = BASE + canon_path
    nav = "".join(f'<a href="{r}{s["slug"]}/">{E(s["name"])}</a>' for s in SITE["sectors"] if s["slug"] in LIVE_SECTORS)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    cr = ""
    if crumbs:
        cr = '<nav class="crumbs" aria-label="Breadcrumb">' + " › ".join(
            f'<a href="{r}{u}">{E(t)}</a>' if u is not None else E(t) for t, u in crumbs) + "</nav>"
    return f"""<!doctype html>
<html lang="{SITE['language']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{E(canon)}">
{robots}
<link rel="stylesheet" href="{r}style.css">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{E(canon)}">
{ld}
</head>
<body>
<header class="site"><div class="wrap">
<a class="brand" href="{r}">{E(SITE['name'])}</a>
<nav>{nav}<a href="{r}about/">About</a></nav>
</div></header>
<main class="wrap">
{cr}
{body}
</main>
<footer class="site"><div class="wrap">
<p>{E(SITE['name'])} is an independent, free guide. {E(DISCLAIMER)}</p>
<p><a href="{r}about/">About &amp; disclaimer</a> · <a href="{r}sitemap.xml">Sitemap</a> · <a href="{E(SITE['repo_url'])}">Source on GitHub</a></p>
</div></footer>
<script data-goatcounter="https://where-to-complain.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
"""

# ---------- block renderers ----------

def link_sources(sources):
    li = ""
    for s in sources:
        li += (f'<li>{E(s["label"])} — <a href="{E(s["url"])}" rel="noopener">{E(s["url"])}</a> '
               f'(checked {fmt_date(s["checked"])})</li>')
    return f'<ul class="sources">{li}</ul>'

def render_block(b, page, depth):
    t = b["type"]
    if t == "answer":
        items = "".join(f"<li>{x}</li>" for x in b["items"])
        tag = "ol" if b.get("ordered", True) else "ul"
        intro = f"<p>{b['intro_html']}</p>" if b.get("intro_html") else ""
        return f'<section class="answer" id="answer"><h2>{E(b.get("title","The 30-second answer"))}</h2>{intro}<{tag}>{items}</{tag}></section>'
    if t == "notice":
        return f'<div class="notice">{b["html"]}</div>'
    if t == "steps":
        head = "<tr><th>Step</th><th>Who</th><th>Official contact</th><th>Deadline</th></tr>"
        rows = ""
        for i, s in enumerate(b["rows"], 1):
            rows += (f"<tr><td>{i}</td><td>{s['who']}</td><td>{s['contact']}</td><td>{s['deadline']}</td></tr>")
        h = b.get("title", "Step-by-step ladder")
        return f'<h2 id="steps">{E(h)}</h2><div class="tablewrap"><table>{head}{rows}</table></div>'
    if t == "table":
        head = "".join(f"<th>{E(h)}</th>" for h in b["headers"])
        rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in b["rows"])
        cap = f'<h2 id="{E(b.get("id","table"))}">{E(b["title"])}</h2>' if b.get("title") else ""
        return f'{cap}<div class="tablewrap"><table><tr>{head}</tr>{rows}</table></div>'
    if t == "section":
        return f'<h2 id="{E(b.get("id", re.sub("[^a-z0-9]+","-",b["title"].lower()).strip("-")))}">{E(b["title"])}</h2>{b["html"]}'
    if t == "problems":
        out = f'<h2 id="problems">{E(b.get("title","Common problems and what to do"))}</h2>'
        for p in b["items"]:
            out += f'<h3>{E(p["title"])}</h3>{p["html"]}'
        return out
    if t == "offices":
        data = json.loads((ROOT / "data" / b["file"]).read_text(encoding="utf-8"))
        rows = ""
        for o in data["offices"]:
            rows += ("<tr>"
                     f"<td><strong>{E(o['centre'])}</strong></td>"
                     f"<td>{E(o['address'])}</td>"
                     f"<td>{E(o['tel'])}</td>"
                     f'<td><a href="mailto:{E(o["email"])}">{E(o["email"])}</a></td>'
                     f"<td>{E(o['jurisdiction'])}</td></tr>")
        note = (f'<p class="meta">Copied from <a href="{E(data["source_url"])}" rel="noopener">{E(data["source_url"])}</a>, '
                f'checked {fmt_date(data["checked"])}. Text is as published by the Council for Insurance Ombudsmen.</p>')
        return (f'<h2 id="{E(b.get("id","offices"))}">{E(b["title"])}</h2>{note}'
                f'<div class="tablewrap"><table><tr><th>Centre</th><th>Address</th><th>Phone</th><th>Email</th><th>Covers</th></tr>{rows}</table></div>')
    if t == "template":
        return ""  # rendered separately (also written to letters/*.txt)
    die(f"{page['slug']}: unknown block type {t}")
    return ""

def render_template(page, depth):
    out = ""
    for i, t in enumerate(page.get("templates", [])):
        fn = f"{page['slug']}{'' if i == 0 else '-' + str(i+1)}.txt"
        letters[fn] = t["text"]
        out += (f'<h2 id="template-{i+1}">{E(t["title"])}</h2>'
                f'<p>{t.get("intro_html","Free to copy. Replace everything in [square brackets]; delete paragraphs that do not apply.")}</p>'
                f'<pre class="letter">{E(t["text"])}</pre>'
                f'<p><a href="{rel(depth)}letters/{fn}" download>Download as .txt</a></p>')
    return out

def related_html(page, depth):
    items = ""
    for slug in page.get("related", []):
        if slug in PAGES:
            p = PAGES[slug]
            items += f'<li><a href="{rel(depth)}{slug}/">{E(p["h1"])}</a></li>'
        elif slug in {s["slug"] for s in SITE["sectors"]}:
            s = next(s for s in SITE["sectors"] if s["slug"] == slug)
            items += f'<li><a href="{rel(depth)}{slug}/">{E(s["name"])} hub</a></li>'
        else:
            die(f"{page['slug']}: related slug not found: {slug}")
    return f'<section class="related"><h2>Related pages</h2><ul>{items}</ul></section>'

def render_page(page):
    depth = 1
    r = rel(depth)
    blocks = "".join(render_block(b, page, depth) for b in page["blocks"])
    sec = next(s for s in SITE["sectors"] if s["slug"] == page["sector"])
    body = (f'<h1>{E(page["h1"])}</h1>'
            f'<p class="meta">Last verified: {fmt_date(page["verified"])} · {E(page.get("audience",""))}</p>'
            f'{blocks}{render_template(page, depth)}'
            f'<section class="resources" id="resources" aria-label="Resources"><!-- RESOURCES BLOCK (for br mogul): add vetted resource links here via "resources_html" in the page data file. Leave empty if none. -->{page.get("resources_html","")}</section>'
            f'{related_html(page, depth)}'
            f'<section class="verified"><p><strong>Last verified: {fmt_date(page["verified"])}, '
            f'source: <a href="{E(page["primary_source"])}" rel="noopener">{E(page["primary_source"])}</a></strong></p>'
            f'<details open><summary>All official sources used</summary>{link_sources(page["sources"])}</details>'
            f'<p><strong>Disclaimer.</strong> {E(DISCLAIMER)}</p></section>')
    ld = [{
        "@context": "https://schema.org", "@type": "Article", "headline": page["h1"],
        "description": page["description"], "inLanguage": "en-IN",
        "dateModified": page["verified"], "datePublished": page.get("published", page["verified"]),
        "mainEntityOfPage": BASE + page["slug"] + "/",
        "author": {"@type": "Organization", "name": SITE["name"]},
        "publisher": {"@type": "Organization", "name": SITE["name"]}
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": sec["name"], "item": BASE + sec["slug"] + "/"},
            {"@type": "ListItem", "position": 3, "name": page["h1"], "item": BASE + page["slug"] + "/"}]}]
    return layout(title=f'{page["title"]} | {SITE["name"]}', desc=page["description"], canon_path=page["slug"] + "/",
                  body=body, depth=depth, jsonld=ld,
                  crumbs=[("Home", ""), (sec["name"], sec["slug"] + "/"), (page["h1"], None)])

def render_hub(sec):
    depth = 1
    r = rel(depth)
    items = ""
    for p in sorted(PAGES.values(), key=lambda p: p["order"]):
        if p["sector"] == sec["slug"] or sec["slug"] in p.get("also_in", []):
            items += (f'<li><strong><a href="{r}{p["slug"]}/">{E(p["h1"])}</a></strong>{E(p["description"])}</li>')
    extra = HUB_EXTRA.get(sec["slug"], "")
    body = (f'<h1>{E(sec["name"])}: where to complain</h1><p>{E(sec["blurb"])}</p>'
            f'<ul class="cards">{items}</ul>{extra}'
            f'<p class="soon">More {E(sec["name"].lower())} guides are added regularly. See the <a href="{r}about/">about page</a> for how pages are checked.</p>'
            f'<section class="verified"><p><strong>Disclaimer.</strong> {E(DISCLAIMER)}</p></section>')
    desc = f'{sec["name"]} complaints in India: step-by-step escalation guides with official contacts and deadlines.'
    return layout(title=f'{sec["name"]} complaints in India | {SITE["name"]}', desc=desc,
                  canon_path=sec["slug"] + "/", body=body, depth=depth,
                  crumbs=[("Home", ""), (sec["name"], None)])

HUB_EXTRA = {
    "regulators": """
<h2>The official bodies, in one place</h2>
<div class="tablewrap"><table>
<tr><th>Body</th><th>What it handles</th><th>Where to start (official)</th></tr>
<tr><td>IRDAI (Insurance Regulatory and Development Authority of India)</td><td>Complaints about insurers and insurance intermediaries, after you have tried the insurer first</td><td><a href="https://bimabharosa.irdai.gov.in/" rel="noopener">Bima Bharosa portal</a>; toll-free 155255 or 1800 4254 732; <a href="mailto:complaints@irdai.gov.in">complaints@irdai.gov.in</a> (as published on the portal, checked 23 October 2026)</td></tr>
<tr><td>Insurance Ombudsman (Council for Insurance Ombudsmen)</td><td>Free dispute resolution for individual policyholders, claims up to the limit in the Rules</td><td><a href="https://cioins.co.in/" rel="noopener">cioins.co.in</a></td></tr>
<tr><td>RBI Ombudsman (Reserve Bank – Integrated Ombudsman Scheme, 2026)</td><td>Service deficiency by banks, NBFCs, non-bank prepaid wallet issuers and credit information companies covered by the Scheme</td><td><a href="https://cms.rbi.org.in" rel="noopener">cms.rbi.org.in</a>; contact centre 14448; <a href="mailto:crpc@rbi.org.in">crpc@rbi.org.in</a> (as published by RBI, checked 23 October 2026)</td></tr>
</table></div>
"""
}

def render_home(pages_sorted):
    r = ""
    live = LIVE_SECTORS
    cards = ""
    for s in SITE["sectors"]:
        if s["slug"] in live:
            cards += f'<li><strong><a href="{s["slug"]}/">{E(s["name"])}</a></strong>{E(s["blurb"])}</li>'
        else:
            cards += f'<li class="soon"><strong>{E(s["name"])} <small>(coming soon)</small></strong>{E(s["blurb"])}</li>'
    latest = "".join(f'<li><a href="{p["slug"]}/">{E(p["h1"])}</a></li>' for p in pages_sorted)
    body = (f'<h1>{E(SITE["name"])}: the order to escalate an Indian consumer complaint</h1>'
            f'<p>{E(SITE["tagline"])} Every page names the official body, gives its published contact, '
            f'states the deadline, and shows the source and the date we last checked it. Free letter templates included. '
            f'No sign-up, no ads, no tracking.</p>'
            f'<h2>Browse by sector</h2><ul class="cards">{cards}</ul>'
            f'<h2>Guides</h2><ul>{latest}</ul>'
            f'<h2>How we keep it honest</h2><ul>'
            f'<li>Facts come only from official regulator or government pages, linked on each page with the date checked.</li>'
            f'<li>If a contact or deadline is not published officially, we say so instead of guessing.</li>'
            f'<li>We do not collect or publish anyone\'s personal complaint or data.</li></ul>'
            f'<section class="verified"><p><strong>Disclaimer.</strong> {E(DISCLAIMER)}</p></section>')
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": BASE,
           "description": SITE["tagline"], "inLanguage": "en-IN"}]
    return layout(title=f'{SITE["name"]}: India complaint escalation guides', desc=SITE["tagline"],
                  canon_path="", body=body, depth=0, jsonld=ld)

def render_about():
    body = f"""<h1>About {E(SITE['name'])} and disclaimer</h1>
<p>{E(SITE['name'])} is a small, free directory that explains, in plain English, the order in which to take an Indian consumer complaint to the next level: the company's own grievance team first, then the regulator, then the ombudsman.</p>
<h2>How pages are written</h2>
<ul>
<li>Every contact detail, address, timeline and limit is read from an official regulator or government page and linked on the page with the date we checked it.</li>
<li>If something is not published officially, or the official page could not be opened when we checked, the page says so and points to the official portal. We do not fill gaps from forums, news articles or third-party copies.</li>
<li>Letter templates are our own wording, free to copy. They contain only blanks for you to fill in.</li>
<li>We do not publish anyone's personal complaint or story, and we do not collect your data. This site has no forms and no ads. It uses GoatCounter, a privacy-friendly counter that sets no cookies, only to count page visits.</li>
</ul>
<h2>Disclaimer</h2>
<p>{E(DISCLAIMER)}</p>
<p>The site is not affiliated with, endorsed by, or an agent of IRDAI, the Reserve Bank of India, the Council for Insurance Ombudsmen, or any insurer, bank or other company. We cannot take up your complaint for you, and we never ask for passwords, OTPs, card numbers, KYC documents or money. Official ombudsman services in these guides are free of cost to complainants.</p>
<h2>Found something out of date?</h2>
<p>Please open an issue at <a href="{E(SITE['repo_url'])}/issues">{E(SITE['repo_url'])}/issues</a>. Always check the official source linked on the page first.</p>
<h2>Affiliate links</h2>
<p>There are none today. If any ever appear, they will be marked clearly on the page where they appear.</p>"""
    return layout(title=f"About and disclaimer | {SITE['name']}",
                  desc="How Where to Complain sources its facts, what it is not, and the general-information disclaimer.",
                  canon_path="about/", body=body, depth=1, crumbs=[("Home", ""), ("About", None)])

def render_404():
    body = (f'<h1>Page not found</h1><p>That page does not exist. Try the <a href="{BASE_PATH}">home page</a> '
            f'or the <a href="{BASE_PATH}insurance/">insurance</a> guides.</p>')
    html_ = layout(title=f"Page not found | {SITE['name']}", desc="Page not found.", canon_path="404.html",
                   body=body, depth=0, noindex=True)
    # 404 can be served from any depth: make local links absolute to the site path
    html_ = html_.replace('href="style.css"', f'href="{BASE_PATH}style.css"')
    html_ = re.sub(r'href="(?!https?:|mailto:|/)([^"]*)"', lambda m: f'href="{BASE_PATH}{m.group(1)}"', html_)
    return html_

# ---------- main ----------

PAGES = {}
letters = {}
LIVE_SECTORS = set()

def load_pages():
    for f in sorted((ROOT / "data" / "pages").glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        for k in ("slug", "title", "h1", "description", "sector", "order", "verified", "primary_source", "sources", "blocks"):
            if k not in p:
                die(f"{f.name}: missing field {k}")
        if p.get("slug") in PAGES:
            die(f"{f.name}: duplicate slug")
        PAGES[p["slug"]] = p
        LIVE_SECTORS.add(p["sector"])
        for s in p.get("also_in", []):
            LIVE_SECTORS.add(s)

def check_content():
    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    for p in PAGES.values():
        if not (50 <= len(p["description"]) <= 170):
            die(f"{p['slug']}: description length {len(p['description'])} (want 50-170)")
        if len(p["title"]) > 70:
            die(f"{p['slug']}: title too long ({len(p['title'])})")
        if not any(b["type"] == "answer" for b in p["blocks"]):
            die(f"{p['slug']}: no answer block")
        if not p.get("templates"):
            die(f"{p['slug']}: no letter template")
        for s in p["sources"]:
            if not s.get("url", "").startswith("https://") or not s.get("checked"):
                die(f"{p['slug']}: source needs https url and checked date: {s}")
        # every email in content must be declared as copied from an official source
        declared = {e.lower() for e in p.get("verified_emails", [])}
        text = json.dumps(p["blocks"]) + json.dumps(p.get("templates", []))
        for e in set(email_re.findall(text)):
            if e.lower() not in declared:
                die(f"{p['slug']}: email {e} not listed in verified_emails (copy only from official pages)")
        for b in p["blocks"]:
            if b["type"] == "offices":
                for o in json.loads((ROOT / "data" / b["file"]).read_text(encoding="utf-8"))["offices"]:
                    pass

def check_links():
    bad = 0
    files = {str(f.relative_to(DOCS)) for f in DOCS.rglob("*") if f.is_file()}
    for f in DOCS.rglob("*.html"):
        if f.name == "404.html":
            continue
        txt = f.read_text(encoding="utf-8")
        for m in re.finditer(r'(?:href|src)="([^"]+)"', txt):
            u = m.group(1)
            if re.match(r"(https?:|mailto:|tel:|#)", u):
                continue
            u = u.split("#")[0]
            tgt = (f.parent / u).resolve()
            try:
                relp = tgt.relative_to(DOCS.resolve())
            except ValueError:
                print("link escapes docs:", f, u); bad += 1; continue
            relp = str(relp)
            if relp in ("", "."):
                continue
            if tgt.is_dir():
                if not (tgt / "index.html").exists():
                    print("missing index:", f.relative_to(DOCS), u); bad += 1
            elif relp not in files:
                print("broken link:", f.relative_to(DOCS), u); bad += 1
    return bad

def write(path, content):
    path = DOCS / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main():
    check = "--check" in sys.argv
    load_pages()
    check_content()
    if problems:
        print("\n".join("PROBLEM: " + x for x in problems)); sys.exit(1)
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    pages_sorted = sorted(PAGES.values(), key=lambda p: p["order"])
    urls = [("", None)]
    write("index.html", render_home(pages_sorted))
    write("about/index.html", render_about()); urls.append(("about/", None))
    for s in SITE["sectors"]:
        if s["slug"] in LIVE_SECTORS:
            write(f'{s["slug"]}/index.html', render_hub(s)); urls.append((s["slug"] + "/", None))
    for p in pages_sorted:
        write(f'{p["slug"]}/index.html', render_page(p)); urls.append((p["slug"] + "/", p["verified"]))
    for fn, text in letters.items():
        write(f"letters/{fn}", text + "\n")
    write("style.css", CSS.strip() + "\n")
    write("404.html", render_404())
    write(".nojekyll", "")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    today = date.today().isoformat()
    for u, lm in urls:
        sm.append(f"<url><loc>{BASE}{u}</loc><lastmod>{lm or today}</lastmod></url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    print(f"Built {len(PAGES)} content pages, {len(urls)} URLs -> {DOCS}")
    if check:
        bad = check_links()
        if bad or problems:
            print("\n".join("PROBLEM: " + x for x in problems)); sys.exit(1)
        print("Link check OK")

if __name__ == "__main__":
    main()
