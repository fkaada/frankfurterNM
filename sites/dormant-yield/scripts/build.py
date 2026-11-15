"""Static site generator for dormantyield.com. No dependencies (Python 3.9+).

Run from sites/dormant-yield:  python3 scripts/build.py
Writes public/*.html, public/industries/*.html, public/assets/index.json and public/sitemap.xml.
Generated files are committed, so Vercel only serves public/ and runs tests/check.mjs.
"""
import hashlib, html, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
sys.path.insert(0, str(ROOT / "data"))
import industries as db  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
import v4  # noqa: E402

SITE = "https://dormantyield.com"
# Locked by Fred in writing, 15 November 2026 (replaces the /register/ link). Byte-exact. Never edit.
MICRO1 = "https://company.micro1.ai/get-started?referralCode=b6089a23-af54-4292-8bb3-070423a40fc0"
REVIEWED = "15 November 2026"
LASTMOD = "2026-11-15"

COUNTRIES = [  # micro1 defunct-company track, company.micro1.ai/get-started, checked 15 November 2026
    # (code, name, big four, page slug)
    ("gb", "United Kingdom", True, "united-kingdom"), ("us", "United States", True, "united-states"),
    ("ca", "Canada", True, "canada"), ("au", "Australia", True, "australia"),
    ("in", "India", False, None), ("sg", "Singapore", False, None), ("ie", "Ireland", False, None),
    ("nl", "Netherlands", False, None), ("de", "Germany", False, None), ("fr", "France", False, None),
]
BIG4 = [c for c in COUNTRIES if c[2]]

# Rights guidance for the big four. General information only; statute references are the anchor for each claim.
RIGHTS = {
    "gb": dict(
        roles="Administrators and liquidators (licensed insolvency practitioners)",
        control=["In administration or liquidation, the officeholder controls the company's assets and decides whether to license its records.",
                 "In a members' voluntary liquidation, the liquidator appointed by the members holds that authority."],
        dissolved=["Once a company is dissolved, its remaining property generally passes to the Crown as bona vacantia (Companies Act 2006, s.1012).",
                   "Nobody can usually license those records unless the company is first restored to the register."],
        privacy=["Personal data stays covered by UK GDPR and the Data Protection Act 2018 whoever holds it.",
                 "Employee and customer data must be removed or properly de-identified before anything is shared."],
        register="Companies House shows status, dissolution dates and officeholder appointments; The Gazette publishes insolvency notices."),
    "us": dict(
        roles="Chapter 7 and Chapter 11 trustees, debtors in possession, receivers and assignees for the benefit of creditors",
        control=["In bankruptcy, the trustee (or the debtor in possession) sells estate assets, and sales outside the ordinary course need court approval (11 U.S.C. §363).",
                 "In an assignment for the benefit of creditors, the assignee holds the assets under state law."],
        dissolved=["Outside bankruptcy, state law on dissolved corporations decides who can still act for the company and for how long.",
                   "If the company went through bankruptcy, check whether the records were sold with the business assets."],
        privacy=["If the company's privacy policy restricted transfers of personal information, the court may appoint a consumer privacy ombudsman before a sale (11 U.S.C. §§332, 363(b)(1)).",
                 "State privacy laws and contracts with customers can still apply to personal data in the records."],
        register="Court dockets (PACER) show trustee appointments and sale orders; state registries show dissolution."),
    "ca": dict(
        roles="Licensed insolvency trustees, receivers and court-appointed monitors",
        control=["In bankruptcy, the licensed insolvency trustee holds and realises the company's property (Bankruptcy and Insolvency Act).",
                 "In receiverships and CCAA restructurings, asset sales usually need court approval (Companies' Creditors Arrangement Act, s.36)."],
        dissolved=["When a federal corporation is dissolved, property it had not disposed of generally vests in the Crown (Canada Business Corporations Act, s.228). Provincial laws are similar.",
                   "Revival of the corporation may be possible before anything can be licensed."],
        privacy=["PIPEDA, and provincial laws in Quebec, British Columbia and Alberta, continue to apply to personal information in the records.",
                 "PIPEDA allows limited sharing for business transactions only under conditions (s.7.2), so take advice before any sample leaves your hands."],
        register="The Office of the Superintendent of Bankruptcy lists insolvency records; Corporations Canada and provincial registries show status."),
    "au": dict(
        roles="Liquidators, voluntary administrators and receivers (registered liquidators)",
        control=["In liquidation or voluntary administration, the liquidator or administrator controls the company's property (Corporations Act 2001).",
                 "Receivers act for the secured creditor over the assets they were appointed to."],
        dissolved=["When a company is deregistered, its remaining property vests in ASIC (Corporations Act 2001, s.601AD).",
                   "Reinstatement may be possible before anything can be licensed."],
        privacy=["The Privacy Act 1988 and the Australian Privacy Principles may apply to personal information in the records.",
                 "Employee records and customer data need removing or de-identifying before any sample is shared."],
        register="ASIC registers and published notices show company status and external administrators."),
}

e = html.escape
EXT = ' <span aria-hidden="true">↗</span><span class="sr"> (opens in a new tab)</span>'


LISTED = {  # 20 industries shown alongside the 10 key niches (30 listed); all 50 are in the expanded view and search
    "accounting-firms", "legal-practices", "management-consulting", "it-services-msp", "cybersecurity", "telecoms",
    "media-publishing", "real-estate-proptech", "insurance-brokers", "wealth-management", "lending",
    "manufacturing", "automotive-ev", "food-beverage", "restaurants-hospitality", "hotels-travel", "hydrogen-fuel-cells",
    "life-sciences-services", "energy-utilities", "marketplaces-platforms"}
assert len(LISTED) == 20


def industries():
    out = []
    for slug, name, group, records, care, why in db.KEY:
        out.append(dict(slug=slug, name=name, group=group, records=records, care=care, why=why, key=True, listed=True))
    for slug, name, group, records, care in db.OTHER:
        out.append(dict(slug=slug, name=name, group=group, records=records, care=care, why="", key=False, listed=slug in LISTED))
    assert len(out) == 50, len(out)
    assert sum(i["listed"] for i in out) == 30, sum(i["listed"] for i in out)
    assert len({i["slug"] for i in out}) == 50
    return out


INDS = industries()


def phrase(name):
    """'E-commerce and D2C retail' -> 'e-commerce and D2C retail': lower-case ordinary words, keep acronyms."""
    words = name.split(" (")[0].split()
    return " ".join(w if any(c.isupper() for c in w[1:]) or w.isupper() else w.lower() for w in words)


def with_article(np):
    first = np.split()[0]
    an = np[0].lower() in "aeio" or first in ("HR", "IT", "MSPs", "EV")
    return ("an " if an else "a ") + np


def asset(rel):
    """Fingerprinted URL for long-lived caching: /assets/site.css?v=<hash of contents>."""
    h = hashlib.sha256((PUB / rel.lstrip("/")).read_bytes()).hexdigest()[:10]
    return f"{rel}?v={h}"


def apply_link(label="Apply with micro1", cls="btn btn-sprout"):
    return (f'<a class="{cls}" data-partner="micro1-company" href="{MICRO1}" target="_blank" '
            f'rel="sponsored noopener noreferrer">{e(label)}{EXT}</a>')


def chip(src, checked):
    return f'<span class="src" data-verify="{e(src)}" data-verify-status="verified" title="Checked {e(checked)}">{e(src)} · {e(checked)}</span>'


def header():
    key = [i for i in INDS if i["key"]]
    more = [i for i in INDS if i["listed"] and not i["key"]]
    groups = sorted({i["group"] for i in more})
    li = lambda i: f'<li><a href="/industries/{i["slug"]}">{e(i["name"])}</a></li>'
    key_html = "".join(f'<li><a href="/industries/{i["slug"]}"><strong>{e(i["name"])}</strong><span>{e(i["group"])}</span></a></li>' for i in key)
    more_html = "".join(f'<div><p class="mega-sub">{e(g)}</p><ul>{"".join(li(i) for i in more if i["group"] == g)}</ul></div>' for g in groups)
    flag = lambda c: f'<img class="fl" src="/img/flags/{c}.svg" width="24" height="24" alt="">'
    big = "".join(f'<li><a href="/guides/{slug}">{flag(c)}<strong>{e(n)}</strong><span>SME and enterprise guides</span></a></li>' for c, n, _, slug in BIG4)
    rest = "".join(f'<li><a href="/guides/{v4.GUIDE_SLUG[c]}">{flag(c)}{e(n)}</a></li>' for c, n, b, _ in COUNTRIES if not b)
    guides = ('<li><a href="/guides"><strong>Country guides</strong><span>SMEs and enterprises, ten countries</span></a></li>'
              '<li><a href="/how-it-works"><strong>How it works</strong><span>Four steps, what to prepare</span></a></li>'
              '<li><a href="/tools/readiness"><strong>Readiness checklist</strong><span>Twenty checks, tick and copy</span></a></li>'
              '<li><a href="/officeholders"><strong>For officeholders</strong><span>Administrators, liquidators, trustees</span></a></li>'
              '<li><a href="/blog"><strong>Insights</strong><span>Bona vacantia, ABCs, 363 sales and more</span></a></li>'
              '<li><a href="/faq"><strong>FAQ</strong><span>Fees, records, employees, timing</span></a></li>'
              '<li><a href="/about"><strong>About us</strong><span>Who we are and how we are paid</span></a></li>')
    search = lambda sid: (f'<div class="mega-search"><label for="q-{sid}">Search 50 industries and all pages</label>'
                          f'<input id="q-{sid}" class="q" type="search" placeholder="e.g. logistics, SaaS, liquidator, Canada" autocomplete="off" data-results="r-{sid}">'
                          f'<ul id="r-{sid}" class="results" aria-live="polite"></ul></div>')
    ind_inner = (f'<div class="mega-cols"><div><p class="mega-h">Ten key niches</p><ul class="mega-list">{key_html}</ul></div>'
                 f'<div><p class="mega-h">Twenty more, by sector</p><div class="mega-groups">{more_html}</div></div></div>'
                 f'<a class="mega-all" href="/industries">All 50 industries, with filter →</a>')
    ind_panel = search("ind") + ind_inner
    cty_panel = (f'<div class="mega-cols"><div><p class="mega-h">The big four · main focus</p><ul class="mega-list">{big}</ul></div>'
                 f'<div><p class="mega-h">Also on micro1\'s list</p><ul class="mega-flags">{rest}</ul>'
                 f'<p class="small muted">Short guides. Rules differ; take local advice.</p></div></div>'
                 f'<a class="mega-all" href="/guides">All country guides →</a>')
    gd_panel = f'<ul class="mega-list one">{guides}</ul>'
    return f'''<a class="skip" href="#top">Skip to content</a>
<div class="masthead">
<aside class="disclose" aria-label="Referral disclosure">
  <div class="wrap"><span class="badge">Independent referrer</span><span class="d-long">Not affiliated with micro1. If a company applies through our link and a qualifying deal completes, micro1 may pay us a referral fee. You pay nothing.</span><span class="d-short">We may earn a referral fee from micro1. You pay nothing.</span><a href="/about">How we are paid</a></div>
</aside>
<header class="top">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Dormant Yield, home">
      <svg width="30" height="30" viewBox="0 0 40 40" aria-hidden="true"><path class="mk-a" d="M5 4l11 8v16c0 4 2 7 4 8-7 0-15-5-15-14V4z"/><path class="mk-a" d="M35 4l-11 8v16c0 4-2 7-4 8 7 0 15-5 15-14V4z"/><path class="mk-b" d="M14 20l5 4v9l-3-2c-1-1-2-2-2-4v-7zM26 20l-5 4v9l3-2c1-1 2-2 2-4v-7z"/></svg>
      <span>Dormant <b>Yield</b></span>
    </a>
    <nav class="nav-d" aria-label="Main">
      <a href="/how-it-works">How it works</a>
      <details class="mega" data-mega><summary>Industries</summary><div class="mega-panel wide">{ind_panel}</div></details>
      <details class="mega" data-mega><summary>Countries</summary><div class="mega-panel">{cty_panel}</div></details>
      <details class="mega" data-mega><summary>Guides</summary><div class="mega-panel narrow">{gd_panel}</div></details>
    </nav>
    <div class="hdr-end">
      <a class="btn btn-primary hdr-cta" href="/#fit-check">Check your fit</a>
      <details class="mega nav-m" data-mega>
        <summary aria-label="Menu"><span class="burger" aria-hidden="true"><i></i><i></i><i></i></span><span class="m-label">Menu</span></summary>
        <div class="mega-panel sheet">
          {search("m")}
          <details class="acc"><summary>Industries</summary><div class="acc-body">{ind_inner}</div></details>
          <details class="acc"><summary>Countries</summary><div class="acc-body">{cty_panel}</div></details>
          <details class="acc" open><summary>Guides</summary><div class="acc-body">{gd_panel}</div></details>
        </div>
      </details>
    </div>
  </div>
</header>
</div>'''


FOOTER_T = '''<footer>
  <div class="wrap">
    <a class="brand" href="/"><span>Dormant <b>Yield</b></span></a>
    <address class="owner">Kaada Nordic MarTech · Org. no. 936 289 835 (Norway) · <a href="mailto:contact@nordicmartech.com">contact@nordicmartech.com</a></address>
    <p>An independent referrer, not affiliated with, endorsed by or acting for micro1. If a company applies through our link and a qualifying deal completes, micro1 may pay us a referral fee. Companies pay us nothing.</p>
    <p>General information, not legal, tax or insolvency advice. Partner criteria are micro1's and can change; check micro1's current terms before relying on anything here. Page reviewed REVIEWED_DATE.</p>
    <nav class="row foot-nav" aria-label="Footer"><a href="/guides">Country guides</a><a href="/blog">Insights</a><a href="/tools/readiness">Readiness checklist</a><a href="/how-it-works">How it works</a><a href="/officeholders">For officeholders</a><a href="/industries">Industries</a><a href="/countries">Countries</a><a href="/faq">FAQ</a><a href="/about">About</a><a href="/privacy">Privacy</a><a href="/legal">Legal and disclosures</a></nav>
  </div>
</footer>
<script src="{JS}" data-index="{IDX}" defer></script>'''


def footer():
    return (FOOTER_T.replace("REVIEWED_DATE", REVIEWED)
            .replace("{JS}", asset("/assets/site.js")).replace("{IDX}", asset("/assets/index.json")))


def page(path, title, desc, body, jsonld=None, robots="index, follow", canonical=True, og_image="/img/og.jpg"):
    url = SITE + ("/" if path == "" else "/" + path)
    ld = f'<script type="application/ld+json">\n{json.dumps(jsonld, ensure_ascii=False, indent=1)}\n</script>\n' if jsonld else ""
    can = f'<link rel="canonical" href="{url}">\n' if canonical else ""
    doc = f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{can}<meta name="robots" content="{robots}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Dormant Yield">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Dormant Yield: records from closed and closing companies, licensed responsibly">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0E4A3A">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/fonts/plus-jakarta-sans-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/dm-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset('/assets/site.css')}">
{ld}</head>
<body>
{header()}
<main id="top">
{body.strip()}
</main>
{footer()}
</body>
</html>
'''
    out = PUB / ("index.html" if path == "" else f"{path}.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    return out


ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "Kaada Nordic MarTech", "alternateName": "Dormant Yield",
       "url": SITE + "/", "email": "contact@nordicmartech.com",
       "identifier": {"@type": "PropertyValue", "propertyID": "Norwegian organisation number", "value": "936 289 835"},
       "address": {"@type": "PostalAddress", "addressCountry": "NO"}}


def crumbs(*items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": n + 1, "name": name, "item": SITE + url} for n, (name, url) in enumerate(items)]}


# ---------- home ----------
FAQ = [
    ("Do I pay anything?", "No. We charge nothing. Any referral fee is paid by micro1 and is disclosed on this page."),
    ("Will you see our records?", "No. Records go only to the buyer, under its own agreement, after you have signed. Never send records to us or to anyone who asks for them before a contract."),
    ("The company was struck off years ago. Can I still do this?", "In the UK, a dissolved company's property generally passes to the Crown until the company is restored to the register, so nobody can usually license its records directly. Restoration is possible in some cases; speak to a solicitor first. In the US it depends on state law and whether the company went through bankruptcy."),
    ("What about employee data?", "Employee and HR records are the most sensitive part of company data. Expect them to be excluded or properly de-identified, and check whether consent or notice is needed before anything is shared."),
    ("How long does it take?", "micro1 says it reviews and approves the data within 30 days, then pays within 30 days of invoice. Confirming who holds the rights can take longer than either."),
    ("I was a director, not the officeholder. Can I apply?", "Usually not. While a company is in administration, liquidation or bankruptcy, the officeholder controls its assets. Pass this page to them."),
    ("Which countries are covered?", "micro1's defunct-company track lists companies based in the United States, the United Kingdom, Canada, India, Australia, Singapore, Ireland, the Netherlands, Germany and France. Our rights guides cover the big four in detail: the UK, the US, Canada and Australia. Elsewhere, take local advice."),
    ("Does this work in Canada?", "Yes, micro1 lists Canada. In a bankruptcy the licensed insolvency trustee usually decides; a dissolved federal corporation's remaining property generally vests in the Crown until it is revived. See our Canada guide at dormantyield.com/countries/canada."),
    ("Does this work in Australia?", "Yes, micro1 lists Australia. In liquidation or voluntary administration the liquidator or administrator decides; a deregistered company's property vests in ASIC until it is reinstated. See our Australia guide at dormantyield.com/countries/australia."),
    ("Which industries qualify?", "micro1 lists its defunct-company track as open to all industries. Records need to be in English, and the company needs 30 or more employees at its peak."),
    ("Our company is still trading. Is this for us?", "No. This site covers closed and closing companies only. Operating companies can read data.nordicmartech.com."),
    ("Why mention the referral fee so often?", "Because you should know who benefits before you click."),
]


def fill(body):
    """Shared placeholders for content pages."""
    big = "".join(
        f'<li class="main"><a href="/countries/{slug}"><img src="/img/flags/{c}.svg" width="30" height="20" alt=""><span>{e(n)}</span><em>Main focus</em></a></li>'
        for c, n, _, slug in BIG4)
    rest = "".join(f'<li><img src="/img/flags/{c}.svg" width="30" height="20" alt=""><span>{e(n)}</span></li>' for c, n, b, _ in COUNTRIES if not b)
    rights4 = "".join(
        f'<div><h3><img src="/img/flags/{c}.svg" width="24" height="16" alt=""> {e(n)}</h3><ul>'
        f'<li>{e(RIGHTS[c]["control"][0])}</li><li>{e(RIGHTS[c]["dissolved"][0])}</li></ul>'
        f'<a class="more" href="/countries/{slug}">Full {e(n)} guide →</a></div>'
        for c, n, _, slug in BIG4)
    niches = "".join(
        f'<li><a href="/industries/{i["slug"]}"><span class="g">{e(i["group"])}</span><strong>{e(i["name"])}</strong><span class="w">{e(i["why"])}</span></a></li>'
        for i in INDS if i["key"])
    opts_c = "".join(
        f'<label><input type="radio" name="country" id="c-{c}" value="{c}"{" checked" if c == "gb" else ""}><span><img src="/img/flags/{c}.svg" width="18" height="12" alt=""> {e(n)}</span></label>'
        for c, n, _, _ in COUNTRIES) + '<label><input type="radio" name="country" id="c-other" value="other"><span>Elsewhere</span></label>'
    faq_short = "".join(f'<details><summary>{e(q)}</summary><p>{a}</p></details>' for q, a in faq_html()[:6])
    body = (body.replace("{{PILLS}}", v4.flag_pills()).replace("{{FLAGS}}", big + rest).replace("{{RIGHTS4}}", rights4).replace("{{NICHES}}", niches)
            .replace("{{COUNTRY_OPTS}}", opts_c).replace("{{FAQ}}", faq_short).replace("{{APPLY}}", apply_link())
            .replace("{{CHIP_GS}}", chip("company.micro1.ai/get-started", "15 Nov 2026"))
            .replace("{{CHIP_DATA}}", chip("micro1.ai/data", "10 Nov 2026")))
    assert "{{" not in body, "unfilled placeholder"
    return body


def faq_html():
    link = f'<a href="https://data.nordicmartech.com" target="_blank" rel="noopener noreferrer">data.nordicmartech.com{EXT}</a>'
    return [(q, e(a).replace("data.nordicmartech.com", link)) for q, a in FAQ]


def home():
    ld = {"@context": "https://schema.org", "@graph": [
        ORG,
        {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "Dormant Yield", "inLanguage": "en-GB", "publisher": {"@id": SITE + "/#org"}},
    ]}
    page("", "Dormant Yield",
         "For officeholders of closed and closing companies in the UK, US, Canada and Australia: how licensing business records works and where to apply.",
         fill((ROOT / "content/home.html").read_text()), ld)


def faq_page():
    items = "".join(f'<details><summary>{e(q)}</summary><p>{a}</p></details>' for q, a in faq_html())
    body = f"""<section><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>FAQ</span></nav>
<span class="eyebrow">FAQ</span>
<h1>Questions officeholders <em>actually</em> ask</h1>
<p class="lede">Short answers. Where the law matters, we point you to the right adviser rather than guess.</p>
<div>{items}</div>
<div class="row mt20"><a class="btn btn-primary" href="/#fit-check">Check your fit</a><a class="btn btn-ghost" href="/how-it-works">How it works</a></div>
</div></section>"""
    ld = {"@context": "https://schema.org", "@graph": [ORG,
          {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
          crumbs(("Home", "/"), ("FAQ", "/faq"))]}
    page("faq", "FAQ | Dormant Yield", "Answers on fees, records, employee data, timing, countries and who can apply for micro1's defunct-company track.", body, ld)


def country_pages():
    for c, n, _, slug in BIG4:
        r = RIGHTS[c]
        ul = lambda xs: "<ul>" + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul>"
        others = "".join(f'<li><a href="/countries/{s2}"><img src="/img/flags/{c2}.svg" width="24" height="16" alt=""> {e(n2)}</a></li>' for c2, n2, _, s2 in BIG4 if c2 != c)
        body = f"""<section class="ind-hero"><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/countries">Countries</a> / <span>{e(n)}</span></nav>
<span class="eyebrow"><img class="eflag" src="/img/flags/{c}.svg" width="24" height="16" alt=""> {e(n)} · main focus</span>
<h1>Closed and closing companies in {e(n)}: who can license the <em>records</em></h1>
<p class="lede">Records only become an asset for creditors when someone with authority can license them. Here is how that works in {e(n)}, in plain terms.</p>
<p class="small muted">Who usually decides: {e(r["roles"])}.</p>
</div></section>
<section class="pt0"><div class="wrap country-grid">
<div><h2 class="h3">While the company is in a formal process</h2>{ul(r["control"])}</div>
<div><h2 class="h3">After dissolution or deregistration</h2>{ul(r["dissolved"])}</div>
<div><h2 class="h3">Personal data</h2>{ul(r["privacy"])}</div>
<div><h2 class="h3">Where to check status</h2><p>{e(r["register"])}</p></div>
</div></section>
<section class="pt0"><div class="wrap stack">
<h2>micro1 lists {e(n)}</h2>
<dl class="facts">
<div><dt>Country</dt><dd>{e(n)} is one of ten countries on micro1's defunct-company track {chip("company.micro1.ai/get-started", "15 Nov 2026")}</dd></div>
<div><dt>Size</dt><dd>30+ peak employees {chip("company.micro1.ai/get-started", "15 Nov 2026")}</dd></div>
<div><dt>Language</dt><dd>English {chip("company.micro1.ai/get-started", "15 Nov 2026")}</dd></div>
</dl>
<div class="row mt12"><a class="btn btn-primary" href="/#fit-check">Check your fit</a>{apply_link()}</div>
<p class="small muted">Referral link. As an independent referrer we may receive a fee from micro1 if a qualifying deal completes. You pay nothing. micro1 decides what qualifies.</p>
<p class="small muted">General information, not legal advice. Insolvency and privacy rules depend on the facts{ {"gb": "", "us": " and the state", "ca": " and the province", "au": " and the state"}[c] }. Take advice before agreeing anything.</p>
<h2 class="h3 mt20">Other big-four guides</h2><ul class="tags">{others}<li><a href="/countries">All ten countries</a></li></ul>
</div></section>"""
        ld = {"@context": "https://schema.org", "@graph": [ORG,
              {"@type": "WebPage", "name": f"{n}: who can license a closed company's records", "url": f"{SITE}/countries/{slug}", "inLanguage": "en-GB", "dateModified": LASTMOD},
              crumbs(("Home", "/"), ("Countries", "/countries"), (n, f"/countries/{slug}"))]}
        page(f"countries/{slug}", f"{n}: who can license closed company records | Dormant Yield",
             f"{n}: who controls a closed or closing company's records, what happens after dissolution, personal data rules, and micro1's published criteria.", body, ld)

    cards = "".join(
        f'<li><a href="/countries/{slug}"><img src="/img/flags/{c}.svg" width="36" height="24" alt=""><strong>{e(n)}</strong><span>{e(RIGHTS[c]["roles"])}</span><em>Main focus · full guide</em></a></li>'
        for c, n, _, slug in BIG4)
    rest = "".join(f'<li><img src="/img/flags/{c}.svg" width="30" height="20" alt=""><span>{e(n)}</span></li>' for c, n, b, _ in COUNTRIES if not b)
    body = f"""<section><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>Countries</span></nav>
<span class="eyebrow">Countries</span>
<h1>Ten countries. The big four <em>first.</em></h1>
<p class="lede">micro1's defunct-company track lists companies based in ten countries {chip("company.micro1.ai/get-started", "15 Nov 2026")}. We focus on the UK, the US, Canada and Australia, where our rights guidance is detailed.</p>
<ul class="country-cards">{cards}</ul>
<h2 class="h3 mt20">Also on micro1's list</h2>
<ul class="flags">{rest}</ul>
<p class="small muted">India, Singapore, Ireland, the Netherlands, Germany and France have their own insolvency and data protection rules. We do not give guidance for them; take local advice.</p>
</div></section>"""
    ld = {"@context": "https://schema.org", "@graph": [ORG, crumbs(("Home", "/"), ("Countries", "/countries"))]}
    page("countries", "Countries | Dormant Yield", "The ten countries on micro1's defunct-company track, with full rights guides for the UK, US, Canada and Australia.", body, ld)


# ---------- industries ----------
def industry_pages():
    for i in INDS:
        related = [r for r in INDS if r["group"] == i["group"] and r["slug"] != i["slug"]][:4]
        rel = "".join(f'<li><a href="/industries/{r["slug"]}">{e(r["name"])}</a></li>' for r in related)
        why = (f'<div class="callout"><span class="pill">Key niche</span><p>{e(i["why"])}</p></div>' if i["key"] else "")
        extra = ""
        if i["slug"] in db.SYSTEMS:
            sysl = "".join(f"<li>{e(x)}</li>" for x in db.SYSTEMS[i["slug"]])
            extra = (f'<section class="pt0"><div class="wrap ind-deep">'
                     f'<div class="card-soft"><img src="/img/icon-1.webp" width="56" height="59" alt=""><h2 class="h3">Systems to look for</h2><ul>{sysl}</ul><p class="small muted">Export while admin access still works.</p></div>'
                     f'<div class="card-soft"><img src="/img/icon-2.webp" width="56" height="59" alt=""><h2 class="h3">SMEs (30 to 249 staff)</h2><ul><li>{e(v4.SIZES["sme"]["tips"][0])}</li><li>{e(v4.SIZES["sme"]["tips"][1])}</li></ul></div>'
                     f'<div class="card-soft"><img src="/img/icon-4.webp" width="56" height="59" alt=""><h2 class="h3">Enterprises (250+ staff)</h2><ul><li>{e(v4.SIZES["enterprise"]["tips"][0])}</li><li>{e(v4.SIZES["enterprise"]["tips"][1])}</li></ul></div>'
                     f'</div></section>')
        body = f'''<section class="ind-hero"><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/industries">Industries</a> / <span>{e(i["name"])}</span></nav>
<span class="eyebrow">{e(i["group"])}</span>
<h1>{e(i["name"])}: records from closed and closing <em>companies</em></h1>
<p class="lede">If you control the assets of {e(with_article(phrase(i["name"])))} company in administration, liquidation or bankruptcy, its operational records may be licensable. Here is what usually exists, what needs care and how to check fit.</p>
{why}
</div></section>
<section class="pt0"><div class="wrap two">
<div><h2 class="h3">What usually exists</h2><ul>{"".join(f"<li>{e(x)}</li>" for x in i["records"])}</ul></div>
<div><h2 class="h3">What needs care</h2><ul>{"".join(f"<li>{e(x)}</li>" for x in i["care"])}</ul><p class="small muted">Employee and HR records always need the most care, whatever the industry.</p></div>
</div></section>
{extra}
<section class="pt0"><div class="wrap stack">
<h2>micro1's published criteria</h2>
<dl class="facts">
<div><dt>Track</dt><dd>Defunct Company Data Partnership: companies that are no longer operating {chip("company.micro1.ai/get-started", "15 Nov 2026")}</dd></div>
<div><dt>Size</dt><dd>30+ peak employees {chip("company.micro1.ai/get-started", "15 Nov 2026")}</dd></div>
<div><dt>Industries</dt><dd>Open to all industries {chip("company.micro1.ai/get-started", "15 Nov 2026")}</dd></div>
<div><dt>Language</dt><dd>English {chip("company.micro1.ai/get-started", "15 Nov 2026")}</dd></div>
</dl>
<div class="row mt12"><a class="btn btn-primary" href="/#fit-check">Check your fit</a>{apply_link()}</div>
<p class="small muted">Referral link. As an independent referrer we may receive a fee from micro1 if a qualifying deal completes. You pay nothing. micro1 decides what qualifies.</p>
</div></section>
<section class="pt0"><div class="wrap stack"><h2 class="h3">Related industries</h2><ul class="tags">{rel}<li><a href="/industries">All 50 industries</a></li></ul></div></section>
{v4.next_cards("ready", "guides", "blog")}'''
        ld = {"@context": "https://schema.org", "@graph": [ORG,
              {"@type": "WebPage", "name": f'{i["name"]}: records from closed and closing companies', "url": f'{SITE}/industries/{i["slug"]}', "inLanguage": "en-GB", "isPartOf": {"@id": SITE + "/#site"}, "dateModified": LASTMOD},
              crumbs(("Home", "/"), ("Industries", "/industries"), (i["name"], f'/industries/{i["slug"]}'))]}
        page(f'industries/{i["slug"]}', f'{i["name"]}: closed company records | Dormant Yield',
             f'{i["name"]}: which records from closed and closing companies may be licensable, what needs care, and micro1\'s criteria.',
             body, ld, og_image="/img/og.jpg")

    groups = sorted({i["group"] for i in INDS}, key=lambda g: (-sum(1 for i in INDS if i["group"] == g and i["key"]), g))
    def card(i):
        return (f'<li data-name="{e(i["name"].lower())} {e(i["group"].lower())}"><a href="/industries/{i["slug"]}">'
                f'<span class="g">{e(i["group"])}</span><strong>{e(i["name"])}</strong>'
                f'{"<em>Key niche</em>" if i["key"] else ""}</a></li>')
    listed = [i for i in INDS if i["listed"]]
    extra = [i for i in INDS if not i["listed"]]
    sections = "".join(
        f'<section class="grp" data-group><h2 class="h3">{e(g)}</h2><ul class="cards">{"".join(card(i) for i in listed if i["group"] == g)}</ul></section>'
        for g in groups if any(i["group"] == g for i in listed))
    sections += (f'<details class="more-ind" id="more-industries"><summary>Show 20 more industries (all 50)</summary>'
                 f'<section class="grp" data-group><ul class="cards">{"".join(card(i) for i in extra)}</ul></section></details>')
    body = f'''<section><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>Industries</span></nav>
<span class="eyebrow">Industries</span>
<h1>Thirty industries listed. Fifty <em>covered.</em></h1>
<p class="lede">micro1 lists its defunct-company track as open to all industries. Thirty industries are listed here, with ten key niches marked: record-rich sectors where closing companies often had 30 or more staff. Open the expanded view, or search, for all 50.</p>
<div class="mega-search page-search"><label for="q-page">Filter industries</label><input id="q-page" class="q" type="search" placeholder="Type to filter, e.g. energy" autocomplete="off" data-filter=".grp li"></div>
<p class="small muted" id="filter-count" aria-live="polite"></p>
{sections}
</div></section>'''
    ld = {"@context": "https://schema.org", "@graph": [ORG,
          {"@type": "CollectionPage", "name": "Industries", "url": SITE + "/industries", "inLanguage": "en-GB", "isPartOf": {"@id": SITE + "/#site"}},
          crumbs(("Home", "/"), ("Industries", "/industries"))]}
    page("industries", "Industries | Dormant Yield",
         "Guides for 50 industries: which records from closed and closing companies may be licensable, what needs care, and ten key niches.",
         body, ld, og_image="/img/og.jpg")


# ---------- text pages ----------
def text_pages():
    for f in sorted((ROOT / "content").glob("*.html")):
        if f.stem == "home":
            continue
        meta, body = f.read_text().split("\n---\n", 1)
        m = dict(l.split(": ", 1) for l in meta.strip().splitlines())
        wrapcls = m.get("wrap", "wrap doc stack")
        page(f.stem, m["title"], m["description"], fill(f'<section><div class="{wrapcls}">{body}</div></section>'),
             robots=m.get("robots", "index, follow"), canonical=m.get("canonical", "yes") == "yes")


def index_and_sitemap():
    idx = [{"t": "Home", "u": "/", "k": "dormant yield closed company records licence creditors"},
           {"t": "Fit check", "u": "/#fit-check", "k": "fit check eligibility qualify 30 employees"},
           {"t": "Rights check", "u": "/#rights", "k": "rights authority bona vacantia restoration trustee liquidator administrator 363 ombudsman"},
           {"t": "Countries", "u": "/countries", "k": " ".join(n.lower() for _, n, _, _ in COUNTRIES)},
           {"t": "FAQ", "u": "/faq", "k": "questions fee employee data struck off director timing canada australia"},
           {"t": "How it works", "u": "/how-it-works", "k": "steps process timeline prepare sample review contract de-identify"},
           {"t": "For officeholders", "u": "/officeholders", "k": "administrator liquidator trustee receiver insolvency practitioner assignee creditors"},
           {"t": "Country guides", "u": "/guides", "k": "guide sme enterprise steps " + " ".join(n.lower() for _, n, _, _ in COUNTRIES)},
           {"t": "Readiness checklist", "u": "/tools/readiness", "k": "checklist readiness prepare tool authority records people contracts"},
           {"t": "Insights", "u": "/blog", "k": "blog articles insights bona vacantia abc 363 chapter 7 restoration"},
           {"t": "About us", "u": "/about", "k": "about independent referrer fee contact kaada nordic martech"},
           {"t": "Privacy", "u": "/privacy", "k": "privacy gdpr cookies data protection"},
           {"t": "Legal and disclosures", "u": "/legal", "k": "legal disclosure referral fee affiliation"},
           {"t": "All industries", "u": "/industries", "k": "industries sectors list"}]
    for c, n, big, slug in COUNTRIES:
        if big:
            idx.append({"t": f"{n}: SME guide", "u": f"/guides/{slug}/sme", "g": "Guide · main focus", "k": f"{n.lower()} sme small medium guide steps"})
            idx.append({"t": f"{n}: enterprise guide", "u": f"/guides/{slug}/enterprise", "g": "Guide · main focus", "k": f"{n.lower()} enterprise large guide steps"})
        else:
            idx.append({"t": f"{n}: guide", "u": f"/guides/{v4.GUIDE_SLUG[c]}", "g": "Guide", "k": n.lower() + " " + " ".join(v4.LOCAL[c].values()).lower()})
    for f in sorted((ROOT / "content/blog").glob("*.html")):
        m = dict(l.split(": ", 1) for l in f.read_text().split("\n---\n", 1)[0].strip().splitlines())
        idx.append({"t": m["h1"], "u": f"/blog/{f.stem}", "g": "Insight", "k": m["description"].lower()})
    for c, n, _, slug in BIG4:
        idx.append({"t": f"{n}: rights guide", "u": f"/countries/{slug}", "g": "Country · main focus",
                    "k": " ".join([n.lower(), RIGHTS[c]["roles"].lower()] + [x.lower() for x in RIGHTS[c]["control"]])})
    for i in INDS:
        idx.append({"t": i["name"], "u": f'/industries/{i["slug"]}', "g": i["group"] + (" · Key niche" if i["key"] else ""),
                    "k": " ".join([i["group"]] + i["records"]).lower()})
    (PUB / "assets/index.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    urls = (["/", "/how-it-works", "/officeholders", "/industries", "/countries", "/faq", "/about", "/privacy", "/legal", "/tools/readiness", "/blog"]
            + v4.guide_urls() + [f"/blog/{f.stem}" for f in sorted((ROOT / "content/blog").glob("*.html"))]
            + [f"/countries/{slug}" for _, _, _, slug in BIG4] + [f'/industries/{i["slug"]}' for i in INDS])
    sm = "".join(f'  <url><loc>{SITE}{"" if u == "/" else u}{"/" if u == "/" else ""}</loc><lastmod>{LASTMOD}</lastmod></url>\n' for u in urls)
    (PUB / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')


if __name__ == "__main__":
    v4.init(globals())
    index_and_sitemap()
    home()
    v4.guides()
    v4.readiness()
    v4.blog()
    faq_page()
    country_pages()
    industry_pages()
    text_pages()
    print(f"built: home, industries index, {len(INDS)} industry pages, text pages, index.json, sitemap.xml")
