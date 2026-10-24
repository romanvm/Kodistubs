"""Docstrings for API members that Doxygen cannot provide.

Some documentation in Kodi's headers never reaches the Doxygen XML (e.g. Doxygen drops the doc block of
``xbmcgui.Control.getPosition``). The text for such members is kept here, in reStructuredText as produced by
``doc_converter``, keyed by ``module.name`` for functions and ``module.Class.name`` for methods.

An entry is used only when Doxygen has no documentation for the member, so it stops applying once Kodi fixes the
problem. The member is still listed in the report of members without Doxygen documentation, which keeps the
upstream gap visible. Copy the text from the doc comment in the Kodi sources.
"""
from __future__ import annotations

MANUAL_DOCS: dict[str, str] = {
    'xbmcgui.Control.getPosition': """\
Returns the control's current position as a x,y integer tuple.

:return: Current position as a x,y integer tuple

Example::

    ...
    pos = self.button.getPosition()
    ...""",
}
