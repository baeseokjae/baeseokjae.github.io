#!/usr/bin/env python3
"""
Cover image generator for RockB blog posts.
Usage: python3 gen_cover.py <post-slug>
Example: python3 gen_cover.py mcp-vs-rag-vs-ai-agents-2026
"""
import sys, os, hashlib, re
from PIL import Image, ImageDraw, ImageFont

BLOG_DIR  = "/home/ubuntu/blog"
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
W, H      = 1200, 630

PALETTES = [
    {"bg1": (15, 23, 42),  "bg2": (30, 58, 138),  "dot": (99, 179, 237)},   # navy/blue
    {"bg1": (30, 10, 60),  "bg2": (88, 28, 135),   "dot": (196, 132, 252)},  # purple
    {"bg1": (60, 10, 10),  "bg2": (154, 52, 18),   "dot": (251, 146, 60)},   # orange
    {"bg1": (5, 46, 22),   "bg2": (20, 83, 45),    "dot": (74, 222, 128)},   # green
    {"bg1": (12, 10, 55),  "bg2": (30, 27, 75),    "dot": (129, 140, 248)},  # indigo
    {"bg1": (8, 28, 36),   "bg2": (12, 74, 110),   "dot": (34, 211, 238)},   # teal
    {"bg1": (40, 10, 5),   "bg2": (120, 30, 15),   "dot": (251, 113, 133)},  # red/pink
    {"bg1": (20, 5, 45),   "bg2": (76, 29, 149),   "dot": (167, 139, 250)},  # violet
    {"bg1": (8, 25, 35),   "bg2": (12, 60, 80),    "dot": (45, 212, 191)},   # dark teal
    {"bg1": (35, 20, 5),   "bg2": (92, 45, 10),    "dot": (252, 196, 25)},   # amber
]

def pick_palette(slug):
    h = int(hashlib.md5(slug.encode()).hexdigest(), 16)
    return PALETTES[h % len(PALETTES)]

def parse_frontmatter(md_path):
    with open(md_path) as f:
        content = f.read()
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}, content
    fm_text = m.group(1)
    data = {}
    # title
    t = re.search(r'^title:\s*"?(.+?)"?\s*$', fm_text, re.MULTILINE)
    if t: data["title"] = t.group(1).strip('"')
    # tags
    tg = re.search(r'tags:\s*\[([^\]]+)\]', fm_text)
    if tg:
        data["tags"] = [x.strip().strip('"') for x in tg.group(1).split(",")]
    return data

def derive_tag_label(slug, tags):
    """Derive a short uppercase tag from tags or slug keywords."""
    keywords = {
        "mcp": "AI ARCHITECTURE", "rag": "AI ARCHITECTURE",
        "agent": "AGENT AI", "agentic": "AGENT AI",
        "coding": "AI CODING", "code": "AI CODING", "copilot": "AI CODING",
        "image": "IMAGE AI", "midjourney": "IMAGE AI", "dall": "IMAGE AI",
        "video": "AI VIDEO", "sora": "AI VIDEO", "runway": "AI VIDEO",
        "writing": "AI WRITING", "claude": "AI WRITING", "chatgpt": "AI WRITING",
        "seo": "SEO", "blog": "SEO",
        "local": "LOCAL AI", "ollama": "LOCAL AI", "lm studio": "LOCAL AI",
        "framework": "AGENT AI", "langgraph": "AGENT AI", "crewai": "AGENT AI",
    }
    combined = slug + " " + " ".join(tags or [])
    combined_lower = combined.lower()
    for kw, label in keywords.items():
        if kw in combined_lower:
            return label
    return "AI GUIDE"

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def wrap_text(text, font, max_width, draw):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if draw.textlength(test, font=font) <= max_width:
                line = test
            else:
                if line: lines.append(line)
                line = word
        if line: lines.append(line)
    return lines

def generate(slug):
    md_path = os.path.join(BLOG_DIR, "content", "posts", f"{slug}.md")
    if not os.path.exists(md_path):
        print(f"ERROR: {md_path} not found", file=sys.stderr)
        sys.exit(1)

    fm = parse_frontmatter(md_path)
    title = fm.get("title", slug.replace("-", " ").title())
    tags  = fm.get("tags", [])
    p     = pick_palette(slug)
    tag_label = derive_tag_label(slug, tags)

    # Gradient background
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        draw.line([(0, y), (W, y)], fill=lerp_color(p["bg1"], p["bg2"], t))

    # Grid overlay
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(0, W, 60):
        od.line([(x, 0), (x, H)], fill=p["dot"] + (10,), width=1)
    for y in range(0, H, 60):
        od.line([(0, y), (W, y)], fill=p["dot"] + (10,), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Accent bar
    draw.rectangle([0, 0, 6, H], fill=p["dot"])

    # TAG pill
    tag_font = ImageFont.truetype(FONT_BOLD, 18)
    tag_w    = draw.textlength(tag_label, font=tag_font)
    draw.rounded_rectangle([50, 50, 70 + tag_w, 88], radius=6, fill=p["dot"])
    draw.text((60, 60), tag_label, font=tag_font, fill=(10, 10, 10))

    # Split title on ":" into main title + subtitle
    if ":" in title:
        main_title, subtitle = title.split(":", 1)
        main_title = main_title.strip()
        subtitle = subtitle.strip()
    else:
        main_title = title
        subtitle = ""

    # Main title (auto-wrap, large bold)
    for font_size in [68, 56, 46]:
        title_font = ImageFont.truetype(FONT_BOLD, font_size)
        lines = wrap_text(main_title, title_font, W - 120, draw)
        if len(lines) <= 2:
            break

    title_y = 130
    for line in lines[:2]:
        draw.text((60, title_y), line, font=title_font, fill=(255, 255, 255))
        title_y += font_size + 10

    # Subtitle (smaller, lighter gray)
    if subtitle:
        sub_font = ImageFont.truetype(FONT_REG, 30)
        sub_lines = wrap_text(subtitle, sub_font, W - 120, draw)
        title_y += 8
        for line in sub_lines[:2]:
            draw.text((60, title_y), line, font=sub_font, fill=(180, 180, 180))
            title_y += 40

    # Brand line
    brand_font = ImageFont.truetype(FONT_BOLD, 20)
    reg_font   = ImageFont.truetype(FONT_REG, 20)
    draw.text((60, H - 52), "RockB", font=brand_font, fill=p["dot"])
    draw.text(
        (60 + draw.textlength("RockB", font=brand_font) + 16, H - 52),
        "· Stay ahead of AI.", font=reg_font, fill=(160, 160, 160)
    )

    # Decorative circles (top-right)
    for i in range(5):
        r   = 220 - i * 38
        cx, cy = W - 120, 80
        od2  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od2d = ImageDraw.Draw(od2)
        od2d.ellipse([cx-r, cy-r, cx+r, cy+r],
                     outline=p["dot"] + ([120, 90, 60, 40, 24][i],), width=2)
        img  = Image.alpha_composite(img.convert("RGBA"), od2).convert("RGB")
        draw = ImageDraw.Draw(img)

    out_path = os.path.join(BLOG_DIR, "static", "images", f"{slug}.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    print(f"Cover image saved: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gen_cover.py <post-slug>")
        sys.exit(1)
    generate(sys.argv[1])
