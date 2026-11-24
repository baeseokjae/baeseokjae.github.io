#!/usr/bin/env python3
"""Draw the article cover: a conceptual two-lane diagram (no measurement data).

Lane A: the measured single-shot top-5 shape - one question, one retrieval, the bridging
        fact ranked below a five-slot cut.
Lane B: an iterative split (retrieve hop 1, put the intermediate entity into the next
        query) that this run did NOT measure. Labelled as such on the image so that a
        reader who only sees the cover is not told decomposition fixed anything here.
Deliberately carries no numbers - the measured counts live in the article tables.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 720
BG = "#f7f9fc"
INK = "#16202e"
MUTED = "#5b6b80"
OK = "#1f7a4d"
BAD = "#b3261e"
BOX = "#ffffff"
LINE = "#c9d4e3"
ACCENT = "#1f4fd8"
AMBER = "#8a5a00"

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f_title = ImageFont.truetype(FB, 46)
f_sub = ImageFont.truetype(F, 24)
f_lane = ImageFont.truetype(FB, 26)
f_head = ImageFont.truetype(FB, 22)
f_body = ImageFont.truetype(F, 23)
f_q = ImageFont.truetype(FB, 24)
f_small = ImageFont.truetype(F, 21)
f_small2 = ImageFont.truetype(F, 20)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 8], fill=ACCENT)

d.text((40, 26), "Two facts, one question", font=f_title, fill=INK)
d.text((40, 84), "Why one retrieval can carry only half of a two-hop answer", font=f_sub, fill=MUTED)


def box(x, y, w, h, fill=BOX, outline=LINE, width=2):
    d.rounded_rectangle([x, y, x + w, y + h], radius=13, fill=fill, outline=outline, width=width)


def wrap(text, font, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(x, y, text, font, fill, width, lead):
    for line in wrap(text, font, width):
        d.text((x, y), line, font=font, fill=fill)
        y += lead
    return y


def arrow(x, y):
    d.line([x, y, x + 34, y], fill=LINE, width=3)
    d.polygon([(x + 40, y), (x + 28, y - 6), (x + 28, y + 6)], fill=LINE)


COL = {"left": (40, 286), "mid": (380, 452), "right": (882, 274)}

# ---------------- lane A: measured single-shot shape ----------------
y0 = 138
d.text((40, y0), "A. Single-shot top-5", font=f_lane, fill=BAD)
d.text((40, y0 + 32), "the bridge ranks below the five-slot cut", font=f_small, fill=MUTED)
by = y0 + 66

box(COL["left"][0], by, COL["left"][1], 180)
d.text((56, by + 16), "Question", font=f_head, fill=MUTED)
para(56, by + 52, "\u201cWhich database holds orders-api?\u201d", f_q, INK, 254, 30)

arrow(COL["left"][0] + COL["left"][1] + 6, by + 98)

box(COL["mid"][0], by, COL["mid"][1], 180)
d.text((394, by + 16), "Retrieved (1 of 2 facts)", font=f_head, fill=MUTED)
d.text((394, by + 52), "\u2713  orders-api runs in eu-west", font=f_body, fill=OK)
d.text((394, by + 86), "\u2717  eu-west data \u2192 aurora-eu-1", font=f_body, fill=BAD)
d.text((394, by + 126), "second fact ranked below the cut", font=f_small, fill=MUTED)

arrow(COL["mid"][0] + COL["mid"][1] + 6, by + 98)

box(COL["right"][0], by, COL["right"][1], 180, fill="#fdf1f0", outline=BAD)
d.text((896, by + 16), "Answer", font=f_head, fill=MUTED)
para(896, by + 52, "one of the two facts arrives", f_small, BAD, 246, 28)

# ---------------- lane B: iterative split, not measured here ----------------
y1 = 396
d.text((40, y1), "B. Iterative split", font=f_lane, fill=AMBER)
d.text((40, y1 + 32), "not measured in this run: the first hop feeds the next query", font=f_small, fill=MUTED)
by = y1 + 66

box(COL["left"][0], by, COL["left"][1], 196)
d.text((56, by + 16), "Step 1: hop 1", font=f_head, fill=MUTED)
d.text((56, by + 52), "\u2713  orders-api runs in eu-west", font=f_small2, fill=OK)
d.text((56, by + 92), "region now in hand", font=f_small2, fill=INK)

arrow(COL["left"][0] + COL["left"][1] + 6, by + 98)

box(COL["mid"][0], by, COL["mid"][1], 180, fill="#fdf8ec", outline=AMBER)
d.text((394, by + 16), "Step 2: second query", font=f_head, fill=MUTED)
d.text((394, by + 56), "\u2713  eu-west data \u2192 aurora-eu-1", font=f_small2, fill=OK)
d.text((394, by + 100), "reachable only on this second call", font=f_small, fill=MUTED)

arrow(COL["mid"][0] + COL["mid"][1] + 6, by + 98)

box(COL["right"][0], by, COL["right"][1], 180, fill="#fdf8ec", outline=AMBER)
d.text((896, by + 16), "Answer", font=f_head, fill=MUTED)
para(896, by + 52, "both facts, if the loop is run", f_small, AMBER, 246, 28)
d.text((896, by + 130), "cost: one extra round trip", font=f_small2, fill=MUTED)

d.text((40, H - 56), "Lane A is the measured single-shot shape; lane B is the iterative loop this run did not test.",
       font=f_small2, fill=MUTED)
d.text((40, H - 30), "Conceptual diagram of retrieval shape, not measurement data.", font=f_small2, fill=MUTED)

img.save("static/images/agent-memory-multi-hop-recall-2026-cover.png", optimize=True)
print("saved", img.size)
