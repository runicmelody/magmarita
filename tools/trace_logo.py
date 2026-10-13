#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Trace a flat PNG mark into a clean SVG.

Writes a colour trace and a mono (silhouette) trace:
    assets/branding/magmarita-icon.svg       (colour)
    assets/branding/magmarita-icon-mono.svg  (single colour, from the alpha)

Usage: python tools/trace_logo.py [input.png]
"""

import os
import sys
from collections import defaultdict

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_IN = os.path.join(ROOT, "assets", "branding", "source", "mark.png")
OUT_COLOUR = os.path.join(ROOT, "assets", "branding", "magmarita-icon.svg")
OUT_MONO = os.path.join(ROOT, "assets", "branding", "magmarita-icon-mono.svg")

TARGET = 768
NCOLOURS = 6
EPSILON = 1.0
MIN_FRACTION = 0.02      # a colour must cover 2% of the canvas
MIN_COMPONENT = 0.002    # drop blobs smaller than 0.2% of the canvas
MIN_LOOP_AREA = 24.0     # drop loops smaller than this many px^2


def prepare(path):
    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    scale = TARGET / float(max(w, h))
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    im = im.resize((nw, nh), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.0))

    alpha = im.getchannel("A")
    flat = Image.new("RGBA", (nw, nh), (255, 255, 255, 255))
    flat.alpha_composite(im)
    q = flat.convert("RGB").quantize(colors=NCOLOURS, method=Image.MEDIANCUT)
    pal = q.getpalette()
    qi, ai = q.load(), alpha.load()

    alpha_mask = [[1 if ai[x, y] > 127 else 0 for x in range(nw)] for y in range(nh)]
    alpha_mask = despeckle(alpha_mask, nw, nh)

    counts = defaultdict(int)
    grey = [[0] * nw for _ in range(nh)]
    for y in range(nh):
        for x in range(nw):
            if alpha_mask[y][x]:
                counts[qi[x, y]] += 1
                grey[y][x] = qi[x, y]

    layers = []
    for idx, cnt in sorted(counts.items(), key=lambda kv: -kv[1]):
        if cnt < nw * nh * MIN_FRACTION:
            continue
        mask = [[1 if grey[y][x] == idx else 0 for x in range(nw)] for y in range(nh)]
        mask = despeckle(mask, nw, nh)
        if not any(any(r) for r in mask):
            continue
        r, g, b = pal[idx * 3], pal[idx * 3 + 1], pal[idx * 3 + 2]
        layers.append(((r, g, b), mask, cnt))
    return nw, nh, alpha_mask, layers


def despeckle(mask, w, h):
    """Remove connected blobs smaller than MIN_COMPONENT."""
    min_area = max(6, int(w * h * MIN_COMPONENT))
    seen = [[False] * w for _ in range(h)]
    for y0 in range(h):
        for x0 in range(w):
            if not mask[y0][x0] or seen[y0][x0]:
                continue
            stack = [(x0, y0)]
            seen[y0][x0] = True
            blob = []
            while stack:
                x, y = stack.pop()
                blob.append((x, y))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h and mask[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            if len(blob) < min_area:
                for x, y in blob:
                    mask[y][x] = 0
    return mask


TABLE = {
    1: [("left", "bottom")], 2: [("bottom", "right")], 3: [("left", "right")],
    4: [("top", "right")], 5: [("top", "right"), ("left", "bottom")],
    6: [("top", "bottom")], 7: [("top", "left")], 8: [("top", "left")],
    9: [("top", "bottom")], 10: [("top", "left"), ("bottom", "right")],
    11: [("bottom", "right")], 12: [("left", "right")], 13: [("left", "bottom")],
    14: [("top", "left")],
}


def trace(mask, w, h):
    def m(x, y):
        return 0 if (x < 0 or y < 0 or x >= w or y >= h) else mask[y][x]

    segs = []
    for y in range(-1, h):
        for x in range(-1, w):
            v = (m(x, y) << 3) | (m(x + 1, y) << 2) | (m(x + 1, y + 1) << 1) | m(x, y + 1)
            if v in (0, 15):
                continue
            pts = {
                "top": (x + 0.5, float(y)), "right": (float(x + 1), y + 0.5),
                "bottom": (x + 0.5, float(y + 1)), "left": (float(x), y + 0.5),
            }
            for a, b in TABLE[v]:
                segs.append((pts[a], pts[b]))

    edges = defaultdict(list)
    for a, b in segs:
        edges[a].append(b)
        edges[b].append(a)

    used = set()
    loops = []
    for start in list(edges.keys()):
        for first in edges[start]:
            if (start, first) in used:
                continue
            loop = [start, first]
            used.add((start, first))
            used.add((first, start))
            cur = first
            while True:
                nxts = [p for p in edges[cur] if (cur, p) not in used]
                if not nxts:
                    break
                nxt = nxts[0]
                used.add((cur, nxt))
                used.add((nxt, cur))
                loop.append(nxt)
                cur = nxt
                if nxt == start:
                    break
            if len(loop) > 4 and abs(loop_area(loop)) >= MIN_LOOP_AREA:
                loops.append(loop)
    return loops


def loop_area(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def simplify(pts, eps):
    if len(pts) < 4:
        return pts
    keep = {0, len(pts) - 1}

    def dp(lo, hi):
        x1, y1 = pts[lo]
        x2, y2 = pts[hi]
        dmax, idx = 0.0, -1
        for i in range(lo + 1, hi):
            x0, y0 = pts[i]
            num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
            den = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5 or 1.0
            d = num / den
            if d > dmax:
                dmax, idx = d, i
        if dmax > eps and idx > 0:
            keep.add(idx)
            dp(lo, idx)
            dp(idx, hi)

    dp(0, len(pts) - 1)
    return [pts[i] for i in sorted(keep)]


def path_data(mask, w, h):
    d = []
    pts_total = 0
    loops = trace(mask, w, h)
    for loop in loops:
        loop = simplify(loop, EPSILON)
        pts_total += len(loop)
        d.append("M " + " ".join("%.2f %.2f" % p for p in loop) + " Z")
    return " ".join(d), len(loops), pts_total


def write_svg(dst, w, h, body):
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="MagmaRita">\n'
                % (w, h, w, h))
        f.write("  <title>MagmaRita</title>\n")
        for line in body:
            f.write(line + "\n")
        f.write("</svg>\n")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IN
    w, h, alpha_mask, layers = prepare(src)
    print("tracing %s -> %dx%d, %d colour layers" % (os.path.basename(src), w, h, len(layers)))

    body = []
    for (r, g, b), mask, cnt in layers:
        d, nloops, npts = path_data(mask, w, h)
        if not d:
            continue
        body.append('  <path d="%s" fill="#%02X%02X%02X" fill-rule="evenodd"/>' % (d, r, g, b))
        print("  colour #%02X%02X%02X: %d loops, %d points" % (r, g, b, nloops, npts))
    write_svg(OUT_COLOUR, w, h, body)
    print("wrote %s (%.1f KB)" % (OUT_COLOUR, os.path.getsize(OUT_COLOUR) / 1024.0))

    d, nloops, npts = path_data(alpha_mask, w, h)
    write_svg(OUT_MONO, w, h, ['  <path d="%s" fill="#2D9EDE" fill-rule="evenodd"/>' % d])
    print("wrote %s (%d loops, %d points, %.1f KB)"
          % (OUT_MONO, nloops, npts, os.path.getsize(OUT_MONO) / 1024.0))


if __name__ == "__main__":
    main()
