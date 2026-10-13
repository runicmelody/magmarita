# MagmaRita

![MagmaRita](assets/branding/magmarita-logo-horizontal.png)

**Magma-style keybinds, palette and scrubby navigation for Krita.**

> ⚠️ **Unofficial.** Not affiliated with, sponsored by or endorsed by Magma or the
> Krita Foundation. See [CREDITS.md](CREDITS.md).

## Install

Krita **closed**:

~~~
install.bat          (Windows)
./install.sh         (Linux / macOS)
python install.py    (any)
~~~

Every run **backs up** "kritashortcutsrc" and "kritarc" first, next to the
originals as "*.bak-magmarita-<timestamp>".

| flag | effect |
|---|---|
| --no-backup | skip the automatic backup |
| --backup-dir DIR | also copy the backups into DIR |
| --no-plugin | write the keymap only, skip the plugin |
| --uninstall | remove the plugin and restore the newest backup |

Then start Krita.

## Keys

| Key | Does |
|---|---|
| 1 | dropper |
| 2 - 6 | preset slots: small eraser, pen, basic, soft eraser, big eraser |
| B E G U M L V Shift+T C | brush, erase, fill, rectangle, select, lasso, move, transform, crop |
| Z / R | scrubby zoom / scrubby rotate (hold + drag) |
| Ctrl | straight line (hold, drag, release) |
| = - Home End Tab H X | zoom in/out, fit, 100%, toggle UI, flip canvas, swap colours |
| [ ] | brush size |
| Ctrl+Z Ctrl+Shift+Z Ctrl+A Ctrl+D | undo, redo, select all, deselect |

Exact Krita action ids: "pykrita/magmarita/keymap.py".

## Palette

Settings > Dockers > MagmaRita: quick tool buttons, ten preset slots with
thumbnails (click to use, **right-click to bind** a preset or key), Pen Pressure
and Lock Alpha toggles, brush size/opacity sliders.

## Customise

Tools > Scripts > MagmaRita > Settings... - or edit "magmarita.json" in Krita's
resource folder: preset slots, zoom/rotate keys and sensitivity, line assist.

## Notes

- Krita 5.2+ (tested on 5.3.4, Windows).
- To own the keys it needs, MagmaRita clears a few Krita defaults
  (show_color_history, show_common_colors, make_brush_color_lighter,
  decrease_opacity, show_minimal_shade_selector) and canvas-input keys
  0-9, = - +, R and Ctrl. Details in keymap.py.
- Troubleshooting: "%LOCALAPPDATA%\magmarita-diag.log".
- FAQ (also written for search engines): [docs/FAQ.md](docs/FAQ.md)
- Credits: [CREDITS.md](CREDITS.md) - Licence: GPL-3.0-or-later ([LICENSE](LICENSE))
