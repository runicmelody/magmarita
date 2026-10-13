#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Rasterise our simple SVGs (linear gradient + polygon paths) to PNG previews.

Only supports what tools/trace_logo.py emits: userSpaceOnUse linearGradient,
paths made of straight segments, even-odd fill.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, "assets", "branding")
SVG = "{http://www.w3.org/2000/svg}"
SS = 3  # supersampling


def hex_rgb(t):
    t = t.strip().lstrip("#")
    return (int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16))


def parse(d):
    polys = []
    for chunk in d.split("M"):
        nums = [float(x) for x in re.findall(r"-?\d+\.?\d*", chunk)]
        if len(nums) < 6:
            continue
        polys.append([(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)])
    return polys


def gradient(stops):
    def colour(t):
        t = max(0.0, min(1.0, t))
        for i in range(len(stops) - 1):
            o1, c1 = stops[i]
            o2, c2 = stops[i + 1]
            if o1 <= t <= o2:
                f = 0.0 if o2 == o1 else (t - o1) / (o2 - o1)
                return tuple(int(c1[k] + (c2[k] - c1[k]) * f) for k in range(3))
        return stops[-1][1]

    return colour


def render(path, scale=SS, bg=None, fg_override=None):
    tree = ET.parse(path)
    root = tree.getroot()
    vb = [float(v) for v in root.get("viewBox").split()]
    w, h = int(vb[2]), int(vb[3])
    W, H = w * scale, h * scale
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()

    grad = None
    for g in root.iter(SVG + "linearGradient"):
        stops = []
        for st in g.findall(SVG + "stop"):
            stops.append((float(st.get("offset")), hex_rgb(st.get("stop-color"))))
        grad = (gradient(stops), [float(g.get(k, 0)) * scale for k in ("x1", "y1", "x2", "y2")])

    for p in root.findall(SVG + "path"):
        d = p.get("d")
        fill = p.get("fill")
        polys = [[(x * scale, y * scale) for x, y in poly] for poly in parse(d)]
        edges = []
        ymin = H
        ymax = 0
        for poly in polys:
            n = len(poly)
            for i in range(n):
                x1, y1 = poly[i]
                x2, y2 = poly[(i + 1) % n]
                edges.append((x1, y1, x2, y2))
                ymin = min(ymin, y1, y2)
                ymax = max(ymax, y1, y2)
        for yy in range(int(ymin), int(ymax) + 1):
            yc = yy + 0.5
            xs = []
            for (x1, y1, x2, y2) in edges:
                if (y1 <= yc < y2) or (y2 <= yc < y1):
                    xs.append(x1 + (yc - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xa, xb = int(round(xs[i])), int(round(xs[i + 1]))
                if fg_override:
                    col = fg_override
                elif fill and fill.startswith("url(") and grad:
                    fn, (gx1, gy1, gx2, gy2) = grad
                    dx, dy = gx2 - gx1, gy2 - gy1
                    den = dx * dx + dy * dy or 1.0
                    for xx in range(max(0, xa), min(W, xb)):
                        t = ((xx - gx1) * dx + (yc - gy1) * dy) / den
                        px[xx, yy] = fn(t) + (255,)
                    continue
                else:
                    col = hex_rgb(fill)
                for xx in range(max(0, xa), min(W, xb)):
                    px[xx, yy] = col + (255,)

    img = img.resize((w, h), Image.LANCZOS)
    if bg is not None:
        base = Image.new("RGBA", (w, h), bg + (255,))
        base.alpha_composite(img)
        img = base
    return img


def main():
    light = (255, 255, 255)
    dark = (24, 28, 32)
    tiles = []
    for name in ("magmarita-icon.svg", "magmarita-icon-tones.svg", "magmarita-icon-mono.svg"):
        p = os.path.join(BRAND, name)
        if not os.path.exists(p):
            continue
        for bg in (light, dark):
            tiles.append((name, render(p, bg=bg)))

    pad, label_h = 28, 34
    tw = max(t[1].width for t in tiles)
    th = max(t[1].height for t in tiles)
    cols = 3
    rows = 2
    board = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad + label_h) + pad), (238, 240, 243))
    d = ImageDraw.Draw(board)
    f = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 18)
    for i, (name, im) in enumerate(tiles):
        cx = pad + (i % cols) * (tw + pad)
        cy = pad + (i // cols) * (th + pad + label_h)
        base = Image.new("RGB", im.size, (255, 255, 255) if i < cols else (24, 28, 32))
        base.paste(im, (0, 0), im if im.mode == "RGBA" else None)
        board.paste(base, (cx, cy))
        d.text((cx, cy + th + 6), name, font=f, fill=(60, 70, 80))

    out = os.path.join(BRAND, "preview-board.png")
    board.save(out)
    print("wrote", out, board.size)

    render(os.path.join(BRAND, "magmarita-icon.svg"), scale=2, bg=light).save(
        os.path.join(BRAND, "preview-gradient.png"))
    print("wrote preview-gradient.png")


if __name__ == "__main__":
    main()
