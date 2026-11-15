(function () {
  "use strict";
  // Locked micro1 link (Fred, in writing, 15 November 2026). Byte-exact. tests/check.mjs fails the build if it changes.
  var MICRO1 = "https://company.micro1.ai/get-started?referralCode=b6089a23-af54-4292-8bb3-070423a40fc0";
  var EXT = ' <span aria-hidden="true">↗</span><span class="sr"> (opens in a new tab)</span>';
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // Guard: disable any partner link whose URL was altered.
  function guard(root) {
    (root || document).querySelectorAll('[data-partner="micro1-company"]').forEach(function (a) {
      if (a.getAttribute("href") !== MICRO1) { a.removeAttribute("href"); a.textContent = "Link unavailable"; }
    });
  }
  guard();

  // ---------- mega menu: close on outside click, Escape, or link click ----------
  var mega = document.querySelector("details.mega");
  if (mega) {
    document.addEventListener("click", function (ev) { if (mega.open && !mega.contains(ev.target)) mega.open = false; });
    document.addEventListener("keydown", function (ev) { if (ev.key === "Escape" && mega.open) { mega.open = false; mega.querySelector("summary").focus(); } });
    mega.addEventListener("click", function (ev) { if (ev.target.closest("a")) mega.open = false; });
    mega.addEventListener("toggle", function () { if (mega.open && window.innerWidth > 760) { var q = mega.querySelector(".q"); if (q) q.focus(); } });
  }

  // ---------- search over /assets/index.json ----------
  var index = null, loading = null;
  function loadIndex() {
    if (index) return Promise.resolve(index);
    if (!loading) loading = fetch("/assets/index.json").then(function (r) { return r.json(); }).then(function (d) { index = d; return d; }).catch(function () { index = []; return index; });
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
      if (count) count.textContent = v ? shown + " of " + items.length + " industries" : "";
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
    if (c === "us" && s === "defunct") {
      items.unshift("Who can act for the dissolved corporation under state law, or which bankruptcy estate holds the records");
      return render("warn", "Worth checking authority", "micro1 accepts defunct US companies. Authority comes first.", "Confirm who can sign before you apply. micro1 decides what qualifies.", items, applyLink());
    }
    if (c !== "gb" && c !== "us") {
      items.unshift("Local advice on who controls the company's assets in " + NAMES[c]);
      return render("go", "Worth a conversation", "micro1 lists companies based in " + NAMES[c] + ".", "Our rights guidance is UK and US only, so take local advice. micro1 decides what qualifies. Have these ready:", items, applyLink());
    }
    render("go", "Worth a conversation", "On micro1's published criteria, this looks worth an application.", "micro1 decides what qualifies. Have these ready before you start:", items, applyLink());
  }
  form.addEventListener("change", update);
  form.addEventListener("submit", function (ev) { ev.preventDefault(); });
  update();
})();
