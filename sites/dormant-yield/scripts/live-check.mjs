// Live check for dormantyield.com once DNS points at Vercel. No dependencies; Node 18+.
// Usage: node scripts/live-check.mjs            (checks https://dormantyield.com)
//        node scripts/live-check.mjs https://dormant-yield-nordic-mar-tech.vercel.app
// Checks: HTTPS and status of every sitemap URL, security headers, the locked micro1 link on every page,
// share images, and the redirects from www, .co.uk and the outreach domain.
const BASE = (process.argv[2] || "https://dormantyield.com").replace(/\/$/, "");
const MICRO1 = "https://company.micro1.ai/get-started?referralCode=b6089a23-af54-4292-8bb3-070423a40fc0";
const HEADERS = ["content-security-policy", "strict-transport-security", "x-content-type-options", "x-frame-options", "referrer-policy", "permissions-policy"];
const problems = [];
const ok = (m) => console.log("  ok   " + m);
const bad = (m) => { problems.push(m); console.log("  FAIL " + m); };

async function get(url, redirect = "follow") {
  try { return await fetch(url, { redirect, headers: { "user-agent": "dormantyield-live-check" } }); }
  catch (e) { return { status: 0, error: e.message, headers: new Map(), text: async () => "" }; }
}

console.log(`Live check: ${BASE}\n`);

console.log("Redirects");
const isProd = BASE === "https://dormantyield.com";
if (isProd) {
  for (const [from, to, perm] of [
    ["https://www.dormantyield.com/faq", "https://dormantyield.com/faq", true],
    ["https://dormantyield.co.uk/faq", "https://dormantyield.com/faq", true],
    ["https://www.dormantyield.co.uk/", "https://dormantyield.com/", true],
    ["https://dormantyields.com/", "https://dormantyield.com/", false],
    ["http://dormantyield.com/", "https://dormantyield.com/", true],
  ]) {
    const r = await get(from, "manual");
    const loc = r.headers.get ? r.headers.get("location") : null;
    const want = perm ? [301, 308] : [302, 307, 308, 301];
    // Vercel may add a share token when fetched through its tools; ignore query strings.
    const clean = loc ? loc.split("?")[0] : loc;
    if (want.includes(r.status) && clean && clean.replace(/\/$/, "") === to.replace(/\/$/, "")) ok(`${from} → ${loc} (${r.status})`);
    else bad(`${from} → ${loc || "no location"} (${r.status || r.error})`);
  }
} else console.log("  skipped (only for https://dormantyield.com)");

console.log("\nRelease");
// Catches the 15-16 Nov failure: custom domains stuck on an older deployment while vercel.app showed the new one.
try {
  const { readFileSync } = await import("node:fs");
  const local = readFileSync(new URL("../public/index.html", import.meta.url), "utf8");
  const live = await (await get(BASE + "/")).text();
  const v = (h) => (h.match(/site\.css\?v=([a-f0-9]+)/) || [])[1];
  v(live) && v(live) === v(local) ? ok(`live release matches this checkout (css ${v(local)})`)
    : bad(`live release differs from this checkout: live css ${v(live) || "?"}, local ${v(local)}. Re-assign the domains to the latest deployment.`);
} catch (e) { console.log("  skipped (no local build): " + e.message); }

console.log("\nPages");
const sm = await get(BASE + "/sitemap.xml");
const xml = await sm.text();
const urls = [...xml.matchAll(/<loc>https:\/\/dormantyield\.com([^<]*)<\/loc>/g)].map((m) => m[1] || "/");
if (!urls.length) bad(`sitemap.xml unreadable (${sm.status})`);
let links = 0, pages = 0;
const ogs = new Set();
for (const u of urls) {
  const r = await get(BASE + u);
  if (r.status !== 200) { bad(`${u} status ${r.status || r.error}`); continue; }
  pages++;
  if (u === "/") for (const h of HEADERS) r.headers.get(h) ? ok(`header ${h}`) : bad(`missing header ${h}`);
  const html = await r.text();
  for (const m of html.matchAll(/https?:\/\/[a-z0-9.-]*micro1\.ai[^\s"'<>)]*/gi)) {
    if (m[0] === MICRO1) links++; else bad(`${u} has a different micro1 URL: ${m[0]}`);
  }
  const og = (html.match(/<meta property="og:image" content="https:\/\/dormantyield\.com([^"]+)"/) || [])[1];
  if (og) ogs.add(og);
}
ok(`${pages} of ${urls.length} sitemap pages return 200`);
ok(`${links} micro1 links, all byte-exact`);

console.log("\nShare images");
for (const og of ogs) {
  const r = await get(BASE + og);
  r.status === 200 ? null : bad(`${og} status ${r.status}`);
}
ok(`${ogs.size} share images checked`);

console.log(problems.length ? `\n${problems.length} problem(s). Fix before outreach.` : "\nAll checks passed.");
process.exit(problems.length ? 1 : 0);
