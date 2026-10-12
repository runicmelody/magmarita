from krita import Krita

from .magmarita_scrubby_zoom import ScrubbyZoomExtension

Krita.instance().addExtension(ScrubbyZoomExtension(Krita.instance()))
