#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita uninstaller: restores Krita's previous config and removes plugins."""

import importlib.util
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))

PLUGINS = [
    ("magmarita", "magmarita.desktop"),
    ("magmarita_scrubby_zoom", "magmarita_scrubby_zoom.desktop"),
]


def load_keymap():
    path = os.path.join(HERE, "pykrita", "magmarita", "keymap.py")
    spec = importlib.util.spec_from_file_location("magmarita_keymap", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    km = load_keymap()
    dst_root = os.path.join(km.resource_dir(), "pykrita")
    for folder, desktop in PLUGINS:
        pkg = os.path.join(dst_root, folder)
        if os.path.isdir(pkg):
            shutil.rmtree(pkg)
            print("+ removed plugin %s" % pkg)
        dt = os.path.join(dst_root, desktop)
        if os.path.exists(dt):
            os.remove(dt)
            print("+ removed %s" % dt)
    restored = km.restore_latest()
    for r in restored:
        print("+ restored %s" % r)
    if not restored:
        print("! no backup found - nothing to restore")
    print("Done. Restart Krita.")


if __name__ == "__main__":
    main()
