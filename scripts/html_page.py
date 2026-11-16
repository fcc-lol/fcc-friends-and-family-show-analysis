"""Interactive, self-contained HTML page of the gallery crowd charts. Same data as report_apollo.py.

Usage: venv/bin/python scripts/html_page.py output/gallery-crowd-charts.html
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
# Reuse the data loading and helpers from the report script.
_tmp = os.path.join(os.path.dirname(HERE), "build", "_tmp_report.pdf")
_argv = sys.argv; sys.argv = ["report_apollo.py", _tmp]
__file__ = os.path.join(HERE, "report_apollo.py")
exec(open(__file__).read())
sys.argv = _argv; os.remove(_tmp)
OUT = sys.argv[1]  # the report script sets its own OUT; restore ours

samples = [{"ms": int(r["dt"].timestamp() * 1000), "lab": fmt(r["dt"]), "n": r["n"], "on": bool(r["lights_on"]), "day": r["day"],
            "level": r.get("crowd_level", ""), "conf": r.get("confidence", ""), "dogs": int(r.get("dogs", 0) or 0)} for r in rows]

def period(label, rs, suffix=""):
    c = [r["n"] for r in rs]; p = max(rs, key=lambda r: r["n"])
    return {"label": label, "n": len(c), "mean": f"{mean(c):.1f}", "sd": f"{st.pstdev(c):.1f}", "min": min(c), "q1": f"{pct(c, 25):.0f}",
            "med": f"{pct(c, 50):.0f}", "q3": f"{pct(c, 75):.0f}", "max": p["n"], "tmax": fmt(p["dt"]) + suffix, "ph": f"{sum(c) * 5 / 60:.0f}"}
cc = [r["n"] for r in openr]
data = {"samples": samples,
        "stats": [period("Sat. Nov. 14", day[1]), period("Sun. Nov. 15", day[2]), period("Both days", openr, " Sat.")],
        "head": [[str(pk["n"]), f"Most persons in frame ({fmt(pk['dt'])}, Saturday)"], [f"{mean(cc):.1f}", "Mean persons in frame, gallery lights on"],
                 [f"{pct(cc, 50):.0f}", "Median persons in frame"], [bh.strftime("%-I %p"), f"Busiest hour, Saturday (mean {mean(byh[bh]):.1f} persons)"],
                 [f"{busy:.0f}%", "Of samples had 9 or more persons in frame"], [f"{sum(cc) * 5 / 60:.0f}", "Person-hours in frame"]],
        "nAll": len(rows), "nOn": len(openr)}

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FCC Friends &amp; Family Show: occupancy charts</title>
<style>
:root { --bg:#ffffff; --ink:#111111; --muted:#6b6b66; --grid:#e3e2dc; --hover:#f1f0ea; --tipbg:#111111; --tipink:#ffffff; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#141413; --ink:#f0efe9; --muted:#a3a29b; --grid:#33322e; --hover:#22211f; --tipbg:#f0efe9; --tipink:#141413; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:14px/1.5 "SF Mono", ui-monospace, Menlo, Consolas, monospace; -webkit-text-size-adjust:100%; }
main { max-width:900px; margin:0 auto; padding:28px 16px 56px; }
@media (min-width: 768px) { main { padding-top:88px; } }
h1 { font-size:22px; line-height:1.25; margin:0 0 4px; letter-spacing:.02em; text-transform:uppercase; }
.sub { margin:0; color:var(--muted); }
.intro { margin:16px 0 0; max-width:64ch; }
h2 { font-size:14px; letter-spacing:.06em; text-transform:uppercase; margin:44px 0 2px; padding-top:14px; border-top:1.5px solid var(--ink); }
h3 { font-size:13px; margin:22px 0 6px; font-weight:700; }
.note { color:var(--muted); margin:2px 0 0; font-size:12.5px; }
.head { display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:0 28px; margin:22px 0 0; padding:0; list-style:none; }
.head li { display:flex; align-items:center; gap:14px; padding:10px 0; border-bottom:1px dotted var(--muted); }
.head b { font-size:30px; line-height:1; min-width:96px; text-align:right; white-space:nowrap; }
.head span { font-size:12.5px; line-height:1.35; }
.chart { position:relative; width:100%; touch-action:pan-y; }
.chart svg { display:block; width:100%; overflow:visible; }
svg text { font:11.5px "SF Mono", ui-monospace, Menlo, Consolas, monospace; fill:var(--ink); }
svg text.m { fill:var(--muted); }
svg text.b { font-weight:700; font-size:12.5px; }
svg text.halo { paint-order:stroke; stroke:var(--bg); stroke-width:4px; stroke-linejoin:round; }
.grid { stroke:var(--grid); stroke-width:1; }
.axis { stroke:var(--ink); stroke-width:1.2; }
.line { fill:none; stroke:var(--ink); stroke-width:1.5; stroke-linejoin:round; }
.dot { fill:var(--bg); stroke:var(--ink); stroke-width:1.2; }
.dash { stroke:var(--ink); stroke-width:1.2; stroke-dasharray:6 4; fill:none; }
.bar { stroke:var(--ink); stroke-width:1.2; }
.whisk { stroke:var(--ink); stroke-width:1.6; }
.hatchline { stroke:var(--ink); stroke-width:1; }
.hatchline.soft { stroke:var(--muted); }
.rowbg { fill:transparent; }
.rowbg.on { fill:var(--hover); }
.cross { stroke:var(--ink); stroke-width:1; }
.focus { fill:var(--ink); stroke:var(--bg); stroke-width:2; }
.hit { fill:transparent; cursor:crosshair; }
#tip { position:fixed; z-index:10; pointer-events:none; background:var(--tipbg); color:var(--tipink); padding:8px 10px; font-size:12px; line-height:1.45;
       max-width:260px; border-radius:3px; opacity:0; transition:opacity .08s; }
#tip.on { opacity:1; }
#tip b { font-size:15px; display:block; }
#tip i { font-style:normal; opacity:.75; display:block; }
details { margin-top:14px; }
summary { cursor:pointer; padding:6px 0; font-weight:700; }
.scroll { overflow-x:auto; }
.tall { max-height:340px; overflow-y:auto; border:1px solid var(--grid); }
table { border-collapse:collapse; width:100%; font-size:12.5px; }
th, td { padding:5px 8px; border-bottom:1px solid var(--grid); text-align:right; white-space:nowrap; }
th:first-child, td:first-child { text-align:left; }
thead th { border-bottom:1.5px solid var(--ink); position:sticky; top:0; background:var(--bg); }
footer { margin-top:44px; padding-top:14px; border-top:1.5px solid var(--ink); color:var(--muted); font-size:12.5px; max-width:70ch; }
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line class="hatchline" x1="0" y1="0" x2="0" y2="6"/></pattern>
  <pattern id="hatchsoft" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line class="hatchline soft" x1="0" y1="0" x2="0" y2="8"/></pattern>
</defs></svg>
<main>
  <h1>FCC Friends &amp; Family Show</h1>
  <p class="sub">Occupancy as observed by a fixed stream camera. November 14–15, 2026, at 100 N 3rd St.</p>
  <p class="intro" id="intro"></p>
  <ul class="head" id="head"></ul>

  <h2>Persons in frame</h2>
  <p class="note">One point per sample, 5 minutes apart. Breaks in the line are gaps between broadcasts. Point at the chart for each sample.</p>
  <h3>Saturday, November 14</h3><div class="chart" id="tl1"></div>
  <h3>Sunday, November 15</h3><div class="chart" id="tl2"></div>

  <h2>Mean persons in frame by hour</h2>
  <p class="note">The bar is the mean for the hour beginning at the time shown. The line spans the lowest to highest sample in the hour.</p>
  <h3>Saturday, November 14</h3><div class="chart" id="hr1"></div>
  <h3>Sunday, November 15</h3><div class="chart" id="hr2"></div>

  <h2>Distribution of counts</h2>
  <p class="note">Both days, lights-on samples. Number of samples at each count of persons in frame; broken lines divide the crowd levels.</p>
  <div class="chart" id="hist"></div>
  <h3>Share of samples at each crowd level</h3><div class="chart" id="lev"></div>

  <h2>Tables</h2>
  <div class="scroll"><table id="stats"></table></div>
  <p class="note">Person-hours are the sum of each count multiplied by the 5-minute sampling interval.</p>
  <details><summary>Every sample</summary><div class="scroll tall"><table id="all"></table></div></details>

  <footer>Counts are persons in view of the camera at an instant, not visitors. Crowded frames are probably low by 2 or 3. Times are Eastern Standard.</footer>
</main>
<div id="tip" role="status"></div>
<script>
const D = __DATA__;
const NS = "http://www.w3.org/2000/svg";
const on = D.samples.filter(s => s.on);
const DAY = {1: "Saturday", 2: "Sunday"};
const LEVELS = [["Sparse", 1, 3], ["Moderate", 4, 8], ["Busy", 9, 14], ["Packed", 15, 999]];
const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
const cap = s => s ? s[0].toUpperCase() + s.slice(1) : "";
const fmtHour = h => (h % 12 || 12) + (h < 12 ? " AM" : " PM");
const localHour = ms => new Date(ms - 5 * 3600e3).getUTCHours();   // Eastern Standard, UTC-5
function el(tag, attrs, parent, text) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (text != null) e.textContent = text;
  if (parent) parent.appendChild(e);
  return e;
}
function svgIn(box, W, H) { box.textContent = ""; return el("svg", {viewBox: `0 0 ${W} ${H}`, height: H, role: "img"}, box); }
const tip = document.getElementById("tip");
function showTip(html, x, y) {
  tip.innerHTML = html; tip.classList.add("on");
  const r = tip.getBoundingClientRect(), vw = document.documentElement.clientWidth;
  let left = x + 14, top = y - r.height - 12;
  if (left + r.width > vw - 8) left = x - r.width - 14;
  if (left < 8) left = 8;
  if (top < 8) top = y + 18;
  tip.style.left = left + "px"; tip.style.top = top + "px";
}
function hideTip() { tip.classList.remove("on"); }

function timeline(id, day) {
  const box = document.getElementById(id), S = D.samples.filter(s => s.day === day);
  const W = box.clientWidth, H = Math.round(Math.max(250, Math.min(340, W * 0.45))), m = {l: 30, r: 12, t: 30, b: 26};
  const svg = svgIn(box, W, H), x0 = S[0].ms, x1 = S[S.length - 1].ms, pad = (x1 - x0) * 0.015, YMAX = 25;
  const X = ms => m.l + (ms - x0 + pad) / (x1 - x0 + 2 * pad) * (W - m.l - m.r);
  const Y = n => H - m.b - n / YMAX * (H - m.t - m.b);
  for (let v = 0; v <= YMAX; v += 5) {
    el("line", {class: v ? "grid" : "axis", x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v)}, svg);
    el("text", {class: "m", x: m.l - 6, y: Y(v) + 4, "text-anchor": "end"}, svg, v);
  }
  const hours = (x1 - x0) / 3600e3, step = Math.max(1, Math.ceil(hours * 46 / (W - m.l - m.r)));
  for (let t = Math.ceil(x0 / 3600e3) * 3600e3, i = 0; t <= x1; t += 3600e3, i++) {
    el("line", {class: "axis", x1: X(t), x2: X(t), y1: Y(0), y2: Y(0) + (i % step ? 3 : 6)}, svg);
    if (i % step === 0) el("text", {class: "m", x: X(t), y: H - 6, "text-anchor": "middle"}, svg, fmtHour(localHour(t)));
  }
  const off = S.filter(s => !s.on);
  if (off.length) {
    const a = X(off[0].ms), b = X(off[off.length - 1].ms);
    el("rect", {x: a, y: Y(YMAX), width: b - a, height: Y(0) - Y(YMAX), fill: "url(#hatchsoft)"}, svg);
    el("text", {class: "halo", x: (a + b) / 2, y: Y(15), "text-anchor": "middle"}, svg, b - a > 150 ? "Lights off (not counted)" : "Lights off");
  }
  const lit = S.filter(s => s.on), mu = mean(lit.map(s => s.n));
  el("line", {class: "dash", x1: m.l, x2: W - m.r, y1: Y(mu), y2: Y(mu)}, svg);
  let d = "", prev = null;
  for (const s of lit) { d += (prev && s.ms - prev.ms <= 420e3 ? "L" : "M") + X(s.ms).toFixed(1) + " " + Y(s.n).toFixed(1); prev = s; }
  el("path", {class: "line", d}, svg);
  const r = Math.max(1.8, Math.min(3.5, (W - m.l - m.r) / S.length * 0.38));
  for (const s of lit) el("circle", {class: "dot", cx: X(s.ms), cy: Y(s.n), r}, svg);
  el("text", {class: "halo", x: off.length ? m.l + 6 : W - m.r - 4, y: Y(mu) - 6, "text-anchor": off.length ? "start" : "end"}, svg, "Mean " + mu.toFixed(1));
  const pk = lit.reduce((a, b) => b.n > a.n ? b : a);
  el("text", {class: "b halo", x: Math.max(m.l + 60, Math.min(W - m.r - 60, X(pk.ms))), y: Y(pk.n) - 10, "text-anchor": "middle"}, svg, `Max ${pk.n}, ${pk.lab}`);
  const cross = el("line", {class: "cross", y1: Y(YMAX), y2: Y(0), visibility: "hidden"}, svg);
  const focus = el("circle", {class: "focus", r: 5, visibility: "hidden"}, svg);
  const hit = el("rect", {class: "hit", x: m.l, y: m.t - 20, width: W - m.l - m.r, height: H - m.t - m.b + 20}, svg);
  const move = e => {
    const bb = svg.getBoundingClientRect(), px = (e.clientX - bb.left) * W / bb.width;
    let best = S[0]; for (const s of S) if (Math.abs(X(s.ms) - px) < Math.abs(X(best.ms) - px)) best = s;
    cross.setAttribute("x1", X(best.ms)); cross.setAttribute("x2", X(best.ms)); cross.setAttribute("visibility", "visible");
    focus.setAttribute("cx", X(best.ms)); focus.setAttribute("cy", Y(best.n)); focus.setAttribute("visibility", "visible");
    const body = best.on ? `<b>${best.n} ${best.n === 1 ? "person" : "persons"} in frame</b>${cap(best.level)}; counting confidence ${best.conf}` +
      (best.dogs ? `<br>${best.dogs} ${best.dogs === 1 ? "dog" : "dogs"} in frame` : "") : `<b>Lights off</b>Not included in statistics`;
    showTip(`<i>${DAY[day]} ${best.lab}</i>${body}`, bb.left + X(best.ms) * bb.width / W, bb.top + Y(best.n) * bb.height / H);
  };
  hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move);
  hit.addEventListener("pointerleave", () => { cross.setAttribute("visibility", "hidden"); focus.setAttribute("visibility", "hidden"); hideTip(); });
}

function rows(id, items, xmax, tick, labelW, fmtVal) {
  // Horizontal bars. items: {label, value, lo, hi, tip}
  const box = document.getElementById(id), W = box.clientWidth, RH = 32, m = {l: labelW, r: 56, t: 4, b: 24};
  const H = m.t + items.length * RH + m.b, svg = svgIn(box, W, H), X = v => m.l + v / xmax * (W - m.l - m.r), y0 = m.t + items.length * RH;
  for (let v = 0; v <= xmax; v += tick) {
    el("line", {class: v ? "grid" : "axis", x1: X(v), x2: X(v), y1: m.t, y2: y0}, svg);
    el("text", {class: "m", x: X(v), y: H - 6, "text-anchor": "middle"}, svg, v);
  }
  items.forEach((it, i) => {
    const y = m.t + i * RH, cy = y + RH / 2;
    const bg = el("rect", {class: "rowbg", x: 0, y, width: W, height: RH}, svg);
    el("text", {x: m.l - 8, y: cy + 4, "text-anchor": "end"}, svg, it.label);
    el("rect", {class: "bar", x: X(0), y: cy - 9, width: Math.max(1, X(it.value) - X(0)), height: 18, fill: "url(#hatch)"}, svg);
    let end = it.value;
    if (it.lo != null) {
      el("line", {class: "whisk", x1: X(it.lo), x2: X(it.hi), y1: cy, y2: cy}, svg);
      for (const v of [it.lo, it.hi]) el("line", {class: "whisk", x1: X(v), x2: X(v), y1: cy - 5, y2: cy + 5}, svg);
      end = Math.max(end, it.hi);
    }
    el("text", {class: "b", x: X(end) + 7, y: cy + 4}, svg, fmtVal(it.value));
    const hit = el("rect", {class: "hit", x: 0, y, width: W, height: RH}, svg);
    const move = e => { bg.classList.add("on"); showTip(it.tip, e.clientX, e.clientY); };
    hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move);
    hit.addEventListener("pointerleave", () => { bg.classList.remove("on"); hideTip(); });
  });
}
function hourly(id, day) {
  const by = new Map();
  for (const s of on) if (s.day === day) { const k = Math.floor(s.ms / 3600e3); if (!by.has(k)) by.set(k, []); by.get(k).push(s.n); }
  const items = [...by.keys()].sort((a, b) => a - b).map(k => {
    const v = by.get(k), h = localHour(k * 3600e3), lo = Math.min(...v), hi = Math.max(...v);
    return {label: fmtHour(h), value: mean(v), lo, hi,
            tip: `<i>${DAY[day]}, ${fmtHour(h)} to ${fmtHour((h + 1) % 24)}</i><b>Mean ${mean(v).toFixed(1)} persons</b>Lowest ${lo}, highest ${hi}<br>${v.length} samples`};
  });
  rows(id, items, 25, 5, 52, v => v.toFixed(1));
}
function levels() {
  const items = LEVELS.map(([nm, lo, hi]) => {
    const k = on.filter(s => s.n >= lo && s.n <= hi).length, p = 100 * k / on.length;
    return {label: `${nm} (${hi === 999 ? lo + "+" : lo + "–" + hi})`, value: p,
            tip: `<i>${nm}: ${hi === 999 ? lo + " or more" : lo + " to " + hi} persons in frame</i><b>${p.toFixed(1)}% of samples</b>${k} of ${on.length} samples<br>${(k * 5 / 60).toFixed(1)} hours`};
  });
  rows("lev", items, 50, 10, 118, v => v.toFixed(0) + "%");
}
function hist() {
  const box = document.getElementById("hist"), W = box.clientWidth, H = 260, m = {l: 30, r: 12, t: 24, b: 26};
  const svg = svgIn(box, W, H), mx = Math.max(...on.map(s => s.n)), c = Array.from({length: mx + 1}, (_, k) => on.filter(s => s.n === k).length);
  const YMAX = 20, bw = (W - m.l - m.r) / (mx + 1), X = k => m.l + k * bw, Y = v => H - m.b - v / YMAX * (H - m.t - m.b);
  for (let v = 0; v <= YMAX; v += 5) {
    el("line", {class: v ? "grid" : "axis", x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v)}, svg);
    el("text", {class: "m", x: m.l - 6, y: Y(v) + 4, "text-anchor": "end"}, svg, v);
  }
  LEVELS.forEach(([nm, lo, hi]) => {
    el("line", {class: "dash", x1: X(lo), x2: X(lo), y1: m.t - 14, y2: Y(0)}, svg);
    const w = (Math.min(hi, mx) - lo + 1) * bw;
    if (w > nm.length * 7.5 + 8) el("text", {x: X(lo) + w / 2, y: m.t - 6, "text-anchor": "middle"}, svg, nm);
  });
  const every = bw >= 22 ? 1 : bw >= 12 ? 2 : 5;
  c.forEach((v, k) => {
    const bg = el("rect", {class: "rowbg", x: X(k), y: m.t, width: bw, height: Y(0) - m.t}, svg);
    if (v) el("rect", {class: "bar", x: X(k) + 1, y: Y(v), width: Math.max(1, bw - 2), height: Y(0) - Y(v), fill: "url(#hatch)"}, svg);
    if (k % every === 0) el("text", {class: "m", x: X(k) + bw / 2, y: H - 6, "text-anchor": "middle"}, svg, k);
    const hit = el("rect", {class: "hit", x: X(k), y: m.t, width: bw, height: Y(0) - m.t}, svg);
    const lv = LEVELS.find(([, lo, hi]) => k >= lo && k <= hi);
    const move = e => { bg.classList.add("on");
      showTip(`<i>${k} ${k === 1 ? "person" : "persons"} in frame${lv ? " (" + lv[0].toLowerCase() + ")" : ""}</i><b>${v} ${v === 1 ? "sample" : "samples"}</b>${(100 * v / on.length).toFixed(1)}% of ${on.length} lights-on samples`, e.clientX, e.clientY); };
    hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move);
    hit.addEventListener("pointerleave", () => { bg.classList.remove("on"); hideTip(); });
  });
}
function tables() {
  const cols = [["label", "Period"], ["n", "Samples"], ["mean", "Mean"], ["sd", "Std. dev."], ["min", "Min."], ["q1", "Lower quartile"], ["med", "Median"],
                ["q3", "Upper quartile"], ["max", "Max."], ["tmax", "Time of max."], ["ph", "Person-hours"]];
  document.getElementById("stats").innerHTML = "<thead><tr>" + cols.map(c => `<th>${c[1]}</th>`).join("") + "</tr></thead><tbody>" +
    D.stats.map(r => "<tr>" + cols.map(c => `<td>${r[c[0]]}</td>`).join("") + "</tr>").join("") + "</tbody>";
  document.getElementById("all").innerHTML = "<thead><tr><th>Time</th><th>Persons</th><th>Level</th><th>Lights</th><th>Confidence</th><th>Dogs</th></tr></thead><tbody>" +
    D.samples.map(s => `<tr><td>${DAY[s.day].slice(0, 3)}. ${s.lab}</td><td>${s.on ? s.n : ""}</td><td>${s.on ? cap(s.level) : ""}</td><td>${s.on ? "On" : "Off"}</td><td>${s.on ? s.conf : ""}</td><td>${s.dogs || ""}</td></tr>`).join("") + "</tbody>";
}
document.getElementById("intro").textContent = `One frame was taken from the recording every 5 minutes (${D.nAll} samples) and the persons visible in it were counted. Statistics use the ${D.nOn} samples taken with the gallery lights on.`;
document.getElementById("head").innerHTML = D.head.map(h => `<li><b>${h[0]}</b><span>${h[1]}</span></li>`).join("");
function draw() { timeline("tl1", 1); timeline("tl2", 2); hourly("hr1", 1); hourly("hr2", 2); hist(); levels(); }
tables(); draw();
let lastW = document.documentElement.clientWidth, timer;
window.addEventListener("resize", () => { clearTimeout(timer); timer = setTimeout(() => { const w = document.documentElement.clientWidth; if (w !== lastW) { lastW = w; hideTip(); draw(); } }, 120); });
window.addEventListener("scroll", hideTip, {passive: true});
</script>
</body>
</html>
"""
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
open(OUT, "w").write(HTML.replace("__DATA__", json.dumps(data, separators=(",", ":"))))
print("wrote", OUT)
