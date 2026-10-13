#!/usr/bin/env python3
"""Plugin module tests - no Krita, no display required.

Loads keymap.py / scrubby.py / magmarita.py behind a stub "krita" module and a
fake package shim, then exercises the module level helpers: version guard, path
resolution, the opt-in diagnostics gate and small utilities.

Skips (exit 0) when PyQt5 is not installed.
"""

import importlib.util
import os
import shutil
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG_DIR = os.path.join(ROOT, "pykrita", "magmarita")
failures = []


def check(name, condition, detail=""):
    print(("  ok   " if condition else "  FAIL ") + name + (("  [" + detail + "]") if detail else ""))
    if not condition:
        failures.append(name)


class _FakeKrita(object):
    VERSION = "5.3.4"

    def version(self):
        return self.VERSION

    def action(self, _name):
        return None

    def activeWindow(self):
        return None

    def activeDocument(self):
        return None

    def resources(self, _kind):
        return {}

    def addExtension(self, _ext):
        pass

    def addDockWidgetFactory(self, _factory):
        pass


def install_stub_krita():
    instance = _FakeKrita()
    krita = types.ModuleType("krita")
    krita.Extension = type("Extension", (object,), {})
    krita.Krita = type("Krita", (), {"instance": staticmethod(lambda: instance)})
    krita.DockWidget = type("DockWidget", (object,), {})
    krita.DockWidgetFactory = lambda *a, **k: None
    krita.DockWidgetFactoryBase = type("DockWidgetFactoryBase", (), {"DockRight": 0})
    sys.modules["krita"] = krita
    return instance


def load_modules():
    package = types.ModuleType("mgp")
    package.__path__ = [PKG_DIR]
    sys.modules["mgp"] = package
    mods = {}
    for name in ("keymap", "scrubby", "magmarita"):
        spec = importlib.util.spec_from_file_location("mgp." + name, os.path.join(PKG_DIR, name + ".py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules["mgp." + name] = module
        spec.loader.exec_module(module)
        mods[name] = module
    return mods


def main():
    try:
        import PyQt5  # noqa: F401
    except Exception:
        print("PyQt5 not installed - skipping plugin tests")
        return 0

    tmp = tempfile.mkdtemp(prefix="magmarita-plugin-")
    os.environ["LOCALAPPDATA"] = tmp
    os.environ["APPDATA"] = os.path.join(tmp, "roaming")
    os.environ["USERPROFILE"] = tmp
    os.environ["HOME"] = tmp

    instance = install_stub_krita()
    mods = load_modules()
    km, sc, pl = mods["keymap"], mods["scrubby"], mods["magmarita"]
    print("paths:", km.config_dir(), "|", km.resource_dir())

    check("keymap: version guard accepts 5.3.4", km.version_supported("5.3.4"))
    check("keymap: version guard rejects 6.0.0", not km.version_supported("6.0.0"))
    check("scrubby: paths agree with keymap", sc._krita_dirs() == (km.resource_dir(), km.config_dir()))
    check("scrubby: supports 5.3.4", sc._krita_supported())
    instance.VERSION = "6.0.0"
    check("scrubby: refuses 6.0.0 (safe mode)", not sc._krita_supported())
    instance.VERSION = "5.3.4"

    os.makedirs(km.resource_dir(), exist_ok=True)
    check("scrubby: config defaults to empty", sc._config() == {})
    cfg_path = os.path.join(km.resource_dir(), "magmarita.json")
    with open(cfg_path, "w", encoding="utf-8") as fh:
        fh.write('{"zoom_key": "Q", "diagnostics": false}')
    check("scrubby: reads magmarita.json", sc._config().get("zoom_key") == "Q")

    log = km.log_path()
    sc._trace("must not appear")
    check("diagnostics OFF: scrubby writes nothing", not os.path.exists(log))
    with open(cfg_path, "w", encoding="utf-8") as fh:
        fh.write('{"diagnostics": true}')
    sc._trace("hello")
    check("diagnostics ON: scrubby writes the log",
          os.path.exists(log) and "[scrubby] hello" in open(log, encoding="utf-8").read())

    pl.set_diagnostics(False)
    pl._log("must not appear")
    check("diagnostics OFF: plugin writes nothing",
          "must not appear" not in open(log, encoding="utf-8").read())
    pl.set_diagnostics(True)
    pl._log("from the plugin")
    check("diagnostics ON: plugin writes the log",
          "from the plugin" in open(log, encoding="utf-8").read())

    check("magmarita._norm normalises punctuation",
          pl._norm("a) Eraser Circle") == "aerasercircle", pl._norm("a) Eraser Circle"))
    check("keymap defines both scrubby actions",
          "scrubby_zoom_activate" in km.SHORTCUTS and "scrubby_rotate_activate" in km.SHORTCUTS)
    check("keymap clears the Ctrl canvas binding", "1000021" in km.CANVAS_INPUT_KEYS_TO_CLEAR)

    if failures:
        print("\n%d check(s) failed - temp dir kept at %s" % (len(failures), tmp))
        for name in failures:
            print(" -", name)
        return 1
    print("\nall checks passed")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
