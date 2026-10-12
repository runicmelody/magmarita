# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita keymap data + Krita config helpers.

Single source of truth for the Magma -> Krita key mapping.  Free of any
Krita / Qt imports so it can be reused by the PyKrita plugin and by the
standalone installer.
"""

import os
import shutil
import sys
import time

APP_NAME = "MagmaRita"
VERSION = "0.2.1"
HOMEPAGE = "https://github.com/runicmelody/magmarita"

# ---------------------------------------------------------------------------
# Keyboard overrides: key = Krita action id, value = shortcut(s).
# Several shortcuts for one action are separated by "; ".
# ---------------------------------------------------------------------------
SHORTCUTS = {
    # --- Tools: Magma letters -> Krita tools ---
    "KritaSelected/KisToolColorSampler": "I; 1",   # dropper (eyedropper)
    "KritaShape/KisToolBrush": "B",                # brush
    "erase_action": "E",                           # eraser (toggle erase mode)
    "KritaFill/KisToolFill": "G",                  # paint bucket
    "KritaFill/KisToolGradient": "Shift+G",        # gradient
    "KritaShape/KisToolRectangle": "U",            # rectangle
    "KritaShape/KisToolEllipse": "Shift+U",        # ellipse
    "KisToolSelectRectangular": "M",               # selection
    "KisToolSelectPolygonal": "L",                 # lasso
    "KisToolSelectContiguous": "W",                # magic wand
    "KritaTransform/KisToolMove": "V",             # move
    "KisToolTransform": "Shift+T",                 # transform
    "KisToolCrop": "C",                            # crop
    # --- Scrubby zoom (bundled plugin, keeps its classic action id) ---
    "scrubby_zoom_activate": "Z",                  # hold + drag horizontally
    # --- View ---
    "view_zoom_in": "=; Ctrl+=",
    "view_zoom_out": "-; Ctrl+-",
    "zoom_to_fit": "Home",
    "zoom_to_100pct": "End",
    "view_show_canvas_only": "Tab",                # toggle UI
    "mirror_canvas": "H; M",                       # flip horizontally
    "toggle_fg_bg": "X",                           # switch colors
    # --- Editing / selection ---
    "select_all": "Ctrl+A",
    "deselect": "Ctrl+D",
    "invert_selection": "Ctrl+Shift+I",
    "reselect": "Ctrl+Shift+D",
    "edit_undo": "Ctrl+Z",
    "edit_redo": "Ctrl+Shift+Z",
    "clear": "Del",
    # --- Brush ---
    "increase_brush_size": "]",
    "decrease_brush_size": "[",
    "show_brush_presets": "F6",
    # --- Layers ---
    "add_new_paint_layer": "Shift+N; Ins",
    "merge_layer": "Ctrl+E",
    "duplicatelayer": "Ctrl+J",
    "flatten_image": "Ctrl+Shift+E",
    # --- Misc ---
    "filter_apply_again": "Ctrl+F; Ctrl+Alt+F",
    "fullscreen": "Ctrl+Shift+F",
}

# Number key -> brush preset.  Activated by the MagmaRita plugin itself, so it
# does not depend on Krita's Ten Brushes plugin (which needs extra config).
PRESET_SLOTS = [
    ("2", "a) Eraser Small"),
    ("3", "d) Ink-1 Precision"),
    ("4", "b) Basic-5 Size"),
    ("5", "a) Eraser Soft"),
    ("6", "Eraser circle"),
]

# Shortcut entries MagmaRita prunes from kritashortcutsrc: keys it used to
# bind in an older version, or bindings it deliberately drops.
REMOVE_SHORTCUTS = ["ZoomTool"]

# Ten Brushes slot order: slot 1..10 -> keys 1..0.
# Slot 1 stays a spare because key 1 is bound to the dropper tool above.
PRESETS = [
    "Basic tip default",
    "a) Eraser Small",
    "d) Ink-1 Precision",
    "b) Basic-5 Size",
    "a) Eraser Soft",
    "Eraser circle",
    "Ink ballpen",
    "Basic circle",
    "Fill circle",
    "u) Pixel Art Fill",
]

TENBRUSHES_SETTINGS = {
    "tenbrushes": ",".join(PRESETS),
    "tenbrushesAutoBrushOnPress": "True",
    "tenbrushesActivatePrev2ndPress": "True",
    "tenbrushesShowMessage": "True",
}

# PyKrita plugins MagmaRita switches on.  The stock "scrubby_zoom" plugin is
# superseded by the MagmaRita copy, so it is disabled to avoid a duplicate
# action / shortcut conflict.
PYTHON_PLUGINS = {
    "enable_tenbrushes": "true",
    "enable_magmarita": "true",
    "enable_magmarita_scrubby_zoom": "true",
    "enable_scrubby_zoom": "false",
}


def config_dir():
    """Directory that holds kritarc / kritashortcutsrc."""
    if os.name == "nt":
        return os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Preferences")
    return os.path.join(os.path.expanduser("~"), ".config")


def resource_dir():
    """Directory that holds Krita resources (and pykrita/)."""
    if os.name == "nt":
        return os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "krita")
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "krita")
    return os.path.join(os.path.expanduser("~"), ".local", "share", "krita")


def shortcuts_path():
    return os.path.join(config_dir(), "kritashortcutsrc")


def kritarc_path():
    return os.path.join(config_dir(), "kritarc")


def _read(path):
    with open(path, "r", encoding="utf-8", errors="surrogateescape") as f:
        return f.read()


def _write(path, text):
    with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="\n") as f:
        f.write(text)


def _key(line):
    return line.split("=", 1)[0].strip() if "=" in line else ""


def backup(paths=None, tag=None):
    """Back up Krita config files. Returns the list of created backups."""
    tag = tag or time.strftime("%Y%m%d_%H%M%S")
    made = []
    for p in (paths or [shortcuts_path(), kritarc_path()]):
        if os.path.exists(p):
            dst = p + ".bak-magmarita-" + tag
            shutil.copy2(p, dst)
            made.append(dst)
    return made


def apply(do_backup=True):
    """Write the Magma keymap into Krita's config. Returns backup paths."""
    made = backup() if do_backup else []

    # --- kritashortcutsrc (override-only file) ---
    p = shortcuts_path()
    lines = _read(p).splitlines() if os.path.exists(p) else []
    if not any(l.strip() == "[Shortcuts]" for l in lines):
        lines.insert(0, "[Shortcuts]")
    out = [l for l in lines
           if _key(l) not in SHORTCUTS and _key(l) not in REMOVE_SHORTCUTS]
    for k, v in SHORTCUTS.items():
        out.append(k + "=" + v)
    _write(p, "\n".join(out) + "\n")

    # --- kritarc (Ten Brushes plugin + preset slots) ---
    p = kritarc_path()
    lines = _read(p).splitlines() if os.path.exists(p) else []
    lines = [l for l in lines if not l.startswith("tenbrushes")]
    ins = [k + "=" + v for k, v in TENBRUSHES_SETTINGS.items()]
    if lines:
        lines = lines[:1] + ins + lines[1:]
    else:
        lines = ["[General]"] + ins
    enables = [k + "=" + v for k, v in PYTHON_PLUGINS.items()]
    try:
        i = next(n for n, l in enumerate(lines) if l.strip() == "[python]")
        j = i + 1
        while j < len(lines) and not lines[j].startswith("["):
            j += 1
        keys = [e.split("=")[0] + "=" for e in enables]
        sec = [l for l in lines[i + 1:j] if not any(l.startswith(k) for k in keys)]
        sec.extend(enables)
        lines = lines[:i + 1] + sec + lines[j:]
    except StopIteration:
        lines += ["[python]"] + enables
    _write(p, "\n".join(lines) + "\n")

    return made


def restore_latest():
    """Restore the most recent MagmaRita backup of each config file."""
    restored = []
    for p in (shortcuts_path(), kritarc_path()):
        folder = os.path.dirname(p)
        base = os.path.basename(p) + ".bak-magmarita-"
        cands = sorted(
            [os.path.join(folder, f) for f in os.listdir(folder) if f.startswith(base)]
        ) if os.path.isdir(folder) else []
        if cands:
            shutil.copy2(cands[-1], p)
            restored.append(p)
    return restored
