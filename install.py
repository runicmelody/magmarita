#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita standalone installer.

Usage:
    python install.py [--no-plugin]

Copies the MagmaRita PyKrita plugins into Krita's resource folder and writes
the Magma-style keymap into Krita's config files.  Run with Krita CLOSED.
"""

import argparse
import importlib.util
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))

# (folder under pykrita/, desktop file)
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


def install_plugins(km):
    dst_root = os.path.join(km.resource_dir(), "pykrita")
    if not os.path.isdir(dst_root):
        print("! Krita pykrita folder not found at: %s" % dst_root)
        print("  (is Krita installed / has it been run at least once?)")
        return False
    for folder, desktop in PLUGINS:
        src_pkg = os.path.join(HERE, "pykrita", folder)
        dst_pkg = os.path.join(dst_root, folder)
        if os.path.isdir(dst_pkg):
            shutil.rmtree(dst_pkg)
        shutil.copytree(src_pkg, dst_pkg,
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(os.path.join(HERE, "pykrita", desktop),
                     os.path.join(dst_root, desktop))
        print("+ installed %s -> %s" % (folder, dst_pkg))
    return True


def main():
    ap = argparse.ArgumentParser(description="MagmaRita installer")
    ap.add_argument("--no-plugin", action="store_true",
                    help="only write the keymap, do not install the PyKrita plugins")
    args = ap.parse_args()

    km = load_keymap()
    print("%s %s - Magma-style keybinds for Krita" % (km.APP_NAME, km.VERSION))
    print("config dir  : %s" % km.config_dir())
    print("resource dir: %s" % km.resource_dir())
    print()

    if not args.no_plugin:
        install_plugins(km)

    made = km.apply()
    print("+ keymap written to:")
    print("    %s" % km.shortcuts_path())
    print("    %s" % km.kritarc_path())
    if made:
        print("+ backups:")
        for m in made:
            print("    %s" % m)
    print()
    print("Done. Start Krita, then try Z (hold + drag = scrubby zoom) and 1-6 (presets).")


if __name__ == "__main__":
    main()
