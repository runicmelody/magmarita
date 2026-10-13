# Changelog

## 1.0.2 - 2026-10-13
- Scrubby zoom/rotate rewritten as an independent clean-room implementation;
  the interaction idea is credited to 10zindraws/Scrubby-Zoom.
- Added CREDITS.md and a prominent "unofficial" notice.
- README trimmed to the essentials.
- Installer: --no-backup and --backup-dir options.
- Added GitHub Actions CI (byte-compile, keymap load check, zip artifact;
  attaches the zip to typed tags).


## 1.0.1 - 2026-10-13
- Slimmed down: one plugin instead of two (scrubby zoom/rotate now lives in
  pykrita/magmarita/scrubby.py), the installer absorbed the uninstaller
  (install.py --uninstall), the generated shortcut scheme was dropped (the
  plugin applies the keymap at runtime) and docs/KEYMAP.md + CONTRIBUTING.md
  were folded into the README. Old split plugin is removed automatically on
  install.


## 1.0.0 - 2026-10-13
- First stable release.
- Branding: hand-drawn logo, transparent banners in light + dark variants,
  red wordmark with a dark-red tagline.
- Everything from 0.x: palette docker, scrubby zoom (Z), drag-rotate around the
  canvas centre (R), Ctrl line assist, Magma keymap with digit preset slots,
  canvas-input conflict fixes, per-plugin manual.


## 0.9.4 - 2026-10-13
- Line assist uses the normal **Line** tool again: holding Ctrl keeps the Line
  tool active and the line is committed on release; releasing Ctrl returns to
  the brush. (Settings still offers Polyline.)
- Ctrl is still cleared from Krita's canvas input, so it no longer picks colour.

## 0.9.3 - 2026-10-13
- Cleared Ctrl canvas-input bindings; line assist used Polyline.

## 0.9.2 - 2026-10-13
- Line assist switches tool on Ctrl key-down (timing fix).

## 0.9.1 - 2026-10-13
- Cleared the Ctrl+click colour pick.

## 0.9.0 - 2026-10-13
- Rotate around the canvas centre; Ctrl line assist.

## 0.8.0 - 2026-10-13
- Hold R + drag to rotate the canvas.

## 0.7.1 - 2026-10-13
- Fixed H/U/L/I/Shift+N (unbinds Krita defaults that claimed them).

## 0.6.1 - 2026-10-13
- H = flip/mirror; zoom on Z.

## 0.5.0 - 2026-10-13
- MagmaRita palette docker.

## 0.4.0 - 2026-10-13
- Fixed number keys zooming/rotating (canvas-input bindings).

## 0.3.0 - 2026-10-13
- Configurable preset slots, runtime keymap, digit fallback, manual.

## 0.2.0 - 2026-10-12
- Bundled a fixed Scrubby Zoom plugin.

## 0.1.0 - 2026-10-12
- First release.
