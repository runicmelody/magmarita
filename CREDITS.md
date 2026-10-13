# Credits and licensing notes

MagmaRita is an **unofficial community project**. It is **not affiliated with,
sponsored by or endorsed by Magma (magma.com) or the Krita Foundation**.
"Krita" is a trademark of the Krita Foundation; "Magma" is a trademark of its
owner. The MagmaRita logo is an original mark and contains no Krita or Magma
artwork - their brand colours were only used as reference.

## Idea credit: Scrubby Zoom

- Upstream: <https://github.com/10zindraws/Scrubby-Zoom> (by 10zindraws)
- Credit for: the "hold a key and drag horizontally to zoom" interaction.
- The code in "pykrita/magmarita/scrubby.py" is an **independent clean-room
  implementation** written for MagmaRita (it adds centre rotation, configurable
  keys and per-document zoom memory). Upstream publishes no licence file, so no
  code was copied - if you want to reuse *their* code, ask the author first.

## Other acknowledgements

- **Krita** - action ids, canvas-input profile format and the bundled
  "Ten Brushes" plugin (the preset-slot idea) all come from Krita itself.
- Krita's rotation/zoom behaviour was reverse-engineered from Krita 5.3.4 for
  compatibility; the diagnostics log exists for exactly that reason.
- **Segoe UI** (Microsoft) is used for the generated wordmark images.
- Branding assets are CC BY-SA 4.0; the code is GPL-3.0-or-later.
