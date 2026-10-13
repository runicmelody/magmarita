#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Turn a folder of PNG frames into an optimised GIF.

Great with Krita's built-in Recorder (Settings > Dockers > Recorder), which writes
one PNG per captured frame straight from the canvas - sharper and cleaner than a
screen recording.

Usage:
    python tools/frames_to_gif.py <frames-dir> [out.gif] [--fps 12] [--width 900]
"""

import argparse
import os
import sys

from PIL import Image

FRAME_TYPES = (".png", ".jpg", ".jpeg", ".webp")


def frames_in(folder):
    names = sorted(n for n in os.listdir(folder) if n.lower().endswith(FRAME_TYPES))
    return [os.path.join(folder, n) for n in names]


def main():
    ap = argparse.ArgumentParser(description="PNG frames -> GIF")
    ap.add_argument("frames", help="folder containing the PNG frames")
    ap.add_argument("out", nargs="?", default=None, help="output .gif path")
    ap.add_argument("--fps", type=float, default=12.0)
    ap.add_argument("--width", type=int, default=900, help="output width in px (0 = keep)")
    ap.add_argument("--loop", type=int, default=0, help="0 = loop forever")
    args = ap.parse_args()

    files = frames_in(args.frames)
    if not files:
        print("no frames found in", args.frames)
        return 1

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.frames.rstrip("\\/"))),
                                   os.path.basename(args.frames.rstrip("\\/")) + ".gif")
    delay = max(20, int(round(1000.0 / args.fps)))

    images = []
    for path in files:
        frame = Image.open(path).convert("RGBA")
        if args.width and frame.width != args.width:
            height = max(1, int(round(frame.height * args.width / float(frame.width))))
            frame = frame.resize((args.width, height), Image.LANCZOS)
        images.append(frame)

    first, rest = images[0], images[1:]
    first.save(out, save_all=True, append_images=rest, duration=delay,
               loop=args.loop, optimize=True, disposal=2)
    print("wrote %s  (%d frames, %.1f fps, %.1f KB)"
          % (out, len(images), args.fps, os.path.getsize(out) / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
