# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita settings dialog.

Compact and scrollable on purpose: the form used to grow taller than the screen,
which pushed the OK/Cancel buttons out of reach so nothing could be saved.
"""

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
    QVBoxLayout,
    QWidget,
)

from krita import Krita

from . import keymap

MAX_DIALOG_HEIGHT = 640
SLOT_COLUMNS = 2


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
        outer.addWidget(QLabel("Keys are pressed in the field; presets can be typed to search.\n"
                               "Everything here is saved to magmarita.json."))

        # --- scrollable body, so the buttons always stay reachable -----------------
        body = QWidget()
        form = QFormLayout(body)
        form.setContentsMargins(0, 0, 0, 0)
        form.setVerticalSpacing(6)
        form.setHorizontalSpacing(12)
        form.setLabelAlignment(int(form.labelAlignment()))

        # preset slots: 2 columns x 5 rows instead of 10 stacked rows
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
            number.setFixedWidth(16)
            key_edit = QKeySequenceEdit()
            key_edit.setMaximumWidth(110)
            key_edit.setKeySequence(QKeySequence(slot.get("key", "") or ""))
            combo = QComboBox()
            combo.setEditable(True)
            combo.setInsertPolicy(QComboBox.NoInsert)
            combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
            combo.setMinimumContentsLength(18)
            combo.addItem("(none)")
            combo.addItems(self.presets)
            current = slot.get("preset", "") or ""
            if current in self.presets:
                combo.setCurrentText(current)
            elif current:
                combo.setCurrentText(current)
            cell.addWidget(number)
            cell.addWidget(key_edit)
            cell.addWidget(combo, 1)
            holder = QWidget()
            holder.setLayout(cell)
            grid.addWidget(holder, i % 5, i // 5)
            self.key_edits.append(key_edit)
            self.combos.append(combo)
        form.addRow("Preset slots", slots_widget)

        self.zoomkey = QKeySequenceEdit()
        self.zoomkey.setMaximumWidth(140)
        self.zoomkey.setKeySequence(QKeySequence(self.cfg.get("zoom_key", "Z") or "Z"))
        form.addRow("Zoom key", self.zoomkey)

        self.rotatekey = QKeySequenceEdit()
        self.rotatekey.setMaximumWidth(140)
        self.rotatekey.setKeySequence(QKeySequence(self.cfg.get("rotate_key", "R") or "R"))
        form.addRow("Rotate key", self.rotatekey)

        self.rotmode = QComboBox()
        self.rotmode.addItem("Around canvas centre", "center")
        self.rotmode.addItem("Horizontal (scrubby)", "scrubby")
        index = self.rotmode.findData(str(self.cfg.get("rotate_mode", "center")))
        if index >= 0:
            self.rotmode.setCurrentIndex(index)
        form.addRow("Rotate mode", self.rotmode)

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

        self.lineassist = QCheckBox("Ctrl = straight line")
        self.lineassist.setChecked(bool(self.cfg.get("line_assist", True)))
        form.addRow("Line assist", self.lineassist)

        self.linetool = QComboBox()
        self.linetool.addItem("Line (hold key, drag)", "KritaShape/KisToolLine")
        self.linetool.addItem("Polyline (chained clicks)", "KisToolPolyline")
        index = self.linetool.findData(str(self.cfg.get("line_tool", "KritaShape/KisToolLine")))
        if index >= 0:
            self.linetool.setCurrentIndex(index)
        form.addRow("Line tool", self.linetool)

        self.hints = QCheckBox("Show key hints on screen")
        self.hints.setChecked(bool(self.cfg.get("key_hints", True)))
        form.addRow("Key hints", self.hints)

        self.enforce = QCheckBox("Re-apply the Magma keymap on every start")
        self.enforce.setChecked(bool(self.cfg.get("enforce_keymap", True)))
        form.addRow("Enforce keymap", self.enforce)

        self.safe = QCheckBox("Safe mode (skip risky config patching)")
        self.safe.setChecked(bool(self.cfg.get("safe_mode", False)))
        form.addRow("Safe mode", self.safe)

        self.diag = QCheckBox("Write a diagnostics log (off by default)")
        self.diag.setChecked(bool(self.cfg.get("diagnostics", False)))
        form.addRow("Diagnostics", self.diag)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)          # pinned below the scroll area, always visible

        # keep the dialog inside the screen
        try:
            screen = QApplication.primaryScreen().availableGeometry()
            width = min(760, int(screen.width() * 0.75))
            height = min(MAX_DIALOG_HEIGHT, int(screen.height() * 0.8))
        except Exception:
            width, height = 760, MAX_DIALOG_HEIGHT
        self.resize(width, height)

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
