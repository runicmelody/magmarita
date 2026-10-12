# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita palette - a small Magma-style docker.

Quick tool buttons, the ten brush-preset slots (click to activate, right-click
to rebind), brush size / opacity sliders, and shortcuts to Settings / Apply.
"""

from krita import DockWidget, Krita
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QPushButton,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import keymap

try:
    from .magmarita import get_extension
except Exception:
    def get_extension():
        return None


class _PresetPicker(QDialog):
    def __init__(self, parent=None, current=""):
        super(_PresetPicker, self).__init__(parent)
        self.setWindowTitle("Choose brush preset")
        self.resize(340, 440)
        lay = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search presets...")
        lay.addWidget(self.search)
        self.list = QListWidget()
        lay.addWidget(self.list)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)
        try:
            self._names = sorted(Krita.instance().resources("preset").keys())
        except Exception:
            self._names = []
        self._fill()
        self.search.textChanged.connect(self._fill)
        self.list.itemDoubleClicked.connect(lambda _item: self.accept())

    def _fill(self):
        q = (self.search.text() or "").lower()
        self.list.clear()
        for name in self._names:
            if q in name.lower():
                self.list.addItem(name)

    def chosen(self):
        item = self.list.currentItem()
        return item.text() if item else ""


class _KeyPicker(QDialog):
    def __init__(self, parent=None, current=""):
        super(_KeyPicker, self).__init__(parent)
        self.setWindowTitle("Assign key")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Press the key for this slot:"))
        self.edit = QKeySequenceEdit()
        self.edit.setKeySequence(QKeySequence(current or ""))
        lay.addWidget(self.edit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def value(self):
        return self.edit.keySequence().toString()


class MagmaRitaDocker(DockWidget):

    def __init__(self):
        super(MagmaRitaDocker, self).__init__()
        self.setWindowTitle("MagmaRita")
        self.slots = []
        self._slot_buttons = []

        root = QWidget()
        lay = QVBoxLayout(root)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(6)

        tools = QGridLayout()
        tools.setSpacing(3)
        for i, (label, action_id) in enumerate(keymap.TOOL_BUTTONS):
            b = QToolButton()
            b.setText(label)
            b.setToolTip(action_id)
            b.clicked.connect(lambda _checked=False, a=action_id: self._trigger(a))
            tools.addWidget(b, i // 3, i % 3)
        lay.addLayout(tools)

        self.slots_grid = QGridLayout()
        self.slots_grid.setSpacing(4)
        lay.addLayout(self.slots_grid)

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 2000)
        self.size_slider.valueChanged.connect(self._on_size)
        self.size_label = QLabel("Size")
        row = QHBoxLayout()
        row.addWidget(self.size_label)
        row.addWidget(self.size_slider)
        lay.addLayout(row)

        self.op_slider = QSlider(Qt.Horizontal)
        self.op_slider.setRange(0, 100)
        self.op_slider.valueChanged.connect(self._on_opacity)
        self.op_label = QLabel("Opacity")
        row2 = QHBoxLayout()
        row2.addWidget(self.op_label)
        row2.addWidget(self.op_slider)
        lay.addLayout(row2)

        brow = QHBoxLayout()
        b1 = QPushButton("Settings...")
        b1.clicked.connect(self._open_settings)
        b2 = QPushButton("Apply keymap")
        b2.clicked.connect(self._apply_keymap)
        brow.addWidget(b1)
        brow.addWidget(b2)
        lay.addLayout(brow)

        lay.addStretch(1)
        self.setWidget(root)
        self._load()
        self.rebuild()

    # ------------------------------------------------------------------
    def canvasChanged(self, canvas):
        self.refresh_brush()

    def _view(self):
        try:
            w = Krita.instance().activeWindow()
            if w and w.views():
                return w.views()[0]
        except Exception:
            pass
        return None

    def _load(self):
        try:
            self.cfg = keymap.load_config()
            self.slots = list(self.cfg.get("slots", []))
        except Exception:
            self.cfg = {"slots": [], "zoom_sensitivity": 150.0}
            self.slots = []
        while len(self.slots) < 10:
            self.slots.append({"key": "", "preset": ""})

    def _save(self):
        try:
            self.cfg["slots"] = self.slots
            keymap.save_config(self.cfg)
        except Exception:
            pass
        ext = get_extension()
        if ext is not None:
            try:
                ext.reload_config()
            except Exception:
                pass

    def rebuild(self):
        while self.slots_grid.count():
            item = self.slots_grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._slot_buttons = []
        try:
            presets = Krita.instance().resources("preset")
        except Exception:
            presets = {}
        for i, slot in enumerate(self.slots[:10]):
            preset = (slot or {}).get("preset", "") or ""
            key = (slot or {}).get("key", "") or ""
            b = QToolButton()
            b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            b.setMinimumWidth(64)
            b.setText("%s\n%s" % (key or "-", (preset or "(empty)")[:14]))
            b.setToolTip(preset or "(empty slot)")
            if preset and preset in presets:
                try:
                    img = presets[preset].image()
                    if img is not None:
                        b.setIcon(QIcon(QPixmap.fromImage(img)))
                        b.setIconSize(QPixmap.fromImage(img).size().scaled(40, 40, Qt.KeepAspectRatio))
                except Exception:
                    pass
            b.clicked.connect(lambda _checked=False, s=slot: self._activate(s))
            b.setContextMenuPolicy(Qt.CustomContextMenu)
            b.customContextMenuRequested.connect(
                lambda _pos, idx=i: self._slot_menu(idx))
            self.slots_grid.addWidget(b, i // 5, i % 5)
            self._slot_buttons.append(b)
        self.refresh_brush()

    def refresh_brush(self):
        view = self._view()
        if view is None:
            return
        try:
            self.size_slider.blockSignals(True)
            self.size_slider.setValue(int(view.brushSize()))
            self.size_slider.blockSignals(False)
            self.op_slider.blockSignals(True)
            self.op_slider.setValue(int(round(view.paintingOpacity() * 100.0)))
            self.op_slider.blockSignals(False)
            preset = view.currentBrushPreset()
            self.size_label.setText("Size" if preset is None else ("Size - " + preset.name()[:12]))
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _trigger(self, action_id):
        try:
            a = Krita.instance().action(action_id)
            if a is not None:
                a.trigger()
        except Exception:
            pass

    def _activate(self, slot):
        preset = (slot or {}).get("preset", "") or ""
        if not preset:
            return
        ext = get_extension()
        if ext is not None:
            try:
                ext._set_preset(preset)
                return
            except Exception:
                pass
        try:
            view = self._view()
            presets = Krita.instance().resources("preset")
            if view is not None and preset in presets:
                view.setCurrentBrushPreset(presets[preset])
        except Exception:
            pass

    def _slot_menu(self, index):
        try:
            menu = QMenu(self)
            act = menu.addAction("Activate")
            assign_preset = menu.addAction("Assign preset...")
            assign_key = menu.addAction("Assign key...")
            clear = menu.addAction("Clear slot")
            chosen = menu.exec_(self.cursor().pos())
            if chosen is None:
                return
            if chosen is act:
                self._activate(self.slots[index])
            elif chosen is assign_preset:
                dlg = _PresetPicker(self, (self.slots[index] or {}).get("preset", ""))
                exec_fn = getattr(dlg, "exec_", None) or dlg.exec
                if exec_fn():
                    self.slots[index]["preset"] = dlg.chosen()
                    self._save()
                    self.rebuild()
            elif chosen is assign_key:
                dlg = _KeyPicker(self, (self.slots[index] or {}).get("key", ""))
                exec_fn = getattr(dlg, "exec_", None) or dlg.exec
                if exec_fn():
                    self.slots[index]["key"] = dlg.value()
                    self._save()
                    self.rebuild()
            elif chosen is clear:
                self.slots[index] = {"key": "", "preset": ""}
                self._save()
                self.rebuild()
        except Exception:
            pass

    def _on_size(self, value):
        view = self._view()
        if view is not None:
            try:
                view.setBrushSize(float(value))
            except Exception:
                pass

    def _on_opacity(self, value):
        view = self._view()
        if view is not None:
            try:
                view.setPaintingOpacity(float(value) / 100.0)
            except Exception:
                pass

    def _open_settings(self):
        try:
            from .magmarita_settings import MagmaRitaSettings
            dlg = MagmaRitaSettings(self)
            exec_fn = getattr(dlg, "exec_", None) or dlg.exec
            if exec_fn():
                keymap.save_config(dlg.result_config())
                self._load()
                self._save()
                self.rebuild()
        except Exception:
            pass

    def _apply_keymap(self):
        try:
            keymap.apply()
        except Exception:
            pass
