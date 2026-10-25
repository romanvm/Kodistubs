"""API facts that cannot be derived from C++ types.

SWIG turns a null pointer returned by C++ into ``None``, but a pointer return type does not say whether a method
ever returns null. Methods listed here (``module.Class.method``) were checked in Kodi's ``interfaces/legacy``
sources to return null in some cases; their return annotation gets ``| None``.
"""
from __future__ import annotations

NULLABLE_RETURNS: frozenset[str] = frozenset((
    # Control.cpp: returns NULL when the list is empty or nothing is selected.
    'xbmcgui.ControlList.getSelectedItem',
    # Control.cpp: returns the pControlSpin member, which nothing assigns.
    'xbmcgui.ControlList.getSpinControl',
))
