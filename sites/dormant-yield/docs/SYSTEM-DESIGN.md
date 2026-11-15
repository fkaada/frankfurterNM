# Dormant Yield: system design

Status 15 November 2026. Release e4c2629 is served on Vercel; the custom domains are waiting for GoDaddy DNS.

## 1. Requirements

**Functional**
- Explain to officeholders of closed or closing companies how records can be licensed, what to check first and who has authority.
- Cover the big four in detail (UK, US, Canada, Australia), plus the other six countries micro1 lists.
- List 30 industries; cover all 50 in the expanded view and search.
- Run the fit check entirely in the browser.
- Send qualified visitors to micro1 through one locked referral link.

**Non-functional**
- Compliance before features:
  - every link byte-exact
  - fee disclosure next to every link
  - no amounts
  - "independent referrer" wording
  - no cookies and no third-party requests
- Fast on phones, readable by AI search, accessible by keyboard, both colour themes.
- Very low traffic expected (a professional audience in the thousands). Cost should be close to the Vercel Pro seat.

**Constraints**
- One owner (Fred) and AI staff who draft only.
- No back end, no forms that post anywhere, no personal data collected.

## 2. High-level design

```
 data/industries.py ─┐
 content/*.html ─────┤  scripts/build.py   ┌─ public/*.html (64 pages)
 RIGHTS, COUNTRIES ──┘  (Python, no deps) ─┼─ public/assets/index.json (search)
                                           └─ public/sitemap.xml
                                   │
                         tests/check.mjs  (launch gate, Node, no deps)
                                   │  fails the build on any compliance breach
                                   ▼
 GitHub (public repo) ──codeload tarball @ pinned SHA──► Vercel build (deploy.sh)
                                                          │
                                         Vercel CDN + headers (CSP, HSTS…) + Firewall
                                                          │
            dormantyield.com ◄── .co.uk, www (308) · dormantyields.com (307 → home)
                                                          │
                                   Visitor ──► "Apply with micro1" (rel=sponsored) ──► micro1
```

**Data flow:** there is no runtime data. The page fetches only one same-origin file, `index.json`, and only when someone uses search. Attribution lives in micro1's referral portal.

## 3. Deep dive

- **Content model:**
  - `INDS` holds slug, name, group, records, care, why, key and listed.
  - `RIGHTS` holds four countries × roles, control, dissolved, privacy and register.
  - Every claim about micro1 renders with a dated source chip (`data-verify-status`).
- **Launch gate** (`tests/check.mjs`):
  - locked link and its JS copy
  - banned words and amounts
  - owner details on every page
  - no inline style or script
  - no external resources
  - internal links and sitemap URLs resolve
  - duplicate IDs
  - JSON-LD parses
  - CSP not weakened
  - pending facts block production
- **Caching:**
  - HTML: `max-age=0, must-revalidate` (Vercel default).
  - `/assets/*`: fingerprinted with `?v=hash` and served `immutable` for a year.
  - Fonts: immutable. Images: a week.
- **Menu:** native `<details>`, so it works without JS. JS adds four things: one menu open at a time, Escape, closing on an outside click, and closing on resize. Desktop has three panels; screens 960 px and narrower get one sheet with accordions. Search IDs are unique per instance.
- **Errors:**
  - A static 404 page.
  - If the search index fails to load, search returns an empty list.
  - The fit check without JS shows a default answer.

## 4. Scale and reliability

- Static files on Vercel's CDN, so load is not a design concern at this audience size. A sudden spike costs bandwidth only.
- **Firewall** (to be set in the dashboard): Bot Protection on Log, then Challenge; AI bots on Log; probe paths denied; rate limit of 300 requests per 5 minutes per IP.
- **Failure modes:**

| Failure | Effect | Mitigation |
|---|---|---|
| GitHub tarball fetch fails | Build fails | The previous production deploy stays live |
| Gate fails | Build fails | Nothing bad ships |
| DNS misconfigured | vercel.app still serves | Domain config check in DEPLOY.md |

- **Monitoring:** none yet. Proposal: a weekly scheduled read of the live site (status codes, link byte-match, headers), plus Vercel's deployment-failure emails. Cookieless analytics only on Fred's yes.

## 5. Trade-offs

| Decision | Upside | Cost | Revisit when |
|---|---|---|---|
| Static generator in Python, generated HTML committed | No dependencies, reviewable diffs, Vercel only serves files | Two languages (Python build, Node gate) | A CMS or non-technical editors are needed |
| Deploy via pinned tarball | Works without a Vercel–GitHub link; reproducible | A manual redeploy per release | GitHub is connected (then the build command becomes `node tests/check.mjs`) |
| Site in a subfolder of frankfurterNM | Only repo writable from this session | Unrelated repo, public | Fred creates fkaada/dormant-yield (`git subtree split`) |
| Strict CSP, no inline code | XSS resistance, no tracking | Every style lives in CSS files | Never weaken it; add hashes if inline code is ever unavoidable |
| No analytics | No consent banner, privacy by design | No on-site funnel data | First outreach month ends: add cookieless analytics with Fred's yes |
| Rights guides for four countries only | Accuracy over breadth | The six other countries get "take local advice" | Counsel reviews other jurisdictions |
| 50 templated industry pages | Coverage for search and AI answers | Thin-content risk | Search Console shows pages not indexed: merge or enrich the weakest |

## 6. What to revisit as it grows

1. Connect GitHub to Vercel and move the site into its own repo.
2. Add a scheduled live check (link byte-match, headers, status codes) with alerts to BrainMate.
3. Enrich the top 10 industry pages from real officeholder questions (FAQ-style, no quotes without permission).
4. Get counsel review for the other six countries before writing guides for them.
5. If volume grows: per-page OG images and a contact route that stays cookieless (mailto plus copy button).
