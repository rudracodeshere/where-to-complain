# Where to Complain: design system and build rules

The nightly page routine follows this file. The CSS source is `style.css` (build.py copies it to `docs/style.css`). Templates are in `build.py`. Change tokens in `style.css`, never as raw hex inside templates.

## Who it is for and what the page must do

A worried person in India, usually on a phone, whose claim or complaint was ignored. They need to know in seconds who to write to next, by when, and that the facts are official. **Trust and scanability come first. Decoration comes last.**

The one bold element is the **numbered escalation ladder**. Everything around it stays quiet. Don't add a second "hero" treatment.

## Tokens

| Token | Light | Dark | Use |
|---|---|---|---|
| `--paper` | #ffffff | #121619 | page background |
| `--surface` | #f4f6f7 | #1a2024 | header, footer, source box, soon cards |
| `--ink` | #17212b | #e8ecef | body text (16.3:1 / 15.3:1) |
| `--muted` | #4f5b66 | #a9b3bc | meta, labels, crumbs (6.9:1 / 8.5:1) |
| `--line` | #d3dae0 | #2e373e | borders, ladder rail |
| `--accent` | #0b5a47 | #6fd3b4 | links, step numbers, badge, card top (8.2:1 / 10.1:1). A deep "registry" green: calm and official, not a bank blue |
| `--accent-wash` | #e8f2ee | #14251f | 30-second answer, badge fill |
| `--deadline-bg/ink/edge` | #fff3d9 / #5c3500 / #c4861a | #2a2110 / #f6d9a2 / #a8761f | deadlines and notices only (9.7:1 / 11.6:1) |
| `--focus` | #b34700 | #ffb070 | 3px focus outline |

Every text and background pair must be **at least 4.5:1** (WCAG AA). Check any new pair before you use it. Colour never carries meaning alone: deadlines also have the "Deadline" label.

**Type.** Use the system stack only (`system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, ...`), with no web fonts, so pages load fast on Indian mobile data and Noto covers ₹ and Indic names. Letters use the system monospace. The scale is base 17px (1.0625rem) at line-height 1.6, h3 19px, h2 23px (24px on desktop), h1 30px (36px on desktop), small 14px, lede 19 to 20px. Weights are 400 for body, 500 for nav, 600 for labels, 700 for headings. Never set body text below 16px. Use sentence case everywhere, with no ALL-CAPS labels.

**Spacing.** Use a 4px base: `--s1` 4, `--s2` 8, `--s3` 12, `--s4` 16, `--s5` 24, `--s6` 32, `--s7` 48. Space between sections is 48px. Inside a component it is 8 to 16px.

**Layout.** Mobile-first. Use one column at `--measure` 44rem (about 70 characters per line), left-aligned. The breakpoints are 640px (cards go to 2 columns) and 768px (larger headings). Never allow horizontal page scroll. Only wide tables scroll, inside `.tablewrap`. Radius is 6px.

## Components (class names in build.py)

- **Header** `header.site`: brand on the left, and a nav with the live hubs plus About. Each link is at least 44px tall, and the current hub has `aria-current="page"` with an accent underline. There is a "Skip to content" link before it.
- **Breadcrumb** `nav.crumbs > ol`: Home › Hub › Page (Home › About on the about page). The separator comes from CSS, and the last item has `aria-current="page"`. `layout()` builds the BreadcrumbList JSON-LD from the same crumbs, so the two cannot drift. The home page has no breadcrumb.
- **Last checked badge** `.badge`: "Last checked: <date>" (the page's `verified` date), placed directly under the H1 and above the direct answer. This is the official-source signal. The full source list stays in `.verified` at the bottom, with the same "Last checked" wording.
- **Direct answer** `.lede`: the page's `direct_answer`, 2 sentences, under the badge (see the SEO rules).
- **Question answer** `section.qa#question`: an H2 phrased the way people ask, from the page's `question.q`, with a plain paragraph of 40 to 60 words (`question.a`) under it. It renders right after the first block (the 30-second answer). No new CSS.
- **30-second answer** `.answer`: a green-wash box with a left rule and an ordered list.
- **Step ladder** `ol.ladder` (from the `steps` block): a CSS-counter numbered circle, with a vertical rail joining the steps. Each step has `.rung-who` (bold) and a `dl` with "Official contact" and "Deadline". Use numbering only because the content really is a sequence.
- **Deadline callout** `dd.deadline` / `.notice`: amber box with a left edge. Use it only for time limits and warnings.
- **Letter box** `.letter-box > pre.letter + .letter-actions`: monospace, wraps, and has a "Download as .txt" link. When printed, it shows only the content and the letter, in black on white, with no page break inside the letter.
- **Calculator form** `form.calc` + `.calc-result` (tools only, e.g. `/complaint-deadline-calculator/`): surface box; `fieldset`/`legend` radio groups with 44px rows; date inputs with a visible `label[for]`, a muted `.hint` linked by `aria-describedby`; one accent submit button (`--accent` on `--accent-ink`, 8.2:1). Results render into `.calc-result` (`aria-live="polite"`, focused after submit) as the same `ol.ladder` with `dd.deadline` dates, and each result shows its rule, official source link and last-verified date. Script is a local file from `assets/` (no external requests); a `<noscript>` notice points to the rules table. Hidden when printed.
- **Hub cards** `ul.cards`: 1 column on mobile and 2 from 640px, with an accent top border. "Coming soon" cards are grey.
- **Quick answers** `.faq`: `details`/`summary` items that show the page's `faq` and match its FAQPage JSON-LD.
- **Sources box** `.verified`: primary source, all sources with checked dates, and the disclaimer.
- **Resources** `#resources`: keep it empty and hidden unless br mogul adds vetted links.

Quality floor: visible `:focus-visible` outline, 44px touch targets for nav, letter and FAQ actions, `prefers-reduced-motion` respected (there is no motion now), dark mode tested on its own, URLs wrap with `overflow-wrap:anywhere`, and no emoji as icons.

Things to avoid (from the frontend-design skill): uppercase eyebrow labels, identical shadowed SaaS cards, gradient washes, `→` on links, accenting one word in a headline, and decoration with no meaning.

## SEO rules for every guide page (build.py --check enforces them)

1. **`title` must be 60 characters or fewer, with the main search query first**, e.g. "Star Health complaint: escalation steps (India)". Guide titles get no " | Where to Complain" suffix (the brand is in `og:site_name`). Leave the H1 as written unless it is also too long.
2. **`direct_answer`**: 2 sentences, 320 characters or fewer, shown at the top. It answers the main query directly.
3. **`faq`**: 3 to 5 `{q, a}` items, rendered both visibly and as FAQPage JSON-LD.
4. **The direct answer, question answer and FAQ use only facts already on that page** (same numbers, deadlines, contacts and wording), with nothing new. Any email in them must already be in `verified_emails`. The check scans them.
5. **"Last checked: <date>" sits between the H1 and the direct answer** on every guide, and the Article `dateModified` equals that date. (`--check`)
6. **Every guide has at least one question-style H2** (`question`: `q` ends in "?", `a` is about 40 to 60 words and stands on its own when quoted). Phrase it the way people ask, e.g. "Where do I complain if Star Health rejects my claim?". (`--check`)
7. **Every page**: one H1, no skipped heading levels, a self-referencing absolute canonical, a unique title of 60 characters or fewer and a unique meta description of about 150 to 160 characters (check allows 120 to 170), and a listing in `sitemap.xml` unless it is noindex. (`--check`)
8. **Structured data**: JSON-LD in the head, `@context` https://schema.org, absolute URLs, ISO dates. Guides carry Article + BreadcrumbList + FAQPage; hubs, about and tools carry BreadcrumbList; home carries WebSite. Every FAQ question and answer must be visible on the page word for word. Google stopped FAQ rich results in May 2026; keep the markup because other engines read it, but don't add schema just to chase rich results (no HowTo). (`--check` parses every block and checks required fields)

## Page and site rules (from the marketingskills references)

**One page per fact set (programmatic-seo).** Add a page for a company, regulator or tool only when it has its own checked facts: its own contacts, deadlines or rules from its own official pages. No pages that swap a company name into the same text, and no thin "X complaint number" doorway pages. A fact has one owning page (for example the Ombudsman one-year rule lives on the claim-rejected guide); other pages state it briefly and link there. Before publishing: unique title and description, schema present, in the sitemap, linked from its hub, no noindex.

**Hub and spoke (site-architecture).** Home links to every live hub and every guide. A hub lists every guide in its sector (`sector` or `also_in`). Every guide links back to its hub (breadcrumb and `related`) and to the closely related guides with descriptive anchor text (the target's H1, never "click here"). Every page is reachable within 3 clicks of home and has at least one inbound link from another page's main content. URLs are flat (`/<slug>/`) and never change once published. (`--check` fails on orphan pages and on a guide without a link to its hub.)

**Copy-editing pass before publishing (copy-editing).** Read the title, H1, description, direct answer, question answer and FAQ once more before commit. Cut filler and intensifiers (very, really, just, simply, actually, seamless, robust, leverage, utilise, in order to). One idea per sentence, 25 words or fewer where possible, active voice, the answer first. No em dashes in this short copy; use a colon, comma or full stop. Watch for AI tells: "not X, but Y" reveals, lists of three negations, stock openers. If a fact is missing, write `[NEED: ...]` in the draft and find the official source; never fill it in. (`--check` fails on the filler list, on em dashes and on sentences over 40 words in that copy.)

**Citable answers with sources (ai-seo).** Answer engines quote short self-contained blocks, so each guide opens with the direct answer, then the question H2 with its 40 to 60 word answer, both using exact numbers (14 days, 30 days, 90 days, one year, ₹50 lakh). Name the rule behind a fact where the page has it (Rule 14, RB-IOS 2026) and link the official source with the date checked. Keep "Last checked" visible near the top. `robots.txt` allows all crawlers and lists OAI-SearchBot, PerplexityBot, Claude-SearchBot and Bingbot explicitly; whether to block AI training crawlers is Boss's call, and the default is to allow them. `build.py` writes `/llms.txt` (site summary plus every guide and hub with a one-line description) on every build. (`--check` verifies the bots in robots.txt and every guide in llms.txt.)

**Browser smoke test (webapp-testing).** After building, run `python3 tools/test_site.py`. It serves `docs/` locally, opens every page in headless Chromium at 390px and fails on console errors, any internal link or asset that is not 200, sideways scroll, or wrong calculator dates for known inputs.

## Build workflow (from Superpowers: spec, plan, verify)

1. **Spec first.** Before writing, state in one line who the page is for, the main query, and the official sources you will use. If an official page can't be opened, say so on the page and don't guess.
2. **Plan in small steps.** Use the data JSON fields in schema order: sources, then blocks, then templates, then direct_answer and faq (written last, from the finished page), then related. Edit one file per step.
3. **Reuse the components.** No new CSS for a single page. If a new component is truly needed, add it here first, with tokens, then to `style.css`.
4. **Verify before claiming done** (evidence before assertions): run `python3 build.py --check`, `node tools/test_calculator.js` and `python3 tools/test_site.py`, and read the output. `--check` must end with "checks OK". After pushing, fetch the live URL and confirm HTTP 200 and the new title. Don't report "live" until you've seen it.
5. For a visual change, take before and after screenshots with `tools/shots.sh before|after` (headless Chrome, 390px and 1280px) into `design-shots/`, then look at them.
6. Use one focused commit per page or change, update `CHANGELOG.md` and `QUEUE.md`, then push.
