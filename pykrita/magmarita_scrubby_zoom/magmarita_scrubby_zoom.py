# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita Scrubby - hold a key and drag to zoom or rotate the canvas.

* Hold the zoom key (default Z) + drag horizontally  -> zoom, relative to the
  current zoom, remembering the last zoom per document.
* Hold the rotate key (default R) + drag horizontally -> rotate the canvas.

Bundled with MagmaRita: https://github.com/runicmelody/magmarita
"""

import json
import os
import re

from krita import Extension, Krita
from PyQt5.QtCore import QEvent, QObject, Qt, QTimer
from PyQt5.QtGui import QCursor, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QLabel,
    QLineEdit,
    QStatusBar,
    QToolButton,
)

REFERENCE_DPI = 72.0
MIN_SCALE = 0.01     # 1%
MAX_SCALE = 256.0    # 25600%


def _clamp(scale):
    try:
        return max(MIN_SCALE, min(MAX_SCALE, float(scale)))
    except Exception:
        return 1.0


def _diag(msg):
    try:
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        with open(os.path.join(base, "magmarita-diag.log"), "a", encoding="utf-8") as f:
            f.write("[scrubby] " + msg + "\n")
    except Exception:
        pass


def _config(key, default):
    try:
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        with open(os.path.join(base, "krita", "magmarita.json"), encoding="utf-8") as f:
            value = json.load(f).get(key, default)
            return default if value in (None, "") else value
    except Exception:
        return default


def _config_zoom_key():
    return str(_config("zoom_key", "Z"))


def _config_rotate_key():
    return str(_config("rotate_key", "R"))


def _config_zoom_sensitivity():
    try:
        return float(_config("zoom_sensitivity", 150.0))
    except Exception:
        return 150.0


def _config_rotate_sensitivity():
    try:
        return float(_config("rotate_sensitivity", 0.5))
    except Exception:
        return 0.5


class DragFilter(QObject):
    def __init__(self, extension):
        super(DragFilter, self).__init__()
        self.ext = extension

    def eventFilter(self, obj, event):
        if not self.ext.mode_active:
            return False

        t = event.type()

        if t == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.ext.start_drag(self.ext._event_global_pos(event))
                return True

        elif t == QEvent.TabletPress:
            self.ext.start_drag(self.ext._event_global_pos(event))
            return True

        elif t == QEvent.MouseMove:
            if self.ext.is_dragging:
                self.ext.update_drag(self.ext._event_global_pos(event))
                return True

        elif t == QEvent.TabletMove:
            if self.ext.is_dragging:
                self.ext.update_drag(self.ext._event_global_pos(event))
                return True

        elif t == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton and self.ext.is_dragging:
                self.ext.end_drag()
                return True

        elif t == QEvent.TabletRelease:
            if self.ext.is_dragging:
                self.ext.end_drag()
                return True

        elif t == QEvent.KeyRelease:
            if not event.isAutoRepeat():
                self.ext.deactivate()
                return False

        return False


class ScrubbyZoomExtension(Extension):

    def __init__(self, parent):
        super(ScrubbyZoomExtension, self).__init__(parent)

        self.mode_active = False
        self.mode = "zoom"
        self.is_dragging = False

        self.drag_start_x = 0
        self.last_x = 0
        self.active_view = None

        self.current_scale = 1.0
        self.initial_scale = 1.0
        self.rotate_current = 0.0

        self.zoom_sensitivity = 150.0
        self.rotate_sensitivity = 0.5
        self.document_zoom_cache = {}

        self.event_filter = DragFilter(self)
        self.filter_installed = False

        self.zoom_cursor = None
        self._load_cursor()

    def setup(self):
        pass

    # ------------------------------------------------------------------
    def createActions(self, window):
        zoom = window.createAction(
            "scrubby_zoom_activate", "Horizontal Relative Zoom", "tools/scripts")
        zoom.setToolTip("Hold and drag horizontally to zoom relative to the current zoom.")
        zoom.setShortcut(QKeySequence(_config_zoom_key()))
        zoom.triggered.connect(self.activate_zoom_mode)

        rot = window.createAction(
            "scrubby_rotate_activate", "Drag Canvas Rotation", "tools/scripts")
        rot.setToolTip("Hold and drag horizontally to rotate the canvas.")
        rot.setShortcut(QKeySequence(_config_rotate_key()))
        rot.triggered.connect(self.activate_rotate_mode)

        QTimer.singleShot(3000, self._reassert_shortcuts)

    def _reassert_shortcuts(self):
        try:
            for action_id, key in (("scrubby_zoom_activate", _config_zoom_key()),
                                   ("scrubby_rotate_activate", _config_rotate_key())):
                a = Krita.instance().action(action_id)
                if a is not None:
                    a.setShortcut(QKeySequence(key))
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _get_cursor_icon_path(self):
        plugin_dir = os.path.dirname(os.path.realpath(__file__))
        icons_dir = os.path.join(plugin_dir, "Icons")
        available_sizes = [24, 32, 48, 64, 96]
        try:
            screen = QApplication.primaryScreen()
            dpr = screen.devicePixelRatio() if screen else 1.0
        except Exception:
            dpr = 1.0
        target = int(24 * dpr)
        best = available_sizes[-1]
        for size in available_sizes:
            if size >= target:
                best = size
                break
        path = os.path.join(icons_dir, "zoomin" + str(best) + ".png")
        if not os.path.exists(path):
            for size in available_sizes:
                alt = os.path.join(icons_dir, "zoomin" + str(size) + ".png")
                if os.path.exists(alt):
                    path, best = alt, size
                    break
        return path, best, dpr

    def _load_cursor(self):
        try:
            path, icon_size, dpr = self._get_cursor_icon_path()
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    pixmap.setDevicePixelRatio(dpr)
                    hotspot = int(icon_size / (4 * dpr))
                    self.zoom_cursor = QCursor(pixmap, hotspot, hotspot)
                    return
        except Exception:
            pass
        self.zoom_cursor = QCursor(Qt.SizeHorCursor)

    # ------------------------------------------------------------------
    def _has_active_document(self):
        try:
            app = Krita.instance()
            return bool(app and app.activeWindow() and app.activeWindow().activeView()
                        and app.activeDocument())
        except Exception:
            return False

    def _get_current_view(self):
        try:
            app = Krita.instance()
            if app and app.activeWindow():
                return app.activeWindow().activeView()
        except Exception:
            pass
        return None

    def _get_document_id(self):
        try:
            doc = Krita.instance().activeDocument()
            if not doc:
                return None
            fname = doc.fileName()
            return fname if fname else "untitled_" + str(id(doc))
        except Exception:
            return None

    def _event_global_pos(self, event):
        try:
            return event.globalPos()
        except Exception:
            try:
                return event.globalPosF().toPoint()
            except Exception:
                return None

    def _canvas_zoom_raw(self, view):
        try:
            canvas = view.canvas() if view else None
            if canvas:
                return float(canvas.zoomLevel())
        except Exception:
            pass
        return None

    def _current_rotation(self, view):
        try:
            canvas = view.canvas() if view else None
            if canvas:
                return float(canvas.rotation())
        except Exception:
            pass
        return 0.0

    def _current_scale(self, view):
        """Current zoom in the units setZoomLevel() accepts (1.0 == 100%)."""
        raw = self._canvas_zoom_raw(view)
        if raw is not None and raw > 0:
            return _clamp(raw)
        doc_id = self._get_document_id()
        if doc_id and doc_id in self.document_zoom_cache:
            return _clamp(self.document_zoom_cache[doc_id])
        return 1.0

    # ------------------------------------------------------------------
    def _activate(self, mode):
        if not self._has_active_document() or self.mode_active:
            return
        self.mode = mode
        self.mode_active = True
        self.is_dragging = False
        self.active_view = None
        QApplication.setOverrideCursor(self.zoom_cursor)
        if not self.filter_installed:
            QApplication.instance().installEventFilter(self.event_filter)
            self.filter_installed = True

    def activate_zoom_mode(self):
        self._activate("zoom")

    def activate_rotate_mode(self):
        self._activate("rotate")

    def deactivate(self):
        if not self.mode_active:
            return
        self.mode_active = False
        self.is_dragging = False
        self.active_view = None
        try:
            QApplication.restoreOverrideCursor()
        except Exception:
            pass

    # ------------------------------------------------------------------
    def start_drag(self, global_pos):
        if not self._has_active_document() or global_pos is None:
            self.deactivate()
            return

        self.active_view = self._get_current_view()
        self.is_dragging = True
        self.drag_start_x = int(global_pos.x())
        self.last_x = self.drag_start_x

        if self.mode == "rotate":
            self.rotate_sensitivity = _config_rotate_sensitivity()
            self.rotate_current = self._current_rotation(self.active_view)
            _diag("rotate start %.2f deg" % self.rotate_current)
        else:
            self.zoom_sensitivity = _config_zoom_sensitivity()
            self.current_scale = self._current_scale(self.active_view)
            self.initial_scale = self.current_scale
            _diag("zoom start %.5f" % self.current_scale)

    def update_drag(self, global_pos):
        if not self.is_dragging or global_pos is None:
            return
        view = self.active_view
        if not view:
            return
        try:
            canvas = view.canvas()
            if not canvas:
                return
            x = int(global_pos.x())
            dx = x - int(self.last_x)
            self.last_x = x
            dx = max(-300, min(300, dx))

            if self.mode == "rotate":
                self.rotate_current += dx * self.rotate_sensitivity
                angle = self.rotate_current % 360.0
                if angle > 180.0:
                    angle -= 360.0
                canvas.setRotation(angle)
            else:
                factor = 2.0 ** (float(dx) / float(self.zoom_sensitivity))
                self.current_scale = _clamp(float(self.current_scale) * factor)
                canvas.setZoomLevel(self.current_scale)
                doc_id = self._get_document_id()
                if doc_id:
                    self.document_zoom_cache[doc_id] = self.current_scale
        except Exception:
            pass

    def end_drag(self):
        try:
            if self.mode == "rotate":
                _diag("rotate end %.2f deg" % self.rotate_current)
            else:
                _diag("zoom end start=%.5f final=%.5f" % (self.initial_scale, self.current_scale))
        except Exception:
            pass
        self.is_dragging = False
        self.active_view = None
