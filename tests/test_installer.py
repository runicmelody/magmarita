#!/usr/bin/env python3
"""Cross-platform installer dry-run test - no Krita required.

Redirects Krita's config/resource dirs to a temp folder (via env vars), runs the
same code the installer uses, and asserts the result. Catches path regressions
(Linux/macOS/Windows) and canvas-input format drift in CI.
"""

import importlib.util
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "kritadefault.profile")
failures = []


def check(name, condition, detail=""):
    print(("  ok   " if condition else "  FAIL ") + name + (("  [" + detail + "]") if detail else ""))
    if not condition:
        failures.append(name)


def load_keymap():
    path = os.path.join(ROOT, "pykrita", "magmarita", "keymap.py")
    spec = importlib.util.spec_from_file_location("magmarita_keymap", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    tmp = tempfile.mkdtemp(prefix="magmarita-dryrun-")
    os.environ["LOCALAPPDATA"] = tmp
    os.environ["APPDATA"] = os.path.join(tmp, "roaming")
    os.environ["USERPROFILE"] = tmp
    os.environ["HOME"] = tmp
    os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp, ".config")

    km = load_keymap()
    cfg_dir = km.config_dir()
    res_dir = km.resource_dir()
    print("config dir  :", cfg_dir)
    print("resource dir:", res_dir)
    check("paths are redirected into the temp dir", tmp in cfg_dir and tmp in res_dir)

    os.makedirs(os.path.join(res_dir, "input"), exist_ok=True)
    os.makedirs(cfg_dir, exist_ok=True)
    shutil.copy(FIXTURE, os.path.join(res_dir, "input", "kritadefault.profile"))
    with open(os.path.join(cfg_dir, "kritarc"), "w", encoding="utf-8") as fh:
        fh.write("[python]\n\ncurrentInputProfile=Krita Default\n")

    made = km.apply()
    check("backups were created", len(made) >= 1, str(len(made)))

    shortcuts = open(km.shortcuts_path(), encoding="utf-8").read()
    for entry in ("KritaShape/KisToolBrush=B", "scrubby_zoom_activate=Z",
                  "mirror_canvas=H; M", "show_color_history=none"):
        check("shortcuts contains " + entry, entry in shortcuts)

    check("magmarita.json written", os.path.exists(km.config_path()))

    profile = open(os.path.join(res_dir, "input", "kritadefault.profile"), encoding="utf-8").read()
    for stolen in ("[31]", "[32]", "[33]", "[34]", "[35]", "[36]", "[52]", "[3d]", "1000021"):
        check("canvas input no longer binds " + stolen, stolen not in profile)
    check("unrelated bindings kept (space pan)", "[20]" in profile)
    check("dry run reports nothing left to clear", km.patch_canvas_input(dry_run=True) == 0)

    # env overrides work everywhere
    os.environ["MAGMARITA_CONFIG_DIR"] = os.path.join(tmp, "override-config")
    os.environ["MAGMARITA_RESOURCE_DIR"] = os.path.join(tmp, "override-krita")
    check("env override wins for config dir",
          km.config_dir() == os.path.join(tmp, "override-config"))
    check("env override wins for resource dir",
          km.resource_dir() == os.path.join(tmp, "override-krita"))
    del os.environ["MAGMARITA_CONFIG_DIR"]
    del os.environ["MAGMARITA_RESOURCE_DIR"]

    # Flatpak / Snap detection is POSIX only
    if os.name != "nt" and sys.platform != "darwin":
        flat_cfg = os.path.join(tmp, ".var", "app", "org.kde.krita", "config")
        flat_res = os.path.join(tmp, ".var", "app", "org.kde.krita", "data", "krita")
        os.makedirs(flat_cfg, exist_ok=True)
        os.makedirs(flat_res, exist_ok=True)
        check("Flatpak config dir detected", km.config_dir() == flat_cfg, km.config_dir())
        check("Flatpak resource dir detected", km.resource_dir() == flat_res, km.resource_dir())
        shutil.rmtree(os.path.join(tmp, ".var"), ignore_errors=True)
        check("falls back to XDG config dir", km.config_dir().endswith(os.path.join(".config", "")[:-1]) or "config" in km.config_dir())
        snap_cfg = os.path.join(tmp, "snap", "krita", "current", ".config")
        snap_res = os.path.join(tmp, "snap", "krita", "current", ".local", "share", "krita")
        os.makedirs(snap_cfg, exist_ok=True)
        os.makedirs(snap_res, exist_ok=True)
        check("Snap config dir detected", km.config_dir() == snap_cfg, km.config_dir())
        check("Snap resource dir detected", km.resource_dir() == snap_res, km.resource_dir())

    if failures:
        print("\n%d check(s) failed - temp dir kept at %s" % (len(failures), tmp))
        for name in failures:
            print(" -", name)
        return 1
    print("\nall checks passed")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
