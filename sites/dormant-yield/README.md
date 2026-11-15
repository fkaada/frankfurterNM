# Dormant Yield (dormantyield.com)

Static site for people who control the assets of closed or closing UK and US companies. It is owned by Kaada Nordic MarTech (org. no. 936 289 835) and acts as an independent referrer to micro1.

- `public/` is what Vercel serves: HTML, self-hosted fonts and images, one CSS file and one JS file. No cookies and no third-party requests.
- `content/` holds the text pages (privacy, legal, 404). Rebuild them with `python3 scripts/page.py`.
- `tests/check.mjs` is the compliance gate and runs as the Vercel build:
  - the micro1 link must be byte-exact
  - banned words and amounts fail
  - owner details are required on every page
  - no external resources
  - the CSP must stay strict
  - on production, every partner fact must be verified
- `docs/` has the plan (`PLAN.md`), hosting, DNS, firewall and launch steps (`DEPLOY.md`), and the outreach domain (`OUTREACH-DOMAIN.md`).

```bash
npm test               # preview checks
npm run launch-check   # what production enforces
python3 -m http.server -d public 8080
```
