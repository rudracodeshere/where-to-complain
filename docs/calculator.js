/* Where to Complain: complaint deadline calculator.
   Vanilla JS, no external requests. Rules come only from official pages cited below
   (checked 2026-10-24). The same file runs in node for tests (module.exports). */
(function (root) {
  "use strict";
  var VERIFIED = "24 October 2026";
  var SRC = {
    irdai: { label: "IRDAI Master Circular on Protection of Policyholders' Interests, 2024 (para on turnaround time for complaints)", url: "https://irdai.gov.in/en/document-detail?documentId=5625747" },
    rules: { label: "Insurance Ombudsman Rules, 2017 (as amended till 9 November 2023), rule 14(3) and 14(4)", url: "https://cioins.co.in/notification/Insurance%20Ombudsman%20Rules,%202017(%20as%20amended%20till%2009.11.2023).pdf" },
    cio: { label: "Council for Insurance Ombudsmen: FAQs", url: "https://cioins.co.in/Faqs" },
    bima: { label: "IRDAI Bima Bharosa: Our Process", url: "https://bimabharosa.irdai.gov.in/Home/OurProcess" },
    rbi: { label: "RBI FAQs on the Reserve Bank - Integrated Ombudsman Scheme, 2026", url: "https://www.rbi.org.in/commonperson/english/scripts/FAQs.aspx?Id=3407" }
  };
  var MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  var DAY = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];

  function parse(s) {
    if (!s || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return null;
    var p = s.split("-").map(Number), d = new Date(Date.UTC(p[0], p[1] - 1, p[2]));
    return d.getUTCMonth() === p[1] - 1 ? d : null;
  }
  function iso(d) { return d.toISOString().slice(0, 10); }
  function addDays(d, n) { return new Date(d.getTime() + n * 864e5); }
  /* Calendar months; if the day does not exist (31 Jan + 1 month) use the last day of that month (earlier, so safer). */
  function addMonths(d, n) {
    var y = d.getUTCFullYear(), m = d.getUTCMonth() + n, day = d.getUTCDate();
    var last = new Date(Date.UTC(y, m + 1, 0)).getUTCDate();
    return new Date(Date.UTC(y, m, Math.min(day, last)));
  }
  function fmt(d) { return DAY[d.getUTCDay()] + ", " + d.getUTCDate() + " " + MON[d.getUTCMonth()] + " " + d.getUTCFullYear(); }

  /* type: "insurance" | "bank"; reply: "none" | "rejected" | "unsatisfied"
     Returns {error} or {rows:[{label, date, rule, src}], notes:[...], escalateFrom, lastDate} with ISO dates. */
  function calculate(type, complained, reply, replied, today) {
    var c = parse(complained), r = parse(replied), t = parse(today);
    if (!c) return { error: "Enter the date you sent your written complaint to the company." };
    if (t && c > t) return { error: "The complaint date is in the future. Check the date." };
    if (reply !== "none" && !r) return { error: "Enter the date you received the company's reply, or choose 'No reply yet'." };
    if (reply !== "none" && r < c) return { error: "The reply date is before the complaint date. Check both dates." };
    if (reply === "none") r = null;
    var rows = [], notes = [], from, last;

    if (type === "insurance") {
      rows.push({ label: "Insurer should resolve your complaint by", date: iso(addDays(c, 14)),
        rule: "IRDAI: insurers should provide resolution to the complaint within 14 days, with reasons if they do not accept it.", src: "irdai" });
      var month = addMonths(c, 1);           // one month after the written complaint
      var lastNoReply = addMonths(month, 12); // one year after that month expires
      if (!r) {
        from = addDays(month, 1); last = lastNoReply;
        rows.push({ label: "You can go to the Insurance Ombudsman from", date: iso(from),
          rule: "Rule 14(3)(a)(ii): you can complain if you had no reply within one month after the insurer received your complaint.", src: "rules" });
        rows.push({ label: "Last date to file with the Insurance Ombudsman", date: iso(last),
          rule: "Rule 14(3)(b)(iii): within one year after one month has passed from the date you sent your written complaint, if the insurer has not replied.", src: "rules" });
        notes.push("If you sent the complaint by post, the one month for going to the Ombudsman counts from when the insurer received it, so wait a few extra days before filing.");
      } else {
        from = r; last = addMonths(r, 12);
        rows.push({ label: "You can go to the Insurance Ombudsman from", date: iso(from),
          rule: reply === "rejected" ? "Rule 14(3)(a)(i): you can complain once the insurer has rejected your complaint." : "Rule 14(3)(a)(iii): you can complain if you are not satisfied with the insurer's reply.", src: "rules" });
        if (r > month) {
          last = lastNoReply; from = addDays(month, 1);
          rows[1].date = iso(from);
          rows[1].rule = "Rule 14(3)(a)(ii): you could complain once one month passed with no reply, and the reply you got later does not satisfy you.";
          notes.push("The reply came more than one month after your complaint. Rule 14 also counts one year from the end of that first month, which ends sooner, so we show that earlier date to be safe.");
        }
        rows.push({ label: "Last date to file with the Insurance Ombudsman", date: iso(last),
          rule: reply === "rejected" ? "Rule 14(3)(b)(i): within one year after you receive the insurer's order rejecting your complaint." : "Rule 14(3)(b)(ii): within one year after you receive the insurer's decision you are not satisfied with.", src: "rules" });
      }
      notes.push("Bima Bharosa (IRDAI): if your complaint registered there is not attended to within 15 days, or the insurer's resolution is not satisfactory, you may approach the Insurance Ombudsman. Going to IRDAI does not change the Ombudsman's one-year limit.");
      notes.push("The Ombudsman covers losses up to ₹50 lakh and cannot take a dispute already pending before, or decided by, a court, consumer forum or arbitrator.");
      if (t && t > last) notes.unshift("This date has passed. Rule 14(4) lets the Ombudsman condone a delay in cases it considers necessary. Contact your Ombudsman office and explain the reason for the delay.");
    } else if (type === "bank") {
      var wait = addDays(c, 30);
      from = addDays(wait, 1);
      if (r && r < from) from = r;
      last = addDays(wait, 90);
      var lastReply = r ? addDays(r, 90) : null;
      if (lastReply && lastReply > last) last = lastReply;
      rows.push({ label: "The 30-day wait for the bank's reply ends", date: iso(wait),
        rule: "RBI: you can go to the RBI Ombudsman if you have no reply within 30 days after the entity received your complaint (or a longer time set by RBI, NPCI or card-network rules), or if you are not satisfied with its reply.", src: "rbi" });
      rows.push({ label: "You can file with the RBI Ombudsman from", date: iso(from),
        rule: r ? "You have a reply you are not satisfied with, so you do not have to wait for the 30 days to end." : "After the 30-day wait, if the bank has not replied.", src: "rbi" });
      rows.push({ label: "Last date to file with the RBI Ombudsman", date: iso(last),
        rule: "RBI: within 90 days from the date the waiting period ends or from the date of the entity's last communication, whichever is later.", src: "rbi" });
      notes.push("RBI counts the 30 days from when the bank received your complaint. If you sent it by post, add the delivery days.");
      notes.push("For some complaints (for example card or UPI disputes), RBI, NPCI or card-network rules set a longer waiting time. If one applies, both dates above move later. We do not list those periods.");
      notes.push("RBI also needs your complaint to the bank to have been made within the limitation period under the Limitation Act, 1963.");
      if (t && t > last) notes.unshift("This date has passed. RBI's FAQ says complaints filed beyond the 90 days are not maintainable under the Scheme. The RBI FAQ does not describe a way to extend it, so check with the RBI contact centre on 14448.");
    } else {
      return { error: "Choose a complaint type." };
    }
    if (t && t <= last) notes.unshift(t < from ? "Today is too early to file with the Ombudsman." : "You can file with the Ombudsman today.");
    return { rows: rows, notes: notes, escalateFrom: iso(from), lastDate: iso(last) };
  }

  var api = { calculate: calculate, addMonths: addMonths, SRC: SRC, VERIFIED: VERIFIED };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }

  /* ---------- browser UI ---------- */
  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }
  function localToday() {
    var n = new Date();
    return n.getFullYear() + "-" + String(n.getMonth() + 1).padStart(2, "0") + "-" + String(n.getDate()).padStart(2, "0");
  }
  function init() {
    var form = document.getElementById("calc");
    if (!form) return;
    var out = document.getElementById("calc-result");
    var replyDateWrap = document.getElementById("reply-date-wrap");
    form.hidden = false;
    var ns = document.getElementById("calc-nojs"); if (ns) ns.hidden = true;
    form.complained.max = localToday();
    function sync() { replyDateWrap.hidden = form.reply.value === "none"; }
    form.addEventListener("change", sync); sync();
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var res = calculate(form.type.value, form.complained.value, form.reply.value, form.replied.value, localToday());
      out.textContent = "";
      if (res.error) { out.appendChild(el("p", { "class": "notice", role: "alert" }, res.error)); out.focus(); return; }
      out.appendChild(el("h2", { id: "your-dates" }, "Your dates"));
      var ol = el("ol", { "class": "ladder" });
      res.rows.forEach(function (row) {
        var li = el("li"), dl = el("dl");
        li.appendChild(el("p", { "class": "rung-who" }, row.label));
        dl.appendChild(el("dt", {}, "Date"));
        dl.appendChild(el("dd", { "class": "deadline", "data-iso": row.date }, fmt(parse(row.date))));
        dl.appendChild(el("dt", {}, "Rule"));
        dl.appendChild(el("dd", {}, row.rule));
        dl.appendChild(el("dt", {}, "Source"));
        var dd = el("dd"), a = el("a", { href: SRC[row.src].url, rel: "noopener" }, SRC[row.src].label);
        dd.appendChild(a); dd.appendChild(document.createTextNode(". Last checked: " + VERIFIED + "."));
        dl.appendChild(dd);
        li.appendChild(dl); ol.appendChild(li);
      });
      out.appendChild(ol);
      if (res.notes.length) {
        var ul = el("ul");
        res.notes.forEach(function (n) { ul.appendChild(el("li", {}, n)); });
        var box = el("div", { "class": "notice" }); box.appendChild(el("h3", {}, "Good to know")); box.appendChild(ul);
        out.appendChild(box);
      }
      out.appendChild(el("p", { "class": "meta" }, "This is a guide, not legal advice. Check the official rules linked above before you act."));
      out.focus();
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})(this);
