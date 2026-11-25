"""Draw the article cover from the measured comparison (no invented values).

Reads out/retry-policy-compare.csv from the run in this directory and renders a
two-panel explanatory figure: which envelope field decides the class, and how
many server-side requests each retry policy spends per class.

Run from the reproduction directory:
    python3 scripts/make_cover.py ../../../../static/images/model-retirement-error-handling-2026.png
"""
import csv
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "out", "retry-policy-compare.csv")
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
W, H = 1200, 630
BG = (255, 255, 255)
INK = (24, 30, 38)
MUTED = (92, 102, 115)
BOX = (238, 241, 245)
PERM = (176, 42, 42)
TRAN = (32, 96, 168)


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def load_counts():
    counts = {}
    with open(CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            counts[(row["policy"], row["label"])] = int(row["server_requests"])
    return counts


def main():
    out_path = sys.argv[1]
    counts = load_counts()
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((48, 34), "One error status, two retry policies", font=font(38, True), fill=INK)
    d.text((48, 88), "Measured on six frozen envelopes against a loopback mock server",
           font=font(22), fill=MUTED)

    # Panel A: what the envelope supports. Three boxes, one per class the
    # shipped classifier in compare.py can emit for these statuses.
    d.text((48, 132), "1. The envelope decides the class, not the cause",
           font=font(24, True), fill=INK)

    def box(y, lines, label, sub, colour, height):
        d.rounded_rectangle([48, y, 545, y + height], 10, fill=BOX)
        for k, line in enumerate(lines):
            d.text((66, y + 9 + k * 22), line, font=font(20), fill=INK)
        d.text((565, y + 12), "\u2192", font=font(28, True), fill=MUTED)
        d.text((600, y + 7), label, font=font(21, True), fill=colour)
        if sub:
            d.text((600, y + 30), sub, font=font(17), fill=MUTED)

    box(168, ["HTTP 404 + error.type=not_found_error",
              "or error string \"model ... not found\""],
        "model_unavailable  (stop)", "same bytes for a retired ID and a typo",
        PERM, 48)
    box(224, ["HTTP 429"], "rate_limit  (retry)", None, TRAN, 44)
    box(276, ["HTTP 500, 502, 503, 504, 529"], "transient  (retry)", None, TRAN, 44)

    # Panel B: requests spent per class per policy, from the CSV.
    d.text((48, 348), "2. Server-side requests per task (3-attempt cap, 200 ms doubling backoff)",
           font=font(22, True), fill=INK)
    groups = [("retry_all", "retry_all"), ("no_retry_4xx", "no_retry_4xx")]
    base_y, bar_h, pitch = 424, 34, 66
    for i, (key, label) in enumerate(groups):
        x0 = 60 + i * 570
        d.text((x0, base_y - 28), label, font=font(22, True), fill=INK)
        perm = counts[(key, "model_unavailable")]
        tran = counts[(key, "transient")]
        for j, (val, colour, tag) in enumerate(((perm, PERM, "model_unavailable"),
                                               (tran, TRAN, "transient"))):
            y = base_y + j * pitch
            d.text((x0, y), tag, font=font(17), fill=MUTED)
            w = val * 52
            top = y + 18
            d.rectangle([x0 + 205, top, x0 + 205 + w, top + bar_h], fill=colour)
            d.text((x0 + 205 + w + 12, top + 1), f"{val}", font=font(23, True), fill=INK)

    d.text((48, 600), "Source: research/evidence/model-retirement-error-handling-2026/reproduction/out/retry-policy-compare.csv",
           font=font(15), fill=MUTED)
    img.save(out_path, optimize=True)
    print(out_path, img.size)


if __name__ == "__main__":
    main()
