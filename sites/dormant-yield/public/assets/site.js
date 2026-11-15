(function () {
  "use strict";
  // Locked micro1 link (Fred, in writing, 15 November 2026). Byte-exact. tests/check.mjs fails the build if it changes.
  var MICRO1 = "https://company.micro1.ai/get-started?referralCode=b6089a23-af54-4292-8bb3-070423a40fc0";
  var EXT = ' <span aria-hidden="true">↗</span><span class="sr"> (opens in a new tab)</span>';
  var me = document.currentScript;
  var IDX = (me && me.getAttribute("data-index")) || "/assets/index.json";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // Guard: disable any partner link whose URL was altered.
  function guard(root) {
    (root || document).querySelectorAll('[data-partner="micro1-company"]').forEach(function (a) {
      if (a.getAttribute("href") !== MICRO1) { a.removeAttribute("href"); a.textContent = "Link unavailable"; }
    });
  }
  guard();

  // ---------- mega menus: one open at a time; close on outside click, Escape or link click ----------
  var megas = Array.prototype.slice.call(document.querySelectorAll("details[data-mega]"));
  megas.forEach(function (d) {
    d.addEventListener("toggle", function () {
      if (!d.open) return;
      megas.forEach(function (o) { if (o !== d) o.open = false; });
      if (window.innerWidth > 960 && !d.classList.contains("nav-m")) { var q = d.querySelector(".q"); if (q) q.focus({ preventScroll: true }); }
    });
    d.addEventListener("click", function (ev) { if (ev.target.closest("a[href]")) d.open = false; });
  });
  document.addEventListener("click", function (ev) { megas.forEach(function (d) { if (d.open && !d.contains(ev.target)) d.open = false; }); });
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Escape") return;
    megas.forEach(function (d) { if (d.open) { d.open = false; d.querySelector("summary").focus(); } });
  });
  window.addEventListener("resize", function () { megas.forEach(function (d) { if (d.open && d.offsetParent === null) d.open = false; }); });

  // ---------- masthead: compact banner once the page scrolls ----------
  var mast = document.querySelector(".masthead");
  if (mast) {
    var onScroll = function () { mast.classList.toggle("is-compact", window.scrollY > 120); };
    window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  }

  // ---------- readiness checklist (in-page only: nothing stored or sent) ----------
  var rc = document.querySelector("[data-checklist]");
  if (rc) {
    var boxes = rc.querySelectorAll('input[type="checkbox"]'), cnt = rc.querySelector(".ready-count"),
      rbar = rc.querySelector(".m-bar span"), rres = rc.querySelector("[data-ready-result]"), copied = rc.querySelector("[data-copied]");
    var rcUpdate = function () {
      var done = 0; boxes.forEach(function (b) { if (b.checked) done++; });
      cnt.textContent = done + " of " + boxes.length + " done";
      rbar.style.transform = "scaleX(" + (done / boxes.length) + ")";
      var pct = done / boxes.length, tone, pill, h, p;
      if (done === 0) { tone = ""; pill = "Not started"; h = "Tick what is already true."; p = "The answer updates as you go."; }
      else if (pct < 0.5) { tone = "warn"; pill = "Early"; h = "Start with authority and records."; p = "Confirm who can sign and export the records while access still works."; }
      else if (pct < 0.85) { tone = "warn"; pill = "Getting there"; h = "Close the gaps on people and contracts."; p = "Set employee data aside and check customer and software terms before any sample."; }
      else { tone = "go"; pill = "Ready"; h = "Worth a conversation."; p = "Run the fit check, then apply through micro1. micro1 decides what qualifies."; }
      rres.dataset.tone = tone;
      rres.innerHTML = '<span class="pill">' + esc(pill) + '</span><h2 class="h3">' + esc(h) + "</h2><p>" + esc(p) + "</p>";
    };
    boxes.forEach(function (b) { b.addEventListener("change", rcUpdate); });
    rc.querySelector("[data-reset]").addEventListener("click", function () { boxes.forEach(function (b) { b.checked = false; }); rcUpdate(); });
    rc.querySelector("[data-copy]").addEventListener("click", function () {
      var lines = ["Records readiness checklist (dormantyield.com/tools/readiness)"];
      rc.querySelectorAll("fieldset").forEach(function (fs) {
        lines.push("", fs.querySelector("legend").textContent);
        fs.querySelectorAll("li").forEach(function (li) { lines.push((li.querySelector("input").checked ? "[x] " : "[ ] ") + li.textContent.trim()); });
      });
      var text = lines.join("\n");
      var ok = function () { copied.textContent = "Copied."; }, bad = function () { copied.textContent = "Copy failed. Select the list and copy it manually."; };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok, bad); else bad();
    });
    rcUpdate();
  }

  // ---------- search over /assets/index.json ----------
  var index = null, loading = null;
  function loadIndex() {
    if (index) return Promise.resolve(index);
    if (!loading) loading = fetch(IDX).then(function (r) { return r.json(); }).then(function (d) { index = d; return d; }).catch(function () { index = []; return index; });
    return loading;
  }
  function score(item, terms) {
    var t = item.t.toLowerCase(), k = (item.k || "") + " " + (item.g || "").toLowerCase(), s = 0;
    for (var i = 0; i < terms.length; i++) {
      var w = terms[i];
      if (t.indexOf(w) === 0) s += 5; else if (t.indexOf(w) > -1) s += 3; else if (k.indexOf(w) > -1) s += 1; else return 0;
    }
    return s;
  }
  document.querySelectorAll("input.q[data-results]").forEach(function (input) {
    var out = document.getElementById(input.getAttribute("data-results"));
    input.addEventListener("focus", loadIndex, { once: true });
    input.addEventListener("input", function () {
      var v = input.value.trim().toLowerCase();
      if (!v) { out.innerHTML = ""; return; }
      loadIndex().then(function (d) {
        var terms = v.split(/\s+/);
        var hits = d.map(function (it) { return [score(it, terms), it]; }).filter(function (x) { return x[0] > 0; })
          .sort(function (a, b) { return b[0] - a[0]; }).slice(0, 8);
        out.innerHTML = hits.length ? hits.map(function (x) {
          return '<li><a href="' + esc(x[1].u) + '">' + esc(x[1].t) + (x[1].g ? '<span>' + esc(x[1].g) + "</span>" : "") + "</a></li>";
        }).join("") : '<li class="none">No matches. Try a broader word, or <a href="/industries">browse all 50 industries</a>.</li>';
      });
    });
  });

  // ---------- in-page filter on /industries ----------
  document.querySelectorAll("input.q[data-filter]").forEach(function (input) {
    var items = document.querySelectorAll(input.getAttribute("data-filter"));
    var count = document.getElementById("filter-count");
    input.addEventListener("input", function () {
      var v = input.value.trim().toLowerCase(), shown = 0;
      items.forEach(function (li) { var hit = !v || li.getAttribute("data-name").indexOf(v) > -1; li.hidden = !hit; if (hit) shown++; });
      document.querySelectorAll("[data-group]").forEach(function (g) { g.hidden = !g.querySelector("li:not([hidden])"); });
      var more = document.getElementById("more-industries");
      if (more && v) more.open = !!more.querySelector("li:not([hidden])");
      if (count) count.textContent = v ? shown + " of " + items.length + " industries" : "";
    });
  });

  document.querySelectorAll("[data-chip]").forEach(function (b) {
    b.addEventListener("click", function () {
      var q = document.getElementById("q-page"); if (!q) return;
      var on = b.getAttribute("aria-pressed") === "true";
      document.querySelectorAll("[data-chip]").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
      q.value = on ? "" : b.getAttribute("data-chip");
      if (!on) b.setAttribute("aria-pressed", "true");
      q.dispatchEvent(new Event("input"));
    });
  });

  // ---------- explained machine (scrubbable timeline) ----------
  var m = document.querySelector("[data-machine]");
  if (m) {
    var steps = m.querySelectorAll(".m-step"), range = m.querySelector(".m-range"), cap = m.querySelector(".m-cap"),
      bar = m.querySelector(".m-bar span"), play = m.querySelector(".m-play"), timer = null, cur = 0;
    var caps = [
      "Step 1 of 4. Confirm what records exist, in which systems and for which years, and get your authority to license them in writing.",
      "Step 2 of 4. Personal data is removed or de-identified before anything moves. Employee and HR records need the most care.",
      "Step 3 of 4. micro1 reviews a sample for fit and quality. micro1 says it reviews and approves the data within 30 days.",
      "Step 4 of 4. micro1 decides what qualifies and a contract sets the terms. micro1 says it pays within 30 days of invoice. You can still walk away."
    ];
    function go(i) {
      cur = i;
      steps.forEach(function (s, n) { s.classList.toggle("is-on", n <= i); s.classList.toggle("is-cur", n === i); });
      range.value = i; cap.textContent = caps[i];
      bar.style.transform = "scaleX(" + ((i + 1) / steps.length) + ")";
    }
    function stop() { clearInterval(timer); timer = null; play.textContent = "Play"; play.setAttribute("aria-pressed", "false"); }
    function start() {
      if (cur === steps.length - 1) go(0);
      timer = setInterval(function () { if (cur < steps.length - 1) go(cur + 1); else stop(); }, 2400);
      play.textContent = "Pause"; play.setAttribute("aria-pressed", "true");
    }
    play.addEventListener("click", function () { timer ? stop() : start(); });
    range.addEventListener("input", function () { stop(); go(+range.value); });
    steps.forEach(function (s, n) { s.addEventListener("click", function () { stop(); go(n); }); });
    go(0);
    // Autoplay once when visible, only if motion is welcome and the screen is wide enough.
    if (!reduce && "IntersectionObserver" in window && window.innerWidth > 412) {
      var io = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { io.disconnect(); start(); } }, { threshold: 0.6 });
      io.observe(m);
    }
  }

  // ---------- fit check ----------
  var form = document.getElementById("fit"), out = document.getElementById("result");
  if (!form || !out) return;
  var NAMES = { gb: "the United Kingdom", us: "the United States", ca: "Canada", "in": "India", au: "Australia", sg: "Singapore", ie: "Ireland", nl: "the Netherlands", de: "Germany", fr: "France" };

  function v(n) { var el = form.querySelector('input[name="' + n + '"]:checked'); return el ? el.value : ""; }
  function applyLink() {
    return '<a class="btn btn-sprout" data-partner="micro1-company" href="' + MICRO1 + '" target="_blank" rel="sponsored noopener noreferrer">Apply with micro1' + EXT + "</a>" +
      '<p class="small">Referral link. As an independent referrer we may receive a fee from micro1 if a qualifying deal completes. You pay nothing.</p>';
  }
  function render(tone, pill, title, body, items, cta) {
    out.dataset.tone = tone;
    out.innerHTML = '<span class="pill">' + esc(pill) + "</span><h3>" + esc(title) + "</h3><p>" + esc(body) + "</p>" +
      (items && items.length ? "<ul><li>" + items.map(esc).join("</li><li>") + "</li></ul>" : "") + (cta || "");
    guard(out);
  }

  function update() {
    var s = v("status"), c = v("country"), z = v("size"), r = v("role"), l = v("lang");
    if (s === "active") return render("info", "Not this site", "This site covers closed and closing companies only.", "Operating companies have different options.", [],
      '<p><a href="https://data.nordicmartech.com" target="_blank" rel="noopener noreferrer">Go to data.nordicmartech.com' + EXT + "</a></p>");
    if (c === "other") return render("info", "Outside micro1's list", "micro1 lists ten countries for this track.", "Companies based elsewhere are outside its published criteria for now.", []);
    if (z === "small") return render("info", "Probably not a fit", "micro1 lists 30 or more peak employees.", "A smaller company is unlikely to qualify on micro1's published criteria.", []);
    if (l === "no") return render("info", "Probably not a fit", "micro1 lists English as the language for this track.", "Records in other languages are outside its published criteria.", []);
    if (r === "former") return render("warn", "Pass this to the officeholder", "The administrator, liquidator or trustee decides.",
      "Whoever now controls the company's assets is the only person who can apply. Send them this page; it explains the checks they will want to make.", []);
    if (r === "other") return render("warn", "Find the rights holder", "You will need whoever controls the company's assets.",
      "Share this page with the administrator, liquidator or trustee. They decide whether it is worth pursuing for creditors.", []);
    if (c === "gb" && s === "defunct") return render("warn", "Check authority first", "A dissolved UK company's property generally passes to the Crown.",
      "Until the company is restored to the register, nobody can usually license its records. Take advice on restoration before applying anywhere.",
      ["Find the dissolution date on Companies House", "Ask a solicitor whether restoration is possible and worthwhile", "Check the records still exist and can be exported"]);

    var items = ["Written confirmation of your authority to license the records", "A list of systems, years covered and rough volumes", "Where employee and customer personal data sits"];
    if (z === "unknown") items.unshift("Peak headcount (micro1 lists 30 or more)");
    if (c === "ca" && s === "defunct") return render("warn", "Check authority first", "A dissolved Canadian corporation's remaining property generally vests in the Crown.",
      "The corporation may need reviving before anyone can license its records. Take advice before applying anywhere.",
      ["Check status with Corporations Canada or the provincial registry", "Ask a lawyer whether revival is possible and worthwhile", "Check the records still exist and can be exported"]);
    if (c === "au" && s === "defunct") return render("warn", "Check authority first", "A deregistered Australian company's property vests in ASIC.",
      "The company may need reinstating before anyone can license its records. Take advice before applying anywhere.",
      ["Check status on the ASIC register", "Ask a lawyer whether reinstatement is possible and worthwhile", "Check the records still exist and can be exported"]);
    if (c === "us" && s === "defunct") {
      items.unshift("Who can act for the dissolved corporation under state law, or which bankruptcy estate holds the records");
      return render("warn", "Worth checking authority", "micro1 accepts defunct US companies. Authority comes first.", "Confirm who can sign before you apply. micro1 decides what qualifies.", items, applyLink());
    }
    if (["gb", "us", "ca", "au"].indexOf(c) < 0) {
      items.unshift("Local advice on who controls the company's assets in " + NAMES[c]);
      return render("go", "Worth a conversation", "micro1 lists companies based in " + NAMES[c] + ".", "Our rights guides cover the UK, US, Canada and Australia, so take local advice. micro1 decides what qualifies. Have these ready:", items, applyLink());
    }
    if (c === "ca" || c === "au") {
      render("go", "Worth a conversation", "On micro1's published criteria, this looks worth an application.", "micro1 decides what qualifies. Read our " + NAMES[c] + " guide, then have these ready:", items,
        '<p><a href="/countries/' + (c === "ca" ? "canada" : "australia") + '">' + (c === "ca" ? "Canada" : "Australia") + " rights guide →</a></p>" + applyLink());
      return;
    }
    render("go", "Worth a conversation", "On micro1's published criteria, this looks worth an application.", "micro1 decides what qualifies. Have these ready before you start:", items, applyLink());
  }
  var GUIDE = { gb: "united-kingdom", us: "united-states", ca: "canada", au: "australia", "in": "india", sg: "singapore", ie: "ireland", nl: "netherlands", de: "germany", fr: "france" };
  function updateAll() {
    update();
    var c = v("country");
    var extra = document.createElement("p");
    extra.className = "fc-more";
    extra.innerHTML = (GUIDE[c] ? '<a href="/guides/' + GUIDE[c] + '">Read the ' + esc(NAMES[c].replace(/^the /, "")) + " guide →</a>" : "") +
      '<button type="button" class="link-btn" data-copy-result>Copy this answer</button><span class="small muted" data-copy-msg aria-live="polite"></span>';
    out.appendChild(extra);
  }
  out.addEventListener("click", function (ev) {
    if (!ev.target.closest("[data-copy-result]")) return;
    var msg = out.querySelector("[data-copy-msg]");
    var lines = [out.querySelector(".pill").textContent + ": " + out.querySelector("h3").textContent, out.querySelector("h3 + p").textContent];
    out.querySelectorAll("ul li").forEach(function (li) { lines.push("- " + li.textContent); });
    lines.push("", "Check yours: https://dormantyield.com/#fit-check");
    var ok = function () { msg.textContent = " Copied."; }, bad = function () { msg.textContent = " Copy failed. Select the text instead."; };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(lines.join("\n")).then(ok, bad); else bad();
  });
  form.addEventListener("change", updateAll);
  form.addEventListener("submit", function (ev) { ev.preventDefault(); });
  updateAll();
})();
