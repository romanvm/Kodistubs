"""Parse SWIG XML (``-xmlout``) trees to extract Kodi Python API structure.

The XML is the parse tree SWIG dumps after Python processing of Kodi's
``AddonModule*.i`` files (see ``swig_runner.py``), so ``%ignore``, ``%rename``,
``%extend`` and ``-builtin`` operator slots are already applied. Everything
that comes from SWIG's own library or from Kodi's ``kodi_*.i`` plumbing files
is skipped; only declarations from the module's ``.i`` file, ``interfaces/legacy``
headers and the action/key ID headers are part of the Python API.
"""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Iterator, Optional


@dataclass
class Param:
    name: str
    cpp_type: str
    default: Optional[str] = None


@dataclass
class FunctionDef:
    name: str
    params: list[Param]
    cpp_return_type: str
    is_constructor: bool = False


@dataclass
class ClassDef:
    name: str               # Python class name (sym_name)
    cpp_name: str           # Full C++ qualified name
    methods: list[FunctionDef] = field(default_factory=list)
    base_class: Optional[str] = None   # Python base class name (if any)


@dataclass
class ConstantDef:
    name: str
    value: str                      # C++ expression SWIG uses to initialize the constant
    cpp_type: str
    numval: Optional[str] = None    # integer value, if SWIG has already evaluated it


@dataclass
class ModuleAPI:
    name: str
    classes: list[ClassDef] = field(default_factory=list)
    functions: list[FunctionDef] = field(default_factory=list)
    constants: dict[str, ConstantDef] = field(default_factory=dict)
    typedefs: dict[str, str] = field(default_factory=dict)   # qualified C++ name → underlying C++ type


# Module metadata strings published by kodi_common.i; not part of the documented API.
_META_CONSTANTS = frozenset(('__author__', '__date__', '__version__', '__credits__', '__platform__'))

# Include nodes whose contents belong to the Python API (besides the module's own .i file).
_API_INCLUDE_MARKERS = ('interfaces/legacy/', 'input/actions/ActionIDs.h', 'input/keymaps/keyboard/KeyIDs.h')


# ──────────────────────────────────────────────────────────────────────────────
# Attribute helpers
# ──────────────────────────────────────────────────────────────────────────────

def _attrs(node: ET.Element) -> dict[str, str]:
    """Extract the attribute dict from a SWIG XML node's <attributelist>."""
    return {a.get('name', ''): a.get('value', '')
            for a in node.findall('attributelist/attribute')}


def _parms(node: ET.Element) -> list[Param]:
    """Extract parameters from a SWIG cdecl/constructor node."""
    params = []
    for index, parm in enumerate(node.findall('attributelist/parmlist/parm'), start=1):
        pattrs = _attrs(parm)
        cpp_type = pattrs.get('type', '')
        if not cpp_type:
            continue
        params.append(Param(name=pattrs.get('name') or f'arg{index}',
                            cpp_type=cpp_type,
                            default=pattrs.get('value')))
    return params


def _is_ignored(attrs: dict[str, str]) -> bool:
    return bool(attrs.get('feature_ignore'))


def _is_public(attrs: dict[str, str]) -> bool:
    return attrs.get('access', 'public') == 'public'


def _is_api_include(include_name: str, module_interface: str) -> bool:
    normalized = include_name.replace('\\', '/')
    return (os.path.basename(normalized) == module_interface
            or any(marker in normalized for marker in _API_INCLUDE_MARKERS))


# ──────────────────────────────────────────────────────────────────────────────
# Overload selection
# ──────────────────────────────────────────────────────────────────────────────

def _select_overload(group: list[FunctionDef]) -> FunctionDef:
    """Given a list of overloads, select the most complete one.

    Prefer the overload with the most parameters.  Among ties, prefer the one
    whose optional params have explicit default values.
    """
    if len(group) == 1:
        return group[0]

    def score(f: FunctionDef) -> tuple:
        with_defaults = sum(1 for p in f.params if p.default is not None)
        return (len(f.params), with_defaults)

    return max(group, key=score)


# ──────────────────────────────────────────────────────────────────────────────
# Parsing
# ──────────────────────────────────────────────────────────────────────────────

def _function_from_cdecl(cdecl: ET.Element) -> Optional[FunctionDef]:
    attrs = _attrs(cdecl)
    if attrs.get('kind') != 'function' or _is_ignored(attrs) or not _is_public(attrs):
        return None
    sym_name = attrs.get('sym_name', '')
    if not sym_name.isidentifier():
        return None
    return FunctionDef(name=sym_name, params=_parms(cdecl),
                       cpp_return_type=attrs.get('type', 'void'))


def _class_members(class_node: ET.Element) -> Iterator[ET.Element]:
    """Yield member nodes of a class, including those added with ``%extend``."""
    for child in class_node:
        if child.tag == 'extend':
            yield from child
        else:
            yield child


def _parse_class(class_node: ET.Element) -> Optional[ClassDef]:
    """Parse a <class> element into a ClassDef."""
    attrs = _attrs(class_node)
    sym_name = attrs.get('sym_name', '')
    # ``%template()`` instantiations show up as ``__dummy_N__`` classes.
    if not sym_name or sym_name.startswith('__dummy') or _is_ignored(attrs):
        return None

    cls = ClassDef(name=sym_name, cpp_name=attrs.get('name', ''))
    base_node = class_node.find('attributelist/baselist/base')
    if base_node is not None:
        cls.base_class = base_node.get('name')   # C++ name as written; resolved to a Python name later

    ctor_overloads: list[FunctionDef] = []
    method_groups: dict[str, list[FunctionDef]] = {}
    for member in _class_members(class_node):
        if member.tag == 'constructor':
            mattrs = _attrs(member)
            if _is_ignored(mattrs) or not _is_public(mattrs) or not mattrs.get('sym_name'):
                continue
            ctor_overloads.append(FunctionDef(name='__init__', params=_parms(member),
                                              cpp_return_type='void', is_constructor=True))
        elif member.tag == 'cdecl':
            func = _function_from_cdecl(member)
            if func is not None:
                method_groups.setdefault(func.name, []).append(func)

    if ctor_overloads:
        cls.methods.append(_select_overload(ctor_overloads))
    for overloads in method_groups.values():
        cls.methods.append(_select_overload(overloads))
    return cls


def _walk(node: ET.Element, api: ModuleAPI, module_interface: str,
          functions: dict[str, list[FunctionDef]]) -> None:
    """Recursively walk the SWIG XML tree collecting API declarations."""
    for child in node:
        tag = child.tag

        if tag == 'include':
            if _is_api_include(child.get('name') or _attrs(child).get('name', ''), module_interface):
                _walk(child, api, module_interface, functions)

        elif tag in ('module', 'namespace'):
            _walk(child, api, module_interface, functions)

        elif tag == 'class':
            cls = _parse_class(child)
            if cls is not None:
                api.classes.append(cls)

        elif tag == 'constant':
            cattrs = _attrs(child)
            name = cattrs.get('sym_name') or cattrs.get('name', '')
            if name and name not in _META_CONSTANTS and not _is_ignored(cattrs):
                api.constants.setdefault(name, ConstantDef(
                    name=name, value=cattrs.get('value', ''), cpp_type=cattrs.get('type', ''),
                    numval=cattrs.get('numval')))

        elif tag == 'cdecl':
            cattrs = _attrs(child)
            kind = cattrs.get('kind')
            if kind == 'typedef':
                qname, underlying = cattrs.get('name', ''), cattrs.get('type', '')
                if qname and underlying:
                    api.typedefs[qname] = underlying
            elif kind == 'variable' and cattrs.get('feature_immutable') and not _is_ignored(cattrs):
                # constexpr values (e.g. ACTION_* from ActionIDs.h) are exposed as read-only attributes.
                name = cattrs.get('sym_name', '')
                if name and name not in _META_CONSTANTS:
                    api.constants.setdefault(name, ConstantDef(
                        name=name, value=cattrs.get('value', ''), cpp_type=cattrs.get('type', ''),
                        numval=cattrs.get('numval')))
            elif kind == 'function':
                func = _function_from_cdecl(child)
                if func is not None:
                    functions.setdefault(func.name, []).append(func)

        elif tag == 'extend':
            # %extend of a non-class scope adds module-level functions.
            _walk(child, api, module_interface, functions)


def _resolve_bases(api: ModuleAPI) -> None:
    """Replace C++ base class names with Python class names; drop unreflected bases (e.g. AddonClass)."""
    # SWIG records bases as written in the header (usually unqualified), so match on the last name segment.
    by_name = {c.cpp_name.split('::')[-1]: c.name for c in api.classes}
    for cls in api.classes:
        cls.base_class = by_name.get(cls.base_class.split('::')[-1]) if cls.base_class else None


def parse_module(module: str, xml_path: str) -> ModuleAPI:
    """Parse the SWIG XML for a Kodi Python module and return its API structure."""
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f'SWIG XML not found: {xml_path}')

    root = ET.parse(xml_path).getroot()
    api = ModuleAPI(name=module)
    functions: dict[str, list[FunctionDef]] = {}
    _walk(root, api, f'AddonModule{module.capitalize()}.i', functions)
    api.functions = [_select_overload(overloads) for overloads in functions.values()]
    _resolve_bases(api)
    return api
