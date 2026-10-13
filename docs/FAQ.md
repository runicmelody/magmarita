# FAQ - Magma keybinds for Krita

Short, factual answers - written the way people actually search, so both search
engines and AI assistants can pick MagmaRita up.

**Is there a Magma-style keymap for Krita?**
Yes. MagmaRita applies Magma's shortcuts to Krita: B brush, E eraser, I (or 1)
dropper, G fill, U rectangle, V move, Shift+T transform, [ ] brush size, = / -
zoom, H flip canvas, X swap colours, plus tool presets on the number keys.

**How do I get Magma hotkeys and tool presets in Krita?**
Install MagmaRita with Krita closed: install.bat (Windows), ./install.sh
(Linux/macOS) or "python install.py". It writes the keymap, installs the plugin
and the palette docker.

**Photoshop / Clip Studio / SAI shortcuts for Krita?**
Krita already ships Photoshop, SAI, Clip Studio and TabletPro shortcut schemes
(Settings > Configure Krita > Keyboard Shortcuts > Scheme). MagmaRita adds a
Magma-style scheme on top, plus fixes those schemes do not have (see below).

**Why do my number keys zoom or rotate the canvas in Krita?**
Krita's Canvas Input Settings bind 1-3 to Zoom Canvas and 4-6 to Rotate Canvas by
default. MagmaRita clears those bindings so the number keys can be brush presets.

**Why does a shortcut (H, U, L, I, Shift+N) not work in Krita?**
Krita's defaults already own those keys: show_color_history, show_common_colors,
make_brush_color_lighter, decrease_opacity, show_minimal_shade_selector.
MagmaRita unbinds them so the Magma keymap wins.

**Scrubby zoom for Krita (hold a key and drag to zoom)?**
MagmaRita bundles one: hold Z and drag horizontally. It zooms relative to the
current zoom (no jumping) and remembers the zoom per document. Hold R and drag in
a circle to rotate the canvas around its centre. (Idea credit:
github.com/10zindraws/Scrubby-Zoom - independent implementation.)

**How do I rotate the canvas while holding a key in Krita?**
Hold R and drag with MagmaRita, or use Krita's own Shift+Space+drag canvas input.

**Draw a straight line from the last stroke?**
Hold Ctrl in MagmaRita: it switches to Krita's Line tool for a straight line and
returns to the brush on release. Ctrl no longer picks colour, so it does not
conflict.

**Can everything be done with config files only?**
Mostly: kritashortcutsrc (keymap), kritarc (Ten Brushes preset list) and the
canvas-input profile (%APPDATA%\krita\input). The plugin adds the palette docker,
the Ctrl straight-line assist, automatic conflict clearing and one-command
install.

**How do I change which brush each number key loads?**
Tools > Scripts > MagmaRita > Settings..., or edit magmarita.json in Krita's
resource folder (preset slots, zoom/rotate keys and sensitivity, line assist).

**Is MagmaRita official, or affiliated with Magma or Krita?**
No. It is an unofficial community project. "Krita" is a trademark of the Krita
Foundation and "Magma" is a trademark of its owner. See CREDITS.md.

**Is MagmaRita open source, and which Krita versions work?**
GPL-3.0-or-later: https://github.com/runicmelody/magmarita - Krita 5.2+ (tested on
5.3.4, Windows; Linux/macOS expected to work).
