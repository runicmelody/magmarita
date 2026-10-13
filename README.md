# MagmaRita

![MagmaRita](assets/branding/magmarita-logo-horizontal.png)

**Moving from Magma to Krita?** MagmaRita puts Magma's **tool presets on the
number keys** (1 dropper, 2 small eraser, 3 pen, ...) so you no longer set every
tool up by hand - plus the Magma palette docker, scrubby zoom/rotate and the
shortcuts you already know. Also described as *Magma keybinds for Krita* or
*Magma shortcuts for Krita*.

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

Then start Krita. Flatpak and Snap installs are found automatically; override
with MAGMARITA_CONFIG_DIR / MAGMARITA_RESOURCE_DIR if needed.

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
resource folder: preset slots, zoom/rotate keys and sensitivity, line assist,
on-canvas key hints.

## Notes

- Krita 5.2+.
- **Testing status:** developed and manually tested on **Windows, Krita 5.3.4**.
  Linux and macOS are covered by **CI dry-run tests only** (installer logic, path
  resolution, canvas-input patching) - they have **not been run inside real Krita**
  yet. Treat them as untested.
- To own the keys it needs, MagmaRita clears a few Krita defaults
  (show_color_history, show_common_colors, make_brush_color_lighter,
  decrease_opacity, show_minimal_shade_selector) and canvas-input keys
  0-9, = - +, R and Ctrl. Details in keymap.py.
- Troubleshooting: **Tools > Scripts > MagmaRita > Diagnostics...** (Krita
  version, resolved keys, cleared conflicts, preset check) - the fastest way to
  report a bug. Set "Diagnostics" in Settings to also write a log in Krita's
  resource folder.
- **Scrubby zoom is not our work** - it comes from Scrubby Zoom by 10zindraws
  and is only adapted here. See [CREDITS.md](CREDITS.md).
- FAQ (also written for search engines): [docs/FAQ.md](docs/FAQ.md)
- Recording a demo GIF: [docs/GIF.md](docs/GIF.md)
- Prefer to set it up by hand? [docs/MANUAL-SETUP.md](docs/MANUAL-SETUP.md)
- Less forceful: turn off "Enforce keymap" in Settings and MagmaRita only fills
  gaps, leaving your own bindings alone.
- Credits: [CREDITS.md](CREDITS.md) - Licence: GPL-3.0-or-later ([LICENSE](LICENSE))
