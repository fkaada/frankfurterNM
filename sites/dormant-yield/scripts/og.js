// Renders share cards (1200x630) for jobs written by build.py into scripts/og-jobs.json.
// Local only (needs Playwright). Run: node scripts/og.js   then commit public/img/og/*.jpg
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const root = path.join(__dirname, ".."), pub = path.join(root, "public");
const jobs = JSON.parse(fs.readFileSync(path.join(__dirname, "og-jobs.json"), "utf8"));
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const font = (f, w, file) => `@font-face{font-family:${f};font-weight:${w};src:url(file://${pub}/fonts/${file})}`;
const css = `${font("J", 800, "plus-jakarta-sans-latin-800-normal.woff2")}${font("D", 500, "dm-sans-latin-500-normal.woff2")}${font("D", 700, "dm-sans-latin-700-normal.woff2")}
*{margin:0;box-sizing:border-box}body{width:1200px;height:630px;font-family:D;overflow:hidden;position:relative}
.brand{display:flex;align-items:center;gap:12px;font:800 30px J}.brand b{color:#1FA971}
h1{font:800 60px/1.06 J;letter-spacing:-.02em}
.pill{display:inline-block;background:#1FA971;color:#062018;font:700 22px D;padding:12px 24px;border-radius:999px}
.url{position:absolute;right:48px;bottom:40px;font:700 20px D}`;
const mark = `<svg width="40" height="40" viewBox="0 0 40 40"><path fill="#1FA971" d="M5 4l11 8v16c0 4 2 7 4 8-7 0-15-5-15-14V4zM35 4l-11 8v16c0 4-2 7-4 8 7 0 15-5 15-14V4z"/><path fill="#EEF4EF" d="M14 20l5 4v9l-3-2c-1-1-2-2-2-4v-7zM26 20l-5 4v9l3-2c1-1 2-2 2-4v-7z"/></svg>`;
function html(j) {
  const flag = j.c ? `file://${pub}/img/flags/${j.c}.svg` : "";
  if (j.kind === "cover") return `<style>${css}body{background:#0E4A3A;color:#EEF4EF}
.ring{position:absolute;right:-120px;bottom:-140px;width:520px;height:520px;border-radius:50%;border:70px solid rgba(255,255,255,.05)}
.l{position:absolute;left:72px;top:60px;right:120px;display:flex;flex-direction:column;gap:30px}
.ey{display:flex;align-items:center;gap:14px;font:700 22px D;letter-spacing:.12em;text-transform:uppercase;color:#4BE0A0}
.ey img{width:48px;height:48px;border-radius:50%;object-fit:cover;box-shadow:0 0 0 3px rgba(255,255,255,.3)}
.url{color:#B9CEC4}</style><div class="ring"></div><div class="l"><div class="brand">${mark}<span>Dormant <b>Yield</b></span></div>
<div class="ey">${flag ? `<img src="${flag}">` : ""}<span>${esc(j.eyebrow)} · Insights</span></div><h1>${esc(j.title)}</h1>
<span class="pill" style="align-self:flex-start">Read the article →</span></div><div class="url">dormantyield.com</div>`;
  return `<style>${css}body{background:#F3F0E6;color:#0B2A22}
.l{position:absolute;left:72px;top:60px;width:700px;display:flex;flex-direction:column;gap:26px}.brand b{color:#0A6B45}
.sub{font:500 24px/1.35 D;color:#3D5750}
.seal{position:absolute;right:90px;top:135px;width:360px;height:360px;border-radius:50%;background:radial-gradient(circle,#F3F0E6 58%,transparent 59%),conic-gradient(#1FA971 0 25%,#0E4A3A 0 50%,#1FA971 0 75%,#0E4A3A 0);display:grid;place-items:center}
.seal img{width:270px;height:270px;border-radius:50%;object-fit:cover;box-shadow:0 0 0 8px #F3F0E6}
.pill{background:#0E4A3A;color:#EEF4EF}.url{color:#3D5750}</style>
<div class="l"><div class="brand">${mark.replace('#EEF4EF', '#0E4A3A')}<span>Dormant <b>Yield</b></span></div><h1>${esc(j.title)}</h1><p class="sub">${esc(j.sub || "")}</p><span class="pill" style="align-self:flex-start">Check your fit →</span></div>
<div class="seal"><img src="${flag}"></div><div class="url">dormantyield.com</div>`;
}
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  const tmp = path.join(__dirname, ".og-tmp.html");
  for (const j of jobs) {
    fs.writeFileSync(tmp, `<!doctype html><meta charset="utf-8">${html(j)}`);
    await p.goto("file://" + tmp); await p.waitForTimeout(150);
    await p.screenshot({ path: path.join(pub, "img/og", j.slug + ".jpg"), type: "jpeg", quality: 80 });
  }
  fs.unlinkSync(tmp); await b.close(); console.log("og cards:", jobs.length);
})();
