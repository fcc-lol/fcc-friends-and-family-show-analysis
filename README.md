# FCC Friends & Family Show Analysis

Crowd counts from the live-stream recording of the FCC Friends & Family Show, November 14-15, 2026, at 100 N 3rd St.

- `output/gallery-crowd-report.pdf`: two-page report
- `output/gallery-crowd-slides.pdf` and `output/phone-slides/`: seven phone-sized slides
- `output/gallery-crowd-charts.html`: interactive charts in one self-contained page
- `PROCESS.md`: how the video, counts, report, slides and page were made

To rebuild the outputs:

```
python3 -m venv venv && venv/bin/pip install -r requirements.txt
venv/bin/python scripts/report_apollo.py output/gallery-crowd-report.pdf
venv/bin/python scripts/slides.py output
venv/bin/python scripts/html_page.py output/gallery-crowd-charts.html
```

The sampled video frames and filmstrips (`data/frames/`, `data/strips/`) are not in this repository. The counts
made from them are in `data/counts/` and `data/arrivals/`, which is all the scripts need. The slides use the
SF Mono font, which is on macOS.
