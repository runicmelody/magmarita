# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita settings dialog: key + brush preset per slot, zoom sensitivity."""

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from krita import Krita

from . import keymap


class MagmaRitaSettings(QDialog):

    def __init__(self, parent=None):
        super(MagmaRitaSettings, self).__init__(parent)
        self.setWindowTitle("MagmaRita settings")
        self.resize(520, 420)

        self.cfg = keymap.load_config()
        try:
            self.presets = sorted(Krita.instance().resources("preset").keys())
        except Exception:
            self.presets = []

        slots = list(self.cfg.get("slots", []))
        while len(slots) < 10:
            slots.append({"key": "", "preset": ""})

        outer = QVBoxLayout(self)
        outer.addWidget(QLabel("Assign a brush preset and a key to each slot.\n"
                               "Digits 1-6 are the Magma default."))
        form = QFormLayout()
        self.key_edits = []
        self.combos = []
        for i in range(10):
            slot = slots[i] or {}
            ke = QKeySequenceEdit()
            ke.setKeySequence(QKeySequence(slot.get("key", "") or ""))
            cb = QComboBox()
            cb.addItem("(none)")
            cb.addItems(self.presets)
            cur = slot.get("preset", "") or ""
            if cur in self.presets:
                cb.setCurrentText(cur)
            row = QHBoxLayout()
            row.addWidget(ke)
            row.addWidget(cb)
            holder = QWidget()
            holder.setLayout(row)
            form.addRow("Slot %d" % (i + 1), holder)
            self.key_edits.append(ke)
            self.combos.append(cb)

        self.zoomkey = QKeySequenceEdit()
        self.zoomkey.setKeySequence(QKeySequence(self.cfg.get("zoom_key", "H") or "H"))
        form.addRow("Scrubby zoom key", self.zoomkey)

        self.zoom = QDoubleSpinBox()
        self.zoom.setRange(10.0, 2000.0)
        self.zoom.setSingleStep(10.0)
        self.zoom.setValue(float(self.cfg.get("zoom_sensitivity", 150.0)))
        form.addRow("Zoom sensitivity (px per doubling)", self.zoom)
        outer.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

    def result_config(self):
        slots = []
        for ke, cb in zip(self.key_edits, self.combos):
            key = ke.keySequence().toString()
            preset = cb.currentText() if cb.currentIndex() > 0 else ""
            slots.append({"key": key, "preset": preset})
        return {"version": 1, "slots": slots,
                "zoom_key": self.zoomkey.keySequence().toString() or "H",
                "zoom_sensitivity": float(self.zoom.value())}
