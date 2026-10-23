# Changelog

## 2026-10-23: first release
- Built the static site: `build.py`, one JSON file per page in `data/pages/`, one shared layout, output in `docs/`.
- Home page, sector hubs (Insurance, Banks, Regulators), About and disclaimer page, `sitemap.xml`, `robots.txt`, 404 page.
- Published 3 pages, all checked against official sources on 2026-10-23:
  1. Health insurance claim rejected: what to do
  2. Insurance Ombudsman offices: which one covers your state (all 18 centres)
  3. How to file a complaint on the RBI CMS portal (RB-IOS 2026)
- Added `--check` mode in `build.py`: validates required fields, description and title length, that every email in a page is declared in `verified_emails`, and that every internal link resolves.
- Credit cards and Telecom hubs are not generated yet (no pages); the home page lists them as "coming soon".
- Known gaps recorded on the pages: the RBI CMS portal and the Scheme PDF could not be opened by automated checks, so portal screens are not described; the CIO site shows two versions of its centre list and an inconsistent home page, handled as described on the Ombudsman offices page.
