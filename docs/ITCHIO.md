# Publishing MagmaRita on itch.io

## 0. Build the package

~~~
python tools/build_itch.py
~~~

That writes "dist/magmarita-<version>.zip" (plugin + installer + docs + branding).

## 1. Create the project

1. Log in to <https://itch.io> -> **Dashboard -> Create new project**.
2. **Title:** MagmaRita - Magma-style keybinds for Krita
3. **Project URL:** magmarita   (=> https://runicmelody.itch.io/magmarita)
4. **Project kind:** *Tool* (or *Other*)
5. **Classification:** *Free* / tick *"Name your own price"* and set a suggested
   price of 0.
6. **Short description / tagline:**

   ~~~
   Magma-style keyboard shortcuts, palette and scrubby zoom/rotate for Krita.
   ~~~

## 2. Cover + screenshots

- **Cover image:** upload "assets/branding/itch-cover-630x250.png".
- **Screenshots:** grab 2-4 from Krita:
  1. Settings > Dockers > MagmaRita (the palette) docked over the canvas.
  2. Configure Krita > Keyboard Shortcuts filtered to "Magma".
  3. A canvas showing the scrubby zoom / rotate in action.
  Use "Home + PrtScr" or Snipping Tool; 1280x720 or larger is fine.

## 3. Upload the build

- **Uploads -> Upload files:** "dist/magmarita-<version>.zip"
- Tick **"This file will be played in the browser"** OFF (it is a download).
- Leave the platform tags as "Windows", "Linux", "macOS".

## 4. Description (paste this, edit freely)

~~~
MagmaRita gives Magma artists their muscle memory back inside Krita.

**Keymap**
- 1 dropper - 2 small eraser - 3 pen - 4 basic - 5 soft eraser - 6 big eraser
- B brush - E erase - G fill - U rectangle - M/L select/lasso - V move - Shift+T transform
- H flip canvas - X switch colours - [ ] brush size - Home fit - End 100%
- Z scrubby zoom (hold + drag) - R rotate around the centre (hold + drag)
- Ctrl straight line (hold Ctrl, drag, release). Ctrl no longer picks colour.

**Palette docker** (Settings > Dockers > MagmaRita)
Quick tool buttons, ten brush-preset slots with thumbnails (click to activate,
right-click to bind a preset or key), Pen Pressure / Lock Alpha toggles, brush
Size/Opacity sliders.

**Configurable**
Tools > Scripts > MagmaRita > Settings... or edit magmarita.json - preset slots,
zoom/rotate keys and sensitivity, line assist.

**Install**
1. Close Krita.
2. Run install.bat (Windows), ./install.sh (Linux/macOS) or "python install.py".
3. Start Krita. Enable the plugin in Settings > Configure Krita > Python Plugin
   Manager if you want the menu/docker.

**Notes**
- Requires Krita 5.2+ (tested on 5.3.4).
- Unofficial community project; not affiliated with Magma or the Krita team.
- Source + issues: https://github.com/runicmelody/magmarita
~~~

## 5. Tags

~~~
krita  magma  brush  painter  art  plugin  python  keyboard-shortcuts  creative-tools  windows  linux
~~~

## 6. Publish

- Visibility: **Public**.  Then **Save & view page**.
- Optional: **Devlog** a short "v0.9 released" post linking the GitHub release.

## 7. Every new version

1. Bump the version in "pykrita/magmarita/keymap.py".
2. "python tools/build_itch.py"
3. itch.io -> your project -> **Edit game -> Uploads** -> upload the new zip ->
   tick **"This is the latest version"** (or use *Channel* / *Version*) -> Save.
