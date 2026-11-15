"""v4 additions for dormantyield.com: country guides (SME and enterprise), blog, readiness checklist,
contextual 'next step' cards, round flag pills. Imported by build.py; uses its helpers via init()."""
import html, json

e = html.escape
B = {}  # filled by init() with build.py globals


def init(g):
    B.update(g)


# ---------- shared graphics ----------
def flag(c, size=28, cls="fl"):
    return f'<img class="{cls}" src="/img/flags/{c}.svg" width="{size}" height="{size}" alt="">'


def flag_pills(link=True):
    out = []
    for c, n, big, slug in B["COUNTRIES"]:
        href = f"/guides/{slug or GUIDE_SLUG[c]}"
        inner = f'{flag(c)}<span>{e(n)}</span>' + ('<em>Main focus</em>' if big else "")
        out.append(f'<li class="{"main" if big else ""}"><a href="{href}">{inner}</a></li>' if link else f"<li>{inner}</li>")
    return f'<ul class="pills">{"".join(out)}</ul>'


CARDS = {
    "fit": ("/img/icon-1.webp", "Run the fit check", "Five questions, one straight answer. Nothing is sent anywhere.", "/#fit-check"),
    "ready": ("/img/icon-2.webp", "Readiness checklist", "Twenty checks before you talk to any buyer. Tick, copy, share with your team.", "/tools/readiness"),
    "rights": ("/img/icon-3.webp", "Who holds the rights?", "Authority, dissolution and personal data rules in the big four.", "/countries"),
    "guides": ("/img/icon-4.webp", "Country guides", "Step-by-step guides for SMEs and enterprises in ten countries.", "/guides"),
    "blog": ("/img/icon-2.webp", "Insights", "Plain-English articles on bona vacantia, ABCs, 363 sales and more.", "/blog"),
    "how": ("/img/icon-1.webp", "How it works", "Four steps from the vault to a licence.", "/how-it-works"),
}


def next_cards(*keys, title="Next steps"):
    lis = "".join(
        f'<li><a href="{CARDS[k][3]}"><img src="{CARDS[k][0]}" width="72" height="76" alt="" loading="lazy">'
        f'<span class="nc-t">{e(CARDS[k][1])}</span><span class="nc-d">{e(CARDS[k][2])}</span><span class="nc-go" aria-hidden="true">→</span></a></li>'
        for k in keys)
    return f'<section class="pt0"><div class="wrap stack"><h2 class="h3">{e(title)}</h2><ul class="ncards">{lis}</ul></div></section>'


def cta_band(sub=""):
    return (f'<div class="cta-band"><div><p class="cta-h">See if your company fits</p><p>{e(sub or "Two minutes, nothing sent, a straight answer.")}</p></div>'
            f'<div class="row"><a class="btn btn-light" href="/#fit-check">Check your fit</a>{B["apply_link"]("Apply with micro1", "btn btn-sprout")}</div>'
            f'<p class="small">Referral link. As an independent referrer we may receive a fee from micro1 if a qualifying deal completes. You pay nothing.</p></div>')


# ---------- size segments ----------
SIZES = {
    "sme": dict(label="SMEs", range="30 to 249 staff at their peak", tips=[
        "Act within weeks. Software subscriptions lapse after closure and exports disappear with them.",
        "One person usually knew every system. Get their help with exports before they move on.",
        "Keep it simple: one export per system, one adviser, one decision.",
        "Ask the former IT provider or MSP for admin access and a list of tools in use."]),
    "enterprise": dict(label="enterprises", range="250 or more staff at their peak", tips=[
        "Start with a data map: systems, owners, years, volumes and where personal data sits.",
        "Carve out privileged, regulated and client-confidential material before any sample is prepared.",
        "Plan phased samples by business unit rather than one large transfer.",
        "Agree sign-off with the creditors' committee or the court where your process requires it.",
        "Check outsourcing and cloud contracts: some vendors delete data soon after non-payment."]),
}

GUIDE_SLUG = {"in": "india", "sg": "singapore", "ie": "ireland", "nl": "netherlands", "de": "germany", "fr": "france"}
LOCAL = {  # roles and laws to name for the six other countries; general information, take local advice
    "in": dict(roles="insolvency and resolution professionals, and liquidators", law="Insolvency and Bankruptcy Code 2016", privacy="Digital Personal Data Protection Act 2023"),
    "sg": dict(roles="judicial managers and liquidators", law="Insolvency, Restructuring and Dissolution Act 2018", privacy="Personal Data Protection Act 2012"),
    "ie": dict(roles="liquidators and examiners", law="Companies Act 2014", privacy="GDPR and the Data Protection Act 2018"),
    "nl": dict(roles="the curator (bankruptcy trustee)", law="Bankruptcy Act (Faillissementswet)", privacy="GDPR"),
    "de": dict(roles="the insolvency administrator (Insolvenzverwalter)", law="Insolvency Code (Insolvenzordnung)", privacy="GDPR and the Federal Data Protection Act (BDSG)"),
    "fr": dict(roles="the judicial liquidator (liquidateur judiciaire)", law="Commercial Code, Book VI", privacy="GDPR and the Loi Informatique et Libertés"),
}

CHIP = lambda: B["chip"]("company.micro1.ai/get-started", "15 Nov 2026")


def steps_html(steps):
    return '<ol class="steps">' + "".join(
        f'<li><span class="sn">{n}</span><div><h2 class="h3">{e(t)}</h2><p>{d}</p></div></li>' for n, (t, d) in enumerate(steps, 1)) + "</ol>"


def guide_big(c, n, slug, size):
    R = B["RIGHTS"][c]; S = SIZES[size]; other = "enterprise" if size == "sme" else "sme"
    court = {"us": " In bankruptcy, a sale outside the ordinary course needs court approval.",
             "ca": " In receiverships and CCAA proceedings, sales usually need court approval."}.get(c, "")
    steps = [
        ("Confirm who can sign", e(R["control"][0]) + " Get the authority in writing before you speak to any buyer."),
        ("Check the company's status", e(R["register"]) + " " + e(R["dissolved"][0])),
        ("Map the records" if size == "enterprise" else "Export the records now",
         "List each system, the years it covers and roughly how much it holds. Check the records are in English." if size == "enterprise"
         else "List the tools the company used, then export from each one while access still works. Check the records are in English."),
        ("Take people out", e(R["privacy"][0]) + " Employee and HR records are usually left out entirely."),
        ("Run the fit check, then apply", f"micro1 lists companies that are no longer operating, with 30+ peak employees and English records, in ten countries including {e(n)} {CHIP()}. Our fit check takes two minutes."),
        ("Review, take advice, sign or walk away", "micro1 says it reviews and approves the data within 30 days, then pays within 30 days of invoice." + court + " Take advice on the contract; you can stop at any point before signing."),
    ]
    tips = "".join(f"<li>{e(t)}</li>" for t in S["tips"])
    body = f'''<section class="ind-hero"><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/guides">Guides</a> / <a href="/guides/{slug}">{e(n)}</a> / <span>{"SMEs" if size == "sme" else "Enterprises"}</span></nav>
<span class="eyebrow">{flag(c, 22, "fl inline")} {e(n)} · guide for {S["label"]}</span>
<h1>{e(n)}: a step-by-step guide for <em>{S["label"]}</em></h1>
<p class="lede">For companies with {S["range"]} that are in a formal insolvency process or have closed. Six steps, in order, from authority to a signed licence.</p>
<div class="glance"><div><span>Who decides</span><strong>{e(R["roles"])}</strong></div><div><span>This guide</span><strong>{e(S["range"].capitalize())}</strong></div><div><span>micro1 timing</span><strong>Review within 30 days, pay within 30 days of invoice</strong></div><div><span>Cost to you</span><strong>Nothing from us</strong></div></div>
<p class="small muted"><a href="/guides/{slug}/{other}">Read the {"enterprise" if other == "enterprise" else "SME"} guide instead →</a></p>
</div></section>
<section class="pt0"><div class="wrap stack">{steps_html(steps)}</div></section>
<section class="pt0"><div class="wrap split">
<div class="stack"><h2 class="h3">Tips for {S["label"]}</h2><ul class="ticks">{tips}</ul></div>
<div class="stack"><h2 class="h3">Common pitfalls</h2><ul class="ticks warn"><li>{e(R["dissolved"][0])}</li><li>Sending a sample before a contract covers handling and confidentiality.</li><li>Leaving employee or customer personal data in the export.</li></ul>
<p class="small muted">General information, not legal advice. <a href="/countries/{slug}">Full {e(n)} rights guide →</a></p></div>
</div></section>
<section class="pt0"><div class="wrap">{cta_band(f"Built for {S['label']} in {n}.")}</div></section>
{next_cards("ready", "rights", "blog")}'''
    ld = {"@context": "https://schema.org", "@graph": [B["ORG"],
          {"@type": "Article", "headline": f"{n}: a step-by-step guide for {S['label']}", "inLanguage": "en-GB", "datePublished": B["LASTMOD"], "dateModified": B["LASTMOD"],
           "author": {"@id": B["SITE"] + "/#org"}, "publisher": {"@id": B["SITE"] + "/#org"}, "mainEntityOfPage": f'{B["SITE"]}/guides/{slug}/{size}'},
          B["crumbs"](("Home", "/"), ("Guides", "/guides"), (n, f"/guides/{slug}"), ("SMEs" if size == "sme" else "Enterprises", f"/guides/{slug}/{size}"))]}
    og = og_job(f"guide-{slug}-{size}", "seal", c=c, n=n, title=f"{n}: a step-by-step guide for {S['label']}", sub=S["range"].capitalize())
    B["page"](f"guides/{slug}/{size}", f"{n} guide for {S['label']} | Dormant Yield",
              f"Six steps for {S['label']} in {n} with {S['range']}: authority, status, records, personal data, fit check and contract.", body, ld,
              og_image=og, visual=seal(c, n, R["roles"], f"Guide for {S['label']}"))


def guide_country_hub(c, n, slug):
    body = f'''<section class="ind-hero"><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/guides">Guides</a> / <span>{e(n)}</span></nav>
<span class="eyebrow">{flag(c, 22, "fl inline")} {e(n)} · main focus</span>
<h1>{e(n)}: pick your <em>guide</em></h1>
<p class="lede">Two guides, depending on how large the company was at its peak. Both end with a two-minute fit check.</p>
<ul class="seg">
<li><a href="/guides/{slug}/sme"><img src="/img/panel-1.webp" width="150" height="343" alt="" loading="lazy"><strong>SMEs</strong><span>30 to 249 staff at their peak. Move fast before exports disappear.</span><em>Open the SME guide →</em></a></li>
<li><a href="/guides/{slug}/enterprise"><img src="/img/panel-3.webp" width="150" height="336" alt="" loading="lazy"><strong>Enterprises</strong><span>250 or more staff. Data map, carve-outs, phased samples, sign-off.</span><em>Open the enterprise guide →</em></a></li>
</ul>
<p class="small muted"><a href="/countries/{slug}">{e(n)} rights guide: who can license the records →</a></p>
</div></section>
{next_cards("fit", "ready", "blog")}'''
    ld = {"@context": "https://schema.org", "@graph": [B["ORG"], B["crumbs"](("Home", "/"), ("Guides", "/guides"), (n, f"/guides/{slug}"))]}
    og = og_job(f"guide-{slug}", "seal", c=c, n=n, title=f"{n}: guides for SMEs and enterprises", sub="Six steps from authority to a signed licence")
    B["page"](f"guides/{slug}", f"{n} guides for SMEs and enterprises | Dormant Yield",
              f"Step-by-step guides for SMEs and enterprises in {n}: licensing a closed or closing company's records responsibly.", body, ld,
              og_image=og, visual=seal(c, n, B["RIGHTS"][c]["roles"], "Main focus"))


def guide_local(c, n):
    L = LOCAL[c]; slug = GUIDE_SLUG[c]
    steps = [
        ("Find who controls the assets", f"In {e(n)}, that is usually {e(L['roles'])} under the {e(L['law'])}. Confirm their authority in writing."),
        ("Check the company's status", "Check the national company register for the current status and any appointed officeholder. A dissolved company may need restoring before anything can be licensed."),
        ("Export the records", "List each system, the years it covers and roughly how much it holds. micro1 lists English as the language for this track."),
        ("Take people out", f"Personal data stays protected under the {e(L['privacy'])}. Employee and HR records are usually left out entirely."),
        ("Run the fit check, then apply", f"micro1 lists {e(n)} among ten countries for companies that are no longer operating, with 30+ peak employees {CHIP()}."),
        ("Take local advice and decide", "Our detailed rights guides cover the UK, US, Canada and Australia only. Ask a local insolvency or data protection adviser before you agree anything."),
    ]
    body = f'''<section class="ind-hero"><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/guides">Guides</a> / <span>{e(n)}</span></nav>
<span class="eyebrow">{flag(c, 22, "fl inline")} {e(n)} · on micro1's list</span>
<h1>{e(n)}: licensing a closed company's <em>records</em></h1>
<p class="lede">A short guide for SMEs and enterprises. The steps are the same everywhere; the people and laws differ. Take local advice before you agree anything.</p>
<div class="glance"><div><span>Usually decides</span><strong>{e(L["roles"]).capitalize()}</strong></div><div><span>Insolvency law</span><strong>{e(L["law"])}</strong></div><div><span>Personal data</span><strong>{e(L["privacy"])}</strong></div><div><span>Cost to you</span><strong>Nothing from us</strong></div></div>
</div></section>
<section class="pt0"><div class="wrap stack">{steps_html(steps)}</div></section>
<section class="pt0"><div class="wrap">{cta_band()}</div></section>
{next_cards("ready", "guides", "fit")}'''
    ld = {"@context": "https://schema.org", "@graph": [B["ORG"], B["crumbs"](("Home", "/"), ("Guides", "/guides"), (n, f"/guides/{slug}"))]}
    og = og_job(f"guide-{slug}", "seal", c=c, n=n, title=f"{n}: licensing a closed company's records", sub=L["law"])
    B["page"](f"guides/{slug}", f"{n}: closed company records guide | Dormant Yield",
              f"{n}: who usually controls a closed company's assets, which laws apply to personal data, and six steps to check fit with micro1.", body, ld,
              og_image=og, visual=seal(c, n, L["roles"], "On micro1's list"))


def guides():
    for c, n, big, slug in B["COUNTRIES"]:
        if big:
            guide_country_hub(c, n, slug)
            for size in ("sme", "enterprise"):
                guide_big(c, n, slug, size)
        else:
            guide_local(c, n)
    big4 = "".join(
        f'<li><div class="gc-top">{flag(c, 40)}<strong>{e(n)}</strong><em>Main focus</em></div>'
        f'<a href="/guides/{slug}/sme">SME guide <span aria-hidden="true">→</span></a><a href="/guides/{slug}/enterprise">Enterprise guide <span aria-hidden="true">→</span></a>'
        f'<a class="muted" href="/countries/{slug}">Rights guide</a></li>'
        for c, n, big, slug in B["COUNTRIES"] if big)
    body = f'''<section><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>Guides</span></nav>
<span class="eyebrow">Country guides</span>
<h1>Step-by-step guides for SMEs and <em>enterprises</em></h1>
<p class="lede">Pick your country. The big four have separate guides for SMEs (30 to 249 staff at their peak) and enterprises (250 or more). The other six share one short guide each.</p>
<div class="band-card">{flag_pills()}</div>
<h2 class="h3 mt20">The big four</h2>
<ul class="gcards">{big4}</ul>
</div></section>
<section class="pt0"><div class="wrap">{cta_band()}</div></section>
{next_cards("ready", "how", "blog")}'''
    ld = {"@context": "https://schema.org", "@graph": [B["ORG"], B["crumbs"](("Home", "/"), ("Guides", "/guides"))]}
    B["page"]("guides", "Country guides for SMEs and enterprises | Dormant Yield",
              "Step-by-step guides for licensing a closed company's records in ten countries, with separate SME and enterprise guides for the UK, US, Canada and Australia.", body, ld)


def guide_urls():
    urls = ["/guides"]
    for c, n, big, slug in B["COUNTRIES"]:
        urls += [f"/guides/{slug}", f"/guides/{slug}/sme", f"/guides/{slug}/enterprise"] if big else [f"/guides/{GUIDE_SLUG[c]}"]
    return urls


# ---------- readiness checklist ----------
READY = [
    ("Authority", ["Your appointment or the sale agreement covers the company's records", "You know who signs, and you have it in writing", "The company is not dissolved, or restoration has been considered"]),
    ("Records", ["You have a list of every system the company used", "Admin access still works, or the vendor can still export", "You know which years each system covers", "Most records are in English", "Exports are stored safely, away from former staff accounts"]),
    ("People", ["Employee and HR records are identified and set aside", "Customer personal data is identified for removal or de-identification", "Payment card and bank data is excluded", "Health, children's and biometric data is excluded"]),
    ("Contracts", ["Customer contracts and confidentiality clauses are checked", "Software and cloud terms allow export and onward use", "Privileged or client-confidential material is identified", "Any regulator or court approval needed is known"]),
    ("Decision", ["Peak headcount was 30 or more", "Creditors or a committee will be informed in the usual way", "You have an adviser lined up to review any contract", "No sample leaves your hands before an agreement covers handling"]),
]


def readiness():
    n = 0; groups = []
    for g, items in READY:
        lis = []
        for it in items:
            n += 1
            lis.append(f'<li><label><input type="checkbox" id="rc-{n}"><span>{e(it)}</span></label></li>')
        groups.append(f'<fieldset><legend>{e(g)}</legend><ul>{"".join(lis)}</ul></fieldset>')
    body = f'''<section><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>Readiness checklist</span></nav>
<span class="eyebrow">Tool</span>
<h1>Records readiness <em>checklist</em></h1>
<p class="lede">Twenty checks before you talk to any buyer. Your ticks stay on this page only; nothing is stored or sent. Copy the list to share it with your team.</p>
<div class="ready" data-checklist>
<div class="ready-bar"><span class="ready-count" aria-live="polite">0 of {n} done</span><div class="m-bar"><span></span></div></div>
{"".join(groups)}
<div class="row"><button type="button" class="btn btn-ghost" data-copy>Copy checklist</button><button type="button" class="btn btn-ghost" data-reset>Clear ticks</button><span class="small muted" data-copied aria-live="polite"></span></div>
<div class="result" data-ready-result><span class="pill">Not started</span><h2 class="h3">Tick what is already true.</h2><p>The answer updates as you go.</p></div>
</div>
</div></section>
<section class="pt0"><div class="wrap">{cta_band("Ready on most of these? Check fit in two minutes.")}</div></section>
{next_cards("fit", "guides", "rights")}'''
    ld = {"@context": "https://schema.org", "@graph": [B["ORG"], B["crumbs"](("Home", "/"), ("Readiness checklist", "/tools/readiness"))]}
    B["page"]("tools/readiness", "Records readiness checklist | Dormant Yield",
              "Twenty checks for officeholders before licensing a closed company's records: authority, records, personal data, contracts and decision.", body, ld)


# ---------- blog ----------
def blog():
    posts = []
    for f in sorted((B["ROOT"] / "content/blog").glob("*.html")):
        meta, body = f.read_text().split("\n---\n", 1)
        m = dict(l.split(": ", 1) for l in meta.strip().splitlines())
        m["slug"] = f.stem; m["body"] = body
        posts.append(m)
    posts.sort(key=lambda p: (p["date"], p["title"]), reverse=True)
    for p in posts:
        c = p.get("country", "")
        body = f'''<article><section class="ind-hero"><div class="wrap narrow-col stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/blog">Insights</a> / <span>{e(p["eyebrow"])}</span></nav>
<span class="eyebrow">{flag(c, 22, "fl inline") + " " if c else ""}{e(p["eyebrow"])}</span>
<h1>{e(p["h1"])}</h1>
<p class="lede">{e(p["description"])}</p>
<p class="byline">Dormant Yield editorial · {e(p["display_date"])} · General information, not legal advice</p>
</div></section>
<section class="pt0"><div class="wrap narrow-col prose">{B["fill"](p["body"])}</div></section></article>
<section class="pt0"><div class="wrap">{cta_band()}</div></section>
{next_cards("ready", "guides", "fit", title="Keep going")}'''
        ld = {"@context": "https://schema.org", "@graph": [B["ORG"],
              {"@type": "BlogPosting", "headline": p["h1"], "description": p["description"], "inLanguage": "en-GB",
               "datePublished": p["date"], "dateModified": p["date"], "author": {"@id": B["SITE"] + "/#org"}, "publisher": {"@id": B["SITE"] + "/#org"},
               "mainEntityOfPage": f'{B["SITE"]}/blog/{p["slug"]}', "image": B["SITE"] + "/img/og.jpg"},
              B["crumbs"](("Home", "/"), ("Insights", "/blog"), (p["eyebrow"], f'/blog/{p["slug"]}'))]}
        og = og_job(f'blog-{p["slug"]}', "cover", c=c, eyebrow=p["eyebrow"], title=p["h1"], date=p["display_date"])
        B["page"](f'blog/{p["slug"]}', p["title"], p["description"], body, ld, og_image=og,
                  visual=cover(c, p["eyebrow"], p["h1"], p["display_date"]))
    cards = "".join(
        f'<li><a href="/blog/{p["slug"]}">{cover(p.get("country", ""), p["eyebrow"], p["h1"], p["display_date"], "sm")}'
        f'<span class="w">{e(p["description"])}</span><em>Read →</em></a></li>' for p in posts)
    body = f'''<section><div class="wrap stack">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>Insights</span></nav>
<span class="eyebrow">Insights</span>
<h1>Plain answers for <em>officeholders</em></h1>
<p class="lede">Short articles on the questions behind every closed company's records: who owns them, what can be shared and how to decide. General information, not legal advice.</p>
<img class="photo" src="/img/cabinet.webp" width="900" height="538" alt="A dark green filing cabinet with documents turning into charts" loading="lazy">
<ul class="blog-cards">{cards}</ul>
</div></section>
{next_cards("fit", "ready", "guides")}'''
    ld = {"@context": "https://schema.org", "@graph": [B["ORG"], {"@type": "Blog", "name": "Dormant Yield insights", "url": B["SITE"] + "/blog", "inLanguage": "en-GB"},
          B["crumbs"](("Home", "/"), ("Insights", "/blog"))]}
    B["page"]("blog", "Insights for officeholders | Dormant Yield",
              "Plain-English articles for administrators, liquidators and trustees on company records, bona vacantia, ABCs, 363 sales and personal data.", body, ld)
    return posts


# ---------- v6: content-built visuals (no stock, no generated imagery) ----------
import re as _re


def drawer(name, group, records):
    cards = "".join(
        f'<div class="dr-card"><span class="dr-k">{n:02d}</span><span class="dr-t">{e(r)}</span></div>'
        for n, r in enumerate(records[:4], 1))
    return (f'<div class="drawer"><div class="dr-cards">{cards}</div>'
            f'<div class="dr-front"><span class="dr-plate">{e(group)}</span><span class="dr-pull"></span></div>'
            f'<p class="dr-cap">{e(name)} · what usually exists</p></div>')


def seal(c, n, roles, tag):
    return (f'<div class="seal"><div class="seal-ring">{flag(c, 132, "fl seal-fl")}</div>'
            f'<div class="seal-card"><span>Who usually decides in {e(n)}</span><strong>{e(roles[0].upper() + roles[1:])}</strong></div>'
            f'<span class="seal-tag">{e(tag)}</span></div>')


def cover(c, eyebrow, title, date, size="lg"):
    fl = flag(c, 30, "fl") if c else '<span class="cv-dot"></span>'
    return (f'<div class="cover cover-{size}"><span class="cv-top">{fl}<span>{e(eyebrow)}</span></span>'
            f'<strong class="cv-t">{e(title)}</strong><span class="cv-foot">Dormant Yield · Insights · {e(date)}</span></div>')


def with_visual(body, visual):
    """Turn the first hero section into a two-column hero with a decorative visual on the right."""
    m = _re.search(r'<section class="ind-hero"><div class="wrap(?: narrow-col)? stack">', body)
    if not m:
        return body
    end = body.index("</div></section>", m.end())
    inner = body[m.end():end]
    return (body[:m.start()] + '<section class="ind-hero"><div class="wrap hero2"><div class="stack">' + inner +
            f'</div><div class="hv" aria-hidden="true">{visual}</div></div></section>' + body[end + len("</div></section>"):])


OG_JOBS = []


def og_job(slug, kind, **kw):
    """Queue a share card for scripts/og.js and return its path."""
    OG_JOBS.append(dict(slug=slug, kind=kind, **kw))
    return f"/img/og/{slug}.jpg"
