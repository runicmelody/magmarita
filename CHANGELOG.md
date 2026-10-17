# Changelog

## 1.5.2 - 2026-10-17
- **Fixed the settings dialog**: the form could grow taller than the screen, so
  the OK/Cancel buttons were unreachable and nothing could be saved. It now lives
  in a scroll area with the buttons pinned at the bottom, the ten preset slots are
  a compact 2-column grid, preset boxes are searchable, and the window is clamped
  to 80% of the screen height.


## 1.5.1 - 2026-10-13
- Credits clarified everywhere: scrubby zoom is **not** this project's work, it
  comes from Scrubby Zoom by 10zindraws and is only adapted here.


## 1.5.0 - 2026-10-13
- Flatpak and Snap Krita installs are detected automatically; env overrides
  MAGMARITA_CONFIG_DIR / MAGMARITA_RESOURCE_DIR for anything unusual.
- New tools/frames_to_gif.py - turns Krita Recorder PNG frames (or any PNG
  sequence) into an optimised GIF.
- docs/GIF.md documents the Recorder workflow.


## 1.4.0 - 2026-10-13
- Added plugin-module tests (tests/test_plugin.py): version guard, path
  agreement between modules, opt-in diagnostics gate, small helpers - run in CI
  with a stubbed Krita, no display needed.
- README now states the testing status honestly: manual testing on Windows +
  Krita 5.3.4; Linux/macOS only dry-run tested, never run in real Krita.


## 1.3.0 - 2026-10-13
- **Version guard + safe mode**: outside the tested Krita range (5.2-5.3) or with
  "Safe mode" enabled, MagmaRita skips canvas-input patching and conflict clearing
  and says so, instead of changing things it cannot verify.
- **Diagnostics… menu action**: one window with Krita version, every shortcut
  (wanted vs. actual), cleared conflicts, canvas-input dry run and a preset check,
  with a copy button.
- **Cross-platform dry-run test** (tests/test_installer.py) + CI matrix on
  Ubuntu / macOS / Windows: redirects Krita's dirs to a temp folder, runs the
  installer logic and asserts the result - no Krita required.


## 1.2.0 - 2026-10-13
- Settings: **Enforce keymap** can be turned off - MagmaRita then only fills in
  keys you have not bound yourself instead of re-applying everything on start.
- Settings: **Diagnostics** log is now opt-in (off by default, nothing written).
- Cross-platform: config and log paths now resolve correctly on Linux
  (~/.config, ~/.local/share/krita) and macOS (Library/Preferences,
  Library/Application Support/krita).
- Docs: added docs/MANUAL-SETUP.md (pure-GUI recipe; promo/itch notes moved out
  of the repo).

## 1.1.0 - 2026-10-13
- New: **on-canvas key hints** - flashes the key/preset name (View.floatingMessage)
  when you switch presets, arm zoom/rotate or start the line assist. Toggle in
  Settings ("Key hints") or magmarita.json. Handy for demos/GIFs.


## 1.0.3 - 2026-10-13
- Discoverability: docs/FAQ.md with the questions people actually search for,
  a keyword-rich landing page (site/) for GitHub Pages, richer GitHub repo
  description and topics.


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