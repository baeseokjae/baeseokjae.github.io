#!/usr/bin/env python3
"""Draw the article cover: three memory traces from the published span dump.

No invented numbers: the figures drawn from spans.json are the record counts
(record.count = 51 on create_memory, record.count = 1 on both searches) and the
evicted_reason value on the delete span. The two values the searches returned
are *not* span attributes — the dump stores no record content — so they are
drawn from the run log captured in method.md and labelled as such in the
footer. The footer also says the layout is span shape, not a performance
measurement.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 820
BG = "#f7f9fc"
BOX = "#ffffff"
LINE = "#c9d4e3"
INK = "#16202e"
MUTED = "#5b6b80"
OK = "#1f7a4d"
BAD = "#b3261e"
ACCENT = "#1f4fd8"
AMBER = "#8a5a00"

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)


def font(size, bold=False, mono=False):
    return ImageFont.truetype(FM if mono else (FB if bold else F), size)


title = font(33, bold=True)
sub = font(21)
lab = font(20)
lab_b = font(20, bold=True)
mono = font(19, mono=True)
small = font(18)
foot = font(17)

d.text((48, 32), "Agent memory trace: one span per memory operation", font=title, fill=INK)
d.text((48, 78), "create_memory  ·  search_memory  ·  delete_memory      GenAI semconv shape, fixture dump",
       font=sub, fill=MUTED)

TOP = 126
TRACE_H = 206
BAR_X0, BAR_X1 = 320, W - 72
NOTE_X = 714


def note_font(text):
    """Largest mono size whose text fits between NOTE_X and the box edge."""
    for size in (19, 18, 17, 16, 15):
        f = font(size, mono=True)
        if d.textlength(text, font=f) <= BAR_X1 - NOTE_X - 6:
            return f
    return font(15, mono=True)


def block(y, header, rows):
    d.rounded_rectangle([48, y, W - 48, y + TRACE_H - 18], radius=14, fill=BOX, outline=LINE, width=2)
    d.text((68, y + 12), header, font=small, fill=MUTED)
    py = y + 40
    d.rounded_rectangle([BAR_X0, py, BAR_X1, py + 30], radius=8, fill="#e8eefb", outline=ACCENT, width=2)
    d.text((BAR_X0 + 14, py + 4), "invoke_agent memory-fixture", font=mono, fill=INK)
    for i, (name, note, colour, fill) in enumerate(rows):
        ry = py + 44 + i * 42
        d.rounded_rectangle([BAR_X0, ry, 700, ry + 32], radius=8, fill=fill, outline=colour, width=2)
        d.text((BAR_X0 + 14, ry + 5), name, font=mono, fill=INK)
        d.text((NOTE_X, ry + 5), note, font=note_font(note), fill=colour)


block(TOP, "trace 1 · write path",
      [("create_memory", "record.count = 51", OK, "#eaf6ef")])

block(TOP + TRACE_H, "trace 2 · two searches, same query",
      [("search_memory", 'returns "UTC+8" *  count=1', OK, "#eaf6ef"),
       ("search_memory", 'returns "UTC+9" *  count=1', BAD, "#fdeceb")])
# callout to the left of the two search rows
cy = TOP + TRACE_H + 40 + 44
d.line([296, cy + 16, 316, cy + 16], fill=BAD, width=3)
d.text((78, cy - 10), "no write span", font=lab_b, fill=BAD)
d.text((78, cy + 14), "between these", font=lab, fill=BAD)
d.text((78, cy + 38), "two reads → stale", font=lab, fill=BAD)

block(TOP + 2 * TRACE_H, "trace 3 · eviction",
      [("delete_memory", "evicted_reason=superseded_by_newer_value", AMBER, "#fff6e6")])

d.text((48, H - 74), "Span shape from spans.json: record counts are dump attributes; the two returned values come from the run log in method.md.",
       font=foot, fill=MUTED)
d.text((48, H - 48), "Not a performance measurement. GenAI semantic conventions pinned at commit e6658f14, Development status.",
       font=foot, fill=MUTED)
d.text((48, H - 24), "* values marked with an asterisk are returned content, recorded in the run log, not span attributes.",
       font=foot, fill=MUTED)

img.save("static/images/agent-memory-observability-otel-spans-2026-cover.png", format="PNG", optimize=True)
print("wrote cover")
