# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita Scrubby Zoom - horizontal relative zoom for Krita.

Hold the shortcut ("Z" in MagmaRita), then drag horizontally to zoom
relative to the *current* zoom level.

Bundled with MagmaRita: https://github.com/runicmelody/magmarita

Why this fork exists
--------------------
Krita's libkis has two known quirks:

* Canvas.zoomLevel() goes through zoomManager()->zoom() while
  Canvas.setZoomLevel() goes through zoomController()->setZoom(
  ZOOM_CONSTANT, value).  Depending on the Krita build and the document
  the two can disagree by a document-dependent factor (KDE bug 437068),
  which used to make "scrubby zoom" jump far out or in on the first drag.
* The zoom percentage Krita shows in the status bar is what the user
  actually sees, and it is always in the same units as setZoomLevel().

So this fork:

1. anchors on the real, on-screen zoom percentage (the zoom widget),
2. *learns* the zoomLevel() <-> percent factor and caches it per DPI, so
   the raw API stays usable as a fallback,
3. remembers the last zoom per document, so re-activating always continues
   from where you left off instead of resetting the view.

The action id is kept as "scrubby_zoom_activate" so existing shortcuts keep
working.
"""

import os
import re

from krita import Extension, Krita
from PyQt5.QtCore import QEvent, QObject, Qt
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


class ZoomEventFilter(QObject):
    def __init__(self, extension):
        super(ZoomEventFilter, self).__init__()
        self.ext = extension

    def eventFilter(self, obj, event):
        if not self.ext.zoom_mode_active:
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
                self.ext.update_zoom(self.ext._event_global_pos(event))
                return True

        elif t == QEvent.TabletMove:
            if self.ext.is_dragging:
                self.ext.update_zoom(self.ext._event_global_pos(event))
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
                self.ext.deactivate_zoom_mode()
                return False

        return False


class ScrubbyZoomExtension(Extension):

    def __init__(self, parent):
        super(ScrubbyZoomExtension, self).__init__(parent)

        self.zoom_mode_active = False
        self.is_dragging = False

        self.drag_start_x = 0
        self.last_x = 0
        self.active_view = None

        # Absolute zoom (ZOOM_CONSTANT units, 1.0 == 100%) we track
        self.current_scale = 1.0

        # Learning / remembering
        self.raw_to_scale_factor = {}   # dpi-key -> raw/percent factor
        self.document_zoom_cache = {}   # doc id -> last known scale

        self.zoom_sensitivity = 150.0

        self.event_filter = ZoomEventFilter(self)
        self.filter_installed = False

        self.zoom_cursor = None
        self._load_cursor()

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction(
            "scrubby_zoom_activate",
            "Horizontal Relative Zoom",
            "tools/scripts",
        )
        action.setToolTip("Hold and drag horizontally to zoom relative to the current zoom.")
        action.setShortcut(QKeySequence("Z"))
        action.triggered.connect(self.activate_zoom_mode)

    # ------------------------------------------------------------------
    # Cursor
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

        target_physical_size = int(24 * dpr)
        best_size = available_sizes[-1]
        for size in available_sizes:
            if size >= target_physical_size:
                best_size = size
                break

        cursor_path = os.path.join(icons_dir, "zoomin" + str(best_size) + ".png")
        if not os.path.exists(cursor_path):
            for size in available_sizes:
                fallback_path = os.path.join(icons_dir, "zoomin" + str(size) + ".png")
                if os.path.exists(fallback_path):
                    cursor_path = fallback_path
                    best_size = size
                    break

        return cursor_path, best_size, dpr

    def _load_cursor(self):
        try:
            cursor_path, icon_size, dpr = self._get_cursor_icon_path()
            if os.path.exists(cursor_path):
                pixmap = QPixmap(cursor_path)
                if not pixmap.isNull():
                    pixmap.setDevicePixelRatio(dpr)
                    hotspot = int(icon_size / (4 * dpr))
                    self.zoom_cursor = QCursor(pixmap, hotspot, hotspot)
                    return
        except Exception:
            pass
        self.zoom_cursor = QCursor(Qt.SizeHorCursor)

    # ------------------------------------------------------------------
    # Small helpers
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
            if fname:
                return fname
            return "untitled_" + str(id(doc))
        except Exception:
            return None

    def _doc_dpi(self, view):
        try:
            doc = view.document() if view else None
            if doc:
                dpi = float(doc.resolution())
                if dpi > 0:
                    return dpi
        except Exception:
            pass
        return REFERENCE_DPI

    def _dpi_key(self, view):
        return round(self._doc_dpi(view), 3)

    def _event_global_pos(self, event):
        try:
            return event.globalPos()
        except Exception:
            try:
                return event.globalPosF().toPoint()
            except Exception:
                return None

    # ------------------------------------------------------------------
    # Reading the real zoom (the fix)
    # ------------------------------------------------------------------
    def _percent_widgets(self):
        """Widgets that may show the zoom percentage (strict, then status bar)."""
        out = []
        try:
            win = Krita.instance().activeWindow()
            qwin = win.qwindow() if win else None
            if not qwin:
                return out

            named = []
            for w in qwin.findChildren((QComboBox, QLineEdit, QToolButton, QLabel)):
                try:
                    obj = (w.objectName() or "").lower()
                    acc = (w.accessibleName() or "").lower()
                    if "zoom" in obj or "zoom" in acc:
                        named.append(w)
                except Exception:
                    continue
            if named:
                return named

            bar = qwin.findChild(QStatusBar)
            if bar:
                out = bar.findChildren((QComboBox, QLineEdit, QToolButton, QLabel))
        except Exception:
            pass
        return out

    @staticmethod
    def _read_percent(widget):
        try:
            if isinstance(widget, QComboBox):
                text = widget.currentText()
            elif isinstance(widget, QLineEdit):
                text = widget.text()
            else:
                text = widget.text()
        except Exception:
            return None
        if not text:
            return None
        m = re.match(r"^\s*([\d.]+)\s*%\s*$", str(text))
        if not m:
            return None
        try:
            return float(m.group(1)) / 100.0
        except Exception:
            return None

    def _zoom_scale_from_ui(self):
        for w in self._percent_widgets():
            val = self._read_percent(w)
            if val is not None and MIN_SCALE <= val <= MAX_SCALE:
                return val
        return None

    def _canvas_zoom_raw(self, view):
        try:
            canvas = view.canvas() if view else None
            if canvas:
                return float(canvas.zoomLevel())
        except Exception:
            pass
        return None

    def _current_scale(self, view):
        """Best estimate of the current zoom in ZOOM_CONSTANT units."""
        ui = self._zoom_scale_from_ui()
        raw = self._canvas_zoom_raw(view)
        dpi_key = self._dpi_key(view)
        doc_id = self._get_document_id()

        # 1) The percentage Krita shows is the ground truth.
        if ui is not None:
            if raw is not None and raw > 0:
                self.raw_to_scale_factor[dpi_key] = raw / ui
            return _clamp(ui)

        # 2) Fall back to the raw canvas value, corrected with a learned
        #    factor (or the documented dpi/72 relation on first use).
        if raw is not None and raw > 0:
            factor = self.raw_to_scale_factor.get(dpi_key)
            if factor is None:
                factor = max(self._doc_dpi(view) / REFERENCE_DPI, 1e-3)
                self.raw_to_scale_factor[dpi_key] = factor
            candidate = raw / factor
            remembered = self.document_zoom_cache.get(doc_id) if doc_id else None
            if remembered and (candidate > remembered * 8.0 or candidate < remembered / 8.0):
                return _clamp(remembered)
            return _clamp(candidate)

        # 3) Last resort: what we last set for this document.
        if doc_id and doc_id in self.document_zoom_cache:
            return _clamp(self.document_zoom_cache[doc_id])

        return 1.0

    # ------------------------------------------------------------------
    # Mode lifecycle
    # ------------------------------------------------------------------
    def activate_zoom_mode(self):
        if not self._has_active_document() or self.zoom_mode_active:
            return

        self.zoom_mode_active = True
        self.is_dragging = False
        self.active_view = None

        QApplication.setOverrideCursor(self.zoom_cursor)

        if not self.filter_installed:
            QApplication.instance().installEventFilter(self.event_filter)
            self.filter_installed = True

    def deactivate_zoom_mode(self):
        if not self.zoom_mode_active:
            return

        self.zoom_mode_active = False
        self.is_dragging = False
        self.active_view = None

        try:
            QApplication.restoreOverrideCursor()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Drag + zoom
    # ------------------------------------------------------------------
    def start_drag(self, global_pos):
        if not self._has_active_document() or global_pos is None:
            self.deactivate_zoom_mode()
            return

        self.active_view = self._get_current_view()
        self.is_dragging = True
        self.drag_start_x = int(global_pos.x())
        self.last_x = self.drag_start_x

        self.current_scale = self._current_scale(self.active_view)

        doc_id = self._get_document_id()
        if doc_id:
            self.document_zoom_cache[doc_id] = self.current_scale

    def update_zoom(self, global_pos):
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
            delta_x = x - int(self.last_x)
            self.last_x = x

            # Relative, exponential zoom from the *current* value.
            factor = 2.0 ** (float(delta_x) / float(self.zoom_sensitivity))
            self.current_scale = _clamp(float(self.current_scale) * factor)

            canvas.setZoomLevel(self.current_scale)

            doc_id = self._get_document_id()
            if doc_id:
                self.document_zoom_cache[doc_id] = self.current_scale
        except Exception:
            pass

    def end_drag(self):
        self.is_dragging = False
        self.active_view = None
