# SPDX-License-Identifier: GPL-3.0-or-later
from krita import Krita

from .magmarita import MagmaRitaExtension

Krita.instance().addExtension(MagmaRitaExtension(Krita.instance()))
