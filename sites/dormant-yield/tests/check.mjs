// Compliance and build checks for dormantyield.com. No dependencies.
// Runs as the Vercel build command, so any failure stops the deploy.
// On a production deploy (VERCEL_ENV=production) or with --launch, unverified partner facts also fail the build.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const pub = join(root, "public");
const LAUNCH = process.argv.includes("--launch") || process.env.VERCEL_ENV === "production";

// Locked by Fred in writing, 15 November 2026 (replaces the /register/ link). Never edit without his written instruction.
const MICRO1 = "https://company.micro1.ai/get-started?referralCode=b6089a23-af54-4292-8bb3-070423a40fc0";

const OWNER = ["Kaada Nordic MarTech", "936 289 835", "contact@nordicmartech.com"];

// Outbound links allowed in href (exact origins). Anything else fails.
const ALLOWED_OUT = ["https://company.micro1.ai", "https://data.nordicmartech.com", "https://dormantyield.com"];

const BANNED = [
  [/referral partner/i, "say 'independent referrer', never 'partner'"],
  [/\bpartner(s|ed)? (of|with) micro1/i, "never claim partnership with micro1"],
  [/\bofficial partner/i, "never 'official partner'"],
  [/\bpartnered\b/i, "never 'partnered'"],
  [/guarantee/i, "no guarantees"],
  [/\bunlock/i, "banned word 'unlock'"],
  [/unlimited/i, "banned word 'unlimited'"],
  [/zero risk/i, "banned phrase 'zero risk'"],
  [/100\s?%/i, "no '100%'"],
  [/[$£€]\s?\d/, "no fee or deal amounts"],
  [/\b\d+(\.\d+)?\s?(k|m|bn|million|billion)\b(?![a-z])/i, "no fee or deal amounts"],
  [/\bworth (up to|millions|thousands)/i, "no value claims"],
  [/passive income|goldmine|monetis|monetiz/i, "salesy wording"],
  [/spirit airlines|airline/i, "unsourced airline claim removed (15 November 2026)"],
  [/fonts\.(googleapis|gstatic)\.com/i, "fonts must be self-hosted"],
  [/lovable/i, "no platform leaks"],
];

const errors = [];
const fail = (file, msg) => errors.push(`${file}: ${msg}`);

function walk(dir) {
  return readdirSync(dir).flatMap((n) => {
    const p = join(dir, n);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
}

const files = walk(pub);
const html = files.filter((f) => f.endsWith(".html"));
const text = files.filter((f) => /\.(html|js|css|txt|xml|json)$/.test(f) && !/OFL-/.test(f));
const isCopy = (f) => /\.(html|js)$/.test(f);

let partnerLinks = 0;
let pending = 0;

for (const f of text) {
  const rel = relative(root, f);
  const src = readFileSync(f, "utf8");
  // Strip JSON-LD identifiers and URLs before word checks so domain names do not trip them.
  const words = src.replace(/https?:\/\/[^\s"'<>)]+/g, "URL");
  for (const [re, why] of BANNED) {
    const isFont = re.source.includes("fonts");
    if (!isFont && !isCopy(f)) continue;
    if (re.test(isFont ? src : words)) fail(rel, why);
  }

  // Every micro1 URL anywhere must be the locked link, byte for byte.
  for (const m of src.matchAll(/https?:\/\/[a-z0-9.-]*micro1\.ai[^\s"'<>)]*/gi)) {
    if (m[0] !== MICRO1) fail(rel, `micro1 URL differs from the locked link: ${m[0]}`);
  }
}

for (const f of html) {
  const rel = relative(root, f);
  const src = readFileSync(f, "utf8");

  if (!/<html lang="en-GB">/.test(src)) fail(rel, 'needs <html lang="en-GB">');
  if (!/<title>[^<]+<\/title>/.test(src)) fail(rel, "missing <title>");
  for (const o of OWNER) if (!src.includes(o)) fail(rel, `owner detail missing: ${o}`);
  if (!src.includes('href="/privacy"') || !src.includes('href="/legal"')) fail(rel, "footer must link /privacy and /legal");
  if (/\sstyle="/.test(src)) fail(rel, "inline style attribute (blocked by CSP)");
  if (/<script(?![^>]*(src=|application\/ld\+json))[^>]*>/.test(src)) fail(rel, "inline executable script (blocked by CSP)");
  for (const m of src.matchAll(/<(img|script|link|iframe|source|video|audio)\b[^>]*>/gi)) {
    if (/rel="canonical"/.test(m[0])) continue;
    if (/\s(src|href)="(https?:)?\/\//i.test(m[0])) fail(rel, `external resource loaded: ${m[0].slice(0, 80)}`);
  }

  for (const m of src.matchAll(/<a\b[^>]*>/g)) {
    const tag = m[0];
    const href = (tag.match(/href="([^"]*)"/) || [])[1] || "";
    if (/^https?:\/\//.test(href)) {
      const origin = new URL(href).origin;
      if (!ALLOWED_OUT.includes(origin)) fail(rel, `outbound link not on allow-list: ${href}`);
      if (!/target="_blank"/.test(tag) || !/rel="[^"]*noopener[^"]*noreferrer/.test(tag)) fail(rel, `external link needs target=_blank rel=noopener noreferrer: ${href}`);
    }
    if (/data-partner=/.test(tag)) {
      partnerLinks++;
      if (href !== MICRO1) fail(rel, "partner link is not the locked micro1 link");
      if (!/rel="sponsored noopener noreferrer"/.test(tag)) fail(rel, "partner link needs rel=\"sponsored noopener noreferrer\"");
    }
  }

  // JSON-LD must parse.
  for (const m of src.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    try { JSON.parse(m[1]); } catch (e) { fail(rel, `JSON-LD does not parse: ${e.message}`); }
  }

  pending += (src.match(/data-verify-status="pending"/g) || []).length;
}

const js = readFileSync(join(pub, "assets/site.js"), "utf8");
if (!js.includes(`var MICRO1 = "${MICRO1}";`)) fail("public/assets/site.js", "locked link constant changed");
if (partnerLinks < 1) fail("public/index.html", "no partner link found");

const vercel = JSON.parse(readFileSync(join(root, "vercel.json"), "utf8"));
const csp = vercel.headers.flatMap((h) => h.headers).find((h) => h.key === "Content-Security-Policy")?.value || "";
if (!csp || /unsafe-inline|unsafe-eval|\*/.test(csp)) fail("vercel.json", "CSP missing or weakened");

// Every page with a partner link carries the disclosure nearby; every internal link resolves; sitemap URLs exist.
import { existsSync } from "node:fs";
const resolveLocal = (u) => {
  const path = u.split("#")[0].split("?")[0];
  if (path === "/" || path === "") return true;
  const p = join(pub, path);
  return existsSync(p) && statSync(p).isFile() || existsSync(p + ".html") || existsSync(join(p, "index.html"));
};
for (const f of html) {
  const rel = relative(root, f);
  const src = readFileSync(f, "utf8");
  if (src.includes('data-partner="micro1-company"') && !/Referral link/.test(src)) fail(rel, "partner link without 'Referral link' disclosure");
  for (const m of src.matchAll(/\s(?:href|src)="(\/[^"]*)"/g)) if (!resolveLocal(m[1])) fail(rel, `broken internal link: ${m[1]}`);
}
const sitemap = readFileSync(join(pub, "sitemap.xml"), "utf8");
for (const m of sitemap.matchAll(/<loc>https:\/\/dormantyield\.com([^<]*)<\/loc>/g)) if (!resolveLocal(m[1] || "/")) fail("public/sitemap.xml", `sitemap URL has no page: ${m[1]}`);

if (pending) {
  const msg = `${pending} partner fact(s) still data-verify-status="pending". Fred must click-check each on micro1's site, then set "verified".`;
  if (LAUNCH) fail("public/index.html", msg);
  else console.warn(`warning: ${msg}`);
}

if (errors.length) {
  console.error(`\n${errors.length} problem(s):\n- ` + errors.join("\n- "));
  process.exit(1);
}
console.log(`ok: ${html.length} pages, ${partnerLinks} partner link(s), locked link intact${LAUNCH ? ", launch checks on" : ""}.`);
