# MagmaRita keymap reference

Mapping of Magma defaults to Krita actions. Krita action ids are the values
used in "kritashortcutsrc".

## Tools

| Magma key | Action | Krita action id |
|-----------|--------|-----------------|
| I (and 1) | Dropper | KritaSelected/KisToolColorSampler |
| B | Brush | KritaShape/KisToolBrush |
| E | Eraser | erase_action |
| G | Paint bucket | KritaFill/KisToolFill |
| Shift+G | - | KritaFill/KisToolGradient |
| U | Rectangle | KritaShape/KisToolRectangle |
| Shift+U | - | KritaShape/KisToolEllipse |
| M | Selection | KisToolSelectRectangular |
| L | Lasso | KisToolSelectPolygonal |
| W | - | KisToolSelectContiguous |
| V | Move | KritaTransform/KisToolMove |
| Shift+T | Transform | KisToolTransform |
| C | - | KisToolCrop |
| H | Scrubby zoom (hold + drag) | scrubby_zoom_activate |

## View

| Magma key | Action | Krita action id |
|-----------|--------|-----------------|
| = | Zoom in | view_zoom_in |
| - | Zoom out | view_zoom_out |
| Home | Fit on screen | zoom_to_fit |
| End | Actual pixels | zoom_to_100pct |
| Tab | Toggle UI | view_show_canvas_only |
| H | Flip horizontally | mirror_canvas |
| X | Switch colours | toggle_fg_bg |

## Edit / selection / layers

| Magma key | Action | Krita action id |
|-----------|--------|-----------------|
| Ctrl+Z | Undo | edit_undo |
| Ctrl+Shift+Z | Redo | edit_redo |
| Ctrl+A | Select all | select_all |
| Ctrl+D | Deselect | deselect |
| Ctrl+Shift+I | Invert selection | invert_selection |
| Delete | Delete | clear |
| [ / ] | Brush size | decrease_brush_size / increase_brush_size |
| Shift+N | Add layer | add_new_paint_layer |
| Ctrl+E | Merge down | merge_layer |
| Ctrl+J | Duplicate layer | duplicatelayer |

## Tool presets (handled by the MagmaRita plugin)

| Key | Preset slot |
|-----|-------------|
| 2 | a) Eraser Small |
| 3 | d) Ink-1 Precision |
| 4 | b) Basic-5 Size |
| 5 | a) Eraser Soft |
| 6 | Eraser circle |

Edit them in Krita: *Tools > Scripts > Ten Brushes*.
