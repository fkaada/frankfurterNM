# Dormant Yield: post-launch sprint (v5) backlog

Agreed 15 November 2026: launch the live release first, then customise pages only where Google Search Console shows traction. The live site is release 89d4101, called "v4" in the repo; this sprint is **v5**, to avoid two "v4"s.

## Gate to start v5
- dormantyield.com has served for at least 4 weeks with the GSC Domain property verified (see task P1).
- GSC Performance, filtered to /industries/ and /guides/, shows which pages earn impressions. Customise the top 5–10 by impressions. Merge or `noindex` pages with zero impressions after 8 weeks.

## 1. Theme toggle: vanilla, not React
The site is static HTML with a strict CSP and no framework. React, Tailwind and lucide would add a build system and an extra library, and the CSP would block Tailwind's CDN. The proposed `useEffect` version also flashes the wrong theme on load, because it runs after first paint.

Plan, about 30 lines:
- `/assets/theme.js` loads in `<head>` without `defer`, before the CSS paints. It reads `localStorage.theme` and sets `<html data-theme>`. The CSS already supports `[data-theme]`.
- A `<button>` in the header with `aria-pressed`, and a sun/moon SVG drawn inline in HTML (no icon library).
- Privacy: a theme preference in localStorage is storage on the device. It is a user-requested setting, but the Privacy page currently says nothing is stored, so add one line about it before shipping.

## 2. Mega menu enrichment: corrected
Keep the "featured guide" idea. Fix these first:
- **Remove "1.25x premium in the AI training market"**: an unsourced number, banned by the no-amounts and no-unsourced-claims rules.
- **Retitle "High-Yield Data Assets"**: hype. Use "Most-read guide" and choose it from GSC data.
- **Remove "Digital Health" as a featured niche**: health information is excluded entirely. Healthtech appears only as "business records only".
- **Keep the SVG flags**: emoji flags render as two letters on Windows.
- **Keep the existing slugs**: `/countries/united-kingdom`, `/industries/software-saas`. Renaming to `uk` and `saas` breaks indexed URLs and needs 301s for no gain.

## 3. Custom industry copy: extend the data file, no routing rewrite
The generator is already data-driven (`data/industries.py` plus `SYSTEMS`), so dynamic routing in `/industries/[slug].js` (Next.js) is not needed. Add optional fields per slug: `headline`, `records_extra`, `exclusions_extra`, `context`. `build.py` renders them only when present.

Copy rules for `context`:
- No unsourced market claims. "One of the most liquid assets in a wind-down" is out.
- Describe the records, not their value.
- Every factual claim gets a dated source.

Sample, rewritten within the rules:
- headline: "Software and SaaS: records from closed and closing companies"
- records_extra: "Resolved Jira tickets with full bug timelines", "Pull request discussions with personal data removed", "Roadmap and design pages in Confluence"
- exclusions_extra: "Personal data scrubbed from support tickets", "Source code only if licences and escrow allow"

## 4. Not in v5 unless data asks
- Rewriting all 50 industry pages
- New countries beyond micro1's ten
