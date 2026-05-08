"""Generate Python stub package files from parsed API + documentation."""
from __future__ import annotations
import os
import re
import textwrap
import xml.etree.ElementTree as ET
from typing import Optional

from .swig_parser import ClassDef, FunctionDef, ModuleAPI, Param
from .doxy_parser import DoxygenIndex, get_class_doc, get_class_inheritance, get_member_doc
from .type_mapper import default_return, map_default_value, map_type
from .doc_converter import group_class_to_rst, group_module_to_rst, member_to_rst


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _indent(text: str, spaces: int = 4) -> str:
    prefix = ' ' * spaces
    return '\n'.join(prefix + line if line.strip() else line
                     for line in text.splitlines())


def _format_docstring(rst: str, indent: int = 4) -> str:
    """Wrap an RST string as an indented docstring."""
    if not rst.strip():
        return ''
    prefix = ' ' * indent
    lines = ['"""']
    for line in rst.rstrip().splitlines():
        lines.append(line.replace('\\', '\\\\'))
    lines.append('"""')
    return textwrap.indent('\n'.join(lines), prefix)


def _needs_optional(params: list[Param]) -> bool:
    return any(p.default is not None for p in params)


def _build_signature(func: FunctionDef, module: str,
                     is_method: bool = False) -> tuple[str, set[str]]:
    """Build a Python function signature string and collect typing imports."""
    typing_imports: set[str] = set()
    parts = []
    if is_method:
        parts.append('self')
    for param in func.params:
        py_type, ti = map_type(param.cpp_type, module)
        typing_imports |= ti
        if param.default is not None:
            py_default = map_default_value(param.default)
            if py_default == 'None' and not py_type.startswith('Optional'):
                py_type = f'Optional[{py_type}]'
                typing_imports.add('Optional')
            parts.append(f'{param.name}: {py_type} = {py_default}')
        else:
            parts.append(f'{param.name}: {py_type}')

    py_ret, ti = map_type(func.cpp_return_type, module)
    typing_imports |= ti

    if func.is_constructor:
        return_ann = ' -> None'
    elif py_ret == 'None':
        return_ann = ' -> None'
    else:
        return_ann = f' -> {py_ret}'

    params_str = ', '.join(parts)
    return f'({params_str}){return_ann}', typing_imports


# ──────────────────────────────────────────────────────────────────────────────
# Function / method generation
# ──────────────────────────────────────────────────────────────────────────────

def _generate_function(func: FunctionDef, module: str,
                       dox: DoxygenIndex,
                       class_name: Optional[str] = None,
                       indent: int = 0) -> tuple[str, set[str]]:
    """Generate a Python function/method definition string."""
    typing_imports: set[str] = set()
    prefix = ' ' * indent
    lines = []

    sig, ti = _build_signature(func, module, is_method=class_name is not None)
    typing_imports |= ti

    py_ret, _ = map_type(func.cpp_return_type, module)
    body_stmt = default_return(py_ret)

    func_name = func.name

    lines.append(f'{prefix}def {func_name}{sig}:')

    # Docstring
    memberdef = get_member_doc(dox, func_name, class_name)
    if memberdef is not None:
        rst = member_to_rst(memberdef)
    else:
        rst = ''

    if rst.strip():
        lines.append(_format_docstring(rst, indent + 4))

    # Body
    lines.append(f'{prefix}    {body_stmt}')

    return '\n'.join(lines), typing_imports


# ──────────────────────────────────────────────────────────────────────────────
# Class generation
# ──────────────────────────────────────────────────────────────────────────────

def _generate_class(cls: ClassDef, module: str,
                    dox: DoxygenIndex, xml_dir: str) -> tuple[str, set[str]]:
    """Generate a Python class definition string."""
    typing_imports: set[str] = set()
    lines = []

    # Inheritance
    base = cls.base_class or get_class_inheritance(xml_dir, module, cls.name)

    if base:
        lines.append(f'class {cls.name}({base}):')
    else:
        lines.append(f'class {cls.name}:')

    # Class docstring
    group_compound = get_class_doc(dox, cls.name)
    if group_compound is not None:
        rst = group_class_to_rst(group_compound)
    else:
        rst = ''

    if rst.strip():
        lines.append(_format_docstring(rst, 4))
    else:
        lines.append('    ...')

    # Methods
    has_methods = False
    for method in cls.methods:
        mdef, ti = _generate_function(
            method, module, dox,
            class_name=cls.name,
            indent=4,
        )
        typing_imports |= ti
        lines.append('')
        lines.append(mdef)
        has_methods = True

    if not has_methods:
        lines.append('')
        lines.append('    pass')

    return '\n'.join(lines), typing_imports


# ──────────────────────────────────────────────────────────────────────────────
# Module generation
# ──────────────────────────────────────────────────────────────────────────────

def generate_module(
    api: ModuleAPI,
    dox: DoxygenIndex,
    constants: dict[str, object],
    xml_dir: str,
    output_dir: str,
) -> None:
    """Generate a Python stub __init__.py for a Kodi module."""
    module = api.name
    typing_imports: set[str] = set()
    sections: list[str] = []

    # ── Module docstring ──────────────────────────────────────────────────────
    module_rst = ''
    if dox.top_compound is not None:
        has_inner_class = bool(dox.top_compound.findall('innerclass'))
        module_rst = group_module_to_rst(dox.top_compound, has_inner_class)
    if module_rst.strip():
        sections.append(f'"""\n{module_rst}\n"""')
    else:
        sections.append(f'"""\n**{module} module**\n"""')

    # ── Placeholder for imports (filled later) ────────────────────────────────
    import_placeholder = '<<IMPORTS>>'
    sections.append(import_placeholder)

    # ── Sentinel ─────────────────────────────────────────────────────────────
    sections.append('__kodistubs__ = True')

    # ── Constants ────────────────────────────────────────────────────────────
    if constants:
        const_lines = []
        for name in sorted(constants.keys()):
            val = constants[name]
            if isinstance(val, str):
                const_lines.append(f'{name} = {val!r}')
            else:
                const_lines.append(f'{name} = {val}')
        sections.append('\n'.join(const_lines))

    # ── Classes ──────────────────────────────────────────────────────────────
    for cls in api.classes:
        cls_code, ti = _generate_class(cls, module, dox, xml_dir)
        typing_imports |= ti
        sections.append(cls_code)

    # ── Module-level functions ────────────────────────────────────────────────
    for func in api.functions:
        func_code, ti = _generate_function(func, module, dox, indent=0)
        typing_imports |= ti
        sections.append(func_code)

    # ── Assemble imports ──────────────────────────────────────────────────────
    # Determine which typing names are actually used
    all_code = '\n\n'.join(s for s in sections if s != import_placeholder)

    # Also check for Optional usage (any param with default=None needs Optional)
    needs_optional = _check_needs_optional(api)
    if needs_optional:
        typing_imports.add('Optional')

    if typing_imports:
        import_line = f'from typing import {", ".join(sorted(typing_imports))}'
    else:
        import_line = ''

    # ── Final assembly ────────────────────────────────────────────────────────
    header = (
        '# This file is generated from Kodi source code and post-edited\n'
        '# to correct code style and docstrings formatting.\n'
        '# License: GPL v.3 <https://www.gnu.org/licenses/gpl-3.0.en.html>'
    )

    output_parts = [header]
    for section in sections:
        if section == import_placeholder:
            if import_line:
                output_parts.append(import_line)
        else:
            output_parts.append(section)

    content = '\n\n'.join(output_parts) + '\n'

    # Write output
    pkg_dir = os.path.join(output_dir, module)
    os.makedirs(pkg_dir, exist_ok=True)

    # Write __init__.py
    init_path = os.path.join(pkg_dir, '__init__.py')
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Write py.typed marker for PEP 561
    typed_path = os.path.join(pkg_dir, 'py.typed')
    if not os.path.exists(typed_path):
        with open(typed_path, 'w', encoding='utf-8') as f:
            pass


def _check_needs_optional(api: ModuleAPI) -> bool:
    """Check if any parameter has a None default (needs Optional import)."""
    def _check_params(params: list[Param]) -> bool:
        for p in params:
            if p.default in ('NULL', 'nullptr', '0x0', None):
                if p.cpp_type not in ('int', 'bool', 'double', 'float'):
                    return True
        return False

    for func in api.functions:
        if _check_params(func.params):
            return True
    for cls in api.classes:
        for method in cls.methods:
            if _check_params(method.params):
                return True
    return False
