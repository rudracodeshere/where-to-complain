# Where to Complain

**Live site:** https://rudracodeshere.github.io/where-to-complain/
**Repo:** https://github.com/rudracodeshere/where-to-complain

A free static directory with no ads and no cookies (JavaScript only on tool pages, plus the privacy-friendly GoatCounter visit counter) of Indian complaint escalation ladders: who to write to first, who to escalate to next, the official contact, the deadline, and a copy-paste letter. Every fact on a page is copied from an official regulator or government page, with the URL and the date it was checked. If something is not published officially, the page says so instead of guessing.

**Who it helps:** people in India whose insurance claim was rejected, whose bank or lender did not resolve a complaint, and anyone who needs to know which ombudsman office covers them.

## Pages (as of 2026-10-24)

| Page | URL |
|------|-----|
| Home | https://rudracodeshere.github.io/where-to-complain/ |
| Health insurance claim rejected: what to do | https://rudracodeshere.github.io/where-to-complain/health-insurance-claim-rejected/ |
| Insurance Ombudsman offices: which one covers your state | https://rudracodeshere.github.io/where-to-complain/insurance-ombudsman-offices-by-state/ |
| How to file a complaint on the RBI CMS portal | https://rudracodeshere.github.io/where-to-complain/how-to-file-complaint-rbi-cms-portal/ |
| Star Health complaint escalation: GRO, IRDAI, Ombudsman, letter | https://rudracodeshere.github.io/where-to-complain/star-health-complaint-escalation/ |
| Complaint deadline calculator (tool, JavaScript) | https://rudracodeshere.github.io/where-to-complain/complaint-deadline-calculator/ |
| Hubs: Insurance, Banks, Regulators | `/insurance/`, `/banks/`, `/regulators/` |
| About and disclaimer | `/about/` |
| How we check facts, Privacy (trust pages) | `/how-we-check-facts/`, `/privacy/` |
| Sitemap, robots | `/sitemap.xml`, `/robots.txt` |

The queue of planned pages is in [QUEUE.md](QUEUE.md). Release notes are in [CHANGELOG.md](CHANGELOG.md).

## Analytics status

GoatCounter (free, no cookies) is live. Dashboard: https://where-to-complain.goatcounter.com (account email: Boss's; login needs Boss). The snippet is in the layout in build.py, so every new page gets it. Google Search Console: verified (HTML file google26140f3f31e49c14.html, kept by build.py). Sitemap submitted 2026-10-23.

## Project layout

```
build.py                  generator (Python 3, standard library only)
style.css                 design-system CSS source (copied to docs/style.css)
DESIGN.md                 design tokens, components, SEO and build rules: follow it for every page
assets/*.js               tool scripts (copied to docs/), e.g. calculator.js
tools/test_calculator.js  node tests for the calculator date logic
tools/test_site.py        Playwright smoke test of every built page (console errors, links, 390px, calculator)
tools/shots.sh            before/after screenshots with headless Chrome into design-shots/
site.json                 site name, base URL, sector list, IndexNow key
data/pages/NN-slug.json   one file per content page
data/ombudsman_offices.json  data used by the "offices" block
tools/check_pages.py      on-page checker from BUILD-PLAYBOOK.md (run by build.py --check; --live checks the deployed site)
tools/indexnow.py         IndexNow ping after a deploy (all sitemap URLs, or the URLs given)
tools/make_images.py      makes assets/og.png, logo.png, favicon.svg in brand colours (Pillow)
assets/*.png, *.svg       share image, logo, favicon (copied to docs/)
BUILD-PLAYBOOK.md         skill rules, nightly page checklist, ranked site fixes
tools/fetch_text.py       helper: fetch an official page as readable text (python3 + curl; usage: python3 tools/fetch_text.py URL)
docs/                     generated site, served by GitHub Pages (commit it)
QUEUE.md                  todo/done list of pages
```

## How to add a page

1. Copy an existing file in `data/pages/` to `data/pages/NN-new-slug.json` (`NN` is the next number).
2. Set `slug`, `order`, `sector` (one of the slugs in `site.json`), `title` (60 characters or fewer, main query first; see DESIGN.md), `h1`, `description` (120 to 160 characters), `verified` (date you checked, `YYYY-MM-DD`), `primary_source` (official URL), and `sources` (every official page you used, each with `url`, `label`, `checked`).
   Also set `direct_answer` (40 to 60 words, answer-first: name the body and the number or deadline) and `faq` (3 to 5 `{q, a}` items). Both use only facts already on the page.
3. Fill `blocks`, in the order they should appear:
   - `answer`: the 30-second answer box (`items`, an ordered list).
   - `steps`: the ladder table (`rows` with `who`, `contact`, `deadline`; the Step number is added automatically).
   - `problems`: sub-sections for "If it's about X" (`items` with `title` and `html`).
   - `section`: any other heading plus `html` (use it for the regulator step).
   - `table`: a generic table (`headers`, `rows`).
   - `offices`: the Ombudsman office table from a JSON file in `data/`.
   - `notice`: a highlighted note.
4. Add `templates`: a list of `{title, text, intro_html}`. The text is also written to `docs/letters/<slug>.txt` for download.
5. Add `related` (slugs of other pages or sector hubs), `also_in` (extra sector hubs to list the page in), and leave `resources_html` as `""`. The page renders an empty `<section class="resources" id="resources">`, reserved for br mogul. It is hidden until it has content.
6. Add `question`: `{q, a}`, a question-style H2 (ending in "?") with a 40 to 60 word answer using only facts on the page.
7. Run `python3 build.py --check`. It fails if a required field is missing, a description or title is the wrong length or duplicated, a link is broken, a page is an orphan, the JSON-LD is invalid, the "Last checked" line or question H2 is missing, the short copy fails the copy-editing lint, or an email address appears in the content without being listed in `verified_emails`. Then run `python3 tools/test_site.py`.
8. Mark the row in `QUEUE.md` as `done`, add a line to `CHANGELOG.md`, commit, and push. GitHub Pages serves the `docs/` folder from `main`.

A sector hub (`/insurance/`, etc.) is generated automatically once at least one page uses that sector. Credit cards and Telecom hubs will appear when their first page is added.

### Accuracy rules (do not skip)

- Copy contacts, deadlines and limits only from the company's or regulator's own page, and cite the URL and date.
- Never invent or "fix" an email, phone number, address or deadline. If it is not published, write "not published; use `<official portal>`".
- Re-check every deadline on the day you publish. Search-engine summaries are not a source.
- If an official page cannot be opened, say so on the page rather than filling the gap from a forum or news article.
- No personal complaints or stories copied from X or Reddit. No personal data.
- Disclose any affiliate link. There are none today.
- Keep the disclaimer. It is added automatically.

## Build and publish

```
python3 build.py --check             # links, fields, SEO/schema/copy rules from DESIGN.md + tools/check_pages.py
node tools/test_calculator.js        # calculator date logic
python3 tools/test_site.py           # browser smoke test of docs/ (needs Playwright; see below)
git add -A && git commit -m "Add page: <title>" && git push
python3 tools/indexnow.py <changed URLs>   # after the deploy is live (key file must return 200)
```

`tools/test_site.py` needs Playwright (`python3 -m venv .venv && .venv/bin/pip install playwright && .venv/bin/playwright install chromium`, or set `CHROME=/usr/bin/google-chrome` to use an installed Chrome). On the shared box: `CHROME=/usr/bin/google-chrome /workspace/boring-realty/.venv/bin/python tools/test_site.py`.

The base URL in `site.json` controls canonical links and `sitemap.xml`. Internal links are relative, so the site also works from a custom domain if `base_url` is changed.
