#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build a distributable zip for itch.io / GitHub releases."""

import importlib.util
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")

INCLUDE_DIRS = ["pykrita", "shortcuts"]
INCLUDE_FILES = ["install.py", "install.bat", "install.sh", "uninstall.py",
                 "README.md", "LICENSE", "CHANGELOG.md"]
INCLUDE_TREES = ["docs"]
SKIP_BRANDING = ["github-social-1280x640.png"]


def version():
    path = os.path.join(ROOT, "pykrita", "magmarita", "keymap.py")
    spec = importlib.util.spec_from_file_location("km", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.VERSION


def add_tree(zf, base, rel):
    for folder, _dirs, files in os.walk(os.path.join(base, rel)):
        for name in files:
            if name.endswith(".pyc") or "__pycache__" in folder:
                continue
            full = os.path.join(folder, name)
            zf.write(full, os.path.relpath(full, base))


def main():
    ver = version()
    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, "magmarita-%s.zip" % ver)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in INCLUDE_DIRS:
            add_tree(zf, ROOT, d)
        for f in INCLUDE_FILES:
            zf.write(os.path.join(ROOT, f), f)
        for t in INCLUDE_TREES:
            add_tree(zf, ROOT, t)
        brand = os.path.join(ROOT, "assets", "branding")
        for name in os.listdir(brand):
            if name in SKIP_BRANDING or not name.endswith(".png"):
                continue
            zf.write(os.path.join(brand, name), "assets/branding/" + name)
    print("wrote %s (%.1f KB)" % (out, os.path.getsize(out) / 1024.0))


if __name__ == "__main__":
    main()
