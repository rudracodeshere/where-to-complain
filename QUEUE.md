# Page queue

Order matters: the nightly job takes the first `todo` row. After publishing, change it to `done` and add the live URL.
Source of the list: `/workspace/boring-realty/picks/01-escalation-ladder-directory.md`.

## Priority order (re-ranked 2026-10-24 using br grower's Bing keyword data: consumer court 233, NCH 217, CPGRAMS 1,313, "rbi complaint" 93 searches per 12 weeks; single insurers barely register)

| # | Status | Page | Slug | Notes |
|---|--------|------|------|-------|
| 1 | done | Health insurance claim rejected: what to do | `health-insurance-claim-rejected` | Published 2026-10-23 |
| 2 | done | Insurance Ombudsman offices: which one covers your state | `insurance-ombudsman-offices-by-state` | Published 2026-10-23 |
| 3 | done | Star Health: grievance officer, escalation ladder, claim-rejected template | `star-health-complaint-escalation` | Published 2026-10-24: https://rudracodeshere.github.io/where-to-complain/star-health-complaint-escalation/ . GRO details from starhealth.in grievance page + IRDAI/CIO GRO lists (they differ on the GRO email; both shown). |
| 6 | done | How to file a complaint on the RBI CMS portal | `how-to-file-complaint-rbi-cms-portal` | Published 2026-10-23. Follows RB-IOS 2026 (30-day wait, 90-day window). |
| 10 | done 2026-10-25 https://rudracodeshere.github.io/where-to-complain/consumer-court-complaint-e-jagriti/ | Consumer court complaint online: e-Jagriti (e-Daakhil) step by step | `consumer-court-complaint-e-jagriti` | e-Daakhil was replaced by e-Jagriti (e-jagriti.gov.in) on 1 Jan 2025 per br grower; VERIFY on official govt press release / edaakhil.nic.in notice / e-jagriti.gov.in. Build around e-Jagriti, mention e-Daakhil as old name. Fee slabs and limitation only from official Consumer Protection rules. Bing cluster ~2,830. Link from insurance page and hubs. |
| 22 | done 2026-10-26 https://rudracodeshere.github.io/where-to-complain/national-consumer-helpline-complaint/ | National Consumer Helpline (NCH 1915): how to complain, 1915 / app / WhatsApp, what happens next | `national-consumer-helpline-complaint` | Only from consumerhelpline.gov.in / DoCA official pages. Title must include "NCH" and "1915". Bing cluster ~585. |
| 23 | done 2026-10-27 https://rudracodeshere.github.io/where-to-complain/cpgrams-grievance-complaint/ | CPGRAMS: register/login, file a grievance, track status, appeal | `cpgrams-grievance-complaint` | Only from pgportal.gov.in / DARPG official pages. Bing: ~1,313 searches/12 wks. Built from pgportal FAQ + DARPG OM of 23 Aug 2024 (21 days, appeal 30/30). Not covered: PMO grievance route (pmopg status) and feedback call centre number (not on a page checked). |
| 8 | done 2026-10-28 https://rudracodeshere.github.io/where-to-complain/sbi-complaint-escalation/ | SBI complaint escalation: branch -> regional -> PNO -> CMS | `sbi-complaint-escalation` | SBI moved to sbi.bank.in (old sbi.co.in grievance pages 404). Built from SBI Customer Grievance Redressal Policy 2026-27 PDF, Level 2/3/4 escalation PDFs and contact pages, plus RB-IOS 2026. Policy lists @sbi.bank.in emails, site lists @sbi.co.in: both shown. |
| 20 | done 2026-10-28 https://rudracodeshere.github.io/where-to-complain/airline-complaint-airsewa/ | IndiGo / Air India: AirSewa and DGCA complaint route | `airline-complaint-airsewa` | Built from DGCA CAR Section 3 Series M Part IV Rev 4 (PDF), airsewa.gov.in, PIB 2 Feb 2023, Lok Sabha USQ 6226 (2 Apr 2026, 14-day refund rule from CAR M Part II rev effective 26 Mar 2026). DGCA CAR list page loads by script: newer Part IV revision not confirmed. AirSewa passenger charter link is dead. |
| 4 | todo | Care Health: cashless denied / claim rejected ladder + template | `care-health-complaint-escalation` | Same method as #3. |
| 5 | todo | HDFC Bank: escalation matrix and nodal officer, then RBI CMS (what to attach) | `hdfc-bank-complaint-escalation` | Copy matrix only from hdfcbank.com's own page; link RBI CMS page. |
| 7 | todo | ICICI Bank credit card dispute: nodal officer letter template | `icici-bank-credit-card-dispute` | Check card-network/RBI turnaround rules from official pages before stating any deadline. |
| 9 | todo | Jio / Airtel / Vi: appellate authority and TRAI/CPGRAMS route | `telecom-appellate-authority-trai-cpgrams` | Needs the telecom sector hub (set `"sector": "telecom"`). Verify TRAI consumer complaint rules (TCCCPR) from trai.gov.in. |

## Next 10 (from the brief)

| # | Status | Page | Suggested slug | Notes |
|---|--------|------|----------------|-------|
| 11 | todo | Niva Bupa: grievance officer and claim-rejected ladder | `niva-bupa-complaint-escalation` | |
| 12 | todo | HDFC Ergo: grievance officer and claim-rejected ladder | `hdfc-ergo-complaint-escalation` | |
| 13 | todo | ICICI Lombard: grievance officer and claim-rejected ladder | `icici-lombard-complaint-escalation` | |
| 14 | todo | Axis Bank: escalation matrix and nodal officer, then RBI CMS | `axis-bank-complaint-escalation` | |
| 15 | todo | Kotak Mahindra Bank: escalation matrix and nodal officer | `kotak-bank-complaint-escalation` | |
| 16 | todo | IndusInd Bank: escalation matrix and nodal officer | `indusind-bank-complaint-escalation` | |
| 17 | todo | Amazon India: complaint escalation and the consumer route | `amazon-india-complaint-escalation` | Use Amazon's own grievance officer page; National Consumer Helpline official page. |
| 18 | todo | Flipkart: complaint escalation and the consumer route | `flipkart-complaint-escalation` | |
| 19 | todo | Zomato / Swiggy: complaint escalation | `zomato-swiggy-complaint-escalation` | |
| 21 | todo | RERA Maharashtra / Karnataka: how to file a complaint | `rera-complaint-maharashtra-karnataka` | Possibly split into two pages. |

(The brief's "Next 10" line lists 11 items because it ends with two RERA states. They are kept as one row and may be split.)

## Ideas added by the builder (not in the brief; lower priority)

| Status | Page | Notes |
|--------|------|-------|
| todo | Life insurance claim rejected: what to do (LIC and private insurers) | Same ladder; reuse verified rules. Also check IRDAI rules specific to life claims. |
| todo | Motor insurance claim rejected: what to do | Check surveyor/claim timelines from the IRDAI Protection of Policyholders circular. |
| todo | Insurance Ombudsman: how to track and what happens after you file | Uses CIO pages. |
| done | Complaint deadline calculator (tool) | Published 2026-10-24: https://rudracodeshere.github.io/where-to-complain/complaint-deadline-calculator/ . Insurance + RBI only. |


## Standing on-page rules from br grower (2026-10-24)
- Each guide needs at least 3 internal links in from other pages.
- No per-city Ombudsman pages (0 searches).
- Cluster owners: see /workspace/boring-realty/growth-playbook.md; never build a page that competes with an existing owner page.

## PF section (from br scout pick 02, picks/02-pf-claim-fixer.md), added 2026-10-25
Built as a /pf/ hub on this site, interleaved after #22 NCH and #23 CPGRAMS, roughly every 3rd night. Follow the accuracy rules in the pick brief.
| PF1 | todo | EPFO grievance: how to file and escalate on EPFiGMS | `epfo-grievance-complaint` | Bing "epfo grievance" 346/12 wks. Official epfigms.gov.in + EPFO circulars only. Links: CPGRAMS, consumer court. 2026-10-28: epfindia.gov.in and its Citizen Charter PDF return 403 from the box (CloudFront); EPFiGMS opens but publishes no time limits. Needs another official source before building. |
| PF2 | todo | PF claim status: what each status means and what to do | `pf-claim-status-meaning` | Bing "pf claim status" 128. Only statuses shown on official EPFO pages. |
| PF3 | todo | PF claim rejected: common reasons and fixes | `pf-claim-rejected-reasons` | Only reasons published by EPFO. |
