#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Rebuild every MagmaRita branding PNG from your hand-drawn mark.

1. Draw the mark in Krita (square canvas, transparent) and export it to
   assets/branding/source/mark.png
2. Run:  python tools/make_branding_from_mark.py

Produces: icon sizes (never upscaled), horizontal logo, wordmark, itch cover
(630x250), GitHub social (1280x640), a vector trace and a preview board.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "branding")
SRC = os.path.join(OUT, "source", "mark.png")

RED = (224, 43, 45)        # wordmark
RED_DEEP = (176, 28, 32)   # second half, for a bit of depth
INK = (20, 28, 38)         # tagline: near-black for contrast
BG = (255, 255, 255)
FB = r"C:\Windows\Fonts\segoeuib.ttf"
FR = r"C:\Windows\Fonts\segoeui.ttf"
ICON_SIZES = (1024, 512, 256, 128, 64, 48, 32)
TAGLINE = "Magma-style keybinds for Krita"


def _normalise(im):
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    side = max(int(max(w, h) * 1.14), 64)
    out = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    out.paste(im, ((side - w) // 2, (side - h) // 2), im)
    return out


def load_mark():
    path = SRC if os.path.exists(SRC) else os.path.join(OUT, "magmarita-icon-218.png")
    print("using", path)
    return _normalise(Image.open(path).convert("RGBA"))


def block_height(lines):
    total = 0
    for _t, f, _c, gap in lines:
        a, d = f.getmetrics()
        total += a + d + gap
    return total


def draw_block(d, x, y, lines):
    for text, f, colour, gap in lines:
        a, dd = f.getmetrics()
        d.text((x, y), text, font=f, fill=colour + (255,), anchor="la")
        y += a + dd + gap
    return y


def compose(mark, width, height, icon_px, title_px, sub_px, pad, tagline=True):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))   # transparent banner
    icon_px = min(icon_px, mark.width)
    icon = mark.resize((icon_px, icon_px), Image.LANCZOS)
    img.paste(icon, (pad, (height - icon_px) // 2), icon)

    f1 = ImageFont.truetype(FB, title_px)
    parts = [("Magma", f1, RED), ("Rita", f1, RED_DEEP)]
    lines = []
    if tagline:
        lines.append(("TITLE", f1, RED, int(title_px * 0.30)))
        lines.append((TAGLINE, ImageFont.truetype(FR, sub_px), INK, 0))
    else:
        lines.append(("TITLE", f1, RED, 0))

    x = pad + icon_px + int(pad * 0.7)
    y = (height - block_height(lines)) // 2
    d = ImageDraw.Draw(img)
    for text, f, colour, gap in lines:
        a, dd = f.getmetrics()
        if text == "TITLE":
            d.text((x, y), parts[0][0], font=f1, fill=RED + (255,), anchor="la")
            d.text((x + f1.getlength(parts[0][0]), y), parts[1][0], font=f1,
                   fill=RED_DEEP + (255,), anchor="la")
        else:
            d.text((x, y), text, font=f, fill=colour + (255,), anchor="la")
        y += a + dd + gap
    return img


def main():
    mark = load_mark()
    os.makedirs(OUT, exist_ok=True)

    cap = mark.width
    sizes = sorted({s for s in ICON_SIZES if s <= cap} | {cap}, reverse=True)
    print("source mark: %dpx -> icons %s (never upscaled)" % (cap, sizes))
    for size in sizes:
        mark.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, "magmarita-icon-%d.png" % size))
    mark.resize((min(cap, 512), min(cap, 512)), Image.LANCZOS).save(os.path.join(OUT, "magmarita-icon.png"))

    compose(mark, 1200, 372, 240, 128, 46, 42).save(os.path.join(OUT, "magmarita-logo-horizontal.png"))
    compose(mark, 1200, 300, 240, 140, 40, 42, tagline=False).save(os.path.join(OUT, "magmarita-wordmark.png"))
    compose(mark, 630, 250, 150, 54, 22, 26).save(os.path.join(OUT, "itch-cover-630x250.png"))
    compose(mark, 1280, 640, 300, 96, 36, 64).save(os.path.join(OUT, "github-social-1280x640.png"))
    print("composed logo + wordmark + cover + social")

    # preview board so the layout can be eyeballed in one image
    tiles = [
        ("magmarita-logo-horizontal.png", 900),
        ("magmarita-wordmark.png", 900),
        ("github-social-1280x640.png", 900),
        ("itch-cover-630x250.png", 630),
    ]
    ims = []
    for name, w in tiles:
        p = os.path.join(OUT, name)
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            ims.append((name, im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)))
    if ims:
        pad, lab = 22, 28
        tw = max(i.width for _n, i in ims)
        th = sum(i.height + lab for _n, i in ims) + pad
        W = tw * 2 + pad * 3
        H = th + pad
        board = Image.new("RGB", (W, H), (232, 235, 238))
        d = ImageDraw.Draw(board)
        f = ImageFont.truetype(FB, 16)
        y = pad
        for name, im in ims:
            for j, bg in enumerate(((255, 255, 255), (26, 30, 36))):
                x = pad + j * (tw + pad)
                tile = Image.new("RGB", im.size, bg)
                tile.paste(im, (0, 0), im)
                board.paste(tile, (x, y))
                d.text((x, y + im.height + 4), name + ("  (on dark)" if j else "  (on light)"),
                       font=f, fill=(70, 80, 92))
            y += im.height + lab
        board.save(os.path.join(OUT, "preview-logos.png"))
        print("wrote preview-logos.png", board.size)




if __name__ == "__main__":
    main()
