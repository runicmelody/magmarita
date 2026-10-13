#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Rebuild every MagmaRita branding PNG from your hand-drawn mark.

1. Draw the mark in Krita (square canvas, transparent), export to
   assets/branding/source/mark.png
2. Run:  python tools/make_branding_from_mark.py

Emits transparent banners in two flavours:
    <name>.png        for light backgrounds (dark-red tagline)
    <name>-dark.png   for dark backgrounds  (light tagline)
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "branding")
SRC = os.path.join(OUT, "source", "mark.png")

FB = r"C:\Windows\Fonts\segoeuib.ttf"
FR = r"C:\Windows\Fonts\segoeui.ttf"
ICON_SIZES = (1024, 512, 256, 128, 64, 48, 32)
TAGLINE = "Magma-style keybinds for Krita"

LIGHT = {"a": (224, 43, 45), "b": (176, 28, 32), "tag": (142, 27, 31)}
DARK = {"a": (255, 88, 90), "b": (224, 43, 45), "tag": (255, 214, 216)}


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


def compose(mark, width, height, icon_px, title_px, sub_px, pad, pal, tagline=True):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    icon_px = min(icon_px, mark.width)
    icon = mark.resize((icon_px, icon_px), Image.LANCZOS)
    img.paste(icon, (pad, (height - icon_px) // 2), icon)

    f1 = ImageFont.truetype(FB, title_px)
    lines = [("TITLE", f1, pal["a"], int(title_px * 0.30) if tagline else 0)]
    if tagline:
        lines.append((TAGLINE, ImageFont.truetype(FR, sub_px), pal["tag"], 0))

    x = pad + icon_px + int(pad * 0.7)
    y = (height - block_height(lines)) // 2
    d = ImageDraw.Draw(img)
    for text, f, colour, gap in lines:
        a, dd = f.getmetrics()
        if text == "TITLE":
            d.text((x, y), "Magma", font=f1, fill=pal["a"] + (255,), anchor="la")
            d.text((x + f1.getlength("Magma"), y), "Rita", font=f1,
                   fill=pal["b"] + (255,), anchor="la")
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

    specs = [
        ("magmarita-logo-horizontal", 1200, 372, 240, 128, 46, 42, True),
        ("magmarita-wordmark", 1200, 300, 240, 140, 40, 42, False),
        ("itch-cover-630x250", 630, 250, 150, 54, 22, 26, True),
        ("github-social-1280x640", 1280, 640, 300, 96, 36, 64, True),
    ]
    made = []
    for name, w, h, ic, t, sub, pad, tag in specs:
        for suffix, pal in (("", LIGHT), ("-dark", DARK)):
            fn = "%s%s.png" % (name, suffix)
            compose(mark, w, h, ic, t, sub, pad, pal, tag).save(os.path.join(OUT, fn))
            made.append(fn)
    print("composed %d banners (light + dark)" % len(made))

    tiles = []
    for name, w, _h, _ic, _t, _sub, _pad, _tag in specs:
        pair = []
        for suffix in ("", "-dark"):
            p = os.path.join(OUT, "%s%s.png" % (name, suffix))
            if os.path.exists(p):
                im = Image.open(p).convert("RGBA")
                pair.append(im.resize((w, int(im.height * w / im.width)), Image.LANCZOS))
        tiles.append((name, pair))

    pad, lab = 22, 26
    tw = max(im.width for _n, pair in tiles for im in pair)
    rows_h = sum(max(im.height for im in pair) + lab for _n, pair in tiles) + pad
    board = Image.new("RGB", (tw * 2 + pad * 3, rows_h), (232, 235, 238))
    d = ImageDraw.Draw(board)
    f = ImageFont.truetype(FB, 16)
    y = pad
    for name, pair in tiles:
        for j, im in enumerate(pair):
            x = pad + j * (tw + pad)
            bg = (255, 255, 255) if j == 0 else (26, 30, 36)
            tile = Image.new("RGB", im.size, bg)
            tile.paste(im, (0, 0), im)
            board.paste(tile, (x, y))
            d.text((x, y + im.height + 3), name + (" on dark" if j else " on light"),
                   font=f, fill=(70, 80, 92))
        y += max(im.height for im in pair) + lab
    board.save(os.path.join(OUT, "preview-logos.png"))
    print("wrote preview-logos.png", board.size)


if __name__ == "__main__":
    main()
