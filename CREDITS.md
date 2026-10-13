# Credits and licensing notes

MagmaRita is an **unofficial community project**. It is **not affiliated with,
sponsored by or endorsed by Magma (magma.com) or the Krita Foundation**.
"Krita" is a trademark of the Krita Foundation; "Magma" is a trademark of its
owner. The MagmaRita logo is an original mark and contains no Krita or Magma
artwork - their brand colours were only used as reference.

## The name

"MagmaRita" is a pun on **Magma** + **Margherita** (the pizza) - it is not
derived from the Krita wordmark. It is still an unofficial fan project, hence the
disclaimer above.

## Scrubby zoom is NOT our work

The **scrubby zoom** feature - hold a key and drag horizontally to zoom - comes
from **Scrubby Zoom by 10zindraws**: <https://github.com/10zindraws/Scrubby-Zoom>.
It is **not original to MagmaRita**; the MagmaRita author did not invent it. It is
included here because it is what Magma users expect, and it has been **lightly
edited/adapted** for this project.

What MagmaRita changed:
- added canvas rotation around the centre (hold R) and the Ctrl line assist hook,
- made the keys and sensitivities configurable (Settings / magmarita.json),
- added per-document zoom memory and tablet support,
- rewrote the module ("pykrita/magmarita/scrubby.py") so no code is copied from
  upstream, because that project publishes **no licence file** (default: all
  rights reserved). If you want to reuse *their* code, ask its author first.

If upstream later adds a licence and you prefer their code directly, reuse it
under their terms and keep this credit visible.

## Other acknowledgements

- **Krita** - action ids, canvas-input profile format and the bundled
  "Ten Brushes" plugin (the preset-slot idea) all come from Krita itself.
- Krita's rotation/zoom behaviour was reverse-engineered from Krita 5.3.4 for
  compatibility; the diagnostics log exists for exactly that reason.
- **Segoe UI** (Microsoft) is used for the generated wordmark images.
- Branding assets are CC BY-SA 4.0; the code is GPL-3.0-or-later.
