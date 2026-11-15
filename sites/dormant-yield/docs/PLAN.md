# Dormant Yield: research, recommendation and plan

Prepared 15 November 2026. UK English. **Approved by Fred 15 November 2026, with the edits in section 0.** Status: preview. Nothing is published.

## 0. Edits from Fred's review (15 November 2026)

1. "Independent referrer" everywhere; never "partner". The site says "not affiliated with micro1".
2. No fee or deal amounts on any site or public document, and no anecdotes such as deal stories from community groups. The $ range was removed from the page, and the build fails on any amount.
3. Fonts are self-hosted (DM Sans, Plus Jakarta Sans, OFL). Nothing loads from Google or any third party.
4. Owner details are on every page: Kaada Nordic MarTech, org. no. 936 289 835, contact@nordicmartech.com. The site has Privacy and Legal pages.
5. Every micro1 fact is marked `pending` until Fred click-checks it. Production deploys fail while any fact is pending.
6. The US airline bankruptcy line is removed because it had no source.
7. Closed firms: **officeholders only** (ruling Q14). Former directors are told to pass the page on and get no apply button.
8. Framing: "a possible extra asset for creditors", with no pressure (Q33).
9. Domains: dormantyield.com is the main site, dormantyield.co.uk redirects to it, and dormantyields.com is for outreach email only (web visitors are redirected). See `DEPLOY.md` and `OUTREACH-DOMAIN.md`.
10. Hosting: Vercel Pro with DNS at GoDaddy and the Vercel Firewall. No cookies, and a strict security policy.
11. Outreach follows the current rulings (send cap, follow-up sequence v2, country rules) rather than the generic advice in section 4.

## 1. micro1 referral terms: what we found

The session's network blocks micro1.ai, so these facts come from micro1's own pages **as indexed by web search**. None has been click-checked. Every figure on the site carries `data-verify` and must be click-checked by Fred before going live.

| Fact | Source page | Confidence |
|---|---|---|
| micro1 runs a track for **defunct companies** ("no longer operating") | micro1.ai/company-referral | Search snippet, needs click-check |
| Defunct track: **30+ employees** (one snippet also says "operations in 10+ countries", which is unclear) | micro1.ai/company-referral | Search snippet, needs click-check |
| Company compensation range for approved data packages | micro1.ai/company-referral | Search snippet. **Never quoted: no amounts on any site.** |
| Referrer reward for defunct deals (fixed amount up to a deal size, then a percentage) | micro1.ai/company-referral | Search snippet. Internal only, never published. |
| Operating-company referral headline differs across company-referral, creators and forum pages | company-referral, creators, forum | Conflicting. Do not quote. |
| Sub-affiliate: extra 20% of approved company referral bonuses | micro1.ai/sub-affiliate | Search snippet. Not relevant to this MVP. |
| Bonus not earned on registration, application or signature alone; paid after data transfer and approval, then a payout-approval process | company-referral, referral-terms | Search snippet |
| Attribution: company must register through your link; attribution **cannot be changed retroactively** if it registered elsewhere first | company-referral | Search snippet |
| Referral terms last updated **14 October 2026** (Legal Center) | micro1.ai/legal/referral-terms | Search snippet |
| Conduct rules: truthful, transparent, non-misleading; no impersonating micro1 or acting as its agent or spokesperson; **no guarantees about compensation**; no deceptive or coercive tactics; use your own email domain for company outreach | micro1.ai/legal/referral-terms | Search snippet |
| micro1 may withhold, delay, reduce or refuse payouts, and change eligibility at any time | micro1.ai/legal/referral-terms | Search snippet |
| Payment wording (verified 10 November 2026): "micro1 reviews and approves the data within 30 days, then pays within 30 days of invoice" | micro1.ai/data | Verified per master rules v5.4 |

**This changes master rule 2 (v5.4).** The 10 November check said the closed-company track had gone from micro1.ai/data. It now appears on micro1.ai/company-referral. If Fred confirms that by clicking through, the closed-company copy can come back to data.nordicmartech.com too.

Still unknown, and worth checking on the full referral-terms page: rules on paid ads and brand bidding, email or cold-outreach rules beyond the domain point, cookie window or attribution length, payment method, tax forms, minimum payout and how geography is handled.

## 2. Closed firms only, or operating and closed?

**Recommendation: Dormant Yield covers closed and closing firms only. Operating firms go to data.nordicmartech.com.**

Why:
1. **The brand only makes sense for closed firms.** "Dormant" and "legacy records" sound wrong to a CEO whose company is trading. Adding operating firms would blur the message and set up a weaker copy of data.nordicmartech.com.
2. **It avoids cannibalising your own site.** Two sites after the same operating-company audience would split links, search signals and trust. One site per audience lets both rank.
3. **The audience is different and easier to find.** UK administrators and liquidators are listed by The Gazette and Companies House; US bankruptcy trustees are on public court rolls. That is a small, professional and findable audience that already sells assets for a living.
4. **The economics look better, if confirmed.** The reported defunct-deal referral terms are higher than the operating track's headline.

**One refinement that matters more than closed vs operating: aim at *closing* firms, not long-dead ones.**
- **Best fit:** in administration, liquidation or Chapter 7/11, or a solvent wind-down. The records usually still exist, and someone clearly has authority to sell.
- **Weak fit:** dissolved or struck off. In the UK, remaining property passes to the Crown as *bona vacantia* (Companies Act 2006, s.1012) until the company is restored. Records are often lost when software subscriptions lapse. The fit check warns about this rather than sending people to apply.
- **US nuance:** a bankruptcy sale needs court approval, and where the privacy policy restricted transfers a consumer privacy ombudsman may be appointed (11 U.S.C. §§332, 363(b)(1)). Employee data draws objections in bankruptcy data sales.

## 3. Measuring it

micro1's link must stay byte-exact, so no UTMs on it. Measure on our side and read the result in micro1's referral portal (refer.micro1.ai).

| Stage | Metric | Where it comes from |
|---|---|---|
| Reach | Visits by channel | Cookieless analytics (Cloudflare Web Analytics or Plausible). No consent banner needed under PECR because nothing is stored on the device. |
| Engagement | Fit checks completed, by result (go / warn / out of scope) | One custom event per result. No personal data. |
| Intent | Clicks on "Apply with micro1", by section | Outbound click event on `[data-partner]` |
| Conversion | Registrations attributed to you | micro1 referral portal |
| Outcome | Approved deals, payouts | micro1 referral portal |
| Quality | Share of "go" results versus warnings | If most visitors get warnings, the traffic is wrong |

Channel attribution without touching the link: clean landing paths such as `/l/linkedin`, `/l/ip` (insolvency practitioners), `/l/trustee`, each serving the same page. Same rule as data.nordicmartech.com: **needs Fred's written yes.**

### Targets (assumptions to test, not forecasts)
- First 90 days: 25 conversations with officeholders or former directors → 5 applications → 1 approved deal.
- Leading indicator to watch weekly: fit checks with a "go" result per 100 visits. Below 10 means the wrong audience is arriving.
- Stop or rethink signal: after 60 days, zero applications from 15+ real conversations.

## 4. 30 / 60 / 90 days

**Days 1–30: verify and launch quietly**
- Fred click-checks every `data-verify` fact on micro1's pages and the locked link (code intact).
- Read the full referral terms for ad, email and brand-bidding rules.
- Choose hosting (static: Cloudflare Pages or Vercel) and a domain. Add cookieless analytics.
- Write three guides that answer real questions: "Can a liquidator license company data?", "Bona vacantia and company records", "Employee data in a business wind-down".

**Days 31–60: professional audience**
- Build a list of UK insolvency practitioners from public appointments in The Gazette, and US Chapter 7 trustees from court panels. One personal, plain email each from Fred's own domain, no attachments, no link in the first message. Follow PECR and UK GDPR (B2B corporate addresses, legitimate interest assessment, clear opt-out) and CAN-SPAM.
- Offer a 15-minute explainer call, not a pitch.

**Days 61–90: review**
- Compare channels in the portal. Double down on the one that produced applications.
- Turn repeated questions into FAQ entries.
- Decide whether closed-company copy also belongs on data.nordicmartech.com.

## 5. Not sounding salesy

1. **Lead with the obstacle, not the money.** Open with "who holds the rights" and the four checks. Ranges appear once, low down, attributed, labelled "indicative, not an offer".
2. **Disclose the fee before anyone asks.** Top strip, next to every link, and in the footer. Say plainly that the company pays nothing.
3. **Tell people when it is not for them.** The fit check says "not a fit" or "check authority first" and sends operating firms elsewhere. Saying no earns trust for the yes.
4. **Never quote your own reward** on company-facing pages. It is irrelevant to them and reads as self-interest.
5. **One link, labelled, and late.** No referral link in the hero. It appears after the reader has learned something.
6. **Use the officeholder's language.** "Realise assets for creditors", "authority", "restoration", "estate". Not "monetise", "hidden goldmine", "passive income".
7. **Banned words, kept from the data.nordicmartech.com rules:** guarantee, unlock, unlimited, zero risk, 100%, capital, "worth millions". The logo tagline "Unlocking value in dormant data" is fine on artwork, but the site copy avoids it.
8. **Answer first, link second, pitch never** in communities. On LinkedIn or Reddit, answer the question. Link to a guide only if it answers better than your reply. Never post the raw referral link.
9. **Outreach: no link in message one.** Ask whether data was part of the asset schedule. Send the page only if they reply.
10. **Do not overclaim our role.** "Independent referrer." Never "partner", "partner of", "on behalf of" or "representing" micro1 (their terms and our rules forbid it).

## 6. Open items for Fred

- [ ] Click-check micro1.ai/company-referral: defunct track, 30+ threshold, "10+ countries" meaning.
- [ ] Click-test the locked micro1 company link with the code intact.
- [ ] Confirm the company referral link is the right one for defunct companies (or whether micro1 issues a separate defunct link).
- [ ] Read the full referral terms for ad, email and brand-bidding rules.
- [ ] Yes or no on the `/l/*` landing paths.
- [ ] Domain and hosting.
- [ ] Say "publish" when ready. Nothing goes live before that.
