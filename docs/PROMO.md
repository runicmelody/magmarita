# Launch kit - copy-paste posts

## 9) Naming rules (use these exact phrases everywhere)

| Use | Don't |
|---|---|
| **MagmaRita** | magmarita / Magma Rita / MagmaRita Krita |
| **one-liner:** Magma-style keybinds for Krita | "Magma for Krita" (implies official) |
| **alt phrasings:** Magma keybinds for Krita · Magma shortcuts for Krita | "Krita Magma edition" |
| **always add:** Free, open source (GPL-3.0). Unofficial - not affiliated with Magma or the Krita Foundation. | using their logos or "official" anywhere |

Links to reuse:
- Repo: https://github.com/runicmelody/magmarita
- Releases: https://github.com/runicmelody/magmarita/releases/latest
- Docs site: https://runicmelody.github.io/magmarita/
- FAQ: https://github.com/runicmelody/magmarita/blob/main/docs/FAQ.md

---

## 2) krita-artists.org

**Category:** Plugins / Resources   **Tags:** krita, plugin, shortcuts, presets, zoom, workflow

**Title:** MagmaRita - Magma-style keybinds, palette and scrubby zoom for Krita

**Body:**

I paint in Magma and Krita and kept fumbling the shortcuts, so I built MagmaRita:
a small plugin + installer that puts Magma's keys onto Krita.

What it does
- Tool presets on the number keys: 1 dropper, 2 small eraser, 3 pen, 4 basic, 5 soft eraser, 6 big eraser
- Magma letters: B brush, E erase, G fill, U rectangle, M/L select/lasso, V move, Shift+T transform, H flip, X swap colours, [ ] brush size
- Hold Z + drag = scrubby zoom (relative to the current zoom, remembered per document)
- Hold R + drag = rotate the canvas around its centre
- Hold Ctrl + drag = straight line
- A palette docker (Settings > Dockers > MagmaRita): tool buttons, ten preset slots with thumbnails (right-click to rebind), Pen Pressure / Lock Alpha toggles, size + opacity sliders

Two Krita gotchas it fixes
- Krita's Canvas Input Settings bind 1-3 to zoom and 4-6 to rotate by default, which is why number keys "go crazy". MagmaRita clears those bindings.
- H / U / L / I / Shift+N are taken by Krita defaults (colour history, common colours, ...). MagmaRita unbinds them so the Magma keymap wins.

Install (Krita closed)
~~~
install.bat          (Windows)
./install.sh        (Linux / macOS)
python install.py    (any)
~~~
It backs up kritashortcutsrc and kritarc first. Settings live in magmarita.json
or Tools > Scripts > MagmaRita > Settings.

Free, GPL-3.0. Unofficial - not affiliated with Magma or the Krita Foundation.
Feedback very welcome: https://github.com/runicmelody/magmarita

---

## 3a) Reddit - r/krita

**Flair:** Resource / Tutorial (whichever fits)

**Title:** I made MagmaRita - Magma's keybinds, palette and scrubby zoom for Krita

**Body:**

[GIF: switching 2-6 presets, then Z zoom, then R rotate]

Coming from Magma I kept hitting the wrong keys in Krita, so I built a small
plugin that ports the feel over:

- 1-6 = tool presets (dropper, small eraser, pen, basic, soft eraser, big eraser)
- B/E/G/U/M/L/V/Shift+T = Magma's tool letters
- Hold Z + drag = zoom, hold R + drag = rotate around the centre, hold Ctrl = straight line
- A palette docker with preset thumbnails, pressure/alpha toggles and size/opacity sliders

It also clears the two Krita defaults that fight you: Canvas Input Settings
number keys (why 1-6 zoom/rotate) and the H/U/L/I/Shift+N shortcuts.

One command to install (Krita closed), it backs up your config first:
~~~
install.bat      (Windows)
./install.sh     (Linux / macOS)
python install.py
~~~

Free and open source (GPL-3.0). Unofficial, not affiliated with Magma or the Krita Foundation.
https://github.com/runicmelody/magmarita - happy to take requests.

---

## 3b) Reddit - r/DigitalPainting (shorter variant)

**Title:** MagmaRita - Magma-style keybinds + palette for Krita (free, open source)

**Body:**

If you paint in Magma and Krita: I made MagmaRita, which gives Krita Magma's
shortcuts - tool presets on 1-6, B/E/G/U/M/L/V, hold Z to scrubby-zoom, hold R to
rotate, hold Ctrl for a straight line - plus a small palette docker with preset
thumbnails and size/opacity sliders.

It also fixes the classic Krita annoyance where the number keys zoom or rotate
the canvas (that is Krita's Canvas Input Settings, and MagmaRita clears it).

Install: "python install.py" with Krita closed. Free, GPL-3.0, unofficial.
https://github.com/runicmelody/magmarita

---

## 4a) KDE Discuss (discuss.kde.org) - "Krita" category

**Title:** MagmaRita: unofficial Krita plugin adding a Magma-style keymap (feedback welcome)

**Body:**

Hello Krita folk - I maintain MagmaRita, an unofficial plugin that applies a
Magma-style keymap to Krita and smooths over two defaults that surprise new users:

1. **Canvas Input Settings** bind 1-3 to Zoom Canvas and 4-6 to Rotate Canvas.
   MagmaRita clears those entries from the active canvas-input profile so the
   number keys can be presets.
2. A few core shortcuts already own keys people expect (show_color_history = H,
   show_common_colors = U, make_brush_color_lighter = L, decrease_opacity = I,
   show_minimal_shade_selector = Shift+N). MagmaRita unbinds them.

It also ships a scrubbier zoom/rotate (hold a key + drag), which is an
independent implementation of the interaction - idea credited to
10zindraws/Scrubby-Zoom.

Everything lives in user config (kritashortcutsrc, kritarc, the canvas-input
profile, pykrita) - nothing in the Krita install directory. Code is GPL-3.0:
https://github.com/runicmelody/magmarita

I would welcome review from Krita devs, especially on the canvas-input/profile
patching and on whether any of it could become a first-party shortcut scheme.

---

## 4b) invent.kde.org (MR/issue comment)

Short version to paste when relevant:

> There is an unofficial plugin doing this today (clears the Canvas Input
> Settings zoom/rotate key bindings and the H/U/L/I/Shift+N overlaps):
> https://github.com/runicmelody/magmarita - might be useful prior art if a
> "Magma-compatible" scheme ever ships in Krita itself.

---

## Best ROI: replies to existing questions

Search these phrases monthly and answer them with a two-sentence reply + link
(this is what actually ranks):

- "magma keybinds krita" / "magma shortcuts for krita"
- "krita number keys zoom" / "why do my number keys rotate in krita"
- "scrubby zoom krita"
- "krita rotate canvas while holding key"
- "photoshop shortcuts for krita" / "clip studio shortcuts krita"

Canned reply:

> Krita's Canvas Input Settings are what makes 1-6 zoom/rotate by default.
> I put together MagmaRita, which clears those and applies Magma's keymap
> (presets on 1-6, hold Z to zoom, hold R to rotate): <link>. It is free and
> unofficial.

## Posting checklist

- [ ] Record a 5-10s GIF: presets 2-6, then Z zoom, then R rotate, then Ctrl line
- [ ] Post once per community; do not cross-post the same minute
- [ ] Always link the latest release
- [ ] Always include the "unofficial" line
- [ ] Answer every comment for the first day
