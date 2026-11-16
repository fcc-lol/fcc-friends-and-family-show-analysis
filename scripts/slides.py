"""Phone-sized (1080x1920) slides of the gallery crowd report, same data and style as report_apollo.py."""
import sys, os, textwrap
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = sys.argv[1]
PNGDIR = os.path.join(OUTDIR, "phone-slides")
os.makedirs(PNGDIR, exist_ok=True)
# Reuse the data loading and helpers from the report script.
_argv = sys.argv; sys.argv = ["report_apollo.py", os.path.join(os.path.dirname(HERE), "build", "_tmp_report.pdf")]
__file__ = os.path.join(HERE, "report_apollo.py")
exec(open(__file__).read())
sys.argv = _argv; os.remove(os.path.join(os.path.dirname(HERE), "build", "_tmp_report.pdf"))

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.backends.backend_pdf import PdfPages

plt.rcParams.update({"font.family": "SF Mono", "font.size": 12.5, "font.weight": 500, "axes.labelsize": 13, "axes.labelweight": 600, "axes.linewidth": 1.4,
                     "xtick.labelsize": 12.5, "ytick.labelsize": 12.5, "xtick.major.size": 7, "ytick.major.size": 7,
                     "xtick.minor.size": 3.5, "ytick.minor.size": 3.5, "xtick.major.width": 1.2, "ytick.major.width": 1.2,
                     "xtick.minor.width": 0.8, "ytick.minor.width": 0.8, "hatch.linewidth": 0.8})
WIN, HIN, DPI = 5.4, 9.6, 200
AX = [0.15, 0.2, 0.79, 0.655]
figs = []
ARROW = dict(arrowstyle="-|>", lw=1.1, color=K, mutation_scale=13)

def slide(n, title, caption, plot=True):
    fig = plt.figure(figsize=(WIN, HIN), dpi=DPI)
    if title: fig.text(0.5, 0.915, title, ha="center", va="center", fontsize=14.5, fontweight=700, linespacing=1.15)
    if caption: fig.text(0.5, 0.125, "\n".join(textwrap.wrap(caption, 48)), ha="center", va="top", fontsize=10, fontweight="normal", linespacing=1.15)
    fig.text(0.5, 0.02, f"{n}", ha="center", fontsize=11)
    ax = fig.add_axes(AX) if plot else None
    figs.append((n, fig)); return fig, ax

# 1. Title and principal results
fig, _ = slide(1, None, None, plot=False)
fig.text(0.5, 0.875, "FCC FRIENDS & FAMILY SHOW\nOCCUPANCY AS OBSERVED\nBY A FIXED STREAM CAMERA", ha="center", va="center", fontsize=16, fontweight=700, linespacing=1.15)
fig.text(0.5, 0.80, "November 14-15, 2026, at 100 N 3rd St", ha="center", va="center", fontsize=12)
fig.text(0.5, 0.735, "\n".join(textwrap.wrap(f"One frame was taken from the recording every 5 minutes ({len(rows)} samples) and the persons visible in it were counted.", 40)),
         ha="center", va="center", fontsize=11, fontweight="normal", linespacing=1.15)
fig.text(0.5, 0.637, "PRINCIPAL RESULTS", ha="center", fontsize=12.5, fontweight=700)
fig.add_artist(Line2D([0.28, 0.72], [0.628, 0.628], color=K, lw=1.0))
cc_ = [r["n"] for r in openr]
items = [(f"{pk['n']}", f"Most persons in frame\n{fmt(pk['dt'])}, Saturday"), (f"{mean(cc_):.1f}", "Mean persons in frame,\ngallery lights on"),
         (f"{pct(cc_, 50):.0f}", "Median persons in frame"), (bh.strftime("%-I %p"), f"Busiest hour, Saturday\n(mean {mean(byh[bh]):.1f} persons)"),
         (f"{busy:.0f}%", "Of samples had 9 or\nmore persons in frame"), (f"{sum(cc_) * 5 / 60:.0f}", "Person-hours in frame")]
y = 0.565
for v, lab in items:
    fig.text(0.37, y, v, ha="right", va="center", fontsize=25, fontweight=700); fig.text(0.42, y, lab, ha="left", va="center", fontsize=11.5, fontweight="normal", linespacing=1.15)
    fig.add_artist(Line2D([0.08, 0.92], [y - 0.039, y - 0.039], color=K, lw=0.6, ls=(0, (2, 3)))); y -= 0.078
fig.text(0.5, 0.075, f"Statistics use the {len(openr)} samples taken\nwith the gallery lights on.", ha="center", va="center", fontsize=11, fontweight="normal", linespacing=1.15)

# 2, 3. Time series
def tl(n, d, tag):
    rs = [r for r in rows if r["day"] == d]
    fig, ax = slide(n, f"PERSONS IN FRAME\n{'SATURDAY, NOVEMBER 14' if d == 1 else 'SUNDAY, NOVEMBER 15'}",
                    f"Figure 1({tag}).- Persons in frame at each sample. Breaks in the curve are gaps between broadcasts.")
    xs, ys, prev = [], [], None
    for r in rs:
        if prev is not None and (r["dt"] - prev).total_seconds() > 420:
            xs.append(prev + timedelta(seconds=1)); ys.append(float("nan"))
        xs.append(r["dt"]); ys.append(r["n"]); prev = r["dt"]
    xn = mdates.date2num(xs)
    ax.plot(xn, ys, color=K, lw=1.1, marker="o", ms=3.3 if d == 1 else 5.5, mfc="white", mec=K, mew=0.9, zorder=3)
    m = mean([r["n"] for r in rs if r["lights_on"]]); ax.axhline(m, color=K, lw=1.3, ls=(0, (6, 3)), zorder=2)
    dk = [r for r in rs if not r["lights_on"]]
    if dk:
        a, b = mdates.date2num(dk[0]["dt"]), mdates.date2num(dk[-1]["dt"])
        ax.axvspan(a, b, facecolor="none", edgecolor=K, hatch="///", lw=0, zorder=0)
        ax.text((a + b) / 2, 17, "LIGHTS\nOFF", ha="center", va="center", fontsize=11.5, bbox=dict(fc="white", ec=K, lw=1.0, pad=4))
    p = max(rs, key=lambda r: r["n"]); px = mdates.date2num(p["dt"])
    ax.annotate(f"Maximum = {p['n']}\nat {fmt(p['dt'])}", (px, p["n"] + 0.4), xytext=(0, 24), textcoords="offset points", fontsize=11.5, ha="center", va="bottom", arrowprops=ARROW)
    ax.set_xlim(xn[0] - 0.008, xn[-1] + 0.008); ax.set_ylim(0, 35); ax.set_yticks(range(0, 31, 5)); ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis_date(tz=TZ)
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(1, 24, 2) if d == 1 else None, tz=TZ)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I\n%p", tz=TZ))
    ax.xaxis.set_minor_locator(mdates.HourLocator(tz=TZ) if d == 1 else mdates.MinuteLocator(byminute=[15, 30, 45], tz=TZ))
    h = [Line2D([], [], color=K, lw=1.1, marker="o", ms=5.5, mfc="white", mec=K, mew=0.9, label="One sample (5 min apart)"),
         Line2D([], [], color=K, lw=1.3, ls=(0, (6, 3)), label=f"Mean = {m:.1f}")]
    if dk: h.append(Patch(facecolor="white", edgecolor=K, hatch="///", lw=1.0, label="Lights off (not counted)"))
    ax.legend(handles=h, loc="upper left", fontsize=10.5, frameon=True, fancybox=False, edgecolor=K, framealpha=1, borderpad=0.6, handlelength=2.4).get_frame().set_linewidth(1.0)
tl(2, 1, "a"); tl(3, 2, "b")

# 4, 5. Hourly means, drawn as horizontal bars so every hour and value has room
def hr(n, d, tag):
    fig, ax = slide(n, f"MEAN PERSONS IN FRAME BY HOUR\n{'SATURDAY, NOVEMBER 14' if d == 1 else 'SUNDAY, NOVEMBER 15'}",
                    f"Figure 2({tag}).- The bar is the mean for the hour, with its value at right. The line spans the lowest to highest sample in the hour.")
    by = {}
    for r in day[d]: by.setdefault(r["dt"].replace(minute=0, second=0, microsecond=0), []).append(r["n"])
    hs = sorted(by); vals = [mean(by[h]) for h in hs]
    ax.barh(range(len(hs)), vals, height=0.62, facecolor="white", edgecolor=K, lw=1.2, hatch="////", zorder=2)
    for i, h in enumerate(hs):
        lo, hi = min(by[h]), max(by[h])
        ax.plot([lo, hi], [i, i], color=K, lw=1.5, zorder=3)
        for xx in (lo, hi): ax.plot([xx, xx], [i - 0.17, i + 0.17], color=K, lw=1.5, zorder=3)
        ax.text(max(hi, vals[i]) + 0.7, i, f"{vals[i]:.1f}", ha="left", va="center", fontsize=13, fontweight=700)
    ax.set_yticks(range(len(hs))); ax.set_yticklabels([h.strftime("%-I %p") for h in hs]); ax.invert_yaxis()
    ax.tick_params(axis="y", which="both", right=False, length=0)
    ax.set_xlim(0, 28.5); ax.set_xticks(range(0, 26, 5)); ax.xaxis.set_minor_locator(MultipleLocator(1))
hr(4, 1, "a"); hr(5, 2, "b")

# 6. Distribution (top) and crowd levels (bottom)
fig, _ = slide(6, "DISTRIBUTION OF COUNTS\nBOTH DAYS, LIGHTS-ON SAMPLES",
               "Figure 3.- Number of samples at each count of persons in frame (top) and percent of samples at each crowd level (bottom).", plot=False)
ax = fig.add_axes([0.15, 0.49, 0.79, 0.365])
mx = max(cc_); h = [cc_.count(k) for k in range(mx + 1)]
ax.bar(range(mx + 1), h, width=1.0, facecolor="white", edgecolor=K, lw=1.1, hatch="////", zorder=2)
LEVELS = (("Sparse", 1, 3), ("Moderate", 4, 8), ("Busy", 9, 14), ("Packed", 15, 999))
for _, lo, _hi in LEVELS: ax.axvline(lo - 0.5, color=K, lw=1.2, ls=(0, (6, 3)), zorder=1)
ax.annotate(f"Mean = {mean(cc_):.1f}", (mean(cc_), h[10] + 0.3), xytext=(4.6, 20.5), fontsize=11.5, va="center", ha="center", bbox=dict(fc="white", ec="none", pad=2), arrowprops=ARROW)
ax.set_xlim(-0.6, mx + 0.6); ax.set_ylim(0, 23); ax.set_xticks(range(0, mx + 1, 5)); ax.xaxis.set_minor_locator(MultipleLocator(1)); ax.tick_params(axis="x", which="both", top=False)
ax.set_yticks(range(0, 21, 5)); ax.yaxis.set_minor_locator(MultipleLocator(1))
ax2 = fig.add_axes([0.33, 0.2, 0.61, 0.22])
shares = [100 * sum(1 for v in cc_ if lo <= v <= hi) / len(cc_) for _, lo, hi in LEVELS]
ax2.barh(range(4), shares, height=0.62, facecolor="white", edgecolor=K, lw=1.2, hatch="////", zorder=2)
for i, s_ in enumerate(shares): ax2.text(s_ + 1.2, i, f"{s_:.0f}%", ha="left", va="center", fontsize=13, fontweight=700)
ax2.set_yticks(range(4)); ax2.set_yticklabels([f"{nm}\n{lo} to {hi}" if hi != 999 else f"{nm}\n{lo} or more" for nm, lo, hi in LEVELS], fontsize=11, linespacing=1.15)
ax2.invert_yaxis(); ax2.tick_params(axis="y", which="both", right=False, length=0)
ax2.set_xlim(0, 50); ax2.set_xticks(range(0, 51, 10)); ax2.xaxis.set_minor_locator(MultipleLocator(5))

# 7. Summary table
fig, _ = slide(7, "TABLE I.- SUMMARY OF PERSONS\nIN FRAME, LIGHTS-ON SAMPLES", "Person-hours are the sum of each count multiplied by the 5-minute sampling interval.", plot=False)
def col(rs):
    c = [r["n"] for r in rs]; p = max(rs, key=lambda r: r["n"])
    return [f"{len(c)}", f"{mean(c):.1f}", f"{st.pstdev(c):.1f}", f"{min(c)}", f"{pct(c, 25):.0f}", f"{pct(c, 50):.0f}", f"{pct(c, 75):.0f}", f"{p['n']}", fmt(p["dt"]).replace(" ", "\n"), f"{sum(c) * 5 / 60:.0f}"]
labels = ["Samples", "Mean", "Std. deviation", "Minimum", "Lower quartile", "Median", "Upper quartile", "Maximum", "Time of maximum", "Person-hours"]
cols = [col(day[1]), col(day[2]), col(openr)]; cols[2][8] += " Sat."
ta = fig.add_axes([0.07, 0.19, 0.86, 0.665]); ta.axis("off"); ta.set_xlim(0, 1); ta.set_ylim(0, 1)
xs_ = [0.0, 0.46, 0.64, 0.82, 1.0]; nrow = len(labels) + 1; rh = 1 / nrow
for i, t in enumerate(["", "Sat.\nNov. 14", "Sun.\nNov. 15", "Both\ndays"]):
    ta.text((xs_[i] + xs_[i + 1]) / 2, 1 - rh / 2, t, ha="center", va="center", fontsize=10.5, fontweight=700, linespacing=1.15)
for j, lab in enumerate(labels):
    yy = 1 - rh * (j + 1.5)
    ta.text(0.03, yy, lab, ha="left", va="center", fontsize=12, fontweight="normal")
    for i in range(3): ta.text((xs_[i + 1] + xs_[i + 2]) / 2, yy, cols[i][j], ha="center", va="center", fontsize=13 if j != 8 else 10, fontweight=600, linespacing=1.15)
    ta.plot([0, 1], [1 - rh * (j + 1), 1 - rh * (j + 1)], color=K, lw=1.3 if j == 0 else 0.5)
ta.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color=K, lw=1.6, clip_on=False)
for x in xs_[1:-1]: ta.plot([x, x], [0, 1], color=K, lw=0.9)

with PdfPages(os.path.join(OUTDIR, "gallery-crowd-slides.pdf")) as pdf:
    for n, fig in figs:
        fig.savefig(os.path.join(PNGDIR, f"slide-{n}.png"), dpi=DPI); pdf.savefig(fig); plt.close(fig)
print("wrote", len(figs), "slides to", OUTDIR)
