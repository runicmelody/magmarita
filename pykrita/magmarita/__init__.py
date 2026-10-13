# SPDX-License-Identifier: GPL-3.0-or-later
"""MagmaRita: Magma-style keybinds, palette and scrubby zoom/rotate for Krita."""

from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita

from .docker import MagmaRitaDocker
from .magmarita import MagmaRitaExtension
from .scrubby import ScrubbyZoomExtension

Krita.instance().addExtension(MagmaRitaExtension(Krita.instance()))
Krita.instance().addExtension(ScrubbyZoomExtension(Krita.instance()))
Krita.instance().addDockWidgetFactory(
    DockWidgetFactory("magmarita", DockWidgetFactoryBase.DockRight, MagmaRitaDocker)
)
