# Where to Complain: build playbook

Written 24 October 2026 (IST). What we took from each skill repo, the checklist every nightly page must pass, and the site-level fixes ranked by impact. The site is static, text-first, a YMYL (consumer/legal money) guide for India, read mostly on phones, with no ads yet. Rules below are filtered for that. Anything that needs a paid API, an account, or a JS framework is skipped.

Checker: `python3 tools/check_pages.py` (stdlib only, read-only; `--live` checks the deployed site, `--external` also checks every outbound source link). It is not wired into build.py. Hook it in after the current build.py work lands.

---

## 1. Per-skill rules

### impeccable (pbakaus)
1. Guides are "Read" mode: one column, 65-75ch measure, body 16px+, line-height 1.5+, contrast 4.5:1 minimum for text. The calculator is "Operate" mode: labels above inputs, result in a fixed spot, no layout jump.
2. Craft floor: no eyebrow/kicker labels above headings, no emoji as icons, no coloured left-border callouts thicker than 1px, no decorative gradients. Themed `:focus-visible` ring and `::selection`.
3. One accent colour, used only for links and the primary action. Hierarchy comes from size and weight, not boxes.
4. Run the 5-dimension critique (out of 20) on DESIGN.md changes before shipping.
Skipped: the `impeccable` CLI/launcher (downloads a binary) and the live-browser "polish" loop. We used the reference docs only.

### web-quality-skills (addyosmani)
1. Budgets per page: total under 1.5 MB, JS under 300 KB, CSS under 100 KB. We are at 15-22 KiB, so the rule is "do not regress": no web fonts, no images over 100 KB, no new third-party script.
2. Core Web Vitals: LCP under 2.5 s, INP under 200 ms, CLS under 0.1, measured on Lighthouse mobile.
3. Accessibility: `lang`, skip link, one `<main>`, one H1, no skipped heading levels, touch targets 24px minimum (44px preferred), descriptive anchor text, visible focus.
4. Best practices: zero console errors (today the only one is the favicon 404), HTTPS-only links, valid HTML.
Skipped: analyze.sh (needs jq; check_pages.py covers the same checks). Header and caching advice (CSP, HSTS, long cache TTL) because GitHub Pages cannot set headers.

### claude-seo: seo-cluster, seo-google, seo-bing (AgriciDaniel)
1. Hub and spoke: every guide links up to its hub (insurance, banks, regulators) and the hub links down to every guide. Each guide links to 2-3 sibling guides. Every page is 2 clicks or fewer from home and has 3+ inbound internal links.
2. Before writing a new page, check overlap with existing ones. If the top-10 Google results for the two target queries share 7-10 URLs, merge them. If they share 4-6, it is the same cluster (link them). If they share 2-3, link once.
3. Google: use the free Search Console UI (sitemap submit, URL Inspection "Request indexing" for each new page) and free PageSpeed Insights. Bing: Bing Webmaster Tools sitemap, plus IndexNow (key file at the site root, ping on every new or changed URL). Bing's index also feeds Copilot citations.
4. YMYL means the highest E-E-A-T bar: named responsibility, sources on every claim, visible dates.
Skipped: the seo-google API scripts (need a GCP project and service account) and DataForSEO features (paid).

### seo-audit-skill (SEOmator CLI)
1. Run `seomator audit` on the homepage monthly. Treat geo, social and eeat as the categories to watch (53, 20 and 74 today).
2. Fix what is real on a static host: favicon, og:image + twitter:card, a byline, contact and privacy pages. Ignore security-header findings (not settable on GitHub Pages).
3. Its crawler drops the `/where-to-complain/` base path and crawls the user-site root, so inner-page results are 404 noise. Only trust homepage findings, or audit inner pages one URL at a time.
Skipped: the cloud/report-upload features (account needed).

### geo-seo-claude (zubair-trabzada)
1. Each guide opens with a 40-60 word answer that stands alone if quoted: who to complain to, deadline, cost. Then each question H2 starts with a 1-2 sentence direct answer that includes the regulator name and the number (days, rupees).
2. Use facts with units and named sources in the same sentence ("IRDAI's 2024 master circular gives insurers 14 days"). Citable passages are 130-170 words, self-contained, with no "as mentioned above".
3. Keep AI crawlers allowed and llms.txt current, but treat llms.txt as low priority (Google says it does not use it).
4. Citability scores today (regex heuristic, directional only): home 30.8, guides 40-42, calculator 47.9. Nearly every block grades D or F. Target 55+ per guide.
Skipped: the paid brand-mention and Ahrefs/Semrush modules.

### kostja94 programmatic-seo (marketing-skills)
1. Every URL needs its own evidence block: the regulator's rule, the deadline, the official link and the date checked. No pages whose only difference is a swapped company name.
2. Keep facts in the data layer (page data files), not prose, so a rule change edits one value. Volatile facts (phone numbers, emails, limits) carry their own "checked on" date.
3. Conditional sections: if a company has no GRO email or no app path, the section is left out rather than rendered empty or with filler.
4. Prune plan: a page with no impressions after 90 days in GSC gets improved, merged, or set to noindex.
Skipped: template-at-scale generation (one checked page per night is the model, by design).

### humanizer (blader)
1. No em dashes or en dashes in copy (36 found today, mostly in the sources lists). Use commas, colons, or full stops.
2. Banned words: additionally, align with, crucial, delve, enhance, garner, intricate, key (as adjective), landscape, meticulous, pivotal, robust, seamless, showcase, tapestry, testament, underscore, valuable, vibrant.
3. No "not X but Y", no forced lists of three, no bold for decoration, no chatbot leftovers ("I hope this helps"), no heading repeated in the first sentence, straight quotes only.
4. Plain register for a stressed reader: short sentences, "you", concrete verbs. Reading level is "difficult" today (Flesch 49); aim for 60+.
Skipped: nothing material. "When not to act" applies: legal names and official titles stay as written even if they sound stiff.

### claude-blog (AgriciDaniel): blog-factcheck, blog-seo-check, blog-cannibalization, blog-decay
1. Factcheck: list every load-bearing claim (deadline, amount, contact, rule number) and check it against the cited page. Score 1.0 only when the exact figure is on the cited page in context. Sources must be tier 1 (regulator, gazette, official portal). Reject tier 4-5 (blogs, aggregators). Echoed reports count as one source.
2. A claim citing a homepage when the figure is on a subpage scores 0.3, so link the exact document, not the portal root.
3. Cannibalisation: before a new page, compare its primary query against existing titles and H1s (exact, stem, subset match). Merge or retarget on overlap.
4. Decay: once GSC has 2 periods, compare clicks. 20-39% drop is a warning, 40-59% high, 60%+ critical; refresh the facts and the "Last checked" date first.
Skipped: blog-image, audio, notebooklm and translate (not text-first, or need paid APIs). The DataForSEO mode (paid).

### affiliate-skills: github-pages-deployer (Affitor)
1. Keep `.nojekyll` and a custom `404.html` in docs/ (both already there). Repo must stay public (free Pages).
2. If we add a custom domain later: a CNAME file with the bare domain, DNS pointed at `rudracodeshere.github.io`, Cloudflare proxy off, then "Enforce HTTPS".
3. Check each deploy: the new URL returns 200 within about 10 minutes, and sitemap.xml shows the new URL.
Skipped: the Actions workflow generator (we deploy from docs/ on main, which works) and the affiliate/landing-page parts (no ads or affiliates yet).

### seo-data (anthonylee991)
1. GSC is "what people searched", GA4 is "what they did". We have GoatCounter, not GA4. Do not mix the two numbers in reports.
2. Weekly once data exists: top queries and pages from GSC, the same for Bing, and pages with impressions but CTR under 1% get a title/description rewrite.
Skipped: running it. It needs a Google Cloud OAuth client and a Bing API key, which means sign-ups. Use the GSC and Bing web UIs by hand until Boss sets up keys.

---

## 2. Nightly page checklist (one new page)

**A. Research and verification**
- [ ] Pick a query from the backlog. Check cannibalisation against existing titles/H1s. If the SERP overlap with an existing page is 7+ URLs, update that page instead.
- [ ] Every load-bearing fact (deadline, amount, phone, email, address, rule) comes from a tier-1 source: regulator site, gazette, official portal, the company's own GRO page.
- [ ] Link the exact document or subpage, not the portal home. Record the date checked next to each source.
- [ ] Open each source today and confirm the exact figure is on it. Anything unconfirmed is cut, not hedged.
- [ ] Data goes in the page data file; no fact appears only in prose.

**B. Writing**
- [ ] First paragraph: 40-60 word answer (who, by when, cost). Plain English, "you", short sentences.
- [ ] No em/en dashes, no banned words, no "not X but Y", no forced triads, no decorative bold, straight quotes.
- [ ] Every section has content specific to this page. Drop empty sections; no filler.
- [ ] Not-legal-advice disclaimer present. The wording matches where the sources sit on the page.
- [ ] 600+ words for a guide, unless the topic is genuinely narrower.

**C. On-page SEO**
- [ ] Title is unique and 50-60 characters (65 max), with the query near the front.
- [ ] Meta description is unique and 120-160 characters, saying what the reader gets.
- [ ] One H1. H2s phrased as the questions people ask. No skipped levels.
- [ ] Canonical = the final trailing-slash URL. og:title, og:description, og:url, og:image.
- [ ] JSON-LD parses: Article (headline up to 110 characters, datePublished, dateModified, author, publisher) + BreadcrumbList; FAQPage only if the Q&A is visible on the page. No HowTo.

**D. Clusters and internal links**
- [ ] Link up to the hub, and add the page to the hub's list.
- [ ] Link to 2-3 sibling guides, and add a link back from at least 2 of them, so the page has 3+ inbound links.
- [ ] Descriptive anchors (never "click here"). Within 2 clicks of home.

**E. GEO / AI citation**
- [ ] Each question H2 opens with a direct answer sentence that names the regulator and the number.
- [ ] At least one self-contained 130-170 word passage with a fact, a unit and a named source.
- [ ] Visible "Last checked" date. The page is listed in llms.txt and sitemap.xml with a real lastmod.

**F. Web quality, performance, accessibility**
- [ ] No new JS or third-party requests. Page under 50 KB. No images without width, height and alt.
- [ ] Lighthouse mobile: Performance 95+, Accessibility 100, Best Practices 100 (after the favicon fix), SEO 100.
- [ ] `python3 tools/check_pages.py` shows 0 FAIL. `python3 tools/test_site.py` passes.

**G. Deploy and submit**
- [ ] Commit and push. Confirm the live URL returns 200 and appears in the live sitemap.xml.
- [ ] `python3 tools/check_pages.py --live` shows 0 FAIL. Run `--external` weekly. Indian gov sites often answer 5xx to foreign IPs, so recheck those in a browser before treating them as dead.
- [ ] Google Search Console: URL Inspection, then Request indexing (new URL plus the hub that now links to it).
- [ ] Bing: IndexNow ping (once the key file exists), or Bing Webmaster Tools URL submission.

---

## 3. Site-level fixes, ranked by impact

| # | Fix | Why | Script-checkable? |
|---|-----|-----|-------------------|
| 1 | Correct the homepage "no tracking" claim. GoatCounter loads on every page. Say "privacy-friendly, cookie-free visit counts (GoatCounter), no ads", or remove the script. | A false trust claim on a YMYL site is the worst kind of error, and easy to spot. | Yes (grep the claim text and the gc.zgo.at script together) |
| 2 | Add a favicon: `docs/favicon.svg` plus `<link rel="icon" href="favicon.svg">` on every page. | The browser requests /favicon.ico at the user-site root, gets a 404, and logs a console error on every page. That is the only reason Best Practices is 96. | Yes (check_pages: "no link rel=icon"; Lighthouse errors-in-console) |
| 3 | E-E-A-T pages: a named person responsible (byline and short bio on About), an editorial/methodology page (how facts are checked, tier-1-only sources, re-check cadence, corrections email), a contact page, and a privacy page. Set Article.author to that Person, with publisher = Organization. | YMYL bar. SEOmator eeat 74, no author or contact found. | Partly (presence of pages and author field yes; quality no) |
| 4 | Answer-first rewrite of existing guides: a 40-60 word lead answer plus a direct first sentence under each question H2. | Citability scores of 30-48 with most blocks D/F. This is the main lever for AI Overviews, Copilot and Perplexity citations. | Partly (question H2 presence yes; answer quality no) |
| 5 | og:image (one 1200x630 PNG under 100 KB for the site, optional per-hub variants) plus `twitter:card=summary_large_image`. | Pages get shared on WhatsApp and X with no preview today. SEOmator social score 20. | Yes |
| 6 | Strip em/en dashes from copy (36 across 6 pages, mostly the " — " in source lists) and run the banned-word list. | House style (humanizer). Dashes are a strong "AI-written" tell for readers. | Yes (check_pages) |
| 7 | IndexNow: add a key file `docs/<key>.txt` and a nightly ping for new or changed URLs (free, no account). Also verify the site in Bing Webmaster Tools and submit the sitemap. | Faster Bing indexing, and Bing feeds Copilot. | Yes (key file present; ping result) |
| 8 | Host-root robots.txt: rudracodeshere.github.io/robots.txt only lists the profit-calculator sitemap. Crawlers ignore /where-to-complain/robots.txt. Add the WTC sitemap line in the user-site repo (outside this repo, so Boss must OK it). | Sitemap discovery for crawlers that do not get a GSC/Bing submission. | Yes (curl) |
| 9 | JSON-LD: wrap it in `{"@context":..., "@graph":[...]}`, give WebSite and Organization an `@id`, and reference them from Article. | Valid as is for Google, but some parsers (SEOmator) report "no @type". @graph with @id makes one clean entity. | Yes |
| 10 | Brand link `href=""` should be `href="./"` on home and the relative root elsewhere (or the absolute base URL). | An empty href reloads the page and is flagged by audits and some screen readers. | Yes (check_pages) |
| 11 | Plain-language pass: Flesch about 49 now, target 60+. Shorter sentences, fewer nested clauses. | Stressed, often second-language readers on phones. | Yes (readability score as a proxy) |
| 12 | The disclaimer says "confirm on the official source linked below", but on the homepage, hubs and About no source follows it, and on guides the sources sit above it. It also appears twice per page. Reword to "linked on this page" and show it once. | Small trust and copy bug on every page. | Yes (check_pages) |
| 13 | Remove the canonical from 404.html (keep noindex). | Canonical on an error page is a mixed signal. | Yes (check_pages) |
| 14 | Trim the 3 guide meta descriptions that run 168-169 chars to 160 or fewer. | Truncated in results. | Yes |
| 15 | Inline the 3.3 KB style.css into each page `<head>` (optional). | Removes the only render-blocking request. Main gain is on the guide with LCP 2.6 s. Low priority, since everything already scores 97-100. | Yes (Lighthouse render-blocking) |
| 16 | GSC 90-day prune review: pages with zero impressions get improved, merged or noindexed. | Thin pages on a small YMYL site drag down the rest. | No (needs GSC data) |

Cannot fix on GitHub Pages (do not spend time): security headers (CSP, HSTS, X-Content-Type-Options), cache TTL (fixed at 600 s), and the 301 from no-slash to slash URLs (that one is fine anyway).

---

## 4. Audit snapshot (24 October 2026, IST)

- Lighthouse 13.5.0, mobile, all 10 live pages: Performance 100 on 9 pages, 97 on health-insurance-claim-rejected (LCP 2.6 s). Accessibility 100, Best Practices 96, SEO 100 on all. CLS 0, TBT 0, page weight 15-22 KiB, LCP 0.8-2.6 s. Failing audits: errors-in-console (favicon 404, every page), render-blocking style.css (3.3 KB), cache TTL 600 s (host limit). Note: commit cd31ed8 went live during this run, so a few pages were measured just before it. Re-run after the next deploy.
- SEOmator 7.0.0, homepage: 86/100 (B). Weakest categories: geo 53, social 20, eeat 74, content 77. Real findings: no favicon, no og:image or twitter:card, empty brand href, JSON-LD array not recognised, no WebSite @id, no author/contact/privacy. Inner pages were not audited because of the base-path crawl bug.
- geo-seo-claude citability (heuristic): home 30.8, rbi-cms 40.5, star-health 40.4, ombudsman-offices 41.4, health-claim-rejected 41.8, calculator 47.9.
- check_pages.py on docs/ and live: 0 FAIL, 30-32 WARN. Main warnings: og:image missing (10), dashes (6 pages), disclaimer wording (all pages), long descriptions (3), empty href (1), 404 canonical (1). All internal links resolve; no orphans; every page is in the sitemap. `--external`: irdai.gov.in and bimabharosa.irdai.gov.in returned 500/504 and cms.rbi.org.in did not connect from the audit box. These are likely geo-blocking or flaky gov hosts. Recheck from an Indian connection before changing any link.
- Already good: en-IN lang, viewport, unique titles, canonicals match, BreadcrumbList on all inner pages, Article + FAQPage on guides with the FAQ visible, "Last checked" with dated tier-1 sources, a disclaimer on every guide, llms.txt, a sitemap with real lastmod, AI crawlers allowed, `.nojekyll`, custom 404.
