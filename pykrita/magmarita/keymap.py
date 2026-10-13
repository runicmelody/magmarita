# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita keymap data + Krita config helpers.

Single source of truth for the Magma -> Krita key mapping.  Free of any
Krita / Qt imports so it can be reused by the PyKrita plugin and by the
standalone installer.
"""

import json
import os
import re
import shutil
import sys
import time

APP_NAME = "MagmaRita"
# Krita versions this mapping has actually been tested against (major.minor).
TESTED_KRITA = ("5.2", "5.3")
VERSION = "1.5.0"
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
    "scrubby_zoom_activate": "Z",                  # hold + drag to zoom
    "scrubby_rotate_activate": "R",                # hold + drag to rotate
    # --- View ---
    "view_zoom_in": "=; Ctrl+=",
    "view_zoom_out": "-; Ctrl+-",
    "zoom_to_fit": "Home",
    "zoom_to_100pct": "End",
    "view_show_canvas_only": "Tab",                # toggle UI
    "mirror_canvas": "H; M",                       # flip / mirror canvas
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
    "add_new_paint_layer": "Shift+N",
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
    ("6", "a) Eraser Circle"),
]

# Quick tool buttons shown in the MagmaRita palette (label, Krita action id).
TOOL_BUTTONS = [
    ("Dropper", "KritaSelected/KisToolColorSampler"),
    ("Brush", "KritaShape/KisToolBrush"),
    ("Erase", "erase_action"),
    ("Fill", "KritaFill/KisToolFill"),
    ("Rect", "KritaShape/KisToolRectangle"),
    ("Select", "KisToolSelectRectangular"),
    ("Lasso", "KisToolSelectPolygonal"),
    ("Move", "KritaTransform/KisToolMove"),
    ("Transform", "KisToolTransform"),
    ("Crop", "KisToolCrop"),
]

# Checkable toggle buttons in the palette: (label, Krita action id, tooltip).
TOGGLE_BUTTONS = [
    ("Pen Pressure", "disable_pressure",
     "Use Pen Pressure: let pen pressure affect size and opacity"),
    ("Lock Alpha", "preserve_alpha",
     "Preserve Alpha: lock the layer's transparency while painting"),
]

# Number key -> Krita tool action (for keys that are tools, not presets).
TOOL_KEYS = {
    "1": "KritaSelected/KisToolColorSampler",
}

# Krita core actions whose DEFAULT shortcut would otherwise steal a key
# MagmaRita needs (H, U, L, I, Shift+N, Ctrl+Shift+I).  MagmaRita unbinds them
# so its own keys (and the Magma keymap) win.
CONFLICT_CLEAR = [
    "show_color_history",            # H
    "show_common_colors",            # U
    "make_brush_color_lighter",      # L
    "decrease_opacity",              # I
    "show_minimal_shade_selector",   # Shift+N
    "invert",                        # Ctrl+Shift+I
]

# Shortcut entries MagmaRita prunes from kritashortcutsrc: keys it used to
# bind in an older version, or bindings it deliberately drops.
REMOVE_SHORTCUTS = [
    "ZoomTool",
    # v0.2 and earlier used Krita's Ten Brushes; the MagmaRita plugin owns the
    # number keys itself now, so these are pruned to avoid double bindings.
    "activate_preset_1", "activate_preset_2", "activate_preset_3",
    "activate_preset_4", "activate_preset_5", "activate_preset_6",
    "activate_preset_7", "activate_preset_8", "activate_preset_9",
    "activate_preset_0",
]

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
    "enable_scrubby_zoom": "false",
}


DEFAULT_ZOOM_SENSITIVITY = 150.0
DEFAULT_ROTATE_SENSITIVITY = 0.5


def _default_config():
    slots = []
    for i in range(10):
        key, preset = PRESET_SLOTS[i] if i < len(PRESET_SLOTS) else ("", "")
        slots.append({"key": key, "preset": preset})
    return {"version": 1, "slots": slots, "zoom_key": "Z",
            "rotate_key": "R",
            "rotate_mode": "center",
            "line_assist": True,
            "key_hints": True,
            "enforce_keymap": True,
            "diagnostics": False,
            "safe_mode": False,
            "line_tool": "KritaShape/KisToolLine",
            "line_restore_tool": "KritaShape/KisToolBrush",
            "zoom_sensitivity": DEFAULT_ZOOM_SENSITIVITY,
            "rotate_sensitivity": DEFAULT_ROTATE_SENSITIVITY}


def config_path():
    return os.path.join(resource_dir(), "magmarita.json")


def save_config(cfg):
    try:
        with open(config_path(), "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        return True
    except Exception:
        return False


def load_config():
    """Load magmarita.json (creating it with defaults on first run)."""
    default = _default_config()
    cfg = None
    try:
        if os.path.exists(config_path()):
            with open(config_path(), "r", encoding="utf-8") as f:
                cfg = json.load(f)
    except Exception:
        cfg = None
    if not isinstance(cfg, dict):
        save_config(default)
        return default
    cfg.setdefault("version", 1)
    cfg.setdefault("slots", default["slots"])
    cfg.setdefault("zoom_key", "Z")
    cfg.setdefault("rotate_key", "R")
    cfg.setdefault("rotate_mode", "center")
    cfg.setdefault("line_assist", True)
    cfg.setdefault("key_hints", True)
    cfg.setdefault("enforce_keymap", True)
    cfg.setdefault("safe_mode", False)
    cfg.setdefault("diagnostics", False)
    cfg.setdefault("line_tool", "KritaShape/KisToolLine")
    cfg.setdefault("line_restore_tool", "KritaShape/KisToolBrush")
    cfg.setdefault("zoom_sensitivity", DEFAULT_ZOOM_SENSITIVITY)
    cfg.setdefault("rotate_sensitivity", DEFAULT_ROTATE_SENSITIVITY)
    return cfg


# Keys that Krita's *Canvas Input Settings* grab by default and that MagmaRita
# takes over: number keys (presets) and = / - / + (zoom).  These live in a
# canvas-input profile, NOT in the keyboard shortcuts, so they have to be
# cleared separately or they fight MagmaRita.
# Whole canvas-input sections MagmaRita clears.  "Change Primary Setting" is
# Krita's Ctrl+click colour picker, which collides with the Ctrl straight-line
# assist.
CANVAS_INPUT_SECTIONS_TO_CLEAR = []

CANVAS_INPUT_KEYS_TO_CLEAR = [
    "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",  # 0-9
    "2b", "2d", "3d",                                            # + - =
    "52",                                                        # R (rotate)
    "1000021",                                                   # Ctrl (line assist)
]


def _active_input_profile_name():
    try:
        for line in _read(kritarc_path()).splitlines():
            if line.startswith("currentInputProfile="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return "Krita Default"


def _profile_filename(name):
    return re.sub(r"[^a-z0-9]", "", (name or "Krita Default").lower()) + ".profile"


def patch_canvas_input(dry_run=False):
    """Drop the number/zoom key bindings from Krita's active canvas-input
    profile so they stop zooming/rotating the canvas.  Returns count removed."""
    path = os.path.join(resource_dir(), "input", _profile_filename(_active_input_profile_name()))
    if not os.path.exists(path):
        return 0
    out = []
    idx = -1
    removed = 0
    section = ""
    for line in _read(path).splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            idx = -1
            section = s[1:-1]
            out.append(line)
            continue
        if not re.match(r"^\s*\d+\s*=", line):
            out.append(line)
            continue
        if section in CANVAS_INPUT_SECTIONS_TO_CLEAR:
            removed += 1
            continue
        codes = re.search(r"\[([0-9a-fA-F,]+)\]", line)
        if codes:
            parts = [c.strip().lower() for c in codes.group(1).split(",")]
            if any(c in CANVAS_INPUT_KEYS_TO_CLEAR for c in parts):
                removed += 1
                continue
        idx += 1
        out.append(re.sub(r"^\s*\d+", str(idx), line))
    if removed and not dry_run:
        _write(path, "\n".join(out) + "\n")
    return removed


def version_supported(version):
    """True when "version" (e.g. 5.3.4) is inside the tested range."""
    try:
        parts = str(version).split(".")
        return ".".join(parts[:2]) in TESTED_KRITA
    except Exception:
        return False


def log_path():
    """Diagnostics log lives next to Krita's resources, on every platform."""
    return os.path.join(resource_dir(), "magmarita-diag.log")


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
    managed = dict(SHORTCUTS)
    for name in CONFLICT_CLEAR:
        managed[name] = "none"
    try:
        for i, slot in enumerate(load_config().get("slots", [])):
            key = (slot or {}).get("key", "") or ""
            if (slot or {}).get("preset") and key:
                managed["magmarita_preset_%d" % (i + 1)] = key
    except Exception:
        pass

    out = [l for l in lines
           if _key(l) not in managed and _key(l) not in REMOVE_SHORTCUTS
           and not _key(l).startswith("magmarita_preset_")]
    for k, v in managed.items():
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

    patch_canvas_input()

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
