# Changelog

## 0.2.0 - 2026-10-12
- Bundled a fixed **Scrubby Zoom** plugin (hold Z, drag horizontally).
  - Anchors on Krita's real on-screen zoom percentage instead of guessing,
    so it no longer jumps far out/in on the first drag.
  - Learns the zoomLevel() <-> percentage factor per DPI and remembers the
    last zoom per document ("remembers its spot").
  - Replaces the stock scrubby_zoom plugin (which is disabled to avoid a
    duplicate action).
- Dropped the plain "Z = Krita zoom tool" binding; Z is now scrubby zoom.
- Installer/uninstaller now handle both bundled plugins.

## 0.1.0 - 2026-10-12
- First release.
- Magma-style keymap (tools, view, selection, layers).
- Tool presets on keys 2-6 via Krita's Ten Brushes plugin.
- PyKrita plugin with Apply / Restore actions.
- Installer for Windows / Linux / macOS.
- Importable Krita shortcut scheme.
