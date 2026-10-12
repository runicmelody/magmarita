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
from PyQt5.QtCore import QEvent, QObject, Qt, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAbstractSpinBox,
    QAction,
    QApplication,
    QComboBox,
    QKeySequenceEdit,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QTextEdit,
)

from . import keymap

_DIGIT_KEYS = {
    Qt.Key_1: "1", Qt.Key_2: "2", Qt.Key_3: "3", Qt.Key_4: "4", Qt.Key_5: "5",
    Qt.Key_6: "6", Qt.Key_7: "7", Qt.Key_8: "8", Qt.Key_9: "9", Qt.Key_0: "0",
}
_INPUT_WIDGETS = (QLineEdit, QAbstractSpinBox, QComboBox, QTextEdit,
                  QPlainTextEdit, QKeySequenceEdit)


class _DigitFilter(QObject):
    """Fallback so the number keys work even if Krita does not dispatch our
    plugin actions.  Ignored while typing into any input widget."""

    def __init__(self, extension):
        super(_DigitFilter, self).__init__()
        self.ext = extension
        self._key_count = 0

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.KeyPress and self._key_count < 400:
                self._key_count += 1
                fw = QApplication.focusWidget()
                _log("[key] key=%s mods=%s focus=%s modal=%s" % (
                    event.key(), int(event.modifiers()),
                    type(fw).__name__ if fw else None,
                    QApplication.activeModalWidget() is not None))
        except Exception:
            pass
        try:
            if event.type() != QEvent.KeyPress:
                return False
            if event.modifiers() != Qt.NoModifier:
                return False
            key = _DIGIT_KEYS.get(event.key())
            if not key or key not in self.ext._preset_by_key:
                return False
            if QApplication.activeModalWidget() is not None:
                return False
            if isinstance(QApplication.focusWidget(), _INPUT_WIDGETS):
                return False
            if not self.ext._has_open_document():
                return False
            self.ext._set_preset(self.ext._preset_by_key[key])
            return True
        except Exception:
            return False

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
        self._preset_by_key = {}
        self._digit_filter = None
        self._filter_installed = False
        self._hooked = set()

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

        if not self._filter_installed:
            app = QApplication.instance()
            if app is not None:
                self._digit_filter = _DigitFilter(self)
                app.installEventFilter(self._digit_filter)
                self._filter_installed = True
                _log("[filter] digit fallback installed")

        QTimer.singleShot(2500, self._bootstrap)

    def _apply_slots(self):
        self._preset_by_index = {}
        self._preset_by_name = {}
        self._preset_by_key = {}
        for i, act in enumerate(self._slot_actions):
            slot = self._slots[i] if i < len(self._slots) else {}
            preset = (slot or {}).get("preset", "") or ""
            key = (slot or {}).get("key", "") or ""
            if preset:
                self._preset_by_index[i] = preset
                self._preset_by_name[act.objectName()] = preset
                if key:
                    self._preset_by_key[key] = preset
                act.setText("Magma preset %d (%s)" % (i + 1, preset))
                act.setShortcut(QKeySequence(key) if key else QKeySequence())
            else:
                act.setText("Magma preset slot %d" % (i + 1))
                act.setShortcut(QKeySequence())

    def _make_trigger_logger(self, name):
        def _cb():
            try:
                a = Krita.instance().action(name)
                _log("[trigger] %s shortcut=%s" % (
                    name, a.shortcut().toString() if a else "?"))
            except Exception:
                _log("[trigger] %s" % name)
        return _cb

    def _has_open_document(self):
        try:
            w = Krita.instance().activeWindow()
            return bool(w and w.views() and Krita.instance().activeDocument())
        except Exception:
            return False

    def _set_preset(self, preset_name):
        try:
            window = Krita.instance().activeWindow()
            if not window or not window.views():
                return
            preset = Krita.instance().resources("preset").get(preset_name)
            if not preset:
                _log("[preset] not found: %s" % preset_name)
                return
            act = Krita.instance().action("KritaShape/KisToolBrush")
            if act is not None:
                act.trigger()
            window.views()[0].setCurrentBrushPreset(preset)
            _log("[preset] ok: %s" % preset_name)
        except Exception as exc:  # noqa: BLE001
            _log("[preset] error: %r" % exc)

    def _activate_preset(self):
        sender = self.sender()
        if sender is None:
            return
        preset_name = self._preset_by_name.get(sender.objectName())
        if not preset_name:
            _log("[preset] no mapping for %r" % sender.objectName())
            return
        self._set_preset(preset_name)

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
            try:
                for aname in ("rotate_canvas_left", "rotate_canvas_right",
                              "rotate_canvas_reset", "reset_canvas_rotation",
                              "zoom_to_100pct", "view_zoom_in", "view_zoom_out",
                              "zoom_to_fit"):
                    if aname in self._hooked:
                        continue
                    a = K.action(aname)
                    if a is None:
                        continue
                    a.triggered.connect(self._make_trigger_logger(aname))
                    self._hooked.add(aname)
            except Exception as exc:
                _log("hook error: %r" % exc)
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
