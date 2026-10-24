// node tools/test_calculator.js : checks the deadline calculator against hand-worked dates.
const c = require("../assets/calculator.js");
const cases = [
  // [type, complained, reply, replied, today, escalateFrom, lastDate]
  ["bank", "2026-10-01", "none", "", "2026-10-24", "2026-11-01", "2027-01-29"],      // 1 Oct +30 = 31 Oct; +90 = 29 Jan
  ["bank", "2026-10-01", "unsatisfied", "2026-10-10", "2026-10-24", "2026-10-10", "2027-01-29"], // early reply: file now; later of 29 Jan / 8 Jan
  ["bank", "2026-10-01", "unsatisfied", "2026-12-15", "2026-12-20", "2026-11-01", "2027-03-15"], // late reply: 15 Dec + 90 = 15 Mar
  ["bank", "2026-01-31", "none", "", "2026-10-24", "2026-03-03", "2026-05-31"],      // 31 Jan +30 = 2 Mar; +90 = 31 May
  ["insurance", "2026-10-01", "none", "", "2026-10-24", "2026-11-02", "2027-11-01"], // month ends 1 Nov; +1 yr
  ["insurance", "2026-10-01", "rejected", "2026-10-20", "2026-10-24", "2026-10-20", "2027-10-20"],
  ["insurance", "2026-10-01", "unsatisfied", "2026-12-10", "2026-12-20", "2026-11-02", "2027-11-01"], // late reply -> earlier date
  ["insurance", "2026-01-31", "none", "", "2026-10-24", "2026-03-01", "2027-02-28"], // 31 Jan + 1 month -> 28 Feb (clamped)
  ["insurance", "2024-02-29", "rejected", "2024-02-29", "2026-10-24", "2024-02-29", "2025-02-28"], // leap day
];
let fail = 0;
for (const [t, cd, rp, rd, today, from, last] of cases) {
  const r = c.calculate(t, cd, rp, rd, today);
  const ok = !r.error && r.escalateFrom === from && r.lastDate === last;
  if (!ok) fail++;
  console.log(ok ? "ok  " : "FAIL", t, cd, rp, rd || "-", "->", r.error || `${r.escalateFrom} / ${r.lastDate}`, ok ? "" : `(want ${from} / ${last})`);
}
// insurance 14-day row
const i = c.calculate("insurance", "2026-10-01", "none", "", "2026-10-24");
if (i.rows[0].date !== "2026-10-15") { fail++; console.log("FAIL 14-day row", i.rows[0].date); } else console.log("ok   insurer 14 days -> 2026-10-15");
// errors
for (const [args, want] of [[["bank", "", "none", "", "2026-10-24"], "Enter the date"], [["bank", "2026-10-10", "unsatisfied", "2026-10-01", "2026-10-24"], "before the complaint"], [["insurance", "2026-12-01", "none", "", "2026-10-24"], "future"], [["insurance", "2026-10-01", "rejected", "", "2026-10-24"], "reply"]]) {
  const r = c.calculate(...args);
  const ok = r.error && r.error.includes(want); if (!ok) fail++;
  console.log(ok ? "ok  " : "FAIL", "error:", r.error);
}
// past deadline notes
const p = c.calculate("bank", "2025-01-01", "none", "", "2026-10-24");
if (!/not maintainable/.test(p.notes[0])) { fail++; console.log("FAIL past bank note"); } else console.log("ok   past bank deadline note");
const q = c.calculate("insurance", "2024-01-01", "none", "", "2026-10-24");
if (!/condone/.test(q.notes[0])) { fail++; console.log("FAIL past insurance note"); } else console.log("ok   past insurance deadline note (condonation)");
console.log(fail ? `${fail} FAILED` : "All calculator tests passed");
process.exit(fail ? 1 : 0);
