# Dormant Yield: handover

15 November 2026. One page for Fred and the team: what exists, how to change it, and what is left to do by hand.

## What exists
- **Live site:** https://dormantyield.com (live since 16 November 2026). Vercel project `dormant-yield`, team Nordic MarTech.
- **Pages (94):**
  - home
  - how it works
  - for officeholders
  - 14 country guides: SME and enterprise for the UK, US, Canada and Australia, plus one short guide for each of India, Singapore, Ireland, the Netherlands, Germany and France
  - 4 rights guides
  - 50 industry pages: 30 listed, 10 of them key niches
  - 8 insight articles
  - readiness checklist, glossary, FAQ, about, privacy, legal, 404
- **The one micro1 link** (locked by Fred, 16 Nov 11:24): `https://company.micro1.ai/register/?referralCode=b6089a23-af54-4292-8bb3-070423a40fc0`
- **Quality at handover:**
  - Lighthouse (phone): performance 96–99; accessibility, best practices and SEO 100.
  - axe: 0 violations.
  - 276 page loads at 360, 768 and 1280 px: 0 failures.
  - Works without JavaScript.
  - No cookies and no third-party requests.

## How to change things
| Change | Where | Then |
|---|---|---|
| Home copy | `content/home.html` | build, check, deploy |
| Privacy, legal, about, how it works, officeholders, glossary | `content/*.html` | same |
| Terms auto-linked to the glossary | `GLOSS_LINKS` in `scripts/build.py` | same |
| Diagrams (records sieve, who-gains flow) | `sieve()`, `flow()` in `scripts/v4.py` | same |
| An insight article | add `content/blog/<slug>.html` (copy an existing header block) | same, then `node scripts/og.js` for its share card |
| Industry facts and systems | `data/industries.py` | same |
| Rights guides (big four) | `RIGHTS` in `scripts/build.py` | same, plus a lawyer check |
| Country guides | `scripts/v4.py` (`SIZES`, `LOCAL`) | same |
| Styles and behaviour | `public/assets/site.css`, `public/assets/site.js` | same |

**Commands**, run from `sites/dormant-yield`:
```bash
python3 scripts/build.py          # regenerate pages, search index and sitemap
node scripts/og.js                # share cards (only when titles change; needs Playwright)
node tests/check.mjs --launch     # the gate: must say ok
```

**Deploy:** open a pull request into `main`. Vercel builds a preview; merging to `main` deploys to production automatically (GitHub connected 16 Nov). After it is live, run `node scripts/live-check.mjs` from `main`. Never re-point the domains to a branch build (see docs/DEPLOY.md).

## Rules the gate enforces (the build fails if broken)
- The micro1 link is byte-exact everywhere, and every page with it carries the "Referral link" disclosure.
- None of these words: "referral partner", "partner of micro1", "guarantee", "unlock", "unlimited", "zero risk", "100%".
- No amounts ($, £, € or "k/m/million") and no salesy words.
- Owner details on every page.
- No external scripts, styles or images; no inline code (strict CSP).
- One h1 per page, alt text on every image, unique titles, descriptions present.
- Internal links, sitemap URLs and share images all resolve.
- Production deploys fail if any partner fact is still marked pending.

## Manual tasks
**The source of truth is Fred's Task Board (lane "Dormant Yield"), not this file.** A copy here goes stale within hours. At 16 November 2026 the lane had finished the launch work (DNS, GitHub, firewall, mailbox, no-mail records, postal address, lawyer read, content approval) and was open on: warm-up start (P11), Postmaster Tools re-test (P12), UK GDPR Article 27 decision (P13), bot-log review on 23 November (P14), the lawyer's contact details for the P7 cover email, the SuperPlug bundle (P16), and a look at CodeFactor's two findings on PR #8.

## Home page order (v7)
Hero, then a numbered path: 1 who this is for, 2 what is licensed, 3 how it works, 4 fit check, 5 checks before you talk to a buyer, then countries, sectors, who gains, 6 apply, our role, further reading, FAQ.

## Known limits
- Statute citations come from Claude's knowledge and await the lawyer read (P7).
- The 50 industry pages are built from one template; customise only those with Search Console traction (docs/V5-BACKLOG.md).
- The site lives in the frankfurterNM repo. A separate `fkaada/dormant-yield` repo is recommended (steps in docs/DEPLOY.md).
- The Claude–Vercel connection cannot change the firewall.
- No analytics; attribution comes from micro1's referral portal only.
