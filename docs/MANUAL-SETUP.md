# Doing it by hand (no plugin)

Everything MagmaRita automates, as a pure GUI recipe. Budget **45-70 minutes** the
first time, ~15-20 if you already know Krita.

## 1. The keymap

Settings > Configure Krita > Keyboard Shortcuts. Search the action name, click the
row, press the key, then Apply.

| Key | Search for | Krita action id |
|---|---|---|
| I (and 1) | Color Sampler | KritaSelected/KisToolColorSampler |
| B | Freehand Brush | KritaShape/KisToolBrush |
| E | Erase | erase_action |
| G | Fill | KritaFill/KisToolFill |
| Shift+G | Gradient | KritaFill/KisToolGradient |
| U | Rectangle | KritaShape/KisToolRectangle |
| Shift+U | Ellipse | KritaShape/KisToolEllipse |
| M | Rectangular Selection | KisToolSelectRectangular |
| L | Polygonal Selection | KisToolSelectPolygonal |
| W | Contiguous Selection | KisToolSelectContiguous |
| V | Move | KritaTransform/KisToolMove |
| Shift+T | Transform | KisToolTransform |
| C | Crop | KisToolCrop |
| H | Mirror Canvas | mirror_canvas |
| X | Toggle Foreground/Background | toggle_fg_bg |
| Tab | Show Canvas Only | view_show_canvas_only |
| = and - | Zoom In / Zoom Out | view_zoom_in / view_zoom_out |
| Home and End | Fit to page / Zoom to 100% | zoom_to_fit / zoom_to_100pct |
| [ and ] | Decrease / Increase brush size | decrease_brush_size / increase_brush_size |
| Ctrl+D | Deselect | deselect |
| Ctrl+Shift+I | Invert Selection | invert_selection |
| Ctrl+A | Select All | select_all |
| Shift+N | Add paint layer | add_new_paint_layer |
| Ctrl+E | Merge with layer below | merge_layer |
| Ctrl+J | Duplicate layer | duplicatelayer |

## 2. Free the keys Krita already owns

Without this, H / U / L / I / Shift+N look broken: Krita's own actions grab them
first. Search each of these in the same dialog and **clear its shortcut**.

| Search for | Key it steals |
|---|---|
| Show color history | H |
| Show common colors | U |
| Make brush color lighter | L |
| Decrease Opacity | I |
| Show minimal shade selector | Shift+N |

## 3. Tool presets on the number keys (Ten Brushes, built in)

1. Settings > Configure Krita > Python Plugin Manager > tick **Ten Brushes**, then
   restart Krita.
2. Tools > Scripts > Ten Brushes: assign 10 presets in the order you want.
3. Keyboard Shortcuts: search "Activate Brush Preset" and bind the ten actions to
   1..0.
4. In the Ten Brushes dialog enable "auto brush on press" and optionally the
   "second press returns to the previous brush" behaviour.

Careful: key "1" can be the dropper or a preset, not both.

## 4. Stop the number keys zooming or rotating the canvas

Settings > Configure Krita > Canvas Input Settings (active profile, usually
"Krita Default"):

- **Zoom Canvas**: delete the entries bound to keys 1, 2 and 3 (and to = - + if you
  bound zoom there).
- **Rotate Canvas**: delete the entries bound to keys 4, 5 and 6.
- If Ctrl opens the colour picker, remove the Ctrl entries under Alternate
  Invocation and Zoom Canvas.

Optional, and quite nice - add single-key gestures there:

- Zoom Canvas > Add > input **Z + Left Button** > action "Zoom in/out"
- Rotate Canvas > Add > input **R + Left Button** > action "Rotate left/right"

That gives you hold-Z-to-zoom and hold-R-to-rotate with no plugin at all.

## 5. Reuse it on another machine

- Keyboard Shortcuts > Scheme > Save as... writes a .shortcuts file you can import
  elsewhere.
- Canvas-input profiles are files in Krita's resource folder under "input" - copy
  one to reuse it.

## 6. What you cannot do by hand

- A palette docker with preset thumbnails, size/opacity sliders and
  pressure/alpha-lock toggles.
- Hold Ctrl and drag for a straight line (switching tools while a key is held).
- Remembering the zoom per document, and clearing the conflicts above
  automatically.

That is the part **MagmaRita** does; it also performs every step on this page in
one command: https://github.com/runicmelody/magmarita
