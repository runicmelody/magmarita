# SPDX-License-Identifier: GPL-3.0-or-later
from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita

from .magmarita import MagmaRitaExtension
from .magmarita_docker import MagmaRitaDocker

Krita.instance().addExtension(MagmaRitaExtension(Krita.instance()))
Krita.instance().addDockWidgetFactory(
    DockWidgetFactory("magmarita", DockWidgetFactoryBase.DockRight, MagmaRitaDocker)
)
