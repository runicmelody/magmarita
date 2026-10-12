# Changelog

## 0.3.0 - 2026-10-13
- Fully configurable: brush presets on any keys via magmarita.json, or the new
  in-Krita **Tools > Scripts > MagmaRita > Settings...** dialog.
- MagmaRita now owns the number-key preset slots itself (Ten Brushes no longer
  required); stale activate_preset_* bindings are pruned so keys are not bound
  twice.
- Keymap is applied at runtime and re-asserted after Krita loads its scheme.
- Diagnostics: startup log at <LOCALAPPDATA>/magmarita-diag.log lists every
  bound shortcut, plus scrubby-zoom activity (anchor, final zoom, ui %).
- Scrubby zoom sensitivity is configurable (zoom_sensitivity).

## 0.2.1 - 2026-10-13
- Apply the Magma keymap at runtime instead of relying on kritashortcutsrc.

## 0.2.0 - 2026-10-12
- Bundled a fixed **Scrubby Zoom** plugin (hold Z, drag horizontally).
- Dropped the plain "Z = Krita zoom tool" binding; Z is now scrubby zoom.

## 0.1.0 - 2026-10-12
- First release: Magma-style keymap, presets on 2-6, installer, scheme.
