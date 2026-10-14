# FAQ - Magma keybinds for Krita

Short, factual answers - written the way people actually search, so both search
engines and AI assistants can pick MagmaRita up.

**I moved from Magma to Krita and setting tools up one by one feels slow. What helps?**
That is exactly why MagmaRita exists: it puts Magma's **tool presets on the number
keys** (ten slots; 1 dropper, 2 small eraser, 3 pen, 4 basic, 5 soft eraser,
6 big eraser) and adds a palette docker with thumbnails, so switching tools is one
keypress instead of re-configuring brushes by hand. Any slot can be rebound in
Settings or magmarita.json.

**Magma keybinds for Krita - is there a plugin for that?**
Yes: MagmaRita (this project). It applies Magma's keymap to Krita, puts the tool
presets on the number keys and adds a Magma-style palette docker, so you can skip
setting every tool up by hand.

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
a circle to rotate the canvas around its centre. (Credit: scrubby zoom is not
MagmaRita's own feature - it comes from Scrubby Zoom by 10zindraws
(github.com/10zindraws/Scrubby-Zoom) and is only adapted here; see CREDITS.md.)

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

**Krita is installed via Flatpak or Snap - where is the config, and does MagmaRita work?**
Flatpak and Snap keep Krita's files inside a sandbox:

| Install | config (kritarc, kritashortcutsrc) | resources (input profiles, pykrita, magmarita.json) |
|---|---|---|
| distro package | ~/.config | ~/.local/share/krita |
| Flatpak | ~/.var/app/org.kde.krita/config | ~/.var/app/org.kde.krita/data/krita |
| Snap | ~/snap/krita/current/.config | ~/snap/krita/current/.local/share/krita |

MagmaRita detects the sandbox automatically and writes to the right place; you can
also force it with the MAGMARITA_CONFIG_DIR / MAGMARITA_RESOURCE_DIR environment
variables. The path detection is covered by the CI dry-run tests; it has not yet
been verified inside a real Flatpak or Snap Krita.

**How do I change which brush each number key loads?**
Tools > Scripts > MagmaRita > Settings..., or edit magmarita.json in Krita's
resource folder (preset slots, zoom/rotate keys and sensitivity, line assist).

**Is MagmaRita official, or affiliated with Magma or Krita?**
No. It is an unofficial community project. "Krita" is a trademark of the Krita
Foundation and "Magma" is a trademark of its owner. See CREDITS.md.

**Is MagmaRita open source, and which Krita versions work?**
GPL-3.0-or-later: https://github.com/runicmelody/magmarita - Krita 5.2+ (tested on
5.3.4, Windows; Linux/macOS expected to work).
