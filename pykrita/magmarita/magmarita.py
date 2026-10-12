# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita PyKrita plugin.

* Adds a "MagmaRita" entry under Tools > Scripts (apply / restore keymap).
* Provides the Magma tool-preset slots on the number keys (2-6) itself.
* At startup it *applies* the Magma keymap to Krita's actions directly and
  fills in anything Krita's shortcut file did not pick up, then writes a small
  diagnostic log so the mapping can be verified.
"""

import os

from krita import Extension, Krita
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMessageBox

from . import keymap


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
        self._preset_for_action = {}

    def setup(self):
        pass

    def createActions(self, window):
        # --- Magma preset slots on the number keys ---
        for key, preset_name in keymap.PRESET_SLOTS:
            action_name = "magmarita_preset_" + key
            act = window.createAction(
                action_name, "Magma preset %s (%s)" % (key, preset_name))
            act.setToolTip("Activate brush preset: %s" % preset_name)
            act.setShortcut(QKeySequence(key))
            act.triggered.connect(self._activate_preset)
            self._preset_for_action[action_name] = preset_name

        # --- menu actions ---
        self._act_apply = window.createAction("magmarita_apply", "Apply Magma keymap")
        self._act_apply.triggered.connect(self._on_apply)

        self._act_restore = window.createAction(
            "magmarita_restore", "Restore previous shortcuts")
        self._act_restore.triggered.connect(self._on_restore)

        self._act_about = window.createAction("magmarita_about", "About MagmaRita")
        self._act_about.triggered.connect(self._on_about)

        # Apply/repair the keymap once everything has loaded.
        QTimer.singleShot(2500, self._bootstrap)

    # ------------------------------------------------------------------
    # Preset activation
    # ------------------------------------------------------------------
    def _activate_preset(self):
        try:
            sender = self.sender()
            name = self._preset_for_action.get(sender.objectName() if sender else None)
            if not name:
                return
            window = Krita.instance().activeWindow()
            if not window or not window.views():
                return
            view = window.views()[0]
            preset = Krita.instance().resources("preset").get(name)
            if not preset:
                return
            act = Krita.instance().action("KritaShape/KisToolBrush")
            if act is not None:
                act.trigger()
            view.setCurrentBrushPreset(preset)
        except Exception as exc:  # noqa: BLE001
            _log("preset error: %r" % exc)

    # ------------------------------------------------------------------
    # Startup bootstrap
    # ------------------------------------------------------------------
    def _bootstrap(self):
        try:
            filled = []
            changed_own = []
            K = Krita.instance()

            # 1) our own preset actions: enforce their shortcut
            for key, _name in keymap.PRESET_SLOTS:
                act = K.action("magmarita_preset_" + key)
                if act is not None and act.shortcut().toString() != key:
                    act.setShortcut(QKeySequence(key))
                    changed_own.append(key)

            # 2) the bundled scrubby zoom action
            act = K.action("scrubby_zoom_activate")
            if act is not None and act.shortcut().isEmpty():
                act.setShortcut(QKeySequence("Z"))
                filled.append("scrubby_zoom_activate=Z")

            # 3) core Magma shortcuts: only fill in what is missing
            for name, keys in keymap.SHORTCUTS.items():
                act = K.action(name)
                if act is None:
                    filled.append("[missing action] " + name)
                    continue
                if not act.shortcut().isEmpty():
                    continue
                seqs = _sequences(keys)
                if len(seqs) > 1:
                    act.setShortcuts(seqs)
                elif seqs:
                    act.setShortcut(seqs[0])
                filled.append(name + "=" + keys)

            # --- diagnostic dump ---
            _log("=== MagmaRita %s bootstrap ===" % keymap.VERSION)
            for key, _name in keymap.PRESET_SLOTS:
                a = K.action("magmarita_preset_" + key)
                _log("preset %s -> %s" % (key, a.shortcut().toString() if a else "(no action)"))
            a = K.action("scrubby_zoom_activate")
            _log("scrubby_zoom_activate -> %s" % (a.shortcut().toString() if a else "(no action)"))
            for name in keymap.SHORTCUTS:
                a = K.action(name)
                _log("core %s -> %s" % (name, a.shortcut().toString() if a else "(no action)"))
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
            msg = "Magma keymap applied and switched on.\n\nRestart Krita if anything still looks off."
            if made:
                msg += "\n\nBackups:\n" + "\n".join(made)
            QMessageBox.information(None, keymap.APP_NAME, msg)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(None, keymap.APP_NAME, "Could not apply keymap:\n%s" % exc)

    def _on_restore(self):
        try:
            restored = keymap.restore_latest()
            if restored:
                QMessageBox.information(
                    None, keymap.APP_NAME,
                    "Restored:\n" + "\n".join(restored) + "\n\nRestart Krita.")
            else:
                QMessageBox.information(None, keymap.APP_NAME, "No backup found.")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(None, keymap.APP_NAME, "Could not restore:\n%s" % exc)

    def _on_about(self):
        QMessageBox.information(
            None, keymap.APP_NAME,
            "%s %s\nMagma-style keybinds for Krita.\n\n%s"
            % (keymap.APP_NAME, keymap.VERSION, keymap.HOMEPAGE))
