"""Parse SWIG XML (.i.xml) files to extract Kodi Python API structure."""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


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
class ModuleAPI:
    name: str
    classes: list[ClassDef] = field(default_factory=list)
    functions: list[FunctionDef] = field(default_factory=list)
    constant_names: list[str] = field(default_factory=list)  # names only; values from const_resolver
    typedefs: dict[str, str] = field(default_factory=dict)   # qualified C++ name → underlying C++ type


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
    for parm in node.findall('.//parm'):
        pattrs = _attrs(parm)
        name = pattrs.get('name', '')
        cpp_type = pattrs.get('type', '')
        default = pattrs.get('value', None)
        if name and cpp_type:
            params.append(Param(name=name, cpp_type=cpp_type, default=default))
    return params


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

def _parse_functions(node: ET.Element,
                     seen: dict[str, list[FunctionDef]]) -> None:
    """Collect cdecl function nodes with sym_name into seen dict."""
    for cdecl in node.findall('cdecl'):
        attrs = _attrs(cdecl)
        if attrs.get('kind') != 'function':
            continue
        sym_name = attrs.get('sym_name', '')
        if not sym_name or not sym_name.isidentifier():
            continue
        func = FunctionDef(
            name=sym_name,
            params=_parms(cdecl),
            cpp_return_type=attrs.get('type', 'void'),
        )
        seen.setdefault(sym_name, []).append(func)


def _parse_class(class_node: ET.Element) -> Optional[ClassDef]:
    """Parse a <class> element into a ClassDef."""
    attrs = _attrs(class_node)
    sym_name = attrs.get('sym_name', '')
    cpp_name = attrs.get('name', '')
    if not sym_name:
        return None

    cls = ClassDef(name=sym_name, cpp_name=cpp_name)

    # Constructor overloads
    ctor_overloads: list[FunctionDef] = []
    for ctor_node in class_node.findall('.//constructor'):
        cattrs = _attrs(ctor_node)
        if not cattrs.get('sym_name'):
            continue
        # Only take constructors with 'access': 'public' or no access attr
        if cattrs.get('access', 'public') != 'public':
            continue
        func = FunctionDef(
            name='__init__',
            params=_parms(ctor_node),
            cpp_return_type='void',
            is_constructor=True,
        )
        ctor_overloads.append(func)

    if ctor_overloads:
        cls.methods.append(_select_overload(ctor_overloads))

    # Method overloads
    method_groups: dict[str, list[FunctionDef]] = {}
    _parse_functions(class_node, method_groups)

    for sym_name_m, overloads in method_groups.items():
        cls.methods.append(_select_overload(overloads))

    return cls


def _walk_for_classes_and_functions(
    node: ET.Element,
    module_api: ModuleAPI,
) -> None:
    """Recursively walk the SWIG XML tree to collect classes and functions."""
    for child in node:
        tag = child.tag

        if tag == 'module':
            _walk_for_classes_and_functions(child, module_api)

        elif tag == 'namespace':
            _walk_for_classes_and_functions(child, module_api)

        elif tag == 'class':
            cls = _parse_class(child)
            if cls is not None:
                module_api.classes.append(cls)
            # Don't recurse into class body for nested classes

        elif tag == 'constant':
            cattrs = _attrs(child)
            name = cattrs.get('sym_name') or cattrs.get('name', '')
            # Skip metadata constants
            if name and name not in ('__author__', '__date__', '__version__',
                                     '__credits__', '__platform__'):
                if name not in module_api.constant_names:
                    module_api.constant_names.append(name)

        elif tag == 'cdecl':
            cattrs = _attrs(child)
            if cattrs.get('kind') == 'typedef':
                qname = cattrs.get('name', '')
                underlying = cattrs.get('type', '')
                if qname and underlying:
                    module_api.typedefs[qname] = underlying
            if cattrs.get('kind') == 'function':
                sym_name = cattrs.get('sym_name', '')
                if sym_name and sym_name.isidentifier():
                    func = FunctionDef(
                        name=sym_name,
                        params=_parms(child),
                        cpp_return_type=cattrs.get('type', 'void'),
                    )
                    # Check if this is an overload of an existing one
                    existing = next((f for f in module_api.functions
                                     if f.name == sym_name), None)
                    if existing is None:
                        module_api.functions.append(func)
                    else:
                        # Replace if new one has more params
                        if len(func.params) > len(existing.params):
                            idx = module_api.functions.index(existing)
                            module_api.functions[idx] = func

        else:
            _walk_for_classes_and_functions(child, module_api)


def parse_module(module: str, swig_dir: str) -> ModuleAPI:
    """Parse the SWIG XML for a Kodi Python module and return its API structure."""
    name_map = {
        'xbmc': 'AddonModuleXbmc',
        'xbmcaddon': 'AddonModuleXbmcaddon',
        'xbmcgui': 'AddonModuleXbmcgui',
        'xbmcplugin': 'AddonModuleXbmcplugin',
        'xbmcvfs': 'AddonModuleXbmcvfs',
        'xbmcdrm': 'AddonModuleXbmcdrm',
    }
    base = name_map.get(module, f'AddonModule{module.capitalize()}')
    xml_path = os.path.join(swig_dir, f'{base}.i.xml')
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f'SWIG XML not found: {xml_path}')

    tree = ET.parse(xml_path)
    root = tree.getroot()

    api = ModuleAPI(name=module)
    _walk_for_classes_and_functions(root, api)

    # Deduplicate function overloads (keep best per name)
    seen: dict[str, list[FunctionDef]] = {}
    for f in api.functions:
        seen.setdefault(f.name, []).append(f)
    api.functions = [_select_overload(overloads)
                     for overloads in seen.values()]

    return api
