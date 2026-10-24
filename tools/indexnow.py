#!/usr/bin/env python3
"""Ping IndexNow (Bing, Yandex, Seznam, Naver and others share submissions) after a deploy.

Usage:  python3 tools/indexnow.py                 # every URL in docs/sitemap.xml
        python3 tools/indexnow.py URL [URL ...]   # only these URLs (new or changed pages)
        python3 tools/indexnow.py --dry-run ...   # print the payload, send nothing

The key lives in site.json ("indexnow_key"); build.py writes docs/<key>.txt, which must be
live (HTTP 200) before pinging. Run this only after the push has deployed. Stdlib only.
HTTP 200 or 202 means accepted."""
import json, re, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
BASE = SITE["base_url"].rstrip("/") + "/"
ENDPOINT = "https://api.indexnow.org/indexnow"

def main():
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    key = SITE.get("indexnow_key")
    if not key:
        sys.exit("site.json has no indexnow_key")
    urls = args or re.findall(r"<loc>([^<]+)</loc>", (ROOT / "docs" / "sitemap.xml").read_text(encoding="utf-8"))
    urls = [u for u in urls if u.startswith(BASE)]
    if not urls:
        sys.exit("no URLs under " + BASE)
    host = BASE.split("/")[2]
    payload = {"host": host, "key": key, "keyLocation": f"{BASE}{key}.txt", "urlList": urls}
    if "--dry-run" in sys.argv:
        print(json.dumps(payload, indent=1)); return
    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow HTTP {r.status} for {len(urls)} URLs")
    except urllib.error.HTTPError as e:
        print(f"IndexNow HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
        sys.exit(1)

if __name__ == "__main__":
    main()
