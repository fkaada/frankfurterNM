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

SITE = "https://dormantyield.com"
# Locked by Fred in writing, 15 November 2026 (replaces the /register/ link). Byte-exact. Never edit.
MICRO1 = "https://company.micro1.ai/get-started?referralCode=b6089a23-af54-4292-8bb3-070423a40fc0"
REVIEWED = "15 November 2026"
LASTMOD = "2026-11-15"

COUNTRIES = [  # micro1 defunct-company track, company.micro1.ai/get-started, checked 15 November 2026
    ("gb", "United Kingdom", True), ("us", "United States", True), ("ca", "Canada", False),
    ("in", "India", False), ("au", "Australia", False), ("sg", "Singapore", False),
    ("ie", "Ireland", False), ("nl", "Netherlands", False), ("de", "Germany", False), ("fr", "France", False),
]

e = html.escape
EXT = ' <span aria-hidden="true">↗</span><span class="sr"> (opens in a new tab)</span>'


def industries():
    out = []
    for slug, name, group, records, care, why in db.KEY:
        out.append(dict(slug=slug, name=name, group=group, records=records, care=care, why=why, key=True))
    for slug, name, group, records, care in db.OTHER:
        out.append(dict(slug=slug, name=name, group=group, records=records, care=care, why="", key=False))
    assert len(out) == 50, len(out)
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
    key = "".join(
        f'<li><a href="/industries/{i["slug"]}"><strong>{e(i["name"])}</strong><span>{e(i["group"])}</span></a></li>'
        for i in INDS if i["key"])
    return f'''<a class="skip" href="#top">Skip to content</a>
<div class="disclose" role="note">
  <div class="wrap">Independent referrer, not affiliated with micro1. If a company applies to micro1 through our link and a qualifying deal completes, micro1 may pay us a referral fee. You pay nothing. <a href="/#our-role">How we are paid</a></div>
</div>
<header class="top">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Dormant Yield, home">
      <svg width="30" height="30" viewBox="0 0 40 40" aria-hidden="true"><path class="mk-a" d="M5 4l11 8v16c0 4 2 7 4 8-7 0-15-5-15-14V4z"/><path class="mk-a" d="M35 4l-11 8v16c0 4-2 7-4 8 7 0 15-5 15-14V4z"/><path class="mk-b" d="M14 20l5 4v9l-3-2c-1-1-2-2-2-4v-7zM26 20l-5 4v9l3-2c1-1 2-2 2-4v-7z"/></svg>
      <span>Dormant <b>Yield</b></span>
    </a>
    <nav class="links" aria-label="Main">
      <a href="/#how">How it works</a>
      <details class="mega">
        <summary><span class="d-only">Industries</span><span class="m-only">Menu</span></summary>
        <div class="mega-panel">
          <div class="m-only mega-sections">
            <a href="/#how">How it works</a><a href="/#rights">Rights check</a><a href="/#countries">Countries</a><a href="/#fit-check">Fit check</a><a href="/#faq">FAQ</a>
          </div>
          <div class="mega-search">
            <label for="q-menu">Search 50 industries and pages</label>
            <input id="q-menu" class="q" type="search" placeholder="e.g. logistics, SaaS, liquidator" autocomplete="off" data-results="r-menu">
            <ul id="r-menu" class="results" aria-live="polite"></ul>
          </div>
          <p class="mega-h">Ten key niches</p>
          <ul class="mega-list">{key}</ul>
          <a class="mega-all" href="/industries">All 50 industries →</a>
        </div>
      </details>
      <a href="/#countries" class="d-only">Countries</a>
      <a href="/#faq" class="d-only">FAQ</a>
    </nav>
    <a class="btn btn-primary hdr-cta" href="/#fit-check">Check your fit</a>
  </div>
</header>'''


FOOTER_T = '''<footer>
  <div class="wrap">
    <a class="brand" href="/"><span>Dormant <b>Yield</b></span></a>
    <address class="owner">Kaada Nordic MarTech · Org. no. 936 289 835 (Norway) · <a href="mailto:contact@nordicmartech.com">contact@nordicmartech.com</a></address>
    <p>An independent referrer, not affiliated with, endorsed by or acting for micro1. If a company applies through our link and a qualifying deal completes, micro1 may pay us a referral fee. Companies pay us nothing.</p>
    <p>General information, not legal, tax or insolvency advice. Partner criteria are micro1's and can change; check micro1's current terms before relying on anything here. Page reviewed REVIEWED_DATE.</p>
    <nav class="row foot-nav" aria-label="Footer"><a href="/industries">Industries</a><a href="/privacy">Privacy</a><a href="/legal">Legal and disclosures</a></nav>
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
    ("Which countries are covered?", "micro1's defunct-company track lists companies based in the United States, the United Kingdom, Canada, India, Australia, Singapore, Ireland, the Netherlands, Germany and France. Our rights guidance covers the UK and the US in detail; elsewhere, take local advice."),
    ("Which industries qualify?", "micro1 lists its defunct-company track as open to all industries. Records need to be in English, and the company needs 30 or more employees at its peak."),
    ("Our company is still trading. Is this for us?", "No. This site covers closed and closing companies only. Operating companies can read data.nordicmartech.com."),
    ("Why mention the referral fee so often?", "Because you should know who benefits before you click."),
]


def home():
    flags = "".join(
        f'<li class="{"main" if m else ""}"><img src="/img/flags/{c}.svg" width="30" height="20" alt=""><span>{e(n)}</span>{"<em>Main focus</em>" if m else ""}</li>'
        for c, n, m in COUNTRIES)
    niches = "".join(
        f'<li><a href="/industries/{i["slug"]}"><span class="g">{e(i["group"])}</span><strong>{e(i["name"])}</strong><span class="w">{e(i["why"])}</span></a></li>'
        for i in INDS if i["key"])
    opts_c = "".join(
        f'<label><input type="radio" name="country" id="c-{c}" value="{c}"{" checked" if c == "gb" else ""}><span><img src="/img/flags/{c}.svg" width="18" height="12" alt=""> {e(n)}</span></label>'
        for c, n, _ in COUNTRIES) + '<label><input type="radio" name="country" id="c-other" value="other"><span>Elsewhere</span></label>'
    faq = "".join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in FAQ)
    faq = faq.replace("data.nordicmartech.com.</p>", f'<a href="https://data.nordicmartech.com" target="_blank" rel="noopener noreferrer">data.nordicmartech.com{EXT}</a>.</p>')
    ld = {"@context": "https://schema.org", "@graph": [
        ORG,
        {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "Dormant Yield", "inLanguage": "en-GB", "publisher": {"@id": SITE + "/#org"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
    ]}
    body = (ROOT / "content/home.html").read_text()
    body = (body.replace("{{FLAGS}}", flags).replace("{{NICHES}}", niches).replace("{{COUNTRY_OPTS}}", opts_c)
            .replace("{{FAQ}}", faq).replace("{{APPLY}}", apply_link())
            .replace("{{CHIP_GS}}", chip("company.micro1.ai/get-started", "15 Nov 2026"))
            .replace("{{CHIP_DATA}}", chip("micro1.ai/data", "10 Nov 2026")))
    assert "{{" not in body, "unfilled placeholder"
    page("", "Dormant Yield",
         "For administrators, liquidators and bankruptcy trustees of closed and closing companies: how licensing business records to AI developers works, what to check first and where to apply.",
         body, ld)


# ---------- industries ----------
def industry_pages():
    for i in INDS:
        related = [r for r in INDS if r["group"] == i["group"] and r["slug"] != i["slug"]][:4]
        rel = "".join(f'<li><a href="/industries/{r["slug"]}">{e(r["name"])}</a></li>' for r in related)
        why = (f'<div class="callout"><span class="pill">Key niche</span><p>{e(i["why"])}</p></div>' if i["key"] else "")
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
<section class="pt0"><div class="wrap stack"><h2 class="h3">Related industries</h2><ul class="tags">{rel}<li><a href="/industries">All 50 industries</a></li></ul></div></section>'''
        ld = {"@context": "https://schema.org", "@graph": [ORG,
              {"@type": "WebPage", "name": f'{i["name"]}: records from closed and closing companies', "url": f'{SITE}/industries/{i["slug"]}', "inLanguage": "en-GB", "isPartOf": {"@id": SITE + "/#site"}, "dateModified": LASTMOD},
              crumbs(("Home", "/"), ("Industries", "/industries"), (i["name"], f'/industries/{i["slug"]}'))]}
        page(f'industries/{i["slug"]}', f'{i["name"]}: closed company records | Dormant Yield',
             f'{i["name"]} companies in administration, liquidation or bankruptcy: which operational records may be licensable to AI developers, what needs care, and micro1\'s published criteria.',
             body, ld, og_image="/img/og.jpg")

    groups = sorted({i["group"] for i in INDS})
    def card(i):
        return (f'<li data-name="{e(i["name"].lower())} {e(i["group"].lower())}"><a href="/industries/{i["slug"]}">'
                f'<span class="g">{e(i["group"])}</span><strong>{e(i["name"])}</strong>'
                f'{"<em>Key niche</em>" if i["key"] else ""}</a></li>')
    sections = "".join(
        f'<section class="grp" data-group><h2 class="h3">{e(g)}</h2><ul class="cards">{"".join(card(i) for i in INDS if i["group"] == g)}</ul></section>'
        for g in groups)
    body = f'''<section><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>Industries</span></nav>
<span class="eyebrow">Industries</span>
<h1>Fifty industries, one set of <em>checks</em></h1>
<p class="lede">micro1 lists its defunct-company track as open to all industries. These guides cover what records usually exist in each and what needs care. Ten are key niches: record-rich sectors where closing companies often have 30 or more staff.</p>
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
        page(f.stem, m["title"], m["description"], f'<section><div class="wrap doc stack">{body}</div></section>',
             robots=m.get("robots", "index, follow"), canonical=m.get("canonical", "yes") == "yes")


def index_and_sitemap():
    idx = [{"t": "Home", "u": "/", "k": "dormant yield closed company records licence creditors"},
           {"t": "Fit check", "u": "/#fit-check", "k": "fit check eligibility qualify 30 employees"},
           {"t": "Rights check", "u": "/#rights", "k": "rights authority bona vacantia restoration trustee liquidator administrator 363 ombudsman"},
           {"t": "Countries", "u": "/#countries", "k": " ".join(n.lower() for _, n, _ in COUNTRIES)},
           {"t": "FAQ", "u": "/#faq", "k": "questions fee employee data struck off director"},
           {"t": "Privacy", "u": "/privacy", "k": "privacy gdpr cookies data protection"},
           {"t": "Legal and disclosures", "u": "/legal", "k": "legal disclosure referral fee affiliation"},
           {"t": "All industries", "u": "/industries", "k": "industries sectors list"}]
    for i in INDS:
        idx.append({"t": i["name"], "u": f'/industries/{i["slug"]}', "g": i["group"] + (" · Key niche" if i["key"] else ""),
                    "k": " ".join([i["group"]] + i["records"]).lower()})
    (PUB / "assets/index.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    urls = ["/", "/industries", "/privacy", "/legal"] + [f'/industries/{i["slug"]}' for i in INDS]
    sm = "".join(f'  <url><loc>{SITE}{"" if u == "/" else u}{"/" if u == "/" else ""}</loc><lastmod>{LASTMOD}</lastmod></url>\n' for u in urls)
    (PUB / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')


if __name__ == "__main__":
    index_and_sitemap()
    home()
    industry_pages()
    text_pages()
    print(f"built: home, industries index, {len(INDS)} industry pages, text pages, index.json, sitemap.xml")
