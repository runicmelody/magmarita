# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita settings dialog.

Kept compact and scrollable on purpose: the form used to grow taller *and* wider
than the screen, which pushed OK/Cancel out of reach so nothing could be saved.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from krita import Krita

from . import keymap

MAX_DIALOG_HEIGHT = 620
SLOT_ROWS = 5

FIELD_MIN_WIDTH = 120
COMBO_MAX_WIDTH = 220


def _combo(items, current=None):
    """A combo box that never forces the dialog to be wide."""
    box = QComboBox()
    box.setEditable(True)
    box.setInsertPolicy(QComboBox.NoInsert)
    box.setMinimumContentsLength(10)
    box.setMinimumWidth(FIELD_MIN_WIDTH)
    box.setMaximumWidth(COMBO_MAX_WIDTH)
    box.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
    box.addItem("(none)")
    for item in items:
        box.addItem(item)
    if current:
        box.setCurrentText(current)
    return box


class MagmaRitaSettings(QDialog):

    def __init__(self, parent=None):
        super(MagmaRitaSettings, self).__init__(parent)
        self.setWindowTitle("MagmaRita settings")
        self.setSizeGripEnabled(True)

        self.cfg = keymap.load_config()
        try:
            self.presets = sorted(Krita.instance().resources("preset").keys())
        except Exception:
            self.presets = []

        slots = list(self.cfg.get("slots", []))
        while len(slots) < 10:
            slots.append({"key": "", "preset": ""})

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(8)

        hint = QLabel("Press a key in the field. Preset boxes are searchable.\n"
                      "Everything is saved to magmarita.json.")
        hint.setWordWrap(True)
        outer.addWidget(hint)

        body = QWidget()
        form = QFormLayout(body)
        form.setContentsMargins(0, 0, 0, 0)
        form.setVerticalSpacing(6)
        form.setHorizontalSpacing(10)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # preset slots: 5 rows x 2 columns, compact fields
        slots_widget = QWidget()
        grid = QGridLayout(slots_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(4)
        self.key_edits = []
        self.combos = []
        for i in range(10):
            slot = slots[i] or {}
            cell = QHBoxLayout()
            cell.setSpacing(4)
            number = QLabel("%d" % (i + 1))
            number.setFixedWidth(14)
            key_edit = QKeySequenceEdit()
            key_edit.setMinimumWidth(58)
            key_edit.setMaximumWidth(80)
            key_edit.setKeySequence(QKeySequence(slot.get("key", "") or ""))
            combo = _combo(self.presets, (slot.get("preset", "") or "") or None)
            cell.addWidget(number)
            cell.addWidget(key_edit)
            cell.addWidget(combo, 1)
            holder = QWidget()
            holder.setLayout(cell)
            grid.addWidget(holder, i % SLOT_ROWS, i // SLOT_ROWS)
            self.key_edits.append(key_edit)
            self.combos.append(combo)
            grid.setColumnStretch(i // SLOT_ROWS, 1)
        form.addRow("Slots", slots_widget)

        self.zoomkey = QKeySequenceEdit()
        self.zoomkey.setMaximumWidth(120)
        self.zoomkey.setKeySequence(QKeySequence(self.cfg.get("zoom_key", "Z") or "Z"))
        form.addRow("Zoom key", self.zoomkey)

        self.rotatekey = QKeySequenceEdit()
        self.rotatekey.setMaximumWidth(120)
        self.rotatekey.setKeySequence(QKeySequence(self.cfg.get("rotate_key", "R") or "R"))
        form.addRow("Rotate key", self.rotatekey)

        self.rotmode = _combo(["Around canvas centre", "Horizontal (scrubby)"])
        self.rotmode.setEditable(False)
        data = [("center", "Around canvas centre"), ("scrubby", "Horizontal (scrubby)")]
        self.rotmode.clear()
        for value, label in data:
            self.rotmode.addItem(label, value)
        for i, (value, _label) in enumerate(data):
            if value == str(self.cfg.get("rotate_mode", "center")):
                self.rotmode.setCurrentIndex(i)
        form.addRow("Rotate mode", self.rotmode)

        self.zoom = QDoubleSpinBox()
        self.zoom.setRange(10.0, 2000.0)
        self.zoom.setSingleStep(10.0)
        self.zoom.setValue(float(self.cfg.get("zoom_sensitivity", 150.0)))
        self.zoom.setMaximumWidth(140)
        form.addRow("Zoom sens. (px/double)", self.zoom)

        self.rotzoom = QDoubleSpinBox()
        self.rotzoom.setRange(0.05, 10.0)
        self.rotzoom.setSingleStep(0.1)
        self.rotzoom.setDecimals(2)
        self.rotzoom.setValue(float(self.cfg.get("rotate_sensitivity", 0.5)))
        self.rotzoom.setMaximumWidth(140)
        form.addRow("Rotate sens. (deg/px)", self.rotzoom)

        self.lineassist = QCheckBox("Ctrl = straight line")
        self.lineassist.setChecked(bool(self.cfg.get("line_assist", True)))
        form.addRow("Line assist", self.lineassist)

        self.linetool = QComboBox()
        self.linetool.setEditable(False)
        self.linetool.addItem("Line (drag)", "KritaShape/KisToolLine")
        self.linetool.addItem("Polyline", "KisToolPolyline")
        self.linetool.setMaximumWidth(200)
        index = self.linetool.findData(str(self.cfg.get("line_tool", "KritaShape/KisToolLine")))
        if index >= 0:
            self.linetool.setCurrentIndex(index)
        form.addRow("Line tool", self.linetool)

        self.hints = QCheckBox("Flash hints on canvas")
        self.hints.setChecked(bool(self.cfg.get("key_hints", True)))
        form.addRow("Key hints", self.hints)

        self.enforce = QCheckBox("Re-apply keymap on start")
        self.enforce.setChecked(bool(self.cfg.get("enforce_keymap", True)))
        form.addRow("Enforce", self.enforce)

        self.safe = QCheckBox("Skip risky patches")
        self.safe.setChecked(bool(self.cfg.get("safe_mode", False)))
        form.addRow("Safe mode", self.safe)

        self.diag = QCheckBox("Write a log (off)")
        self.diag.setChecked(bool(self.cfg.get("diagnostics", False)))
        form.addRow("Diagnostics", self.diag)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

        try:
            screen = QApplication.primaryScreen().availableGeometry()
            self.resize(min(680, int(screen.width() * 0.9)),
                        min(MAX_DIALOG_HEIGHT, int(screen.height() * 0.85)))
        except Exception:
            self.resize(680, MAX_DIALOG_HEIGHT)

    def result_config(self):
        slots = []
        for key_edit, combo in zip(self.key_edits, self.combos):
            key = key_edit.keySequence().toString()
            preset = (combo.currentText() or "").strip()
            if preset == "(none)":
                preset = ""
            slots.append({"key": key, "preset": preset})
        return {
            "version": 1,
            "slots": slots,
            "zoom_key": self.zoomkey.keySequence().toString() or "Z",
            "rotate_key": self.rotatekey.keySequence().toString() or "R",
            "zoom_sensitivity": float(self.zoom.value()),
            "rotate_sensitivity": float(self.rotzoom.value()),
            "rotate_mode": self.rotmode.currentData() or "center",
            "line_assist": bool(self.lineassist.isChecked()),
            "line_tool": self.linetool.currentData() or "KritaShape/KisToolLine",
            "key_hints": bool(self.hints.isChecked()),
            "enforce_keymap": bool(self.enforce.isChecked()),
            "safe_mode": bool(self.safe.isChecked()),
            "diagnostics": bool(self.diag.isChecked()),
        }
