(function () {
  "use strict";
  // Locked micro1 company link. Byte-exact. tests/check.mjs fails the build if this or any copy of it changes.
  var MICRO1 = "https://company.micro1.ai/register/?referralCode=b6089a23-af54-4292-8bb3-070423a40fc0";

  // Guard: if a partner link on the page was altered, disable it rather than send someone to a wrong URL.
  document.querySelectorAll('[data-partner="micro1-company"]').forEach(function (a) {
    if (a.getAttribute("href") !== MICRO1) { a.removeAttribute("href"); a.textContent = "Link unavailable"; }
  });

  var form = document.getElementById("fit");
  var out = document.getElementById("result");
  if (!form || !out) return;

  function v(n) { var el = form.querySelector('input[name="' + n + '"]:checked'); return el ? el.value : ""; }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var ext = ' <span aria-hidden="true">↗</span><span class="sr"> (opens in a new tab)</span>';

  function applyLink(label) {
    return '<a class="btn btn-sprout" data-partner="micro1-company" href="' + MICRO1 +
      '" target="_blank" rel="sponsored noopener noreferrer">' + esc(label) + ext + "</a>" +
      '<p class="small">Referral link. As an independent referrer we may receive a fee from micro1 if a qualifying deal completes. You pay nothing.</p>';
  }

  function render(tone, pill, title, body, items, cta) {
    out.dataset.tone = tone;
    out.innerHTML = '<span class="pill">' + esc(pill) + "</span><h3>" + esc(title) + "</h3><p>" + esc(body) + "</p>" +
      (items && items.length ? "<ul><li>" + items.map(esc).join("</li><li>") + "</li></ul>" : "") + (cta || "");
  }

  function update() {
    var s = v("status"), c = v("country"), z = v("size"), r = v("role"), l = v("lang");

    if (s === "operating") {
      return render("info", "Not this site", "This site covers closed and closing companies only.",
        "Operating companies have different options.", [],
        '<p><a href="https://data.nordicmartech.com" target="_blank" rel="noopener noreferrer">Go to data.nordicmartech.com' + ext + "</a></p>");
    }
    if (c === "other") {
      return render("info", "Outside our scope", "We only cover UK and US companies for now.",
        "Rules on who controls a closed company's assets differ by country, so we would rather not guess.", []);
    }
    if (z === "small") {
      return render("info", "Probably not a fit", "micro1 lists 30 or more employees for this track.",
        "A smaller company is unlikely to qualify on micro1's published criteria. Check micro1's own page if in doubt.", []);
    }
    if (c === "uk" && s === "closed") {
      return render("warn", "Check authority first", "A dissolved UK company's property generally passes to the Crown.",
        "Until the company is restored to the register, nobody can usually license its records. Take advice on restoration before applying anywhere.",
        ["Find the dissolution date on Companies House", "Ask a solicitor whether restoration is possible and worthwhile", "Check the records still exist and can be exported"]);
    }
    if (r === "former") {
      return render("warn", "Pass this to the officeholder", "The administrator, liquidator or trustee decides.",
        "Whoever now controls the company's assets is the only person who can apply. Send them this page; it explains the checks they will want to make.", []);
    }
    if (r === "other") {
      return render("warn", "Find the rights holder", "You will need whoever controls the company's assets.",
        "Share this page with the administrator, liquidator or trustee. They decide whether it is worth pursuing for creditors.", []);
    }

    var items = ["Written confirmation of your authority to license the records", "A list of systems, years covered and rough volumes", "Where employee and customer personal data sits"];
    if (z === "unknown") items.unshift("Peak headcount (micro1 lists 30 or more employees)");
    if (l === "no") {
      return render("warn", "Weaker fit", "micro1 says data should be primarily in English.",
        "You can still ask, but expect a lower chance of approval.", items, applyLink("Apply with micro1"));
    }
    render("go", "Worth a conversation", "On micro1's published criteria, this looks worth an application.",
      "micro1 decides what qualifies. Have these ready before you start:", items, applyLink("Apply with micro1"));
  }

  form.addEventListener("change", update);
  form.addEventListener("submit", function (e) { e.preventDefault(); });
  update();
})();
