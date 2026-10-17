#!/usr/bin/env python3
"""Settings dialog regression test (offscreen Qt, stubbed Krita).

The dialog once grew taller AND wider than the screen, pushing OK/Cancel out of
reach so nothing could be saved. This test fails if that comes back.

Skips (exit 0) when PyQt5 is not installed.
"""

import importlib.util
import os
import sys
import tempfile
import types

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG_DIR = os.path.join(ROOT, "pykrita", "magmarita")
SCREEN_BUDGET_WIDTH = 800      # smallest screen we support
failures = []


def check(name, condition, detail=""):
    print(("  ok   " if condition else "  FAIL ") + name + (("  [" + detail + "]") if detail else ""))
    if not condition:
        failures.append(name)


def stub_krita():
    class Instance(object):
        def version(self):
            return "5.3.4"

        def resources(self, _kind):
            return dict((n, None) for n in ("a) Eraser Small", "d) Ink-1 Precision"))

        def action(self, _name):
            return None

        def activeWindow(self):
            return None

        def activeDocument(self):
            return None

    instance = Instance()
    krita = types.ModuleType("krita")
    krita.Extension = type("Extension", (object,), {})
    krita.Krita = type("Krita", (), {"instance": staticmethod(lambda: instance)})
    sys.modules["krita"] = krita


def load(name):
    package = sys.modules.get("mgp")
    if package is None:
        package = types.ModuleType("mgp")
        package.__path__ = [PKG_DIR]
        sys.modules["mgp"] = package
    spec = importlib.util.spec_from_file_location("mgp." + name, os.path.join(PKG_DIR, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules["mgp." + name] = module
    spec.loader.exec_module(module)
    return module


def main():
    try:
        import PyQt5  # noqa: F401
    except Exception:
        print("PyQt5 not installed - skipping settings dialog test")
        return 0
    try:
        from PyQt5.QtWidgets import QApplication, QDialogButtonBox, QScrollArea
        app = QApplication.instance() or QApplication([])
    except Exception as exc:
        print("Qt cannot start here (%s) - skipping" % exc)
        return 0

    tmp = tempfile.mkdtemp(prefix="magmarita-dialog-")
    os.environ["LOCALAPPDATA"] = tmp
    os.environ["APPDATA"] = os.path.join(tmp, "roaming")
    os.environ["USERPROFILE"] = tmp
    os.environ["HOME"] = tmp
    os.makedirs(os.path.join(tmp, "roaming", "krita"), exist_ok=True)

    stub_krita()
    load("keymap")
    settings = load("settings")

    dialog = settings.MagmaRitaSettings(None)
    dialog.show()
    app.processEvents()

    hint = dialog.minimumSizeHint()
    screen = app.primaryScreen().availableGeometry()
    print("min hint %dx%d | opened %dx%d | screen %dx%d"
          % (hint.width(), hint.height(), dialog.width(), dialog.height(),
             screen.width(), screen.height()))

    check("dialog can shrink to a small screen", hint.width() <= SCREEN_BUDGET_WIDTH,
          str(hint.width()))
    check("dialog opens inside the screen",
          dialog.width() <= screen.width() and dialog.height() <= screen.height())
    check("dialog height is clamped", dialog.height() <= settings.MAX_DIALOG_HEIGHT + 1,
          str(dialog.height()))
    check("body scrolls", len(dialog.findChildren(QScrollArea)) >= 1)

    boxes = dialog.findChildren(QDialogButtonBox)
    check("OK/Cancel exist", len(boxes) == 1)
    if boxes:
        geometry = boxes[0].geometry()
        check("OK/Cancel are inside the dialog",
              geometry.y() >= 0 and geometry.bottom() <= dialog.height(),
              "y=%d bottom=%d h=%d" % (geometry.y(), geometry.bottom(), dialog.height()))

    check("ten key editors", len(dialog.key_edits) == 10)
    check("ten preset combos", len(dialog.combos) == 10)

    config = dialog.result_config()
    check("ten slots returned", len(config.get("slots", [])) == 10)
    check("all settings keys returned",
          set(["zoom_key", "rotate_key", "rotate_mode", "line_assist", "line_tool",
               "key_hints", "enforce_keymap", "safe_mode", "diagnostics",
               "zoom_sensitivity", "rotate_sensitivity"]).issubset(config.keys()))
    check("defaults round-trip",
          config["zoom_key"] == "Z" and config["rotate_key"] == "R"
          and config["rotate_mode"] in ("center", "scrubby"))

    if failures:
        print("\n%d check(s) failed" % len(failures))
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
