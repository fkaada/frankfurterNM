# dormantyields.com: outreach sending domain

Purpose: outbound email to officeholders only. It keeps dormantyield.com's reputation separate from cold email. Web visitors are redirected to https://dormantyield.com (see `vercel.json`).

All rules follow Fred's rulings of 14 November 2026: independent referrer, disclosure in every first message, officeholders only, no amounts, no pressure, and a cap of 20 sends a day until the reply rate is at least 8%.

## 1. Mailbox
- One mailbox on a business email provider (Google Workspace or Microsoft 365), for example `fred@dormantyields.com`. Use a real name and real replies; no shared "info@" sender.
- The display name, "Fred Kaada, Dormant Yield", matches the site. The signature carries:
  - Kaada Nordic MarTech
  - org. no. 936 289 835
  - contact@nordicmartech.com
  - https://dormantyield.com
- Never use a micro1 address or domain.

## 2. DNS at GoDaddy (values come from the mail provider)

| Type | Name | Value |
|---|---|---|
| MX | @ | provider's MX hosts |
| TXT | @ | `v=spf1 include:<provider> -all` (one SPF record only) |
| TXT or CNAME | `<selector>._domainkey` | provider's DKIM key (2048-bit) |
| TXT | `_dmarc` | week 1–2: `v=DMARC1; p=none; rua=mailto:contact@nordicmartech.com; adkim=s; aspf=s` → week 3–4: `p=quarantine` → from week 5, if reports are clean: `p=reject` |
| A / CNAME | @ / www | Vercel (redirect only) |

Optional: a custom tracking domain is **not** used. No open or click tracking, which keeps messages plain and avoids pixel consent questions.

## 3. Warm-up (6 weeks, manual, no warm-up networks)

| Week | Sends a day | What |
|---|---|---|
| 1 | 0 to cold contacts | Send 5–10 genuine emails a day to people you know who will reply. Subscribe to two or three newsletters. |
| 2 | 5 | First officeholder emails, hand-picked |
| 3 | 10 | |
| 4 | 15 | |
| 5+ | 20 (cap) | Stay at 20 until the reply rate is at least 8%, as ruled |

- Weekdays only, no weekend sends.
- One message, then follow-ups on the current sequence (v2, 14 November 2026).

Pause the domain if any of these happens:
- bounce rate above 3%
- any spam complaint (one complaint pauses that sequence, per Q97)
- a blocklist hit (check MXToolbox weekly)
- Google Postmaster shows "Bad" reputation

## 4. Message rules (each send)
- Recipient: an officeholder's business address from a public source (The Gazette, court filings). Never former staff. Never scraped from behind log-ins.
- Subject: a question, under 45 characters. Body: under 90 words, one observation and one question, **no link in the first message**.
- The first message carries "I may receive a referral fee".
- Every message has a plain opt-out line ("Reply 'stop' and I won't write again").
- UK: corporate addresses with opt-out under PECR, and a legitimate interest assessment on file. US: CAN-SPAM, including a postal address and opt-out. Canada: no cold email. Australia: consent or conspicuous publication only.
- Agents draft and Fred sends. A data subject or regulator enquiry stops that firm, is logged and is pushed to Fred.

## 5. Measure
Weekly: sends, bounces, replies, positive replies, fit checks and applications, logged per the pipeline stages (contacted → replied → fit-checked → applied → qualifying set-up → paid).
