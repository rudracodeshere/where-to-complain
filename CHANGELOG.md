# Changelog

## 2026-10-24
- Added page: Star Health complaint escalation: GRO, IRDAI, Ombudsman, letter (`/star-health-complaint-escalation/`). Ladder: customer care (Level 1), Customer Escalations Team form (Level 2), Grievance Redressal Officer S. Chandrabose, Chennai (Level 3), IRDAI Bima Bharosa, Insurance Ombudsman. Includes cashless-denied, rejected, part-paid, no-reply and late-payment sections and a GRO letter template.
- Sources checked 2026-10-24: starhealth.in grievance redressal, service parameters (Citizens' Charter) and claims pages, Star Health's zonal/branch grievance PDFs, IRDAI list of GROs (updated 9 October 2026), CIO GRO list, IRDAI master circulars (re-checked), Bima Bharosa and CIO FAQ pages.
- Gaps noted on the page: Star Health's page gives grievances@starhealth.in for the GRO, while IRDAI's and CIO's lists give gro@starhealth.in (both shown); no contact or time limit published for Level 2 beyond a web form.
- Linked the new page from the health-insurance-claim-rejected and Ombudsman-offices pages; it is listed on the home page, Insurance hub and sitemap.

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

## 2026-10-24 (evening)
- Redesigned the site using the new DESIGN.md design system. Changes: a registry-green palette with tokens and WCAG AA contrast checked in light and dark mode; the system font stack; a header with hub nav, a current-page marker and a skip link; breadcrumbs as a list; a "Last verified" badge; escalation steps as a numbered ladder with amber deadline callouts instead of a table; a letter box with a print stylesheet; and two-column hub cards. CSS moved to `style.css`. All page text, facts, sources, dates, URLs, GoatCounter, the verification file, sitemap and robots are unchanged.
- SEO: guide `<title>`s shortened to 60 characters or fewer with the main query first (no site-name suffix). Each guide now has a 2-sentence direct answer at the top and 3 to 5 "Quick answers" with FAQPage JSON-LD, all taken from facts already on the page. `--check` now enforces these rules.
- Before and after screenshots are in `design-shots/`.
