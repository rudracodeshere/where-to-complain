#!/usr/bin/env python3
"""Browser smoke test of the built site (docs/), served locally. Needs Playwright.

    python3 build.py && python3 tools/test_site.py

Checks every HTML page in docs/:
  - no console errors or page errors (third-party requests are blocked, so the test runs offline)
  - every internal link and asset answers 200 from the local server
  - no sideways scroll at a 390px-wide phone viewport
  - the deadline calculator shows the expected dates for known inputs

Approach from anthropics/skills webapp-testing: native Python Playwright, headless Chromium,
wait for networkidle before inspecting, capture console logs. The local server runs in a thread
here instead of that skill's with_server.py helper, so nothing is spawned through a shell.
Set CHROME=/path/to/chrome to use an installed Chrome instead of Playwright's own Chromium.
"""
import functools, http.server, os, re, sys, threading, urllib.error, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PREFIX = "/where-to-complain/"   # GitHub Pages project path, so absolute links in 404.html work too

# Known inputs -> expected [insurer/bank wait ends, can escalate from, last date]. Same cases as
# tools/test_calculator.js, but driven through the real form in a browser.
CALC_CASES = [
    (("bank", "2026-10-01", "none", None), ["2026-10-31", "2026-11-01", "2027-01-29"]),
    (("bank", "2026-10-01", "unsatisfied", "2026-12-15"), ["2026-10-31", "2026-11-01", "2027-03-15"]),
    (("insurance", "2026-10-01", "rejected", "2026-10-20"), ["2026-10-15", "2026-10-20", "2027-10-20"]),
    (("insurance", "2026-10-01", "none", None), ["2026-10-15", "2026-11-02", "2027-11-01"]),
]

class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if not path.startswith(PREFIX):
            return str(DOCS / "__missing__")
        return super().translate_path("/" + path[len(PREFIX):])
    def log_message(self, *a):
        pass

def serve():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(DOCS)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}{PREFIX}"

def main():
    if not (DOCS / "index.html").exists():
        sys.exit("docs/ is empty: run python3 build.py first")
    srv, base = serve()
    pages = sorted(str(p.relative_to(DOCS)) for p in DOCS.rglob("*.html") if not p.name.startswith("google"))
    fails, link_status = [], {}

    def status(url):
        if url not in link_status:
            try:
                link_status[url] = urllib.request.urlopen(url).status
            except urllib.error.HTTPError as e:
                link_status[url] = e.code
        return link_status[url]

    launch = {"headless": True}
    if os.environ.get("CHROME"):
        launch.update(executable_path=os.environ["CHROME"], args=["--no-sandbox"])
    with sync_playwright() as pw:
        browser = pw.chromium.launch(**launch)
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True)
        ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1)"), lambda route: route.abort())
        for rel in pages:
            page = ctx.new_page()
            errors = []
            page.on("console", lambda m, e=errors: m.type == "error" and e.append(m.text))
            page.on("pageerror", lambda exc, e=errors: e.append(f"page error: {exc}"))
            # third-party (GoatCounter) requests are aborted on purpose; ignore those failures only
            page.on("requestfailed", lambda r, e=errors: r.url.startswith("http://127.0.0.1") and e.append(f"failed: {r.url}"))
            url = base + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
            resp = page.goto(url)
            page.wait_for_load_state("networkidle")
            if not resp or resp.status != 200:
                fails.append(f"{rel}: HTTP {resp and resp.status} (want 200)")
            errors = [e for e in errors if "net::ERR_FAILED" not in e]
            if errors:
                fails.append(f"{rel}: console errors: {errors}")
            sw = page.evaluate("document.documentElement.scrollWidth")
            if sw > 390:
                fails.append(f"{rel}: sideways scroll at 390px (scrollWidth {sw})")
            hrefs = page.eval_on_selector_all("a[href], link[href], script[src], img[src]",
                                              "els => els.map(e => e.href || e.src)")
            for h in hrefs:
                h = h.split("#", 1)[0]
                if h.startswith("http://127.0.0.1") and status(h) != 200:
                    fails.append(f"{rel}: internal link {h[len(base) - len(PREFIX):]} -> {status(h)}")
            if rel == "complaint-deadline-calculator/index.html":
                for (kind, complained, reply, replied), expect in CALC_CASES:
                    page.check(f'input[name="type"][value="{kind}"]')
                    page.fill("#complained", complained)
                    page.check(f'input[name="reply"][value="{reply}"]')
                    if replied:
                        page.fill("#replied", replied)
                    page.click('#calc button[type="submit"]')
                    got = page.eval_on_selector_all("#calc-result dd.deadline", "els => els.map(e => e.dataset.iso)")
                    ok = got == expect
                    print(f"{'ok  ' if ok else 'FAIL'} calculator {kind} {complained} {reply} {replied or ''} -> {got}")
                    if not ok:
                        fails.append(f"calculator {kind} {complained} {reply} {replied}: got {got}, want {expect}")
                    sw = page.evaluate("document.documentElement.scrollWidth")
                    if sw > 390:
                        fails.append(f"calculator result causes sideways scroll (scrollWidth {sw})")
            print(f"{'ok  ' if not any(f.startswith(rel) for f in fails) else 'FAIL'} {rel}")
            page.close()
        browser.close()
    srv.shutdown()
    print(f"\n{len(pages)} pages, {len(link_status)} internal URLs checked")
    if fails:
        print("\n".join("FAIL: " + f for f in fails)); sys.exit(1)
    print("Site smoke test passed")

if __name__ == "__main__":
    main()
