# Hosting, domains and launch

## Status, 15 November 2026 (release 50ebda2, v6: mobile masthead, content-built visuals, share cards; axe 0 violations): published on Vercel, custom domains wait for GoDaddy DNS

- **Vercel project:** `dormant-yield` in team Nordic MarTech (`prj_1tqOBfFP28DV7CE2L967uOaqeFGL`). Production: https://dormant-yield-nordic-mar-tech.vercel.app (served, launch gate passed: 93 pages, 81 partner links, locked link intact; stress test 276 page loads at 360/768/1280 px, 0 failures).
- **Domains added to the project:** dormantyield.com, www.dormantyield.com, dormantyield.co.uk, www.dormantyield.co.uk, dormantyields.com, www.dormantyields.com. All six still point at GoDaddy parking (3.33.130.190, 15.197.148.33).
- **How it deploys today:** GitHub is not connected to Vercel ("add a Login Connection to your GitHub account"), so production uses `scripts/deploy.sh`: it fetches this repo at a pinned commit and runs the launch gate. Connect GitHub (Vercel → Account Settings → Authentication → GitHub, then Project → Settings → Git → connect `fkaada/frankfurterNM`, root directory `sites/dormant-yield`, build command `node tests/check.mjs`) and pushes deploy automatically.
- **Firewall:** the Vercel connection used here was refused access to the firewall API. Apply section 4 in the dashboard (Project → Firewall), or reconnect the Vercel integration with firewall access and ask Claude again.

### Exact GoDaddy records (values Vercel recommends for this project)

For each of dormantyield.com, dormantyield.co.uk and dormantyields.com:

| Type | Name | Value |
|---|---|---|
| A | @ | 216.198.79.1 |
| A | @ | 64.29.17.1 |
| CNAME | www | a0817a7103b70c8a.vercel-dns-017.com |

Delete the existing parking A records (3.33.130.190 and 15.197.148.33) and any GoDaddy forwarding first. The older values (76.76.21.21 and cname.vercel-dns.com) also still work.


Decided 15 November 2026. Status: **preview**. Nothing goes live without Fred's written "publish".

## 1. Hosting decision: Vercel Pro, DNS stays at GoDaddy

| Option | Verdict |
|---|---|
| **Vercel Pro** | **Chosen.** Matches the BrainMate decision (Claude Code + Vercel). It deploys the static site from Git, gives a preview link for each branch, supports security headers and redirects in `vercel.json`, and its Firewall is included. |
| Vercel Hobby | No. Vercel's fair use terms restrict Hobby to personal, non-commercial use. A referral site is commercial. |
| GoDaddy hosting | No. It is weaker on security headers, has no build checks and no preview deployments. Keep GoDaddy for domain registration and DNS only. |
| Cloudflare Pages | A good alternative, but it would add a second vendor for no gain now. |

**Why keep DNS at GoDaddy rather than move nameservers to Vercel:** dormantyields.com needs email records (MX, SPF, DKIM, DMARC) from the mail provider. Keeping every record at the registrar, with GoDaddy's domain protection on, is simpler and avoids nameserver changes. Vercel only needs A and CNAME records.

## 2. Vercel project setup (Fred, about 15 minutes)

1. Vercel → Add New → Project → import the GitHub repo `fkaada/frankfurterNM`. Better: move this folder into its own repo `dormant-yield` first (see section 6).
2. **Root Directory:** `sites/dormant-yield`. Framework preset: **Other**. The build, output and install settings come from `vercel.json`. Leave the dashboard overrides off.
3. Production branch: `main` of the Dormant Yield repo. Every other branch becomes a password-free preview. Turn on **Deployment Protection → Vercel Authentication** for previews so only the team can see them before launch.
4. Settings → Domains → add all six:
   - `dormantyield.com` (primary)
   - `www.dormantyield.com`
   - `dormantyield.co.uk` and `www.dormantyield.co.uk`
   - `dormantyields.com` and `www.dormantyields.com`

   The redirects are already in `vercel.json`: www and .co.uk send a permanent 308 to the same path on dormantyield.com, and dormantyields.com sends a temporary redirect to the home page. Vercel issues TLS certificates for each domain automatically.
5. **The production build fails on purpose until the micro1 facts are verified.** `tests/check.mjs` runs on every deploy. On production (`VERCEL_ENV=production`) it also fails while any fact still carries `data-verify-status="pending"`.

## 3. GoDaddy DNS records

GoDaddy → My Products → Domain → DNS. Use the **exact values Vercel shows** under Settings → Domains. The values below are Vercel's usual ones; confirm them before saving.

| Domain | Type | Name | Value |
|---|---|---|---|
| dormantyield.com | A | @ | the IP Vercel shows (usually 76.76.21.21) |
| dormantyield.com | CNAME | www | the target Vercel shows (usually cname.vercel-dns.com) |
| dormantyield.co.uk | A | @ | as above |
| dormantyield.co.uk | CNAME | www | as above |
| dormantyields.com | A | @ | as above (web visitors are redirected) |
| dormantyields.com | CNAME | www | as above |

Also do the following:
- Delete GoDaddy's default "Parked" A record and any domain forwarding on all three domains, or they will fight Vercel.
- Add a CAA record on each domain if you want to limit which authorities can issue certificates: `0 issue "letsencrypt.org"` (Vercel's issuer). This is optional.
- dormantyield.com and dormantyield.co.uk send no email. Publish "no mail" records so nobody can spoof them:
  - TXT `@` `v=spf1 -all`
  - TXT `_dmarc` `v=DMARC1; p=reject; adkim=s; aspf=s`
- The mail records for dormantyields.com are in `OUTREACH-DOMAIN.md`.

Check after propagation:
```bash
dig A dormantyield.com +short
dig CNAME www.dormantyield.com +short
curl -sIL https://dormantyield.co.uk | grep -iE '^(HTTP|location)'
curl -sI https://dormantyield.com | grep -iE 'content-security|strict-transport'
```

## 4. Vercel Firewall settings

The site is static: no forms, no API, no log-in and no database. There is very little to attack. Keep the firewall simple and do not block people we want to reach.

| Setting | Choice | Why |
|---|---|---|
| Platform DDoS mitigation | On (automatic, every plan) | Nothing to configure. |
| **Bot Protection** managed ruleset | **Log for 7 days, then Challenge** | Logging first shows whether real visitors (insolvency firms behind corporate proxies) would be challenged. |
| **AI Bots** managed ruleset | **Log** (do not block) | Being cited by AI search helps reach officeholders. Revisit if scraping costs bandwidth. |
| Custom rule: rate limit | 300 requests per minute per IP on `/` → Challenge | Generous for people, stops crude floods. |
| Custom rule: block probes | Path starts with `/wp-`, `/.env`, `/.git`, `/xmlrpc.php`, `/phpmyadmin` → Deny | A static site has none of these; it stops log noise. |
| Attack Challenge Mode | Off, switch on only during an attack | It challenges every visitor. |
| IP blocking | None | Add only in response to a real incident. |

The CLI equivalent once the project is linked (`vercel link`):
```bash
vercel firewall rules add "Block probes" --condition '{"type":"path","op":"pre","value":"/wp-"}' --or --condition '{"type":"path","op":"pre","value":"/.env"}' --or --condition '{"type":"path","op":"pre","value":"/.git"}' --action deny --yes
vercel firewall status
```
Check rule limits for your plan in the Firewall tab. They vary by plan.

**Security headers** are set in `vercel.json` and checked by the build:
- a strict Content Security Policy that loads nothing from third parties (no inline scripts, no inline styles, no framing, no form posts)
- HSTS for 2 years
- nosniff
- frame DENY
- strict-origin referrer
- Permissions-Policy that switches off camera, microphone, location, payment and Topics
- COOP and CORP same-origin

Add `preload` to HSTS and submit to hstspreload.org only after a month without problems.

## 5. Launch phases

1. **Project:** create the Vercel project, connect the repo, set Root Directory. ✅ Repo side done.
2. **Content and compliance:** apply the must-fixes. The build tests guard the locked link, banned words, amounts, owner details and external resources. ✅ Done in code.
3. **Verify:** Fred clicks through micro1.ai/company-referral and micro1.ai/data, confirms each fact, and changes `data-verify-status="pending"` to `"verified"` in `public/index.html` (4 places). He also click-tests the micro1 link with the code intact. ⏳ Fred.
4. **Domains:** add DNS at GoDaddy, add domains in Vercel, check the TLS certificates and the redirects. ⏳ Fred.
5. **Firewall:** apply section 4. Bot Protection on Log. ⏳ Fred or Claude, with Vercel access.
6. **Go live:** only on Fred's written "publish". Merge to `main`; the production build runs the launch checks. Then do a cold read of https://dormantyield.com at 360, 390, 1024 and 1280 px in light and dark. Report the rung: drafted → preview → published → served.

## 6. Recommended: give it its own repo

The site sits in `sites/dormant-yield/` because this session can only write to `fkaada/frankfurterNM`, a currency-API repo. The folder is self-contained, so you can move it into a new repo `fkaada/dormant-yield` with its history:

```bash
git clone https://github.com/fkaada/frankfurterNM dy && cd dy
git checkout claude/micro1-referral-mvp-site-7pgkkd
git subtree split --prefix=sites/dormant-yield -b dy-only
git push https://github.com/fkaada/dormant-yield dy-only:main
```

After that, set Root Directory to `.` in Vercel.
