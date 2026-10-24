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
- **Breadcrumb** `nav.crumbs > ol`: Home › Hub › Page. The separator comes from CSS, and the last item has `aria-current="page"`. It matches the BreadcrumbList JSON-LD.
- **Verified badge** `.badge`: "Last verified: <date>", placed directly under the H1. This is the official-source signal. The full source list stays in `.verified` at the bottom.
- **Direct answer** `.lede`: the page's `direct_answer`, 2 sentences, under the badge (see the SEO rules).
- **30-second answer** `.answer`: a green-wash box with a left rule and an ordered list.
- **Step ladder** `ol.ladder` (from the `steps` block): a CSS-counter numbered circle, with a vertical rail joining the steps. Each step has `.rung-who` (bold) and a `dl` with "Official contact" and "Deadline". Use numbering only because the content really is a sequence.
- **Deadline callout** `dd.deadline` / `.notice`: amber box with a left edge. Use it only for time limits and warnings.
- **Letter box** `.letter-box > pre.letter + .letter-actions`: monospace, wraps, and has a "Download as .txt" link. When printed, it shows only the content and the letter, in black on white, with no page break inside the letter.
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
4. **The direct answer and FAQ use only facts already on that page** (same numbers, deadlines, contacts and wording), with nothing new. Any email in them must already be in `verified_emails`. The check scans them.

## Build workflow (from Superpowers: spec, plan, verify)

1. **Spec first.** Before writing, state in one line who the page is for, the main query, and the official sources you will use. If an official page can't be opened, say so on the page and don't guess.
2. **Plan in small steps.** Use the data JSON fields in schema order: sources, then blocks, then templates, then direct_answer and faq (written last, from the finished page), then related. Edit one file per step.
3. **Reuse the components.** No new CSS for a single page. If a new component is truly needed, add it here first, with tokens, then to `style.css`.
4. **Verify before claiming done** (evidence before assertions): run `python3 build.py --check` and read its output. It must end with "Link check OK". After pushing, fetch the live URL and confirm HTTP 200 and the new title. Don't report "live" until you've seen it.
5. For a visual change, take before and after screenshots with `tools/shots.sh before|after` (headless Chrome, 390px and 1280px) into `design-shots/`, then look at them.
6. Use one focused commit per page or change, update `CHANGELOG.md` and `QUEUE.md`, then push.
