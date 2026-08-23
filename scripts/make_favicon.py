"""Compose favicons: white ground, ink serif 'A'. Writes .ico + PNGs at multiple sizes."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BG = (255, 255, 255)
INK = (26, 22, 18)
FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

def render(size):
    img = Image.new("RGBA", (size, size), BG + (255,))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, int(size * 0.82))
    text = "A"
    bb = d.textbbox((0, 0), text, font=f)
    w = bb[2] - bb[0]
    h = bb[3] - bb[1]
    x = (size - w) // 2 - bb[0]
    y = (size - h) // 2 - bb[1] - int(size * 0.02)
    d.text((x, y), text, fill=INK, font=f)
    return img

sizes = [16, 32, 48, 64, 128, 180]
imgs = [render(s) for s in sizes]
imgs[-1].save(ROOT / "apple-touch-icon.png", "PNG", optimize=True)
imgs[3].save(ROOT / "favicon-64.png", "PNG", optimize=True)
imgs[1].save(ROOT / "favicon-32.png", "PNG", optimize=True)
imgs[0].save(ROOT / "favicon.ico", format="ICO", sizes=[(16,16),(32,32),(48,48)])
print("wrote favicon.ico, favicon-32.png, favicon-64.png, apple-touch-icon.png")
