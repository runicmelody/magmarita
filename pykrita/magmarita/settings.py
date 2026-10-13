# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita settings dialog: key + brush preset per slot, zoom sensitivity."""

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QCheckBox,
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

        self.rotatekey = QKeySequenceEdit()
        self.rotatekey.setKeySequence(QKeySequence(self.cfg.get("rotate_key", "R") or "R"))
        form.addRow("Rotate key", self.rotatekey)

        self.zoomkey = QKeySequenceEdit()
        self.zoomkey.setKeySequence(QKeySequence(self.cfg.get("zoom_key", "Z") or "Z"))
        form.addRow("Scrubby zoom key", self.zoomkey)

        self.zoom = QDoubleSpinBox()
        self.zoom.setRange(10.0, 2000.0)
        self.zoom.setSingleStep(10.0)
        self.zoom.setValue(float(self.cfg.get("zoom_sensitivity", 150.0)))
        form.addRow("Zoom sensitivity (px per doubling)", self.zoom)

        self.rotzoom = QDoubleSpinBox()
        self.rotzoom.setRange(0.05, 10.0)
        self.rotzoom.setSingleStep(0.1)
        self.rotzoom.setDecimals(2)
        self.rotzoom.setValue(float(self.cfg.get("rotate_sensitivity", 0.5)))
        form.addRow("Rotate sensitivity (deg per px)", self.rotzoom)

        self.rotmode = QComboBox()
        self.rotmode.addItem("Around canvas centre", "center")
        self.rotmode.addItem("Horizontal (scrubby)", "scrubby")
        idx = self.rotmode.findData(str(self.cfg.get("rotate_mode", "center")))
        if idx >= 0:
            self.rotmode.setCurrentIndex(idx)
        form.addRow("Rotate mode", self.rotmode)

        self.lineassist = QCheckBox("Ctrl = straight line")
        self.lineassist.setChecked(bool(self.cfg.get("line_assist", True)))
        form.addRow("Line assist", self.lineassist)

        self.linetool = QComboBox()
        self.linetool.addItem("Line (hold Ctrl, drag)", "KritaShape/KisToolLine")
        self.linetool.addItem("Polyline (chained clicks)", "KisToolPolyline")
        idx = self.linetool.findData(str(self.cfg.get("line_tool", "KritaShape/KisToolLine")))
        if idx >= 0:
            self.linetool.setCurrentIndex(idx)
        form.addRow("Line tool", self.linetool)
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
                "zoom_key": self.zoomkey.keySequence().toString() or "Z",
                "rotate_key": self.rotatekey.keySequence().toString() or "R",
                "zoom_sensitivity": float(self.zoom.value()),
                "rotate_sensitivity": float(self.rotzoom.value()),
                "rotate_mode": self.rotmode.currentData() or "center",
                "line_assist": bool(self.lineassist.isChecked()),
                "line_tool": self.linetool.currentData() or "KritaShape/KisToolLine"}
