#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Trace a PNG mark into SVGs: a smooth-gradient one, a flat tonal one and a mono one.

    assets/branding/magmarita-icon.svg        silhouette + smooth gradient
    assets/branding/magmarita-icon-tones.svg  flat tonal layers (faithful)
    assets/branding/magmarita-icon-mono.svg   flat single colour silhouette
"""

import os
import sys
from collections import defaultdict

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_IN = os.path.join(ROOT, "assets", "branding", "source", "mark.png")
OUT = os.path.join(ROOT, "assets", "branding")

TARGET = 768
NCOLOURS = 6
EPSILON = 1.0
MIN_FRACTION = 0.02
MIN_COMPONENT = 0.002
MIN_LOOP_AREA = 24.0
GRADIENT_STEPS = 5


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


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

    alpha_mask = despeckle([[1 if ai[x, y] > 127 else 0 for x in range(nw)] for y in range(nh)], nw, nh)

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
        mask = despeckle([[1 if grey[y][x] == idx else 0 for x in range(nw)] for y in range(nh)], nw, nh)
        if not any(any(row) for row in mask):
            continue
        layers.append(((pal[idx * 3], pal[idx * 3 + 1], pal[idx * 3 + 2]), mask, cnt))

    # where are the dark vs light pixels -> gradient direction
    lums = {idx: _lum((pal[idx * 3], pal[idx * 3 + 1], pal[idx * 3 + 2])) for idx in counts}
    order = sorted(counts.items(), key=lambda kv: lums[kv[0]])
    total = sum(counts.values())
    acc, thr = 0, order[-1][0]
    for idx, cnt in order:
        acc += cnt
        if acc >= total * 0.5:
            thr = lums[idx]
            break
    dark = [0.0, 0.0, 0]
    light = [0.0, 0.0, 0]
    for y in range(nh):
        for x in range(nw):
            if not alpha_mask[y][x]:
                continue
            if lums[grey[y][x]] <= thr:
                dark[0] += x
                dark[1] += y
                dark[2] += 1
            else:
                light[0] += x
                light[1] += y
                light[2] += 1
    ax = (dark[0] / dark[2], dark[1] / dark[2]) if dark[2] else (0.0, 0.0)
    bx = (light[0] / light[2], light[1] / light[2]) if light[2] else (float(nw), float(nh))
    return nw, nh, alpha_mask, layers, ax, bx


def despeckle(mask, w, h):
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


def loop_area(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def trace(mask, w, h):
    def m(x, y):
        return 0 if (x < 0 or y < 0 or x >= w or y >= h) else mask[y][x]

    segs = []
    for y in range(-1, h):
        for x in range(-1, w):
            v = (m(x, y) << 3) | (m(x + 1, y) << 2) | (m(x + 1, y + 1) << 1) | m(x, y + 1)
            if v in (0, 15):
                continue
            pts = {"top": (x + 0.5, float(y)), "right": (float(x + 1), y + 0.5),
                   "bottom": (x + 0.5, float(y + 1)), "left": (float(x), y + 0.5)}
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
    loops = trace(mask, w, h)
    for loop in loops:
        loop = simplify(loop, EPSILON)
        d.append("M " + " ".join("%.2f %.2f" % p for p in loop) + " Z")
    return " ".join(d), len(loops)


def _boost(colours, factor):
    """Widen the tonal spread so the fade reads clearly (hue is preserved)."""
    if len(colours) < 2:
        return colours
    mean = [sum(c[k] for c in colours) / float(len(colours)) for k in range(3)]
    out = []
    for c in colours:
        out.append(tuple(min(255, max(0, int(round(mean[k] + (c[k] - mean[k]) * factor))))
                         for k in range(3)))
    return out


def gradient_stops(colours):
    cols = sorted(colours, key=_lum)
    out = []
    segs = max(1, len(cols) - 1)
    for i in range(len(cols) - 1):
        a, b = cols[i], cols[i + 1]
        for s in range(GRADIENT_STEPS):
            t = s / float(GRADIENT_STEPS)
            c = tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))
            out.append((float(i + t) / segs, c))
    out.append((1.0, cols[-1]))
    return cols, out


def write_svg(dst, w, h, defs, body):
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="MagmaRita">\n' % (w, h, w, h))
        f.write("  <title>MagmaRita</title>\n")
        if defs:
            f.write("  <defs>\n" + defs + "\n  </defs>\n")
        for line in body:
            f.write(line + "\n")
        f.write("</svg>\n")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IN
    w, h, alpha_mask, layers, ax, bx = prepare(src)
    print("tracing %s -> %dx%d, %d tonal layers" % (os.path.basename(src), w, h, len(layers)))

    colours = _boost([c for c, _m, _n in layers], 2.6)
    cols, stops = gradient_stops(colours)
    print("gradient: %s -> %s" % ("#%02X%02X%02X" % cols[0], "#%02X%02X%02X" % cols[-1]))
    print("axis: dark %.0f,%.0f -> light %.0f,%.0f" % (ax[0], ax[1], bx[0], bx[1]))

    # fade direction: use the artwork's own dark->light axis when it has one,
    # otherwise fall back to a pleasant diagonal.
    dx, dy = bx[0] - ax[0], bx[1] - ax[1]
    if (dx * dx + dy * dy) ** 0.5 < 0.15 * max(w, h):
        print("no clear spatial axis in the art - fading diagonally")
        x1, y1, x2, y2 = 0.0, 0.0, float(w), float(h)
    else:
        norm = (dx * dx + dy * dy) ** 0.5 or 1.0
        k = max(w, h)
        x1, y1 = ax[0] - dx / norm * k, ax[1] - dy / norm * k
        x2, y2 = bx[0] + dx / norm * k, bx[1] + dy / norm * k

    defs = ['    <linearGradient id="mr" gradientUnits="userSpaceOnUse" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f">' % (x1, y1, x2, y2)]
    for off, c in stops:
        defs.append('      <stop offset="%.3f" stop-color="#%02X%02X%02X"/>' % (off, c[0], c[1], c[2]))
    defs.append("    </linearGradient>")

    d_sil, n_sil = path_data(alpha_mask, w, h)
    write_svg(os.path.join(OUT, "magmarita-icon.svg"), w, h, "\n".join(defs),
              ['  <path d="%s" fill="url(#mr)" fill-rule="evenodd"/>' % d_sil])
    print("wrote magmarita-icon.svg (smooth gradient, %d loops, %.1f KB)"
          % (n_sil, os.path.getsize(os.path.join(OUT, "magmarita-icon.svg")) / 1024.0))

    body = []
    for (c, mask, _cnt) in layers:
        d, n = path_data(mask, w, h)
        if d:
            body.append('  <path d="%s" fill="url(#mr)" fill-rule="evenodd"/>' % d)
    write_svg(os.path.join(OUT, "magmarita-icon-tones.svg"), w, h, "\n".join(defs), body)
    print("wrote magmarita-icon-tones.svg (tonal shapes, shared gradient)")

    write_svg(os.path.join(OUT, "magmarita-icon-mono.svg"), w, h, "",
              ['  <path d="%s" fill="#2D9EDE" fill-rule="evenodd"/>' % d_sil])
    print("wrote magmarita-icon-mono.svg (flat)")


if __name__ == "__main__":
    main()
