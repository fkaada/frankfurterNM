"""Builds the plain text pages (privacy, legal, 404) from one shared shell, so header and footer match index.html.
Run: python3 scripts/page.py   (from sites/dormant-yield). Output goes to public/."""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
idx = (root/'public/index.html').read_text()
header = re.search(r'(<div class="disclose".*?</header>)', idx, re.S).group(1)
header = header.replace('href="#our-role"', 'href="/#our-role"')
header = re.sub(r'<nav class="links".*?</nav>', '<nav class="links" aria-label="Sections"><a href="/#how">How it works</a><a href="/#rights">Rights check</a><a href="/#fit-check">Fit check</a><a href="/#faq">FAQ</a></nav>', header, flags=re.S)
header = header.replace('href="#fit-check"', 'href="/#fit-check"')
footer = re.search(r'(<footer>.*?</footer>)', idx, re.S).group(1)
def build(slug, title, desc, body, canonical=True, robots="index, follow"):
    can = f'<link rel="canonical" href="https://dormantyield.com/{slug}">\n' if canonical else ''
    html = f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
{can}<meta name="robots" content="{robots}">
<meta name="theme-color" content="#0E4A3A">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
{header}
<main id="top"><section><div class="wrap doc stack">
{body.strip()}
</div></section></main>
{footer}
</body>
</html>
'''
    out = root/'public'/(f'{slug}.html' if slug else 'index.html')
    out.write_text(html)
    print('wrote', out.relative_to(root))
for f in sorted((root/'content').glob('*.html')):
    meta, body = f.read_text().split('\n---\n', 1)
    m = dict(l.split(': ', 1) for l in meta.strip().splitlines())
    build(f.stem, m['title'], m['description'], body, m.get('canonical', 'yes') == 'yes', m.get('robots', 'index, follow'))
