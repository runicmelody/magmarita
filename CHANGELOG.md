# Changelog

## 0.4.0 - 2026-10-13
- **Fixed the number keys zooming/rotating the canvas.** Krita's Canvas Input
  Settings (separate from keyboard shortcuts) bind 1-3 to Zoom Canvas and 4-6
  to Rotate Canvas by default. MagmaRita now clears those key bindings from the
  active canvas-input profile, so the number keys are purely MagmaRita's.
- Also clears the default = / - / + canvas-input zoom bindings so zoom steps
  once, not twice.
- 0 = dropper on key 1, big eraser preset fixed (a) Eraser Circle).
- View poller + event logging for diagnosing unexpected canvas changes.

## 0.3.0 - 2026-10-13
- Configurable preset slots (magmarita.json + Settings dialog).
- Runtime keymap application, digit fallback filter, plugin manual.

## 0.2.0 - 2026-10-12
- Bundled a fixed Scrubby Zoom plugin; Z = scrubby zoom.

## 0.1.0 - 2026-10-12
- First release.
