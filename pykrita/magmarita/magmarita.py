# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita PyKrita plugin.

Adds a "MagmaRita" entry under Tools > Scripts that installs the Magma-style
keymap (and the tool-preset slots used by Krita's Ten Brushes plugin).
"""

from krita import Extension

try:
    from PyQt5.QtWidgets import QMessageBox
except ImportError:  # Krita 5.3+ may ship Qt6
    from PyQt6.QtWidgets import QMessageBox

from . import keymap


class MagmaRitaExtension(Extension):

    def __init__(self, parent):
        super(MagmaRitaExtension, self).__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        self._act_apply = window.createAction("magmarita_apply", "Apply Magma keymap")
        self._act_apply.setToolTip(
            "Install Magma-style shortcuts and tool presets into Krita."
        )
        self._act_apply.triggered.connect(self._on_apply)

        self._act_restore = window.createAction(
            "magmarita_restore", "Restore previous shortcuts"
        )
        self._act_restore.triggered.connect(self._on_restore)

        self._act_about = window.createAction("magmarita_about", "About MagmaRita")
        self._act_about.triggered.connect(self._on_about)

    def _on_apply(self):
        try:
            made = keymap.apply()
            msg = "Magma keymap applied.\n\nRestart Krita so every shortcut takes effect."
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
                    "Restored:\n" + "\n".join(restored) + "\n\nRestart Krita."
                )
            else:
                QMessageBox.information(None, keymap.APP_NAME, "No backup found.")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(None, keymap.APP_NAME, "Could not restore:\n%s" % exc)

    def _on_about(self):
        QMessageBox.information(
            None, keymap.APP_NAME,
            "%s %s\nMagma-style keybinds for Krita.\n\n%s"
            % (keymap.APP_NAME, keymap.VERSION, keymap.HOMEPAGE)
        )
