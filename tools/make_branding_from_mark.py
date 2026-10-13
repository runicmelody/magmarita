#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Rebuild every MagmaRita branding PNG from your own hand-drawn mark.

1. Draw the mark in Krita on a SQUARE canvas (2048x2048 recommended), with a
   transparent background, and export it as:
        assets/branding/source/mark.png
2. Run:
        python tools/make_branding_from_mark.py

Regenerates: all icon sizes, the horizontal logo, the wordmark, the itch.io
cover (630x250) and the GitHub social preview (1280x640).
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "branding")
SRC = os.path.join(OUT, "source", "mark.png")

BLUE_TXT = (30, 145, 205)
TEAL_TXT = (20, 170, 155)
INK = (58, 74, 90)
WHITE = (255, 255, 255)
FB = r"C:\Windows\Fonts\segoeuib.ttf"
FR = r"C:\Windows\Fonts\segoeui.ttf"
FL = r"C:\Windows\Fonts\segoeuil.ttf"
ICON_SIZES = (1024, 512, 256, 128, 64, 48, 32)


def load_mark():
    if os.path.exists(SRC):
        print("using", SRC)
        return Image.open(SRC).convert("RGBA")
    fallback = os.path.join(OUT, "magmarita-icon-1024.png")
    print("! %s not found - using %s as placeholder" % (SRC, fallback))
    return Image.open(fallback).convert("RGBA")


def scaled(mark, size):
    return mark.resize((size, size), Image.LANCZOS)


def main():
    mark = load_mark()
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    for size in ICON_SIZES:
        scaled(mark, size).save(os.path.join(OUT, "magmarita-icon-%d.png" % size))
    scaled(mark, 512).save(os.path.join(OUT, "magmarita-icon.png"))

    def wordmark(width, tagline=True):
        ic = int(width * 0.20)
        icon = scaled(mark, ic)
        f1 = ImageFont.truetype(FB, int(width * 0.115))
        f2 = ImageFont.truetype(FL, int(width * 0.045))
        tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        w1 = tmp.textlength("Magma", font=f1)
        height = ic + int(width * 0.03)
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        img.paste(icon, (int(width * 0.03), (height - ic) // 2), icon)
        x = int(width * 0.03) + ic + int(width * 0.03)
        y = (height - int(width * 0.115)) // 2 - (int(width * 0.03) if tagline else 0)
        d = ImageDraw.Draw(img)
        d.text((x, y), "Magma", font=f1, fill=BLUE_TXT + (255,))
        d.text((x + w1, y), "Rita", font=f1, fill=TEAL_TXT + (255,))
        if tagline:
            d.text((x + int(width * 0.004), y + int(width * 0.125)),
                   "Magma-style keybinds for Krita", font=f2, fill=INK + (255,))
        return img

    wordmark(1200).save(os.path.join(OUT, "magmarita-logo-horizontal.png"))
    wordmark(1200, tagline=False).save(os.path.join(OUT, "magmarita-wordmark.png"))

    cover = Image.new("RGBA", (630, 250), WHITE + (255,))
    it = scaled(mark, 150)
    cover.paste(it, (34, 50), it)
    d = ImageDraw.Draw(cover)
    d.text((210, 74), "MagmaRita", font=ImageFont.truetype(FB, 52), fill=BLUE_TXT + (255,))
    d.text((212, 134), "Magma-style keybinds", font=ImageFont.truetype(FB, 22), fill=TEAL_TXT + (255,))
    d.text((212, 162), "for Krita", font=ImageFont.truetype(FR, 22), fill=INK + (255,))
    cover.save(os.path.join(OUT, "itch-cover-630x250.png"))

    social = Image.new("RGBA", (1280, 640), WHITE + (255,))
    sb = scaled(mark, 340)
    social.paste(sb, (110, 150), sb)
    d = ImageDraw.Draw(social)
    d.text((520, 205), "MagmaRita", font=ImageFont.truetype(FB, 104), fill=BLUE_TXT + (255,))
    d.text((524, 330), "Magma-style keybinds & palette", font=ImageFont.truetype(FB, 38), fill=TEAL_TXT + (255,))
    d.text((524, 378), "for Krita", font=ImageFont.truetype(FR, 38), fill=INK + (255,))
    d.text((524, 452), "github.com/runicmelody/magmarita", font=ImageFont.truetype(FL, 30), fill=INK + (200,))
    social.save(os.path.join(OUT, "github-social-1280x640.png"))

    print("done - rebuilt %d icons + logo + cover + social" % len(ICON_SIZES))


if __name__ == "__main__":
    main()
