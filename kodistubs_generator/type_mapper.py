"""Map C++ / SWIG types to Python type annotation strings."""
from __future__ import annotations

import re
from typing import Optional

_SIMPLE = {
    'void': 'None',
    'bool': 'bool',
    'int': 'int',
    'long': 'int',
    'long long': 'int',
    'unsigned int': 'int',
    'unsigned long': 'int',
    'unsigned long long': 'int',
    'unsigned short': 'int',
    'int64_t': 'int',
    'uint64_t': 'int',
    'int32_t': 'int',
    'uint32_t': 'int',
    'int16_t': 'int',
    'uint16_t': 'int',
    'int8_t': 'int',
    'uint8_t': 'int',
    'size_t': 'int',
    'std::size_t': 'int',
    'short': 'int',
    'float': 'float',
    'double': 'float',
    'char': 'str',
    'unsigned char': 'int',
    'XBMCAddon::String': 'str',
    'String': 'str',
    'std::string': 'str',
    'string': 'str',
    'XbmcCommons::Buffer': 'bytearray',
    'bytearray': 'bytearray',
    # ``typedef String StringOrInt``: a plain string at runtime; numbers are only accepted as dictionary values.
    'XBMCAddon::StringOrInt': 'str',
    'StringOrInt': 'str',
    'PyObject': 'Any',
}

# Simple types that need a ``typing`` import.
_TYPING_NEEDED: dict[str, set[str]] = {'Any': {'Any'}}


def _strip_qualifiers(t: str) -> str:
    """Strip SWIG pointer/reference/const qualifiers."""
    while True:
        if t.startswith('r.'):
            t = t[2:]
        elif t.startswith('p.'):
            t = t[2:]
        elif t.startswith('q(const).'):
            t = t[9:]
        else:
            break
    return t.strip()


def _split_template_args(s: str) -> list[str]:
    """Split comma-separated template args respecting nested angle brackets."""
    depth = 0
    parts = []
    current = []
    for ch in s:
        if ch in '<(':
            depth += 1
            current.append(ch)
        elif ch in '>)':
            depth -= 1
            current.append(ch)
        elif ch == ',' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append(''.join(current).strip())
    return [p for p in parts if p]


def map_type(cpp_type: str, current_module: str = '',
             typedefs: Optional[dict] = None,
             for_param: bool = False) -> tuple[str, set[str], set[str]]:
    """Map a C++ / SWIG type to a Python type annotation.

    Returns ``(python_type_str, required_typing_imports, external_modules)`` where
    ``required_typing_imports`` is currently always empty (builtin generics and ``|`` unions
    need no imports) and ``external_modules`` is the set of other ``xbmc*`` stub modules referenced by
    the annotation (callers emit them inside an ``if TYPE_CHECKING:`` block).

    Annotations are emitted unquoted; the caller is expected to add
    ``from __future__ import annotations`` so forward references resolve lazily.

    ``typedefs`` is an optional mapping of fully-qualified C++ typedef names
    (e.g. ``XBMCAddon::xbmc::PlayParameter``) to their underlying SWIG type
    strings; encountered typedefs are expanded recursively.

    ``for_param`` selects annotations for parameters: containers are annotated as the abstract
    ``Sequence`` / ``Mapping`` (imported from ``collections.abc``) instead of ``list`` / ``dict``,
    because the invariant concrete types would make type checkers reject e.g. a ``dict[str, str]``
    argument for a ``dict[str, str | int]`` parameter. Return types keep the concrete types.
    """
    t = _strip_qualifiers(cpp_type.strip())
    if t in ('XBMCAddon::Properties', 'Properties'):
        t = 'XBMCAddon::Dictionary<(XBMCAddon::StringOrInt)>'   # typedef from Dictionary.h, also when it is not in ``typedefs``

    # Resolve typedef chains (with cycle protection)
    if typedefs:
        seen: set[str] = set()
        while t in typedefs and t not in seen:
            seen.add(t)
            t = _strip_qualifiers(typedefs[t].strip())

    # Simple lookup
    # Kodi's Buffer typemap (kodi_buffer.i) accepts str (UTF-8 encoded), bytes and bytearray but returns bytearray.
    if for_param and t == 'XbmcCommons::Buffer':
        return 'str | bytes | bytearray', set(), set()

    if t in _SIMPLE:
        py = _SIMPLE[t]
        return py, _TYPING_NEEDED.get(py, set()), set()

    # std::unique_ptr<(T)>  — treat as the inner type
    m = re.match(r'^std::unique_ptr<\((.+)\)>$', t)
    if m:
        return map_type(m.group(1), current_module, typedefs, for_param)

    # std::vector<(T)> or std::vector<(T, std::allocator<(T)>)> (drop allocator)
    m = re.match(r'^std::vector<\((.+)\)>$', t)
    if m:
        inner, imp, ext = map_type(_split_template_args(m.group(1))[0], current_module, typedefs, for_param)
        if for_param:
            return f'Sequence[{inner}]', imp | {'Sequence'}, ext
        return f'list[{inner}]', imp, ext

    # XBMCAddon::Tuple<(T1, T2, ...)>  or  Tuple<(...)>
    m = re.match(r'^(?:XBMCAddon::)?Tuple<\((.+)\)>$', t)
    if m:
        parts = _split_template_args(m.group(1))
        mapped = [map_type(p.strip(), current_module, typedefs, for_param) for p in parts]
        inner_strs = [x[0] for x in mapped]
        imports = set().union(*[x[1] for x in mapped])
        externals = set().union(*[x[2] for x in mapped])
        return f'tuple[{", ".join(inner_strs)}]', imports, externals

    # Alternative<(T1, T2)>  → T1 | T2
    m = re.match(r'^(?:XBMCAddon::)?Alternative<\((.+)\)>$', t)
    if m:
        parts = _split_template_args(m.group(1))
        mapped = [map_type(p.strip(), current_module, typedefs, for_param) for p in parts]
        inner_strs = [x[0] for x in mapped]
        imports = set().union(*[x[1] for x in mapped])
        externals = set().union(*[x[2] for x in mapped])
        return ' | '.join(inner_strs), imports, externals

    # Dictionary<(T)>  → dict[str, T]
    m = re.match(r'^(?:XBMCAddon::)?Dictionary<\((.+)\)>$', t)
    if m:
        val, imp, ext = map_type(m.group(1), current_module, typedefs, for_param)
        if for_param:
            return f'Mapping[str, {_with_numbers(val)}]', imp | {'Mapping'}, ext
        return f'dict[str, {val}]', imp, ext

    # std::map<(K, V)> or std::map<(K, V, Cmp)> → dict[K, V] (drop comparator)
    m = re.match(r'^std::map<\((.+)\)>$', t)
    if m:
        parts = _split_template_args(m.group(1))
        if len(parts) >= 2:
            key, kimp, kext = map_type(parts[0].strip(), current_module, typedefs, for_param)
            val, vimp, vext = map_type(parts[1].strip(), current_module, typedefs, for_param)
            if for_param:
                return f'Mapping[{key}, {val}]', kimp | vimp | {'Mapping'}, kext | vext
            return f'dict[{key}, {val}]', kimp | vimp, kext | vext

    # XBMCAddon::xbmcMODULE::ClassName  (xbmcMODULE may be bare "xbmc" or "xbmcgui" etc.)
    m = re.match(r'^XBMCAddon::(xbmc\w*)::(\w+)$', t)
    if m:
        mod, cls = m.group(1), m.group(2)
        if mod == current_module:
            return cls, set(), set()
        return f'{mod}.{cls}', set(), {mod}

    # xbmc::ClassName  (from within xbmc module)
    m = re.match(r'^xbmc::(\w+)$', t)
    if m:
        cls = m.group(1)
        if current_module == 'xbmc':
            return cls, set(), set()
        return f'xbmc.{cls}', set(), {'xbmc'}

    # Plain ClassName (uppercase, assumed same-module forward reference)
    if re.match(r'^[A-Z][A-Za-z0-9_]*$', t):
        return t, set(), set()

    # Fallback — bare token (whatever it is, leave unquoted; future annotations
    # defer evaluation, so an unresolved name is harmless until inspected).
    return t, set(), set()


def _with_numbers(py_type: str) -> str:
    """Add ``int | float`` to a dictionary value type.

    Kodi's Dictionary typemap (``kodi_generics.i``) converts ``int`` and ``float`` values with ``str()`` before the
    regular conversion, so they are accepted wherever the value type accepts a string.
    """
    parts = split_union(py_type)
    if 'str' not in parts:
        return py_type
    scalars = [p for p in parts if '[' not in p]
    containers = [p for p in parts if '[' in p]
    scalars += [n for n in ('int', 'float') if n not in scalars]
    return ' | '.join(scalars + containers)


def split_union(py_type: str) -> list[str]:
    """Split ``A | B[C | D]`` at the top-level ``|`` only."""
    depth = 0
    parts = []
    current = []
    for ch in py_type:
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
        if ch == '|' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    parts.append(''.join(current).strip())
    return parts


def default_return(py_type: str) -> str:
    """Return a minimal stub expression for the given Python type."""
    if py_type == 'None':
        return 'pass'
    if py_type == 'bool':
        return 'return True'
    if py_type == 'int':
        return 'return 0'
    if py_type == 'float':
        return 'return 0.0'
    if py_type == 'str':
        return 'return ""'
    if py_type == 'bytearray':
        return 'return bytearray()'
    if py_type == 'Any':
        return 'pass'
    if py_type.startswith('list['):
        return 'return []'
    if py_type.startswith('dict['):
        return 'return {}'
    if py_type.startswith('tuple['):
        # Build a minimal tuple
        inner = py_type[6:-1]
        parts = _split_template_args(inner)
        defaults = []
        for p in parts:
            d = default_return(p.strip())
            if d.startswith('return '):
                defaults.append(d[7:])
            else:
                defaults.append('None')
        return f'return ({", ".join(defaults)},)' if defaults else 'return ()'
    alternatives = split_union(py_type)
    if len(alternatives) > 1:
        # Return the first alternative
        return default_return(alternatives[0])
    # Same-module class name (a bare identifier defined elsewhere in the same file).
    if py_type.isidentifier():
        return f'return {py_type}()'
    # Cross-module class refs (e.g. ``xbmcgui.ListItem``) are imported only
    # under ``TYPE_CHECKING``, so a bare ``return xbmcgui.ListItem()`` would
    # ``NameError`` at runtime. Emit a function-local import so the body
    # both matches the declared return type for static analysis and is
    # safe to call at runtime.
    m = re.match(r'^([a-z][a-zA-Z0-9_]*)\.[A-Z][A-Za-z0-9_]*$', py_type)
    if m:
        return f'import {m.group(1)}\nreturn {py_type}()'
    return 'pass'


def map_default_value(cpp_default: str) -> str:
    """Map a C++ default parameter value to a Python literal."""
    d = cpp_default.strip()
    if d in ('NULL', 'nullptr', '0x0'):
        return 'None'
    if d == 'false':
        return 'False'
    if d == 'true':
        return 'True'
    if d in ('XBMCAddon::emptyString', 'emptyString', '""', "''"):
        return '""'
    # Numeric literal (possibly with cast)
    cast_m = re.match(r'static_cast<[^>]+>\((.+)\)$', d)
    if cast_m:
        return cast_m.group(1)
    d = re.sub(r'(?<=[\d.])[fF]$', '', d)  # C++ float suffix: 0.0f -> 0.0
    if re.match(r'^-?\d+(\.\d*)?([eE][+-]?\d+)?$', d):
        return d + '0' if d.endswith('.') else d
    # Fallback: any unrecognized C++ expression → None
    return 'None'
