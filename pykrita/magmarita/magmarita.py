# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita PyKrita plugin.

* Tools > Scripts > MagmaRita: Apply keymap / Restore / Settings / About.
* Owns the Magma tool-preset slots on the number keys (configurable).
* Applies the Magma keymap to Krita's actions at startup and fills in any
  shortcut Krita did not pick up, so it does not depend on kritashortcutsrc.
* Writes a diagnostic log to <LOCALAPPDATA>/magmarita-diag.log.
"""

import os
import re

from krita import Extension, Krita
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QMessageBox

from . import keymap

DIGITS = "1234567890"


def _log(msg):
    try:
        path = os.path.join(keymap.config_dir(), "magmarita-diag.log")
        with open(path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def _sequences(text):
    return [QKeySequence(s.strip()) for s in text.split(";") if s.strip()]


class MagmaRitaExtension(Extension):

    def __init__(self, parent):
        super(MagmaRitaExtension, self).__init__(parent)
        self.cfg = {}
        self._slots = []
        self._slot_actions = []
        self._preset_by_index = {}
        self._preset_by_name = {}

    def setup(self):
        pass

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def createActions(self, window):
        self.window = window
        self.cfg = keymap.load_config()
        self._slots = list(self.cfg.get("slots", []))
        self._slot_actions = []

        for i in range(10):
            act = window.createAction(
                "magmarita_preset_%d" % (i + 1), "Magma preset slot %d" % (i + 1))
            act.triggered.connect(self._activate_preset)
            self._slot_actions.append(act)
        self._apply_slots()

        self._act_apply = window.createAction("magmarita_apply", "Apply Magma keymap")
        self._act_apply.triggered.connect(self._on_apply)
        self._act_restore = window.createAction("magmarita_restore", "Restore previous shortcuts")
        self._act_restore.triggered.connect(self._on_restore)
        self._act_settings = window.createAction("magmarita_settings", "Settings...")
        self._act_settings.triggered.connect(self._on_settings)
        self._act_about = window.createAction("magmarita_about", "About MagmaRita")
        self._act_about.triggered.connect(self._on_about)

        QTimer.singleShot(2500, self._bootstrap)

    def _apply_slots(self):
        self._preset_by_index = {}
        self._preset_by_name = {}
        for i, act in enumerate(self._slot_actions):
            slot = self._slots[i] if i < len(self._slots) else {}
            preset = (slot or {}).get("preset", "") or ""
            key = (slot or {}).get("key", "") or ""
            if preset:
                self._preset_by_index[i] = preset
                self._preset_by_name[act.objectName()] = preset
                act.setText("Magma preset %d (%s)" % (i + 1, preset))
                act.setShortcut(QKeySequence(key) if key else QKeySequence())
            else:
                act.setText("Magma preset slot %d" % (i + 1))
                act.setShortcut(QKeySequence())

    def _activate_preset(self):
        try:
            sender = self.sender()
            if sender is None:
                return
            preset_name = self._preset_by_name.get(sender.objectName())
            if not preset_name:
                _log("[preset] no mapping for %r" % sender.objectName())
                return
            window = Krita.instance().activeWindow()
            if not window or not window.views():
                return
            preset = Krita.instance().resources("preset").get(preset_name)
            if not preset:
                _log("[preset] not found: %s" % preset_name)
                return
            _log("[preset] ok: %s" % preset_name)
            act = Krita.instance().action("KritaShape/KisToolBrush")
            if act is not None:
                act.trigger()
            window.views()[0].setCurrentBrushPreset(preset)
        except Exception as exc:  # noqa: BLE001
            _log("[preset] error: %r" % exc)

    # ------------------------------------------------------------------
    # Startup bootstrap
    # ------------------------------------------------------------------
    def _bootstrap(self):
        try:
            K = Krita.instance()
            filled = []

            # 1) preset slots (we hold direct references)
            for i, act in enumerate(self._slot_actions):
                slot = self._slots[i] if i < len(self._slots) else {}
                key = (slot or {}).get("key", "") or ""
                if (slot or {}).get("preset") and key:
                    if act.shortcut().toString() != key:
                        act.setShortcut(QKeySequence(key))

            # 2) bundled scrubby zoom
            a = K.action("scrubby_zoom_activate")
            if a is not None and a.shortcut().isEmpty():
                a.setShortcut(QKeySequence("Z"))
                filled.append("scrubby_zoom_activate=Z")

            # 3) core Magma shortcuts: fill in only what is missing
            for name, keys in keymap.SHORTCUTS.items():
                a = K.action(name)
                if a is None:
                    filled.append("[missing] " + name)
                    continue
                if not a.shortcut().isEmpty():
                    continue
                seqs = _sequences(keys)
                if len(seqs) > 1:
                    a.setShortcuts(seqs)
                elif seqs:
                    a.setShortcut(seqs[0])
                filled.append(name + "=" + keys)

            # 4) diagnostics
            _log("=== MagmaRita %s bootstrap ===" % keymap.VERSION)
            for i, act in enumerate(self._slot_actions):
                _log("slot %d -> key %r preset %r" % (
                    i + 1, act.shortcut().toString(),
                    self._preset_by_index.get(i, "")))
            a = K.action("scrubby_zoom_activate")
            _log("scrubby_zoom_activate -> %s" % (a.shortcut().toString() if a else "(no action)"))
            for name in keymap.SHORTCUTS:
                a = K.action(name)
                _log("core %s -> %s" % (name, a.shortcut().toString() if a else "(no action)"))
            # every action bound to a bare digit, or rotate/zoom/reset by name
            try:
                win = Krita.instance().activeWindow()
                qw = win.qwindow() if win else None
                for a in (qw.findChildren(QAction) if qw else []):
                    s = a.shortcut().toString()
                    text = a.text() or ""
                    if not s:
                        continue
                    if (s in DIGITS) or re.search(r"(?i)rotat|zoom|reset", text):
                        _log("BIND key=%r action=%r text=%r" % (s, a.objectName(), text))
            except Exception as exc:
                _log("dump error: %r" % exc)
            _log("filled now: %s" % (", ".join(filled) if filled else "(nothing)"))
        except Exception as exc:  # noqa: BLE001
            _log("bootstrap error: %r" % exc)

    # ------------------------------------------------------------------
    # Menu handlers
    # ------------------------------------------------------------------
    def _on_apply(self):
        try:
            made = keymap.apply()
            self._bootstrap()
            msg = "Magma keymap applied and switched on."
            if made:
                msg += "\n\nBackups:\n" + "\n".join(made)
            QMessageBox.information(None, keymap.APP_NAME, msg)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(None, keymap.APP_NAME, "Could not apply keymap:\n%s" % exc)

    def _on_restore(self):
        try:
            restored = keymap.restore_latest()
            if restored:
                QMessageBox.information(None, keymap.APP_NAME,
                                        "Restored:\n" + "\n".join(restored) + "\n\nRestart Krita.")
            else:
                QMessageBox.information(None, keymap.APP_NAME, "No backup found.")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(None, keymap.APP_NAME, "Could not restore:\n%s" % exc)

    def _on_settings(self):
        try:
            from .magmarita_settings import MagmaRitaSettings
            dlg = MagmaRitaSettings(None)
            exec_fn = getattr(dlg, "exec_", None) or dlg.exec
            if exec_fn():
                self.cfg = dlg.result_config()
                keymap.save_config(self.cfg)
                self._slots = list(self.cfg.get("slots", []))
                self._apply_slots()
                QMessageBox.information(
                    None, keymap.APP_NAME,
                    "Saved to:\n%s\n\nNew number-key shortcuts apply immediately." % keymap.config_path())
        except Exception as exc:  # noqa: BLE001
            _log("settings error: %r" % exc)
            QMessageBox.warning(None, keymap.APP_NAME, "Settings failed:\n%s" % exc)

    def _on_about(self):
        QMessageBox.information(
            None, keymap.APP_NAME,
            "%s %s\nMagma-style keybinds for Krita.\n\n%s\nConfig:\n%s"
            % (keymap.APP_NAME, keymap.VERSION, keymap.HOMEPAGE, keymap.config_path()))
