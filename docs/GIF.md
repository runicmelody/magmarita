# Recording the demo GIF

## 0) Before you hit record

- Krita: new canvas **1920x1080**, 2-3 layers, **a simple drawing already on the
  canvas** (so brush/eraser strokes are visible immediately).
- Open the palette: **Settings > Dockers > MagmaRita**, docked on the right, with
  the preset thumbnails visible.
- Clean the scene: close the Welcome tab, hide anything personal (recent files,
  layer names, dockers you do not need). Keep the **zoom % in the status bar** -
  it proves the scrubby zoom works.
- Reset state: zoom ~**50-70 %**, rotation **0**, foreground/background colours
  set, single brush active.

## 1) Best source: Krita's own Recorder (no screen capture at all)

Settings > Dockers > **Recorder** gives you a clean, canvas-only capture:

1. Set **frame rate 12**, a **capture size** around 50-75 % (720-960 px wide) and an
   **output folder** (one PNG per frame).
2. Press record, do the 9-second routine, press stop.
3. Turn the frames into a GIF:

~~~
python tools/frames_to_gif.py <frames-folder> demo.gif --fps 12 --width 900
~~~

That gives you a GIF with no desktop, no dockers and no mouse cursor clutter - and
it is sharper than a screen recording. Use a screen recorder only when you want to
show the keyboard/interface itself.

## 1b) Capture tool (screen region)

| OS | Tool | Why |
|---|---|---|
| Windows | **ShareX** (region -> GIF) | free, region capture, 30 s limit, easy crop |
| Windows | **ScreenToGif** | simple editor, frame trimming, export MP4/GIF |
| Windows | **OBS** (record MP4) | best quality; convert or upload the MP4 |
| macOS | **Kap** / CleanShot X | quick region GIF |
| Linux | **Peek** / Kooha | simple, produces GIF/WebM |

If the platform accepts **MP4/WebM, prefer it** (Reddit, X/Twitter, YouTube) -
much smaller and sharper than GIF. GIF only where it is required (GitHub README,
itch screenshots).

## 2) Settings

| Setting | Value |
|---|---|
| Capture region | canvas only (or canvas + palette docked) |
| Output width | **800-1000 px** |
| Length | **6-10 seconds**, clean loop |
| Frame rate | 12-15 fps (GIF) / 30 fps (MP4) |
| File size | under ~5 MB (Reddit, itch) / under ~10 MB (GitHub) |
| Audio | none |

## 3) Storyboard - one take, ~9 seconds

| Time | Do this | What it proves |
|---|---|---|
| 0.0-0.5s | hold still | gives the loop a readable start |
| 0.5-3s | press **3**, draw 2-3 bold strokes; press **2** and erase part of it | preset switching = speed |
| 3-5s | hold **Z**, drag left then right | scrubby zoom (watch the % change) |
| 5-7s | hold **R**, drag in a small circle | rotate around the canvas centre |
| 7-8s | hold **Ctrl**, drag | straight line |
| 8-9s | press **1** (dropper), click on the drawing, press **3**, paint a stroke | dropper -> back to pen |

Tips: bold, simple strokes (thin lines turn to mush in a GIF); keep the cursor
visible so viewers can follow; do a couple of practice runs - one clean take is
all you need.

## 4) Where to use it

- **krita-artists.org**: attach the GIF to the post (they host images).
- **Reddit** (r/krita, r/DigitalPainting): upload MP4 if possible, GIF second
  best. Put **the media first**, text after - people scroll past walls of text.
- **itch.io**: cover image is a PNG (assets/branding/itch-cover-630x250.png);
  screenshots can be PNG or GIF.
- **README**: `![demo](assets/branding/demo.gif)` - keep it under ~10 MB.
- **GitHub social preview**: PNG, not GIF (assets/branding/github-social-1280x640.png).

## 5) After posting

- Keep the raw MP4 - reuse it for a YouTube "short" or an X/Twitter clip later.
- Reply to every comment for the first day; link the release, not the repo root.
- Always include the line: *Free, GPL-3.0. Unofficial - not affiliated with Magma
  or the Krita Foundation.*
