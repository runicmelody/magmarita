#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita installer.

    python install.py              install plugin + write the Magma keymap
    python install.py --no-plugin  only write the keymap
    python install.py --uninstall  remove the plugin and restore backups

Run with Krita CLOSED.
"""

import argparse
import importlib.util
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = "magmarita"
DESKTOP = "magmarita.desktop"
LEGACY = ("magmarita_scrubby_zoom", "magmarita_scrubby_zoom.desktop")


def load_keymap():
    path = os.path.join(HERE, "pykrita", PLUGIN, "keymap.py")
    spec = importlib.util.spec_from_file_location("magmarita_keymap", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def install_plugin(km):
    dst_root = os.path.join(km.resource_dir(), "pykrita")
    if not os.path.isdir(dst_root):
        print("! Krita pykrita folder not found at: %s" % dst_root)
        print("  (is Krita installed / has it been run at least once?)")
        return
    dst = os.path.join(dst_root, PLUGIN)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(HERE, "pykrita", PLUGIN), dst,
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(os.path.join(HERE, "pykrita", DESKTOP), os.path.join(dst_root, DESKTOP))
    print("+ plugin installed -> %s" % dst)
    # remove the pre-1.0.1 split plugin if it is still around
    old = os.path.join(dst_root, LEGACY[0])
    if os.path.isdir(old):
        shutil.rmtree(old)
        print("+ removed old plugin %s" % old)
    oldd = os.path.join(dst_root, LEGACY[1])
    if os.path.exists(oldd):
        os.remove(oldd)


def uninstall(km):
    dst_root = os.path.join(km.resource_dir(), "pykrita")
    for name in (PLUGIN, LEGACY[0]):
        p = os.path.join(dst_root, name)
        if os.path.isdir(p):
            shutil.rmtree(p)
            print("+ removed %s" % p)
    for name in (DESKTOP, LEGACY[1]):
        p = os.path.join(dst_root, name)
        if os.path.exists(p):
            os.remove(p)
            print("+ removed %s" % p)
    restored = km.restore_latest()
    for r in restored:
        print("+ restored %s" % r)
    if not restored:
        print("! no backup found - nothing to restore")
    print("Done. Restart Krita.")


def main():
    ap = argparse.ArgumentParser(description="MagmaRita installer")
    ap.add_argument("--no-plugin", action="store_true", help="only write the keymap")
    ap.add_argument("--uninstall", action="store_true", help="remove plugin, restore config")
    args = ap.parse_args()

    km = load_keymap()
    print("%s %s" % (km.APP_NAME, km.VERSION))
    if args.uninstall:
        uninstall(km)
        return

    print("config dir  : %s" % km.config_dir())
    print("resource dir: %s" % km.resource_dir())
    if not args.no_plugin:
        install_plugin(km)
    made = km.apply()
    print("+ keymap written to:\n    %s\n    %s" % (km.shortcuts_path(), km.kritarc_path()))
    for m in made:
        print("+ backup: %s" % m)
    print("\nDone. Start Krita, then try Z (zoom), R (rotate) and 2-6 (presets).")


if __name__ == "__main__":
    main()
