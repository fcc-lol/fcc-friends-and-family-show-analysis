# FCC Friends & Family Show: stream video and crowd report

How the combined video, the crowd counts, the PDF report and the phone slides were made.
Show: November 14-15, 2026, at 100 N 3rd St. Written November 16, 2026.

## Outputs

| What | Where |
|---|---|
| Combined video with burned-in clock (17:37:32, 20 GB) | `~/Desktop/combined-2026-11-14-15.mp4` |
| Two-page report | `output/gallery-crowd-report.pdf` |
| Seven phone slides (1080 x 1920 PNG) | `output/phone-slides/` |
| The seven slides as one PDF | `output/gallery-crowd-slides.pdf` |
| Interactive charts, one self-contained HTML file | `output/gallery-crowd-charts.html` |
| Everything used to make them | `~/Desktop/fcc-friends-and-family-show-analysis/` (this folder) |

## Folder layout

| Folder | Contents |
|---|---|
| `output/` | Finished report PDF, slides PDF, and `phone-slides/` PNGs |
| `scripts/` | The three Python scripts that build the report, slides and HTML page |
| `data/counts/` | People-in-frame counts, one row per sampled frame |
| `data/frames/` | The 212 sampled frames (not in the GitHub repo) |
| `data/arrivals/` | Door-side arrival counts, the instructions used, and `chunks/` (the lists of strips) |
| `data/strips/` | The 867 one-minute filmstrips (not in the GitHub repo) |
| `build/` | Chart images the scripts make on the way to the PDF; safe to delete |
| `venv/` | Python environment |

## 1. Combined video

- Sources: eight Twitch past-broadcast downloads on the Desktop, named `01-…mp4` to `08-…mp4` (720p).
- Order: 01 to 08, matching the Twitch dashboard screenshot read bottom row to top row.
- Start time of each broadcast: looked up by video ID (the second field of the filename) from Twitch's public
  GQL endpoint, field `recordedAt`.

| File | Start (UTC) | Length (s) |
|---|---|---|
| 01 | 2026-11-14 16:05:41 | 792.6 |
| 02 | 2026-11-14 16:24:39 | 18453.8 |
| 03 | 2026-11-14 21:34:13 | 11.3 |
| 04 | 2026-11-14 21:35:33 | 81.4 |
| 05 | 2026-11-14 21:37:53 | 122.6 |
| 06 | 2026-11-14 21:40:33 | 1700.2 |
| 07 | 2026-11-14 22:11:36 | 28364.8 |
| 08 | 2026-11-15 16:48:25 | 13925.5 |

- Clock: ffmpeg `drawtext` with `%{pts:localtime:EPOCH:...}`, one epoch per segment, so the clock shows the real
  local time (EST, UTC-5) and jumps across the gaps between broadcasts. Helvetica 26, black box, bottom left,
  format `Nov 14, 2026  4:34:14 PM`.
- Encode: `hevc_videotoolbox` at 2500k (tag `hvc1`) with AAC 128k, 720p.
- Checked at five points: start, start of 03, end of 07, start of 08, end.

## 2. People-in-frame counts

- Sampling: one frame every 300 s of video time, 212 frames, in `data/frames/NNNNN.jpg` (the name is the video time
  in seconds).
- Counting: each frame was viewed at full resolution by a Claude subagent (six subagents, each given a share of
  the frames) and every visible person counted, including people partly hidden or cut off by the frame edge.
  People depicted in artworks are not counted.
- Results: `data/counts/claude_counts_1.jsonl` to `claude_counts_6.jsonl`, one row per frame with `people_count`,
  `people_partially_visible`, `dogs`, `lights_on`, `crowd_level`, `confidence`, `notes`.
- Not used: an Apple Vision person detector was tried first and dropped because it misses people in crowds
  (for example 12 boxes on the Sunday 12:57 PM frame where the count is 18). Any image with green boxes is from
  that attempt.
- Lights-off frames (40, Saturday 9:48 PM to Sunday 1:03 AM) are kept in the data but left out of all statistics.
- Crowd levels: empty 0, sparse 1-3, moderate 4-8, busy 9-14, packed 15 or more.
- Person-hours: sum of each count times the 5-minute interval.

Caveats: these are people in view at an instant, not visitors. Crowded frames are probably low by 2 or 3.

## 3. Door-side arrivals (not in the report)

- The doorway is just off the right edge of the frame, so this counts people crossing the right edge, which is
  not exactly the same as people coming through the door.
- 867 one-minute filmstrips in `data/strips/SSSSS.jpg`: 30 tiles, 2 s apart, right 400 px of the frame, 10 x 3 grid.
- Split into 24 lists (`data/arrivals/chunks/chunk_01.txt` to `chunk_24.txt`), each read by a Claude subagent following
  `data/arrivals/INSTRUCTIONS.md`.
- Results: `data/arrivals/arrivals_01.jsonl` to `arrivals_24.jsonl` with `arrivals`, `departures`, `door_swings`,
  `visibility`, `confidence`, `reentries`, `notes`.
- Totals: 787 arrivals, 107 re-entries, 466 departures. Reported as roughly 500 arrivals, range about 360 to
  680. Most minutes were low confidence.

## 4. Report and slides

Run from this folder:

```
venv/bin/python scripts/report_apollo.py output/gallery-crowd-report.pdf
venv/bin/python scripts/slides.py output
venv/bin/python scripts/html_page.py output/gallery-crowd-charts.html
```

- `scripts/report_apollo.py`: the current two-page PDF. 1960s technical-note style, Courier, black ink only, 12-hour
  times. Reads `data/counts/` and holds the segment start times and lengths.
- `scripts/slides.py`: the phone slides. Runs `report_apollo.py` first to load the data, then draws seven slides in
  SF Mono with no header and no axis titles.
- `scripts/html_page.py`: the interactive page. Also runs `report_apollo.py` first to load the data, then writes one
  HTML file with the data and chart code inside it (no network needed). Hovering shows each sample, hour or bar.
- `venv/` has reportlab, matplotlib, pillow, numpy.

## To redo this for another show

1. Download the broadcasts and get each one's start time.
2. Join them with a per-segment clock.
3. Pull a frame every 5 minutes.
4. Have Claude subagents view and count each frame into JSONL.
5. Update the segment table, title, dates and address in `scripts/report_apollo.py` and the title in `scripts/slides.py`, then
   run the two commands above.
