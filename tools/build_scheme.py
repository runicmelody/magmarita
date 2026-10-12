#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Regenerate shortcuts/MagmaRita.shortcuts from a real Krita installation.

Combines Krita's shipped default scheme, the per-action defaults declared by
the .action files, and MagmaRita's overrides into one importable scheme.
"""

import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load_keymap():
    path = os.path.join(ROOT, "pykrita", "magmarita", "keymap.py")
    spec = importlib.util.spec_from_file_location("magmarita_keymap", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    share = sys.argv[1] if len(sys.argv) > 1 else r"C:\Program Files\Krita (x64)\share\krita"
    if not os.path.isdir(share):
        print("Krita share dir not found: %s" % share)
        print("usage: build_scheme.py <path-to-krita/share/krita>")
        return 1

    km = load_keymap()
    entries = {}

    default = os.path.join(share, "shortcuts", "krita_default.shortcuts")
    if os.path.exists(default):
        for line in open(default, encoding="utf-8", errors="replace").read().splitlines():
            if "=" in line and line.strip() != "[Shortcuts]":
                k, v = line.split("=", 1)
                entries[k.strip()] = v.strip()

    actions = os.path.join(share, "actions")
    if os.path.isdir(actions):
        for fn in os.listdir(actions):
            if not fn.endswith(".action"):
                continue
            txt = open(os.path.join(actions, fn), encoding="utf-8", errors="replace").read()
            for m in re.finditer(r'<Action name="([^"]+)">(.*?)</Action>', txt, re.S):
                name, body = m.group(1), m.group(2)
                sm = re.search(r"<shortcut>(.*?)</shortcut>", body, re.S)
                if sm and sm.group(1).strip() and name not in entries:
                    entries[name] = sm.group(1).strip()

    entries.update(km.SHORTCUTS)
    for i in range(1, 11):
        entries.setdefault("activate_preset_" + ("0" if i == 10 else str(i)), "none")

    out = ["[Shortcuts]"]
    for k in sorted(entries):
        out.append(k + "=" + entries[k])

    dst = os.path.join(ROOT, "shortcuts", "MagmaRita.shortcuts")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("wrote %s (%d entries)" % (dst, len(entries)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
