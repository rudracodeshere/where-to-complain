#!/usr/bin/env python3
"""Make the share image (assets/og.png, 1200x630), the logo (assets/logo.png, 512x512) and
assets/favicon.svg in the DESIGN.md brand colours. Run once when the brand changes; build.py copies
them into docs/. Needs Pillow (PIL)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "assets"
INK, MUTED, ACCENT, WASH, PAPER, LINE = "#17212b", "#4f5b66", "#0b5a47", "#e8f2ee", "#ffffff", "#d3dae0"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def mark(d, x, y, s, fg, bg):
    """Three rising steps: the escalation ladder (company, regulator, ombudsman)."""
    d.rounded_rectangle([x, y, x + s, y + s], radius=s // 6, fill=bg)
    u = s / 8
    for i in range(3):
        top = y + s - u * (2.2 + i * 1.9)
        d.rectangle([x + u * (1 + i * 2.1), top, x + u * (2.6 + i * 2.1), y + s - u * 1.2], fill=fg)

def og():
    im = Image.new("RGB", (1200, 630), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1200, 630], fill=WASH)
    d.rectangle([0, 590, 1200, 630], fill=ACCENT)
    mark(d, 80, 80, 120, PAPER, ACCENT)
    d.text((80, 250), "Where to Complain", font=ImageFont.truetype(BOLD, 84), fill=INK)
    f = ImageFont.truetype(REG, 40)
    d.text((80, 370), "Who to write to, in what order, by when.", font=f, fill=INK)
    d.text((80, 430), "Indian consumer complaints, from official sources.", font=f, fill=MUTED)
    d.text((80, 598), "rudracodeshere.github.io/where-to-complain", font=ImageFont.truetype(REG, 26), fill=PAPER)
    im.save(A / "og.png", optimize=True)

def logo():
    im = Image.new("RGB", (512, 512), PAPER)
    mark(ImageDraw.Draw(im), 0, 0, 512, PAPER, ACCENT)
    im.save(A / "logo.png", optimize=True)

def favicon():
    (A / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="11" fill="{ACCENT}"/>'
        '<rect x="8" y="42" width="12" height="13" fill="#fff"/>'
        '<rect x="25" y="29" width="12" height="26" fill="#fff"/>'
        '<rect x="42" y="14" width="12" height="41" fill="#fff"/></svg>\n', encoding="utf-8")

if __name__ == "__main__":
    og(); logo(); favicon()
    for n in ("og.png", "logo.png", "favicon.svg"):
        print(n, (A / n).stat().st_size, "bytes")
