# Contributing to MagmaRita

Thanks for helping Magma artists land softly in Krita!

## Ways to help
- Report keys that feel wrong compared to Magma.
- Test the installer on Linux / macOS.
- Add Magma parity for actions we have not covered yet.
- Share preset packs that make the number-key strip shine.

## Editing the keymap
All shortcuts live in pykrita/magmarita/keymap.py (the SHORTCUTS dict and the
PRESETS list). After changing them, regenerate the importable scheme:

~~~
python tools/build_scheme.py
~~~

## Pull requests
1. Fork and branch.
2. Keep the keymap table in README + docs in sync.
3. Add a CHANGELOG entry.
