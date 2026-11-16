# Counting arrivals on the door side of a gallery camera

You are reviewing one-minute "filmstrips" cut from a fixed camera that live-streamed an art gallery show. The goal is to count people arriving and leaving on the door side, minute by minute. The results feed a statistics report, so careful, honest counts matter more than speed. When you cannot tell, say so in the fields below instead of guessing high or low.

## What a strip is

Each strip in data/strips/ is one JPEG covering 60 seconds. It is named by the video second it starts at (e.g. 12600.jpg), and consecutive files are consecutive minutes.

A strip holds 30 tiles in a 10-column by 3-row grid. Time runs left to right along the top row, then the middle row, then the bottom row. Tiles are 2 seconds apart. Each tile shows only the right-hand third of the camera's view.

## The scene

The gallery's doorway is just outside the right edge of every tile. People arriving walk into view from the right edge and move left into the room; people leaving walk to the right edge and disappear.

A glass door leaf (metal frame, glass panel) is sometimes visible on the right. In the daytime it is often propped open and stays in view the whole minute; people passing behind it show as faint figures through the glass, and they count. At other times the door is closed and out of view, and the leaf swings into view for a few tiles when someone opens it.

Late on the first day the room is very crowded and people close to the camera block the right edge. Individual arrivals often cannot be seen then; door swings usually still can.

## What to record for each strip

Open each strip with the Read tool, one image per strip, in the order listed in your chunk file. Do not skip strips or infer one from its neighbours. Follow each person across tiles to judge direction.

- arrivals: people who come into view from the right edge (or from behind the glass door leaf) during this minute and move into the room.
- departures: people who move to the right edge (or behind the glass door leaf) and go out of view during this minute.
- door_swings: how many separate times the door leaf opens (swings into view, or visibly changes angle, then settles or goes back). A leaf that sits propped open and still for the whole strip is 0.
- visibility: "clear" if the right edge was visible throughout, "partial" if it was blocked some of the time, "blocked" if people close to the camera hid it for most of the minute.
- confidence: "high", "medium" or "low" for the arrivals and departures numbers.
- reentries: how many of the arrivals look like someone who had just stepped out of view moments earlier (same clothing) rather than a new person. Use 0 if none or if you cannot tell.
- notes: one short sentence on anything notable; leave empty if nothing.

Rules of thumb:
- Someone already in view at the first tile is not an arrival. Someone still in view at the last tile is not a departure.
- Someone standing or browsing near the right edge without crossing it is neither.
- Count a person once: if someone is halfway in at the end of one strip and continues in the next, count them in the strip where they first appear.
- A group entering together counts each person.
- People who enter or leave the tile on its left side are just moving around the room; ignore them.

## Output

Append one JSON object per line to your output file as you go, so partial work survives. Exactly these fields:

{"file": "12600.jpg", "arrivals": 2, "departures": 1, "door_swings": 0, "visibility": "clear", "confidence": "high", "reentries": 0, "notes": ""}

When finished, reply with just the number of strips written, any strips you could not read, and one or two sentences on anything that affects how far your counts can be trusted.
