"""1960s technical-note style version of the gallery crowd report. Same data; 12-hour times; black ink only."""
import json, glob, os, sys, statistics as st
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from PIL import Image as PI

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "build")  # chart images made on the way to the PDF
os.makedirs(S, exist_ok=True)
OUT = sys.argv[1]
TZ = ZoneInfo("America/New_York")
K = "#111111"

SEGS = [(792.618333, "2026-11-14T16:05:41"), (18453.823333, "2026-11-14T16:24:39"), (11.266333, "2026-11-14T21:34:13"),
        (81.400333, "2026-11-14T21:35:33"), (122.600333, "2026-11-14T21:37:53"), (1700.163667, "2026-11-14T21:40:33"),
        (28364.773667, "2026-11-14T22:11:36"), (13925.471333, "2026-11-15T16:48:25")]
def clock(t):
    c = 0
    for i, (d, s) in enumerate(SEGS):
        if t < c + d or i == len(SEGS) - 1:
            return (datetime.fromisoformat(s).replace(tzinfo=timezone.utc) + timedelta(seconds=t - c)).astimezone(TZ), i
        c += d
rows = {}
for p in sorted(glob.glob(os.path.join(ROOT, "data", "counts", "claude_counts_*.jsonl"))):
    for line in open(p):
        if line.strip():
            r = json.loads(line)
            if "people_count" in r: rows[r["file"]] = r
rows = [rows[k] for k in sorted(rows)]
for r in rows:
    r["t"] = int(r["file"][:5]); r["dt"], r["seg"] = clock(r["t"]); r["day"] = 2 if r["seg"] == 7 else 1; r["n"] = int(r["people_count"])
openr = [r for r in rows if r["lights_on"]]; dark = [r for r in rows if not r["lights_on"]]
day = {d: [r for r in openr if r["day"] == d] for d in (1, 2)}
def fmt(dt): return dt.strftime("%-I:%M %p")
def dlabel(d): return "Sat. Nov. 14" if d == 1 else "Sun. Nov. 15"
def mean(x): return sum(x) / len(x) if x else 0
def pct(x, q): return float(np.percentile(x, q))

MONO = "Courier New"
plt.rcParams.update({"font.family": MONO, "font.size": 9, "axes.edgecolor": K, "axes.linewidth": 0.8, "axes.labelcolor": K, "axes.labelweight": "bold", "axes.labelsize": 9.5, "axes.titlesize": 10, "axes.titleweight": "bold",
                     "xtick.color": K, "ytick.color": K, "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
                     "xtick.major.size": 4, "ytick.major.size": 4, "xtick.minor.size": 2, "ytick.minor.size": 2,
                     "xtick.major.width": 0.7, "ytick.major.width": 0.7, "xtick.minor.width": 0.5, "ytick.minor.width": 0.5,
                     "figure.facecolor": "white", "axes.facecolor": "white", "hatch.linewidth": 0.5})
YMAX = 26
def yaxis(ax):
    ax.set_ylim(0, YMAX); ax.yaxis.set_major_locator(MultipleLocator(5)); ax.yaxis.set_minor_locator(MultipleLocator(1))

def timeline(path):
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 5.9), dpi=220, gridspec_kw={"hspace": 0.46})
    for ax, d, tag in zip(axes, (1, 2), "ab"):
        rs = [r for r in rows if r["day"] == d]
        xs, ys, prev = [], [], None
        for r in rs:
            if prev is not None and (r["dt"] - prev).total_seconds() > 420:
                xs.append(prev + timedelta(seconds=1)); ys.append(float("nan"))
            xs.append(r["dt"]); ys.append(r["n"]); prev = r["dt"]
        xn = mdates.date2num(xs)
        ax.plot(xn, ys, color=K, lw=0.7, marker="o", ms=3.4, mfc="white", mec=K, mew=0.6, zorder=3)
        m = mean([r["n"] for r in rs if r["lights_on"]])
        ax.axhline(m, color=K, lw=0.7, ls=(0, (6, 3)), zorder=2)
        ax.text(xn[0] + (xn[-1] - xn[0]) * 0.988, m + (0.7 if d == 2 else -0.7), f"Mean = {m:.1f}", fontsize=8.5, color=K, ha="right",
                va="bottom" if d == 2 else "top", zorder=6, bbox=dict(fc="white", ec="none", pad=1.5))
        dk = [r for r in rs if not r["lights_on"]]
        if dk:
            a, b = mdates.date2num(dk[0]["dt"]), mdates.date2num(dk[-1]["dt"])
            ax.axvspan(a, b, facecolor="none", edgecolor=K, hatch="////", lw=0, zorder=0)
            ax.text((a + b) / 2, 13, "GALLERY LIGHTS OFF\n(not included in\nstatistics)", ha="center", va="center", fontsize=8.5, color=K, bbox=dict(fc="white", ec=K, lw=0.6, pad=3))
        pk = max(rs, key=lambda r: r["n"]); px = mdates.date2num(pk["dt"])
        ax.annotate(f"Maximum = {pk['n']}\nat {fmt(pk['dt'])}", (px, pk["n"]), xytext=(-88, 8), textcoords="offset points", fontsize=8.5, color=K, va="center",
                    arrowprops=dict(arrowstyle="-|>", lw=0.6, color=K, mutation_scale=7))
        ax.set_xlim(xn[0] - 0.006, xn[-1] + 0.006); yaxis(ax)
        ax.xaxis_date(tz=TZ); ax.xaxis.set_major_locator(mdates.HourLocator(tz=TZ)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I\n%p", tz=TZ))
        ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 30, 45] if d == 1 else range(5, 60, 5), tz=TZ))
        ax.set_ylabel("Number of persons in frame"); ax.set_xlabel("Time of day, Eastern Standard Time", labelpad=3)
        ax.set_title(f"({tag}) {'SATURDAY, NOVEMBER 14' if d == 1 else 'SUNDAY, NOVEMBER 15'}", loc="left", pad=5)
        if d == 1:
            from matplotlib.lines import Line2D
            from matplotlib.patches import Patch
            ax.legend(handles=[Line2D([], [], color=K, lw=0.7, marker="o", ms=3.4, mfc="white", mec=K, mew=0.6, label="One sample (every 5 min)"),
                               Line2D([], [], color=K, lw=0.7, ls=(0, (6, 3)), label="Mean, lights on"),
                               Patch(facecolor="white", edgecolor=K, hatch="////", lw=0.6, label="Lights off")],
                      loc="upper left", fontsize=8, frameon=True, fancybox=False, edgecolor=K, framealpha=1, borderpad=0.5, handlelength=2.6).get_frame().set_linewidth(0.6)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.965, bottom=0.085)
    fig.savefig(path); plt.close(fig)

def hourly(path):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.7), dpi=220, sharey=True, gridspec_kw={"width_ratios": [11, 5], "wspace": 0.05})
    for ax, d, tag in zip(axes, (1, 2), "ab"):
        by = {}
        for r in day[d]: by.setdefault(r["dt"].replace(minute=0, second=0, microsecond=0), []).append(r["n"])
        hs = sorted(by); vals = [mean(by[h]) for h in hs]
        ax.bar(range(len(hs)), vals, width=0.62, facecolor="white", edgecolor=K, lw=0.7, hatch="/////", zorder=2)
        for i, h in enumerate(hs):
            ax.plot([i, i], [min(by[h]), max(by[h])], color=K, lw=0.8, zorder=3)
            for y in (min(by[h]), max(by[h])): ax.plot([i - 0.13, i + 0.13], [y, y], color=K, lw=0.8, zorder=3)
        ax.set_xticks(range(len(hs))); ax.set_xticklabels([h.strftime("%-I\n%p") for h in hs], fontsize=8.5)
        for i, v in enumerate(vals): ax.text(i, 26.6, f"{v:.1f}", fontsize=8, color=K, ha="center", va="center")
        ax.axhline(25.3, color=K, lw=0.6)
        ax.tick_params(axis="x", which="both", top=False); yaxis(ax)
        ax.set_xlabel("Hour beginning", labelpad=3); ax.set_title(f"({tag}) {'SATURDAY, NOVEMBER 14' if d == 1 else 'SUNDAY, NOV. 15'}", loc="left", pad=5)
    axes[0].set_ylabel("Mean number of persons in frame")
    axes[0].annotate("Lowest to highest\nsample in the hour", (5, 17), xytext=(0.0, 21.5), fontsize=8.5, va="center",
                     arrowprops=dict(arrowstyle="-|>", lw=0.6, color=K, mutation_scale=7))
    for ax in axes: ax.set_ylim(0, 28); ax.set_yticks(range(0, 26, 5))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.93, bottom=0.17)
    fig.savefig(path); plt.close(fig)

def hist(path):
    fig, ax = plt.subplots(figsize=(7.0, 3.7), dpi=220)
    c = [r["n"] for r in openr]; mx = max(c); h = [c.count(k) for k in range(mx + 1)]
    ax.bar(range(mx + 1), h, width=1.0, facecolor="white", edgecolor=K, lw=0.7, hatch="/////", zorder=2)
    top = max(h) + 7
    for k, v in enumerate(h):
        if v: ax.text(k, v + 0.35, str(v), ha="center", fontsize=7.5, color=K)
    for b, lab in ((0.5, "SPARSE\n1 to 3"), (3.5, "MODERATE\n4 to 8"), (8.5, "BUSY\n9 to 14"), (14.5, "PACKED\n15 or more")):
        ax.axvline(b, color=K, lw=0.7, ls=(0, (6, 3)), zorder=1); ax.text(b + 0.25, top - 0.8, lab, fontsize=8.5, color=K, va="top")
    ax.annotate(f"Mean = {mean(c):.1f} persons", (mean(c), h[10]), xytext=(mean(c) + 6.5, h[10] + 5), fontsize=8.5, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=K, mutation_scale=7))
    ax.set_xlim(-0.6, mx + 0.6); ax.set_ylim(0, top); ax.set_xticks(range(0, mx + 1, 1)); ax.tick_params(axis="x", which="both", top=False)
    ax.yaxis.set_major_locator(MultipleLocator(5)); ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.set_xlabel("Number of persons in frame"); ax.set_ylabel("Number of 5-minute samples")
    ax.set_title("BOTH DAYS, LIGHTS-ON SAMPLES", loc="left", pad=5)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.93, bottom=0.13)
    fig.savefig(path); plt.close(fig)

timeline(f"{S}/a_tl.png"); hourly(f"{S}/a_hourly.png"); hist(f"{S}/a_hist.png")

# ---------------- PDF ----------------
W = 7.0 * inch
F, FB = "Courier", "Courier-Bold"
TT = ParagraphStyle("tt", fontName=F, fontSize=9, leading=12, alignment=TA_CENTER, textColor=K)
TB = ParagraphStyle("tb", fontName=FB, fontSize=10.5, leading=14, alignment=TA_CENTER, textColor=K)
HD = ParagraphStyle("hd", fontName=F, fontSize=9, leading=12, alignment=TA_CENTER, textColor=K, spaceBefore=9, spaceAfter=5)
BODY = ParagraphStyle("body", fontName=F, fontSize=8.3, leading=11.6, alignment=TA_JUSTIFY, textColor=K, firstLineIndent=22, spaceAfter=4)
CAP = ParagraphStyle("cap", fontName=F, fontSize=8, leading=10.5, alignment=TA_CENTER, textColor=K, spaceBefore=3, spaceAfter=6)
TCAP = ParagraphStyle("tcap", fontName=F, fontSize=8.3, leading=11, alignment=TA_CENTER, textColor=K, spaceBefore=8, spaceAfter=4)
NOTE = ParagraphStyle("note", fontName=F, fontSize=7.3, leading=9.5, textColor=K, spaceBefore=2)
def img(p):
    iw, ih = PI.open(p).size; return Image(p, width=W, height=W * ih / iw)
def tbl(data, widths, right_from=1):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), F, 7.8), ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor(K)),
                           ("ALIGN", (right_from, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(K)), ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor(K)),
                           ("LINEAFTER", (0, 0), (-2, -1), 0.5, colors.HexColor(K)),
                           ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                           ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    return t
def u(s): return f"<u>{s}</u>"

def stats(label, rs, tmax=None):
    c = [r["n"] for r in rs]; pk = max(rs, key=lambda r: r["n"])
    return [label, len(c), f"{mean(c):.1f}", f"{st.pstdev(c):.1f}", int(min(c)), f"{pct(c, 25):.0f}", f"{pct(c, 50):.0f}", f"{pct(c, 75):.0f}",
            pk["n"], tmax or fmt(pk["dt"]), f"{sum(c) * 5 / 60:.0f}"]
pk = max(openr, key=lambda r: r["n"])
srows = [["Period", "Samples", "Mean", "Std.\ndev.", "Min.", "Lower\nquartile", "Median", "Upper\nquartile", "Max.", "Time of\nmaximum", "Person-\nhours"],
         stats(f"{dlabel(1)}\n{fmt(day[1][0]['dt'])} to {fmt(day[1][-1]['dt'])}", day[1]),
         stats(f"{dlabel(2)}\n{fmt(day[2][0]['dt'])} to {fmt(day[2][-1]['dt'])}", day[2]),
         stats("Both days", openr, f"{fmt(pk['dt'])}\nSat.")]
sw = [1.75, 0.6, 0.45, 0.45, 0.4, 0.62, 0.55, 0.62, 0.4, 0.72, 0.6]; sw = [x * 7.0 * inch / sum(sw) for x in sw]
c = [r["n"] for r in openr]
def band(lo, hi): return sum(1 for v in c if lo <= v <= hi)
lrows = [["Level", "Persons in frame", "Samples", "Percent of samples", "Hours"]]
for lab, lo, hi in (("Empty", 0, 0), ("Sparse", 1, 3), ("Moderate", 4, 8), ("Busy", 9, 14), ("Packed", 15, 999)):
    k = band(lo, hi); lrows.append([lab, "0" if hi == 0 else (f"{lo} or more" if hi == 999 else f"{lo} to {hi}"), k, f"{100 * k / len(c):.1f}", f"{k * 5 / 60:.1f}"])
busy = 100 * band(9, 999) / len(c); dogs = sum(1 for r in rows if r.get("dogs", 0) > 0)
conf = {k: sum(1 for r in openr if r.get("confidence") == k) for k in ("high", "medium", "low")}
byh = {}
for r in openr: byh.setdefault(r["dt"].replace(minute=0, second=0, microsecond=0), []).append(r["n"])
bh = max(byh, key=lambda h: mean(byh[h]))

story = [Paragraph("TECHNICAL NOTE", TT), Spacer(1, 5),
         Paragraph("OCCUPANCY OF THE FCC FRIENDS &amp; FAMILY SHOW<br/>AS OBSERVED BY A FIXED STREAM CAMERA", TB), Spacer(1, 3),
         Paragraph("November 14-15, 2026, at 100 N 3rd St", TT), Spacer(1, 8),
         Paragraph(f"One frame was taken from the recording every 5 minutes ({len(rows)} samples) and the persons visible in it were counted. Statistics use the {len(openr)} samples taken with the gallery lights on.", BODY),
         Spacer(1, 4), img(f"{S}/a_tl.png"),
         Paragraph("Figure 1.- Persons in frame at each sample. Breaks in the curve are gaps between broadcasts.", CAP),
         Paragraph("TABLE I.- SUMMARY OF PERSONS IN FRAME, LIGHTS-ON SAMPLES", TCAP), tbl(srows, sw),
         PageBreak(),
         img(f"{S}/a_hourly.png"),
         Paragraph("Figure 2.- Mean persons in frame for each clock hour, lights-on samples. The number at the top of each column is the mean for that hour.", CAP),
         Spacer(1, 14), img(f"{S}/a_hist.png"),
         Paragraph("Figure 3.- Distribution of persons in frame, lights-on samples. The number above each bar is the number of samples.", CAP),
         Spacer(1, 10),
         Paragraph("Counts are persons in view at an instant, not visitors. Crowded frames are probably low by 2 or 3.", NOTE)]

def foot(cv, doc):
    cv.setFont(F, 8.5); cv.setFillColor(colors.HexColor(K)); cv.drawCentredString(4.25 * inch, 0.45 * inch, str(doc.page))
SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch, topMargin=0.6 * inch, bottomMargin=0.7 * inch,
                  title="Occupancy of the FCC Friends & Family Show").build(story, onFirstPage=foot, onLaterPages=foot)
print("wrote", OUT)
