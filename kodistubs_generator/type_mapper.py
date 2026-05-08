"""Map C++ / SWIG types to Python type annotation strings."""
from __future__ import annotations
import re


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
    'XBMCAddon::StringOrInt': 'Union[str, int]',
    'StringOrInt': 'Union[str, int]',
}

_TYPING_NEEDED: dict[str, set[str]] = {
    'Union[str, int]': {'Union'},
}


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


def map_type(cpp_type: str, current_module: str = '') -> tuple[str, set[str]]:
    """Map a C++ / SWIG type to a Python type annotation.

    Returns ``(python_type_str, required_typing_imports)``.
    """
    t = _strip_qualifiers(cpp_type.strip())

    # Simple lookup
    if t in _SIMPLE:
        py = _SIMPLE[t]
        return py, _TYPING_NEEDED.get(py, set())

    # std::unique_ptr<(T)>  — treat as the inner type
    m = re.match(r'^std::unique_ptr<\((.+)\)>$', t)
    if m:
        return map_type(m.group(1), current_module)

    # std::vector<(T)>
    m = re.match(r'^std::vector<\((.+)\)>$', t)
    if m:
        inner, imp = map_type(m.group(1), current_module)
        return f'List[{inner}]', imp | {'List'}

    # XBMCAddon::Tuple<(T1, T2, ...)>  or  Tuple<(...)>
    m = re.match(r'^(?:XBMCAddon::)?Tuple<\((.+)\)>$', t)
    if m:
        parts = _split_template_args(m.group(1))
        mapped = [map_type(p.strip(), current_module) for p in parts]
        inner_strs = [x[0] for x in mapped]
        imports = set().union(*[x[1] for x in mapped]) | {'Tuple'}
        return f'Tuple[{", ".join(inner_strs)}]', imports

    # Alternative<(T1, T2)>  → Union[T1, T2]
    m = re.match(r'^(?:XBMCAddon::)?Alternative<\((.+)\)>$', t)
    if m:
        parts = _split_template_args(m.group(1))
        mapped = [map_type(p.strip(), current_module) for p in parts]
        inner_strs = [x[0] for x in mapped]
        imports = set().union(*[x[1] for x in mapped]) | {'Union'}
        return f'Union[{", ".join(inner_strs)}]', imports

    # Dictionary<(T)>  → Dict[str, T]
    m = re.match(r'^(?:XBMCAddon::)?Dictionary<\((.+)\)>$', t)
    if m:
        val, imp = map_type(m.group(1), current_module)
        return f'Dict[str, {val}]', imp | {'Dict'}

    # XBMCAddon::xbmcMODULE::ClassName
    m = re.match(r'^XBMCAddon::(xbmc\w+)::(\w+)$', t)
    if m:
        mod, cls = m.group(1), m.group(2)
        if mod == current_module:
            return f"'{cls}'", set()
        return f"'{mod}.{cls}'", set()

    # xbmc::ClassName  (from within xbmc module)
    m = re.match(r'^xbmc::(\w+)$', t)
    if m:
        cls = m.group(1)
        if current_module == 'xbmc':
            return f"'{cls}'", set()
        return f"'xbmc.{cls}'", set()

    # Plain ClassName (uppercase, assumed same-module forward reference)
    if re.match(r'^[A-Z][A-Za-z0-9_]*$', t):
        return f"'{t}'", set()

    # Fallback
    return f"'{t}'", set()


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
    if py_type.startswith('List['):
        return 'return []'
    if py_type.startswith('Dict['):
        return 'return {}'
    if py_type.startswith('Tuple['):
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
    if py_type.startswith('Union['):
        # Return the first alternative
        inner = py_type[6:-1]
        first = _split_template_args(inner)[0]
        return default_return(first.strip())
    if py_type.startswith("'") and py_type.endswith("'"):
        cls = py_type[1:-1]
        # Only instantiate simple class names; skip complex/cross-module types
        if cls.isidentifier():
            return f'return {cls}()'
        return 'pass'
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
    if re.match(r'^-?\d+(\.\d+)?([eE][+-]?\d+)?$', d):
        return d
    # Fallback: any unrecognized C++ expression → None
    return 'None'
