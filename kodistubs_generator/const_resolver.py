"""Resolve Kodi Python API constant values from .i.cpp and C++ source."""
from __future__ import annotations
import os
import re
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# Enum-value parsers for specific C++ header files
# ──────────────────────────────────────────────────────────────────────────────

def _parse_sequential_enum(header_path: str, enum_name: str) -> dict[str, int]:
    """Parse a simple C++ enum (sequential values starting from 0) from a header."""
    if not os.path.exists(header_path):
        return {}
    with open(header_path, encoding='utf-8', errors='replace') as f:
        text = f.read()

    # Match enum class/struct block
    patterns = [
        rf'enum\s+class\s+{re.escape(enum_name)}\s*\{{([^}}]+)\}}',
        rf'enum\s+{re.escape(enum_name)}\s*\{{([^}}]+)\}}',
        rf'typedef\s+enum\s*\{{([^}}]+)\}}\s*{re.escape(enum_name)}\s*;',
    ]
    block = None
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL)
        if m:
            block = m.group(1)
            break
    if block is None:
        return {}

    result: dict[str, int] = {}
    current = 0
    # Parse members like: NAME, NAME = 5, NAME /**/ ,
    for m in re.finditer(r'([A-Z_][A-Z0-9_]*)\s*(?:=\s*([^,\n/]+?))?(?:\s*(?:,|//))', block + ','):
        name = m.group(1)
        val_str = m.group(2)
        if val_str is not None:
            val_str = val_str.strip()
            try:
                current = int(val_str, 0)
            except ValueError:
                pass  # keep current value
        result[name] = current
        current += 1
    return result


def _parse_class_enum(header_path: str, class_name: str, enum_name: str) -> dict[str, int]:
    """Parse an enum inside a C++ class."""
    if not os.path.exists(header_path):
        return {}
    with open(header_path, encoding='utf-8', errors='replace') as f:
        text = f.read()

    # Find the class body
    m = re.search(rf'class\s+{re.escape(class_name)}\b', text)
    if not m:
        return {}
    class_body = text[m.start():]
    # Extract up to matching closing brace
    depth = 0
    body_start = class_body.index('{')
    body = []
    for ch in class_body[body_start:]:
        body.append(ch)
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                break
    class_text = ''.join(body)
    return _parse_sequential_enum_from_text(class_text, enum_name)


def _parse_sequential_enum_from_text(text: str, enum_name: str) -> dict[str, int]:
    """Parse an enum block from text."""
    patterns = [
        rf'enum\s+(?:class\s+)?{re.escape(enum_name)}\s*\{{([^}}]+)\}}',
        rf'enum\s*\{{([^}}]+)\}}\s*{re.escape(enum_name)}',
    ]
    block = None
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL)
        if m:
            block = m.group(1)
            break
    if block is None:
        return {}

    result: dict[str, int] = {}
    current = 0
    for m in re.finditer(r'([A-Z_][A-Z0-9_a-z]*)\s*(?:=\s*([^,\n/]+?))?(?:\s*(?:,|//))', block + ','):
        name = m.group(1)
        val_str = m.group(2)
        if val_str is not None:
            val_str = val_str.strip()
            try:
                current = int(val_str, 0)
            except ValueError:
                pass
        result[name] = current
        current += 1
    return result


def _parse_constexpr_ints(header_path: str) -> dict[str, int]:
    """Parse `constexpr int NAME = VALUE;` lines."""
    if not os.path.exists(header_path):
        return {}
    result: dict[str, int] = {}
    with open(header_path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = re.match(r'\s*(?:constexpr|const)\s+int\s+(\w+)\s*=\s*(-?\d+)\s*;', line)
            if m:
                result[m.group(1)] = int(m.group(2))
    return result


# ──────────────────────────────────────────────────────────────────────────────
# C++ expression evaluator (for SWIG constant rawvals)
# ──────────────────────────────────────────────────────────────────────────────

class EnumResolver:
    """Resolves C++ enum/constant expressions to integer values."""

    def __init__(self, kodi_src: str) -> None:
        self.kodi_src = kodi_src
        self._cache: dict[str, Optional[int]] = {}
        self._known: dict[str, int] = {}
        self._load_known()

    def _load_known(self) -> None:
        src = self.kodi_src
        # SortMethod enum (for xbmcplugin SORT_METHOD_* constants)
        sort_h = os.path.join(src, 'xbmc/SortFileItem.h')
        sort_vals = _parse_sequential_enum(sort_h, 'SortMethod')
        self._known.update({f'SortMethod::{k}': v for k, v in sort_vals.items()})

        # xbmc ilog.h (LOGDEBUG, LOGINFO, etc.)
        ilog_h = os.path.join(src, 'xbmc/commons/ilog.h')
        log_vals = _parse_constexpr_ints(ilog_h)
        self._known.update(log_vals)

        # GUIListItem.h enums (ICON_OVERLAY_*, etc.)
        gui_list_h = os.path.join(src, 'xbmc/guilib/GUIListItem.h')
        icon_vals = _parse_class_enum(gui_list_h, 'CGUIListItem', 'GUIIconOverlay')
        self._known.update({f'CGUIListItem::{k}': v for k, v in icon_vals.items()})
        self._known.update(icon_vals)

        # CGUIEditControl INPUT_TYPE_*
        edit_h = os.path.join(src, 'xbmc/guilib/GUIEditControl.h')
        if os.path.exists(edit_h):
            edit_vals = _parse_class_enum(edit_h, 'CGUIEditControl', 'INPUT_TYPE')
            self._known.update({f'CGUIEditControl::{k}': v for k, v in edit_vals.items()})
            self._known.update(edit_vals)

        # Key input constants
        key_h = os.path.join(src, 'xbmc/input/Key.h')
        if os.path.exists(key_h):
            key_vals = self._parse_defines(key_h)
            self._known.update(key_vals)

        # Server constants
        network_h = os.path.join(src, 'xbmc/network/Network.h')
        if os.path.exists(network_h):
            with open(network_h, encoding='utf-8', errors='replace') as f:
                text = f.read()
            enum_vals = _parse_sequential_enum_from_text(text, 'ESERVERS')
            self._known.update(enum_vals)
            self._known.update({f'ESERVERS::{k}': v for k, v in enum_vals.items()})

        # Playlist constants
        playlist_h = os.path.join(src, 'xbmc/playlists/PlayListTypes.h')
        if os.path.exists(playlist_h):
            pl_vals = _parse_sequential_enum(playlist_h, 'Id')
            self._known.update(pl_vals)

        # ISO 639 language code format constants
        self._known.update({'ISO_639_1': 0, 'ISO_639_2': 1, 'ENGLISH_NAME': 2})

    def _parse_defines(self, header_path: str) -> dict[str, int]:
        """Parse #define NAME VALUE lines."""
        result: dict[str, int] = {}
        if not os.path.exists(header_path):
            return result
        with open(header_path, encoding='utf-8', errors='replace') as f:
            for line in f:
                m = re.match(r'\s*#\s*define\s+([A-Z_][A-Z0-9_]+)\s+(\d+)', line)
                if m:
                    try:
                        result[m.group(1)] = int(m.group(2))
                    except ValueError:
                        pass
        return result

    def resolve(self, raw_val: str) -> Optional[int]:
        """Resolve a raw C++ constant expression to an integer."""
        raw_val = raw_val.strip()
        if raw_val in self._cache:
            return self._cache[raw_val]

        result = self._try_resolve(raw_val)
        self._cache[raw_val] = result
        return result

    def _try_resolve(self, expr: str) -> Optional[int]:
        # Direct integer literal
        try:
            return int(expr, 0)
        except ValueError:
            pass

        # Direct lookup
        if expr in self._known:
            return self._known[expr]

        # static_cast<TYPE>(SomeEnum::VALUE)
        m = re.match(r'static_cast<[^>]+>\((.+)\)$', expr)
        if m:
            return self._try_resolve(m.group(1).strip())

        # SomeClass::MEMBER
        m = re.match(r'(\w+)::(\w+)$', expr)
        if m:
            full_key = expr
            if full_key in self._known:
                return self._known[full_key]
            # Try member alone
            member = m.group(2)
            if member in self._known:
                return self._known[member]

        # Getter call like getLOGDEBUG()
        m = re.match(r'get(\w+)\(\)$', expr)
        if m:
            name = m.group(1)
            if name in self._known:
                return self._known[name]

        return None


# ──────────────────────────────────────────────────────────────────────────────
# .i.cpp parser
# ──────────────────────────────────────────────────────────────────────────────

def parse_constants_from_cpp(cpp_path: str,
                              resolver: EnumResolver) -> dict[str, object]:
    """Parse PyModule_Add{Int,String}Constant calls from a .i.cpp file.

    Returns a dict mapping constant name → Python value (int or str).
    """
    if not os.path.exists(cpp_path):
        return {}
    with open(cpp_path, encoding='utf-8', errors='replace') as f:
        text = f.read()

    result: dict[str, object] = {}

    # PyModule_AddIntConstant(module,"NAME",VALUE_EXPR);
    for m in re.finditer(
        r'PyModule_AddIntConstant\s*\(\s*\w+\s*,\s*"(\w+)"\s*,\s*(.+?)\s*\)\s*;',
        text
    ):
        name, val_expr = m.group(1), m.group(2).strip()
        # Try direct int first
        try:
            result[name] = int(val_expr, 0)
            continue
        except ValueError:
            pass
        resolved = resolver.resolve(val_expr)
        if resolved is not None:
            result[name] = resolved
        else:
            # Leave as 0 placeholder with a note
            result[name] = 0

    # PyModule_AddStringConstant(module,"NAME","value");
    _meta = frozenset({'__author__', '__date__', '__version__', '__credits__', '__platform__'})
    for m in re.finditer(
        r'PyModule_AddStringConstant\s*\(\s*\w+\s*,\s*"(\w+)"\s*,\s*"([^"]*)"\s*\)\s*;',
        text
    ):
        name, val = m.group(1), m.group(2)
        if name not in _meta:
            result[name] = val

    # PyModule_AddStringConstant with getter
    for m in re.finditer(
        r'PyModule_AddStringConstant\s*\(\s*\w+\s*,\s*"(\w+)"\s*,\s*get\w+\(\)\s*\)\s*;',
        text
    ):
        name = m.group(1)
        # Skip metadata constants
        if name in ('__author__', '__date__', '__version__', '__credits__',
                    '__platform__'):
            continue
        # String constants we can't resolve - use placeholder
        if name not in result:
            result[name] = ''

    return result


_META_CONSTANTS = frozenset({
    '__author__', '__date__', '__version__', '__credits__', '__platform__',
})


def load_constants(module: str, swig_dir: str, kodi_src: str) -> dict[str, object]:
    """Load all constants for a module from its .i.cpp file."""
    cpp_name_map = {
        'xbmc': 'AddonModuleXbmc',
        'xbmcaddon': 'AddonModuleXbmcaddon',
        'xbmcgui': 'AddonModuleXbmcgui',
        'xbmcplugin': 'AddonModuleXbmcplugin',
        'xbmcvfs': 'AddonModuleXbmcvfs',
        'xbmcdrm': 'AddonModuleXbmcdrm',
    }
    base = cpp_name_map.get(module, f'AddonModule{module.capitalize()}')
    cpp_path = os.path.join(swig_dir, f'{base}.i.cpp')
    resolver = EnumResolver(kodi_src)
    constants = parse_constants_from_cpp(cpp_path, resolver)
    return {k: v for k, v in constants.items() if k not in _META_CONSTANTS}
