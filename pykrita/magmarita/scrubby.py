# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita: hold a key and drag to zoom or rotate the canvas.

Idea credit: "hold a key and drag horizontally to zoom" is the interaction
popularised by the Scrubby Zoom plugin (github.com/10zindraws/Scrubby-Zoom).
The code below is an independent implementation written for MagmaRita; nothing
is copied from that project (which publishes no licence file).

* hold the zoom key (default Z) and drag horizontally -> zoom, relative to the
  current zoom level (remembered per document)
* hold the rotate key (default R) and drag in a circle -> rotate the canvas
  around its centre
"""

import json
import math
import os
import sys

from krita import Extension, Krita
from PyQt5.QtCore import QEvent, QObject, Qt, QTimer
from PyQt5.QtGui import QCursor, QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import QApplication

ZOOM_ACTION = "scrubby_zoom_activate"
ROTATE_ACTION = "scrubby_rotate_activate"

MIN_ZOOM = 0.01
MAX_ZOOM = 256.0
DEFAULT_PIXELS_PER_STEP = 150.0
DEFAULT_DEGREES_PER_PIXEL = 0.5
PIVOT_DEAD_ZONE = 20.0
MAX_STEP_PIXELS = 300
SUPPORTED_KRITA = ("5.2", "5.3")


def _krita_dirs():
    """(resource dir, config dir) - mirrors keymap.py, sandboxes included."""
    home = os.path.expanduser("~")
    if os.name == "nt":
        resource = os.path.join(os.environ.get("APPDATA", home), "krita")
        config = os.environ.get("LOCALAPPDATA", home)
    elif sys.platform == "darwin":
        resource = os.path.join(home, "Library", "Application Support", "krita")
        config = os.path.join(home, "Library", "Preferences")
    else:
        resource = config = None
        for sandbox_resource, sandbox_config in (
                (os.path.join(home, ".var", "app", "org.kde.krita", "data", "krita"),
                 os.path.join(home, ".var", "app", "org.kde.krita", "config")),
                (os.path.join(home, "snap", "krita", "current", ".local", "share", "krita"),
                 os.path.join(home, "snap", "krita", "current", ".config"))):
            if os.path.isdir(sandbox_resource) or os.path.isdir(sandbox_config):
                resource, config = sandbox_resource, sandbox_config
                break
        if resource is None:
            resource = os.path.join(
                os.environ.get("XDG_DATA_HOME") or os.path.join(home, ".local", "share"), "krita")
            config = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
    return (os.environ.get("MAGMARITA_RESOURCE_DIR", resource),
            os.environ.get("MAGMARITA_CONFIG_DIR", config))


def _config():
    try:
        with open(os.path.join(_krita_dirs()[0], "magmarita.json"), encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def _bound(value, low, high):
    try:
        return max(low, min(high, float(value)))
    except Exception:
        return low


def _trace(message):
    if not _config().get("diagnostics", False):
        return
    try:
        with open(os.path.join(_krita_dirs()[0], "magmarita-diag.log"), "a", encoding="utf-8") as handle:
            handle.write("[scrubby] " + message + "\n")
    except Exception:
        pass


def _krita_supported():
    try:
        parts = str(Krita.instance().version()).split(".")
        return ".".join(parts[:2]) in SUPPORTED_KRITA
    except Exception:
        return True


class _DragWatch(QObject):
    """App-wide watcher, active only while a scrubby key is held down."""

    def __init__(self, owner):
        super(_DragWatch, self).__init__()
        self.owner = owner

    def eventFilter(self, widget, event):
        if not self.owner.armed:
            return False
        kind = event.type()
        if kind == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self.owner.press(self._pos(event))
            return True
        if kind == QEvent.TabletPress:
            self.owner.press(self._pos(event))
            return True
        if kind in (QEvent.MouseMove, QEvent.TabletMove) and self.owner.dragging:
            self.owner.move(self._pos(event))
            return True
        if kind == QEvent.MouseButtonRelease and self.owner.dragging:
            self.owner.release()
            return True
        if kind == QEvent.TabletRelease and self.owner.dragging:
            self.owner.release()
            return True
        if kind == QEvent.KeyRelease and not event.isAutoRepeat():
            self.owner.disarm()
        return False

    @staticmethod
    def _pos(event):
        for attr in ("globalPos", "globalPosF"):
            try:
                value = getattr(event, attr)()
                return value.toPoint() if hasattr(value, "toPoint") else value
            except Exception:
                continue
        return None


class ScrubbyZoomExtension(Extension):

    def __init__(self, parent):
        super(ScrubbyZoomExtension, self).__init__(parent)
        self.settings = _config()
        self.armed = False
        self.dragging = False
        self.task = "zoom"
        self.last_x = 0
        self.zoom = 1.0
        self.angle = 0.0
        self.pivot = None
        self.pivot_angle = None
        self.zoom_memory = {}
        self.watch = _DragWatch(self)
        self.watching = False
        self.pointer = self._pointer()

    def setup(self):
        pass

    # ------------------------------------------------------------------
    def createActions(self, window):
        for action_id, text, tip, key in (
            (ZOOM_ACTION, "Horizontal Relative Zoom",
             "Hold and drag horizontally to zoom relative to the current zoom.",
             str(self.settings.get("zoom_key", "Z") or "Z")),
            (ROTATE_ACTION, "Drag Canvas Rotation",
             "Hold and drag in a circle to rotate the canvas around its centre.",
             str(self.settings.get("rotate_key", "R") or "R")),
        ):
            action = window.createAction(action_id, text, "tools/scripts")
            action.setToolTip(tip)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(
                lambda _checked=False, t=("rotate" if action_id == ROTATE_ACTION else "zoom"):
                self.arm(t))
        QTimer.singleShot(3000, self.reassert_shortcuts)

    def reassert_shortcuts(self):
        for action_id, name in ((ZOOM_ACTION, "zoom_key"), (ROTATE_ACTION, "rotate_key")):
            key = str(self.settings.get(name, "Z" if name == "zoom_key" else "R"))
            try:
                action = Krita.instance().action(action_id)
                if action is not None:
                    action.setShortcut(QKeySequence(key))
            except Exception:
                pass

    def _pointer(self):
        try:
            folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Icons")
            for size in (48, 32, 64, 24, 96):
                path = os.path.join(folder, "zoomin%d.png" % size)
                if os.path.exists(path):
                    pixmap = QPixmap(path)
                    if not pixmap.isNull():
                        return QCursor(pixmap, 8, 8)
        except Exception:
            pass
        return QCursor(Qt.SizeHorCursor)

    # ------------------------------------------------------------------
    def view(self):
        try:
            window = Krita.instance().activeWindow()
            if window and window.views() and Krita.instance().activeDocument():
                return window.views()[0]
        except Exception:
            pass
        return None

    def document_key(self):
        try:
            document = Krita.instance().activeDocument()
            if document:
                return document.fileName() or ("untitled_%d" % id(document))
        except Exception:
            pass
        return None

    def _flash(self, text):
        if not self.settings.get("key_hints", True):
            return
        try:
            window = Krita.instance().activeWindow()
            if window and window.views():
                window.views()[0].showFloatingMessage(text, QIcon(), 1200, 1)
        except Exception:
            pass

    def arm(self, task):
        if self.armed or self.view() is None:
            return
        if self.settings.get("safe_mode", False) or not _krita_supported():
            self._flash("Scrubby: safe mode - nothing changed")
            return
        self.armed = True
        self.task = task
        if not self.watching:
            QApplication.instance().installEventFilter(self.watch)
            self.watching = True
        QApplication.setOverrideCursor(self.pointer)
        self._flash("Zoom: hold and drag" if task == "zoom" else "Rotate: drag in a circle")

    def disarm(self):
        if not self.armed:
            return
        self.armed = False
        self.dragging = False
        try:
            QApplication.restoreOverrideCursor()
        except Exception:
            pass

    # ------------------------------------------------------------------
    def press(self, pos):
        view = self.view()
        if view is None or pos is None:
            self.disarm()
            return
        canvas = view.canvas()
        self.dragging = True
        self.last_x = int(pos.x())
        if self.task == "rotate":
            try:
                self.angle = float(canvas.rotation())
            except Exception:
                self.angle = 0.0
            self.pivot = self._centre()
            self.pivot_angle = self._angle(pos)
            _trace("rotate begin %.2f" % self.angle)
        else:
            try:
                self.zoom = _bound(canvas.zoomLevel(), MIN_ZOOM, MAX_ZOOM) or 1.0
            except Exception:
                self.zoom = 1.0
            key = self.document_key()
            if key in self.zoom_memory:
                self.zoom = self.zoom_memory[key]
            _trace("zoom begin %.5f" % self.zoom)

    def move(self, pos):
        view = self.view()
        if view is None or pos is None:
            return
        canvas = view.canvas()
        x = int(pos.x())
        dx = max(-MAX_STEP_PIXELS, min(MAX_STEP_PIXELS, x - self.last_x))
        self.last_x = x
        try:
            if self.task == "rotate":
                delta = None
                if self.pivot is not None:
                    now = self._angle(pos)
                    if now is not None and self.pivot_angle is not None:
                        delta = now - self.pivot_angle
                        while delta > 180.0:
                            delta -= 360.0
                        while delta < -180.0:
                            delta += 360.0
                        self.pivot_angle = now
                if delta is None:
                    per_pixel = float(self.settings.get("rotate_sensitivity", DEFAULT_DEGREES_PER_PIXEL))
                    delta = dx * per_pixel
                self.angle += delta
                shown = self.angle % 360.0
                canvas.setRotation(shown - 360.0 if shown > 180.0 else shown)
            else:
                per_step = float(self.settings.get("zoom_sensitivity", DEFAULT_PIXELS_PER_STEP))
                self.zoom = _bound(self.zoom * (2.0 ** (dx / per_step)), MIN_ZOOM, MAX_ZOOM)
                canvas.setZoomLevel(self.zoom)
                key = self.document_key()
                if key:
                    self.zoom_memory[key] = self.zoom
        except Exception:
            pass

    def release(self):
        _trace("%s end z=%.5f a=%.2f" % (self.task, self.zoom, self.angle))
        self.dragging = False

    def _centre(self):
        try:
            widget = QApplication.focusWidget()
            if widget is not None and widget.width() > 1:
                return widget.mapToGlobal(widget.rect().center())
        except Exception:
            pass
        return None

    def _angle(self, pos):
        if self.pivot is None or pos is None:
            return None
        dx = float(pos.x() - self.pivot.x())
        dy = float(pos.y() - self.pivot.y())
        if dx * dx + dy * dy < PIVOT_DEAD_ZONE ** 2:
            return None
        return math.degrees(math.atan2(dy, dx))
