#!/usr/bin/env python3
"""Static site generator for "Where to Complain".

Usage:  python3 build.py            # build everything into docs/
        python3 build.py --check    # build + verify links, required fields, emails, and the
                                    # SEO/schema/copy rules in DESIGN.md that a machine can check

One JSON file per content page lives in data/pages/. See README.md for the schema.
No third-party packages. No web fonts. JavaScript only for tools (assets/*.js, copied to docs/) plus the GoatCounter counter.
CSS lives in style.css (source) and is copied to docs/style.css. Design rules: DESIGN.md.
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

CSS = (ROOT / "style.css").read_text(encoding="utf-8")

problems = []

def die(msg):
    problems.append(msg)

def rel(depth):
    return "../" * depth

def fmt_date(iso):
    y, m, d = map(int, iso.split("-"))
    return date(y, m, d).strftime("%-d %B %Y")

def layout(*, title, desc, canon_path, body, depth, jsonld=None, noindex=False, crumbs=None, current=None):
    r = rel(depth)
    canon = BASE + canon_path
    cur = lambda slug: ' aria-current="page"' if slug == current else ""
    nav = "".join(f'<a href="{r}{s["slug"]}/"{cur(s["slug"])}>{E(s["name"])}</a>' for s in SITE["sectors"] if s["slug"] in LIVE_SECTORS)
    jsonld = list(jsonld or [])
    if crumbs:  # BreadcrumbList always mirrors the visible breadcrumb trail
        jsonld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": t, "item": BASE + (u if u is not None else canon_path)}
            for i, (t, u) in enumerate(crumbs)]})
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    cr = ""
    if crumbs:
        cr = '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
            f'<li><a href="{r}{u}">{E(t)}</a></li>' if u is not None else f'<li aria-current="page">{E(t)}</li>'
            for t, u in crumbs) + "</ol></nav>"
    return f"""<!doctype html>
<html lang="{SITE['language']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{E(canon)}">
{robots}
<link rel="icon" href="data:,">
<link rel="stylesheet" href="{r}style.css">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{E(SITE['name'])}">
<meta property="og:url" content="{E(canon)}">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap">
<a class="brand" href="{r}">{E(SITE['name'])}</a>
<nav aria-label="Main">{nav}<a href="{r}about/"{cur("about")}>About</a></nav>
</div></header>
<main class="wrap" id="main">
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
        rows = ""
        for i, s in enumerate(b["rows"], 1):
            rows += (f'<li><p class="rung-who">{s["who"]}</p><dl>'
                     f'<dt>Official contact</dt><dd>{s["contact"]}</dd>'
                     f'<dt>Deadline</dt><dd class="deadline">{s["deadline"]}</dd></dl></li>')
        h = b.get("title", "Step-by-step ladder")
        return f'<h2 id="steps">{E(h)}</h2><ol class="ladder">{rows}</ol>'
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
    if t == "calculator":
        return CALCULATOR_HTML.replace("{r}", rel(depth))
    if t == "template":
        return ""  # rendered separately (also written to letters/*.txt)
    die(f"{page['slug']}: unknown block type {t}")
    return ""

CALCULATOR_HTML = """<noscript><p class="notice">This calculator needs JavaScript. Every rule it uses is listed below with its official source, so you can count the dates yourself.</p></noscript>
<form id="calc" class="calc" novalidate>
<fieldset><legend>Who is the complaint against?</legend>
<label class="choice"><input type="radio" name="type" value="insurance" checked> An insurance company</label>
<label class="choice"><input type="radio" name="type" value="bank"> A bank, NBFC, wallet issuer or credit information company (RBI Ombudsman)</label>
</fieldset>
<label for="complained">Date you sent your written complaint to the company</label>
<input type="date" id="complained" name="complained" required aria-describedby="complained-hint">
<p class="hint" id="complained-hint">The first written complaint, by email, online form or letter. Keep its reference number.</p>
<fieldset><legend>What has the company done so far?</legend>
<label class="choice"><input type="radio" name="reply" value="none" checked> No reply yet</label>
<label class="choice"><input type="radio" name="reply" value="rejected"> It rejected my complaint</label>
<label class="choice"><input type="radio" name="reply" value="unsatisfied"> It replied, but I am not satisfied</label>
</fieldset>
<div id="reply-date-wrap">
<label for="replied">Date you received its reply (final or last reply)</label>
<input type="date" id="replied" name="replied">
</div>
<p><button type="submit">Show my dates</button></p>
</form>
<div id="calc-result" class="calc-result" tabindex="-1" aria-live="polite"></div>
<script src="{r}calculator.js" defer></script>"""

def render_template(page, depth):
    out = ""
    for i, t in enumerate(page.get("templates", [])):
        fn = f"{page['slug']}{'' if i == 0 else '-' + str(i+1)}.txt"
        letters[fn] = t["text"]
        out += (f'<h2 id="template-{i+1}">{E(t["title"])}</h2>'
                f'<p>{t.get("intro_html","Free to copy. Replace everything in [square brackets]; delete paragraphs that do not apply.")}</p>'
                f'<div class="letter-box"><pre class="letter">{E(t["text"])}</pre>'
                f'<p class="letter-actions"><a href="{rel(depth)}letters/{fn}" download>Download as .txt</a></p></div>')
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

def faq_html(page):
    if not page.get("faq"):
        return ""
    items = "".join(f'<details><summary>{E(f["q"])}</summary><p>{E(f["a"])}</p></details>' for f in page["faq"])
    return f'<section class="faq" id="faq"><h2>Quick answers</h2>{items}</section>'

def render_page(page):
    depth = 1
    r = rel(depth)
    rendered = [render_block(b, page, depth) for b in page["blocks"]]
    q = page.get("question")
    if q:  # question-style H2 with a self-contained answer, placed after the first block
        rendered.insert(1, f'<section class="qa" id="question"><h2>{E(q["q"])}</h2><p>{E(q["a"])}</p></section>')
    blocks = "".join(rendered)
    sec = next(s for s in SITE["sectors"] if s["slug"] == page["sector"])
    lede = f'<p class="lede">{E(page["direct_answer"])}</p>' if page.get("direct_answer") else ""
    body = (f'<h1>{E(page["h1"])}</h1>'
            f'<p class="meta"><span class="badge">Last checked: {fmt_date(page["verified"])}</span></p>'
            f'<p class="audience">{E(page.get("audience",""))}</p>'
            f'{lede}{blocks}{render_template(page, depth)}'
            f'<section class="resources" id="resources" aria-label="Resources"><!-- RESOURCES BLOCK (for br mogul): add vetted resource links here via "resources_html" in the page data file. Leave empty if none. -->{page.get("resources_html","")}</section>'
            f'{faq_html(page)}{related_html(page, depth)}'
            f'<section class="verified"><p><strong>Last checked: {fmt_date(page["verified"])}, '
            f'source: <a href="{E(page["primary_source"])}" rel="noopener">{E(page["primary_source"])}</a></strong></p>'
            f'<details open><summary>All official sources used</summary>{link_sources(page["sources"])}</details>'
            f'<p><strong>Disclaimer.</strong> {E(DISCLAIMER)}</p></section>')
    ld = [{
        "@context": "https://schema.org", "@type": "Article", "headline": page["h1"],
        "description": page["description"], "inLanguage": "en-IN",
        "dateModified": page["verified"], "datePublished": page.get("published", page["verified"]),
        "mainEntityOfPage": BASE + page["slug"] + "/",
        "author": {"@type": "Organization", "name": SITE["name"], "url": BASE + "about/"},
        "publisher": {"@type": "Organization", "name": SITE["name"], "url": BASE + "about/"}
    }]
    if page.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in page["faq"]]})
    return layout(title=page["title"], desc=page["description"], canon_path=page["slug"] + "/",
                  body=body, depth=depth, jsonld=ld, current=page["sector"],
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
    desc = HUB_DESC.get(sec["slug"], f'{sec["name"]} complaints in India: step-by-step escalation guides with official contacts and deadlines.')
    return layout(title=f'{sec["name"]} complaints in India | {SITE["name"]}', desc=desc,
                  canon_path=sec["slug"] + "/", body=body, depth=depth, current=sec["slug"],
                  crumbs=[("Home", ""), (sec["name"], None)])

HUB_DESC = {
    "insurance": "Insurance complaints in India: claim rejected, no reply or a Star Health dispute? Step-by-step escalation to the insurer, IRDAI and the Insurance Ombudsman.",
    "banks": "Bank, NBFC or wallet complaints in India: how to complain to your lender first, then to the RBI Ombudsman on the CMS portal, with the 30 and 90-day deadlines.",
    "regulators": "Indian complaint regulators in one place: IRDAI Bima Bharosa, the Insurance Ombudsman and the RBI Ombudsman, with official contacts and step-by-step guides.",
}

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

HOME_DESC = "Plain-English escalation ladders for Indian consumer complaints: who to write to, in what order, by when. Insurance and RBI banking guides with official sources."

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
    return layout(title=f'{SITE["name"]}: India complaint escalation guides', desc=HOME_DESC,
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
                  desc="How Where to Complain checks facts: official regulator sources only, a dated check on every page, no guessing. What the site is not, plus the disclaimer.",
                  canon_path="about/", body=body, depth=1, current="about", crumbs=[("Home", ""), ("About", None)])

def render_404():
    body = (f'<h1>Page not found</h1><p>That page does not exist. Try the <a href="{BASE_PATH}">home page</a> '
            f'or the <a href="{BASE_PATH}insurance/">insurance</a> guides.</p>')
    html_ = layout(title=f"Page not found | {SITE['name']}", desc="Page not found.", canon_path="404.html",
                   body=body, depth=0, noindex=True)
    # 404 can be served from any depth: make local links absolute to the site path
    html_ = html_.replace('href="style.css"', f'href="{BASE_PATH}style.css"')
    html_ = re.sub(r'href="(?!https?:|mailto:|data:|/)([^"]*)"', lambda m: f'href="{BASE_PATH}{m.group(1)}"', html_)
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
        if len(p["title"]) > 60:
            die(f"{p['slug']}: title too long ({len(p['title'])}, want 60 or less, main query first)")
        if not p.get("direct_answer"):
            die(f"{p['slug']}: no direct_answer (2-sentence answer shown under the H1)")
        elif len(p["direct_answer"]) > 320:
            die(f"{p['slug']}: direct_answer too long ({len(p['direct_answer'])}, want 320 or less)")
        if not (3 <= len(p.get("faq", [])) <= 5):
            die(f"{p['slug']}: faq needs 3 to 5 items, each from facts already on the page")
        q = p.get("question")
        if not q:
            die(f"{p['slug']}: no question (a question-style H2 with a 40-60 word answer from facts on the page)")
        else:
            if not q["q"].endswith("?"):
                die(f"{p['slug']}: question heading must end with '?': {q['q']}")
            if not (35 <= len(q["a"].split()) <= 65):
                die(f"{p['slug']}: question answer is {len(q['a'].split())} words (want about 40-60)")
        copy_lint(p)
        if not any(b["type"] == "answer" for b in p["blocks"]):
            die(f"{p['slug']}: no answer block")
        if not p.get("templates") and p.get("kind") != "tool":
            die(f"{p['slug']}: no letter template")
        for s in p["sources"]:
            if not s.get("url", "").startswith("https://") or not s.get("checked"):
                die(f"{p['slug']}: source needs https url and checked date: {s}")
        # every email in content must be declared as copied from an official source
        declared = {e.lower() for e in p.get("verified_emails", [])}
        text = (json.dumps(p["blocks"]) + json.dumps(p.get("templates", [])) + json.dumps(p.get("faq", []))
                + p.get("direct_answer", "") + json.dumps(p.get("question", {})))
        for e in set(email_re.findall(text)):
            if e.lower() not in declared:
                die(f"{p['slug']}: email {e} not listed in verified_emails (copy only from official pages)")
        for b in p["blocks"]:
            if b["type"] == "offices":
                for o in json.loads((ROOT / "data" / b["file"]).read_text(encoding="utf-8"))["offices"]:
                    pass

# Copy-editing rules (DESIGN.md "Copy-editing pass") that a machine can catch, applied to
# the short copy that search engines and answer engines quote: title, H1, description,
# direct answer, question answer and FAQ.
FILLER = re.compile(r"\b(very|really|basically|actually|simply|just|seamless(ly)?|robust|leverage|utili[sz]e|"
                    r"in order to|navigate the|delve|game[- ]changer|it'?s important to note|hassle[- ]free)\b", re.I)

def copy_lint(p):
    short = [("title", p["title"]), ("h1", p["h1"]), ("description", p["description"]),
             ("direct_answer", p.get("direct_answer", ""))]
    short += [("question", p.get("question", {}).get("a", ""))]
    short += [(f"faq {i+1}", f["q"] + " " + f["a"]) for i, f in enumerate(p.get("faq", []))]
    for name, t in short:
        m = FILLER.search(t)
        if m:
            die(f"{p['slug']}: {name} uses filler word '{m.group(0)}' (copy-editing pass)")
        if "\u2014" in t:
            die(f"{p['slug']}: {name} uses an em dash; use a colon, comma or full stop")
        for sent in re.split(r"(?<=[.?!])\s+", t):
            if len(sent.split()) > 40:
                die(f"{p['slug']}: {name} has a {len(sent.split())}-word sentence (split it; aim for 25 or fewer)")

class _Page:
    """What --check needs from one built HTML file."""
    def __init__(self, path):
        self.path = path
        self.rel = str(path.relative_to(DOCS))
        self.url = BASE + (self.rel[:-len("index.html")] if self.rel.endswith("index.html") else self.rel)
        self.html = path.read_text(encoding="utf-8")
        h = self.html
        g = lambda rx: (re.search(rx, h, re.S) or [None, None])[1]
        self.title = html.unescape(g(r"<title>(.*?)</title>") or "")
        self.desc = html.unescape(g(r'<meta name="description" content="([^"]*)"') or "")
        self.canon = g(r'<link rel="canonical" href="([^"]*)"')
        self.noindex = 'name="robots" content="noindex"' in h
        self.ld = []
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                d = json.loads(m.group(1))
            except ValueError as e:
                die(f"{self.rel}: JSON-LD does not parse: {e}"); continue
            self.ld += d if isinstance(d, list) else [d]
        body = h.split("<body>", 1)[-1]
        self.visible = html.unescape(re.sub(r"<script.*?</script>|<[^>]+>", " ", body, flags=re.S))
        self.visible = re.sub(r"\s+", " ", self.visible)
        self.headings = [(int(m.group(1)), html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip())
                         for m in re.finditer(r"<h([1-6])[^>]*>(.*?)</h\1>", h, re.S)]
        main = h.split('<main', 1)[-1].split('</main>', 1)[0]
        self.links = set()
        for m in re.finditer(r'href="([^"#]*)(?:#[^"]*)?"', main):
            u = m.group(1)
            if u and not re.match(r"(https?:|mailto:|tel:|data:)", u):
                t = (path.parent / u).resolve()
                if t.is_dir():
                    t = t / "index.html"
                self.links.add(str(t))

def check_built():
    """Rules from DESIGN.md (seo-audit, schema, site-architecture, ai-seo) checked on the built HTML."""
    pages = [_Page(f) for f in sorted(DOCS.rglob("*.html")) if f.name != "404.html" and not f.name.startswith("google")]
    by_title, by_desc, inbound = {}, {}, {str(p.path.resolve()): 0 for p in pages}
    sitemap = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    guide_urls = {BASE + s + "/" for s in PAGES}
    for p in pages:
        by_title.setdefault(p.title, []).append(p.rel)
        by_desc.setdefault(p.desc, []).append(p.rel)
        for t in p.links:
            if t in inbound and t != str(p.path.resolve()):
                inbound[t] += 1
        if p.canon != p.url:
            die(f"{p.rel}: canonical {p.canon} should be {p.url}")
        if not p.noindex and f"<loc>{p.url}</loc>" not in sitemap:
            die(f"{p.rel}: indexable page missing from sitemap.xml")
        if len(p.title) > 60:
            die(f"{p.rel}: title is {len(p.title)} characters (want 60 or less)")
        if not (120 <= len(p.desc) <= 170):
            die(f"{p.rel}: meta description is {len(p.desc)} characters (want about 150-160)")
        levels = [l for l, _ in p.headings]
        if levels.count(1) != 1:
            die(f"{p.rel}: has {levels.count(1)} H1 tags (want exactly 1)")
        for a, b in zip(levels, levels[1:]):
            if b > a + 1:
                die(f"{p.rel}: heading jumps from H{a} to H{b}"); break
        types = {d.get("@type") for d in p.ld}
        for d in p.ld:
            if d.get("@context") != "https://schema.org":
                die(f"{p.rel}: JSON-LD {d.get('@type')} missing @context https://schema.org")
        if p.url != BASE and "BreadcrumbList" not in types:
            die(f"{p.rel}: no BreadcrumbList JSON-LD")
        for d in p.ld:
            if d.get("@type") == "BreadcrumbList":
                items = d.get("itemListElement", [])
                if [i.get("position") for i in items] != list(range(1, len(items) + 1)):
                    die(f"{p.rel}: BreadcrumbList positions must run 1..n")
                for i in items:
                    if not (i.get("name") and str(i.get("item", "")).startswith(BASE)):
                        die(f"{p.rel}: BreadcrumbList item needs name and absolute item URL: {i}")
                    elif i["name"] not in p.visible:
                        die(f"{p.rel}: breadcrumb '{i['name']}' is not visible on the page")
                if items and items[-1].get("item") != p.url:
                    die(f"{p.rel}: last breadcrumb should be the page itself")
            if d.get("@type") == "FAQPage":
                qs = d.get("mainEntity", [])
                if not qs:
                    die(f"{p.rel}: FAQPage has no mainEntity")
                for q in qs:
                    a = (q.get("acceptedAnswer") or {})
                    if q.get("@type") != "Question" or not q.get("name") or a.get("@type") != "Answer" or not a.get("text"):
                        die(f"{p.rel}: FAQPage item needs Question name + acceptedAnswer Answer text: {q}")
                    elif q["name"] not in p.visible or re.sub(r"\s+", " ", a["text"]) not in p.visible:
                        die(f"{p.rel}: FAQ answer must be visible on the page: {q['name']}")
            if d.get("@type") == "Article":
                for k in ("headline", "dateModified", "datePublished", "author", "publisher", "mainEntityOfPage"):
                    if not d.get(k):
                        die(f"{p.rel}: Article missing {k}")
        if p.url in guide_urls:
            slug = p.url[len(BASE):-1]
            pg = PAGES[slug]
            if "Article" not in types or "FAQPage" not in types:
                die(f"{p.rel}: guide needs Article and FAQPage JSON-LD")
            art = next((d for d in p.ld if d.get("@type") == "Article"), {})
            if art.get("dateModified") != pg["verified"]:
                die(f"{p.rel}: Article dateModified must equal the Last checked date")
            top = p.html.split("<h1", 1)[-1].split('class="lede"', 1)[0]
            if f"Last checked: {fmt_date(pg['verified'])}" not in top:
                die(f"{p.rel}: 'Last checked: <date>' must sit between the H1 and the direct answer")
            if not any(l == 2 and t.endswith("?") for l, t in p.headings):
                die(f"{p.rel}: guide needs a question-style H2 (ending in '?')")
            if p.links.isdisjoint({str((DOCS / s / "index.html").resolve()) for s in [pg["sector"]] + pg.get("also_in", [])}):
                die(f"{p.rel}: guide must link up to its hub (hub-and-spoke)")
    for t, fs in by_title.items():
        if len(fs) > 1:
            die(f"duplicate <title> '{t}': {fs}")
    for t, fs in by_desc.items():
        if len(fs) > 1:
            die(f"duplicate meta description: {fs}")
    for t, n in inbound.items():
        if n == 0 and not t.endswith(str(DOCS.resolve() / "index.html")):
            die(f"orphan page (no inbound link from another page's main content): {Path(t).relative_to(DOCS.resolve())}")
    robots = (DOCS / "robots.txt").read_text(encoding="utf-8")
    for bot in AI_SEARCH_BOTS:
        if f"User-agent: {bot}\nAllow: /" not in robots:
            die(f"robots.txt must explicitly allow {bot}")
    llms = (DOCS / "llms.txt").read_text(encoding="utf-8")
    for s in PAGES:
        if f"{BASE}{s}/" not in llms:
            die(f"llms.txt is missing the guide {s}")

AI_SEARCH_BOTS = ["OAI-SearchBot", "PerplexityBot", "Claude-SearchBot", "Bingbot"]

def render_robots():
    out = ["# All crawlers are allowed. AI search crawlers are listed explicitly so the intent is clear.", ""]
    for bot in AI_SEARCH_BOTS:
        out += [f"User-agent: {bot}", "Allow: /", ""]
    out += ["User-agent: *", "Allow: /", "", f"Sitemap: {BASE}sitemap.xml", ""]
    return "\n".join(out)

def render_llms(pages_sorted):
    """Plain-text site summary for answer engines (llmstxt.org format). Regenerated on every build."""
    out = [f"# {SITE['name']}", "", f"> {SITE['tagline']}", "",
           "A free, independent guide for people in India whose complaint to an insurer, bank or other "
           "regulated company has stalled. Each guide gives the official escalation order, the published "
           "contact, the deadline, a free letter template where useful, and links to the official source "
           "with the date it was last checked. General information only, not legal advice. Not affiliated "
           "with any regulator or company.", "", "## Guides", ""]
    for p in pages_sorted:
        out.append(f"- [{p['h1']}]({BASE}{p['slug']}/): {p['description']} Last checked {p['verified']}.")
    out += ["", "## Sector hubs", ""]
    for s in SITE["sectors"]:
        if s["slug"] in LIVE_SECTORS:
            out.append(f"- [{s['name']}]({BASE}{s['slug']}/): {s['blurb']}")
    out += ["", "## About", "", f"- [About and disclaimer]({BASE}about/): how facts are sourced and checked.",
            f"- [Sitemap]({BASE}sitemap.xml)", ""]
    return "\n".join(out)

def check_links():
    bad = 0
    files = {str(f.relative_to(DOCS)) for f in DOCS.rglob("*") if f.is_file()}
    for f in DOCS.rglob("*.html"):
        if f.name == "404.html":
            continue
        txt = f.read_text(encoding="utf-8")
        for m in re.finditer(r'(?:href|src)="([^"]+)"', txt):
            u = m.group(1)
            if re.match(r"(https?:|mailto:|tel:|data:|#)", u):
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
    for js in sorted((ROOT / "assets").glob("*.js")):
        write(js.name, js.read_text(encoding="utf-8"))
    write("404.html", render_404())
    write(".nojekyll", "")
    write("robots.txt", render_robots())
    write("llms.txt", render_llms(pages_sorted))
    write("google26140f3f31e49c14.html", "google-site-verification: google26140f3f31e49c14.html")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    today = date.today().isoformat()
    for u, lm in urls:
        sm.append(f"<url><loc>{BASE}{u}</loc><lastmod>{lm or today}</lastmod></url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    print(f"Built {len(PAGES)} content pages, {len(urls)} URLs -> {DOCS}")
    if check:
        bad = check_links()
        check_built()
        if bad or problems:
            print("\n".join("PROBLEM: " + x for x in problems)); sys.exit(1)
        print("Link check OK; SEO, schema, copy and architecture checks OK")

if __name__ == "__main__":
    main()
