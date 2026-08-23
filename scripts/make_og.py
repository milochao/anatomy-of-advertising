"""Compose the Open Graph image: two portraits vs each other on a white ground.

Run: python3 scripts/make_og.py
Writes: og.png (1200x630)
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORTRAITS = ROOT / "portraits"
OUT = ROOT / "og.png"

W, H = 1200, 630
BG = (255, 255, 255)         # #FFFFFF — matches the current site background
INK = (26, 22, 18)            # near-black warm
MID = (120, 108, 92)          # muted taupe
TRAD_ARISTOTLE = (226, 125, 44)  # ethics — orange
TRAD_KAHNEMAN = (122, 85, 56)    # behavioral — brown

PORTRAIT_SIZE = 290
GAP = 140

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_ITAL = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def load(size, path=SERIF_BOLD):
    return ImageFont.truetype(path, size)

def circle_mask(size):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size, size), fill=255)
    return m

def paste_portrait(canvas, name, x, y, ring):
    p = Image.open(PORTRAITS / f"{name}.png").convert("RGBA")
    p = p.resize((PORTRAIT_SIZE, PORTRAIT_SIZE), Image.LANCZOS)
    d = ImageDraw.Draw(canvas)
    r = PORTRAIT_SIZE // 2
    cx, cy = x + r, y + r
    d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=ring)
    canvas.paste(p, (x, y), circle_mask(PORTRAIT_SIZE))

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

draw.line([(60, 60), (W - 60, 60)], fill=INK, width=2)

eyebrow = load(20, SANS)
draw.text((60, 78), "THE ANATOMY OF ADVERTISING", fill=INK, font=eyebrow)

total_w = PORTRAIT_SIZE * 2 + GAP
start_x = (W - total_w) // 2
py = 150
paste_portrait(img, "aristotle", start_x, py, TRAD_ARISTOTLE)
paste_portrait(img, "kahneman", start_x + PORTRAIT_SIZE + GAP, py, TRAD_KAHNEMAN)

vs_font = load(44, SERIF_BOLD)
vs_text = "VS"
vs_bbox = draw.textbbox((0, 0), vs_text, font=vs_font)
vs_w = vs_bbox[2] - vs_bbox[0]
vs_h = vs_bbox[3] - vs_bbox[1]
vs_x = start_x + PORTRAIT_SIZE + (GAP - vs_w) // 2
vs_y = py + PORTRAIT_SIZE // 2 - vs_h // 2 - 6
draw.text((vs_x, vs_y), vs_text, fill=MID, font=vs_font)

name_font = load(30, SERIF_BOLD)
year_font = load(20, SANS)
def label(name, year, cx, y):
    nb = draw.textbbox((0, 0), name, font=name_font)
    nw = nb[2] - nb[0]
    draw.text((cx - nw // 2, y), name, fill=INK, font=name_font)
    yb = draw.textbbox((0, 0), year, font=year_font)
    yw = yb[2] - yb[0]
    draw.text((cx - yw // 2, y + 42), year, fill=MID, font=year_font)

label_y = py + PORTRAIT_SIZE + 22
label("Aristotle", "384 BCE", start_x + PORTRAIT_SIZE // 2, label_y)
label("Kahneman", "2011",     start_x + PORTRAIT_SIZE + GAP + PORTRAIT_SIZE // 2, label_y)

tag_font = load(26, SERIF_ITAL)
tag = "Thirty-two figures. Pick two. Watch them argue."
tb = draw.textbbox((0, 0), tag, font=tag_font)
tw = tb[2] - tb[0]
draw.text(((W - tw) // 2, H - 90), tag, fill=INK, font=tag_font)

by_font = load(18, SANS)
by = "BY MILO CHAO  ·  A COURSE IN DRAFT"
bb = draw.textbbox((0, 0), by, font=by_font)
bw = bb[2] - bb[0]
draw.text(((W - bw) // 2, H - 46), by, fill=MID, font=by_font)

img.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
