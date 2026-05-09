"""Generate Python stub package files from parsed API + documentation."""
from __future__ import annotations

import os
import re
import textwrap
from typing import Optional

from .doc_converter import group_class_to_rst, group_module_to_rst, member_to_rst
from .doxy_parser import DoxygenIndex, get_class_doc, get_class_inheritance, get_member_doc
from .swig_parser import ClassDef, FunctionDef, ModuleAPI, Param
from .type_mapper import default_return, map_default_value, map_type

MAX_LINE_LENGTH = 120


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _indent(text: str, spaces: int = 4) -> str:
    prefix = ' ' * spaces
    return '\n'.join(prefix + line if line.strip() else line
                     for line in text.splitlines())


_TABLE_SEP_RE = re.compile(r'^\s*[=\-]+(\s+[=\-]+)+\s*$')
_GRID_TABLE_SEP_RE = re.compile(r'^\s*\+[=\-]+(\+[=\-]+)+\+\s*$')
_GRID_TABLE_ROW_RE = re.compile(r'^\s*\|.*\|\s*$')
_FIELD_LIST_RE = re.compile(r'^(:[\w]+(?:\s+[^:]+?)?:)\s+(.*)$')
_BULLET_RE = re.compile(r'^([-*])\s+(.*)$')
_DIRECTIVE_RE = re.compile(r'^\.\.\s+\w[\w\-]*::')


def _wrap_text(text: str, width: int) -> list[str]:
    """Wrap a single text run, never breaking long tokens (preserves inline RST
    markup like ``...``, **...** that may exceed the width)."""
    return textwrap.wrap(text, width=width,
                         break_long_words=False,
                         break_on_hyphens=False) or [text]


def _wrap_literal_block(block: str, width: int) -> str:
    """Wrap Python code lines inside an RST literal block to fit ``width`` chars.

    Each over-length line is wrapped using :func:`_wrap_code_line`, which understands
    Python comments and bracket structure (it splits at top-level commas inside the
    outermost ``(...)`` / ``[...]`` / ``{...}``). Lines that already fit, and lines
    that cannot be safely split, are emitted verbatim.
    """
    out: list[str] = []
    for line in block.split('\n'):
        if len(line) <= width:
            out.append(line)
        else:
            out.extend(_wrap_code_line(line, width))
    return '\n'.join(out)


_COMMENT_PREFIX_RE = re.compile(r'^(#+\s*)(.*)$')


def _wrap_code_line(line: str, width: int) -> list[str]:
    """Wrap one Python code line. Comments wrap as ``# …`` text; statements split at
    top-level commas inside their outermost bracket pair (hanging indent)."""
    stripped = line.lstrip()
    indent = line[:len(line) - len(stripped)]
    if not stripped:
        return [line]

    if stripped.startswith('#'):
        m = _COMMENT_PREFIX_RE.match(stripped)
        if not m:
            return [line]
        prefix = m.group(1)
        content = m.group(2)
        avail = max(20, width - len(indent) - len(prefix))
        wrapped = textwrap.wrap(content, width=avail,
                                break_long_words=False,
                                break_on_hyphens=False)
        if not wrapped:
            return [line]
        return [indent + prefix + w for w in wrapped]

    split = _split_code_at_bracket(line, width)
    if split is not None:
        return split
    return [line]


def _split_code_at_bracket(line: str, width: int) -> Optional[list[str]]:
    """Try to wrap a Python statement by inserting newlines after top-level commas
    inside its outermost bracket pair. Returns the wrapped lines or ``None`` if no
    safe split exists or the result still exceeds ``width``."""
    depth = 0
    in_string: Optional[str] = None
    escape = False
    open_pos: Optional[int] = None
    splits: list[int] = []  # offsets just after a top-level comma
    for i, ch in enumerate(line):
        if escape:
            escape = False
            continue
        if in_string is not None:
            if ch == '\\':
                escape = True
            elif ch == in_string:
                in_string = None
            continue
        if ch == '#':
            break  # inline comment — stop scanning
        if ch in "\"'":
            in_string = ch
            continue
        if ch in '([{':
            if depth == 0:
                open_pos = i
            depth += 1
            continue
        if ch in ')]}':
            depth -= 1
            continue
        if ch == ',' and depth == 1:
            splits.append(i + 1)

    if open_pos is None or not splits:
        return None

    cont_indent = ' ' * (open_pos + 1)
    pieces: list[str] = []
    last = 0
    for pos in splits:
        pieces.append(line[last:pos])
        last = pos
    pieces.append(line[last:])

    out: list[str] = []
    current = pieces[0]
    for piece in pieces[1:]:
        candidate = current + piece
        if len(candidate) <= width:
            current = candidate
        else:
            out.append(current.rstrip())
            current = cont_indent + piece.lstrip()
    out.append(current.rstrip())

    if any(len(line_) > width for line_ in out):
        return None
    return out


def _wrap_paragraph(lines: list[str], width: int, indent_str: str) -> str:
    """Wrap one prose paragraph (already stripped of its leading indent) to ``width``."""
    joined = ' '.join(line.strip() for line in lines if line.strip())
    if not joined:
        return ''
    avail = max(20, width - len(indent_str))
    wrapped = _wrap_text(joined, avail)
    return '\n'.join(indent_str + w for w in wrapped)


def _wrap_field_or_bullet(entry_lines: list[str], width: int, indent_str: str,
                          marker: str, body: str,
                          cont_extra: str) -> str:
    """Wrap a single field-list or bullet-list entry.

    ``marker`` is the leading marker text including its trailing space (e.g. ``:param x: ``
    or ``- ``); ``body`` is the rest of the first line; ``entry_lines`` is the full set of
    raw lines belonging to this entry (subsequent continuations get joined into ``body``).
    ``cont_extra`` is added to ``indent_str`` for continuation lines.
    """
    extra_text = ' '.join(line.strip() for line in entry_lines[1:] if line.strip())
    full_body = (body + (' ' + extra_text if extra_text else '')).strip()
    first_avail = max(20, width - len(indent_str) - len(marker))
    wrapped_body = _wrap_text(full_body, first_avail)
    out = [indent_str + marker + wrapped_body[0]]
    cont_indent = indent_str + cont_extra
    cont_avail = max(20, width - len(cont_indent))
    if len(wrapped_body) > 1:
        rejoined = ' '.join(wrapped_body[1:])
        for cont in _wrap_text(rejoined, cont_avail):
            out.append(cont_indent + cont)
    return '\n'.join(out)


def _wrap_block(block: str, width: int, is_literal: bool = False) -> str:
    """Wrap one RST block (delimited by blank lines) to ``width`` chars per line.

    A field-list block (``:param x: …`` lines) or bullet block is split internally and
    each entry wrapped separately. Tables are preserved. Literal blocks (Python code
    samples) are wrapped at bracket-safe points by ``_wrap_literal_block``.
    """
    if not block.strip():
        return block
    if is_literal:
        return _wrap_literal_block(block, width)
    lines = block.split('\n')

    # Tables: any '===' / '---' simple-table separator, or any grid-table
    # ('+---+---+' / '|cell|cell|') line, disqualifies wrapping.
    if any(_TABLE_SEP_RE.match(line) or _GRID_TABLE_SEP_RE.match(line)
           or _GRID_TABLE_ROW_RE.match(line) for line in lines):
        return block

    # Determine block-leading indent (smallest non-empty-line indent).
    indents = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
    block_indent = min(indents) if indents else 0
    indent_str = ' ' * block_indent

    # Strip the common indent so we work with logically unindented content.
    body_lines = [l[block_indent:] if len(l) >= block_indent else l for l in lines]
    first_stripped = body_lines[0]

    # Directive header line (".. note::", ".. xxx::") — leave as is. Directive content,
    # which arrives in a separate block, is wrapped as paragraphs by the normal path.
    if _DIRECTIVE_RE.match(first_stripped):
        return block

    # Field list: split by lines that begin a new ``:fieldname value: …`` entry.
    if _FIELD_LIST_RE.match(first_stripped):
        entries: list[list[str]] = []
        current: list[str] = []
        for ln in body_lines:
            if _FIELD_LIST_RE.match(ln) and current:
                entries.append(current)
                current = [ln]
            else:
                current.append(ln)
        if current:
            entries.append(current)
        out = []
        for entry in entries:
            m = _FIELD_LIST_RE.match(entry[0])
            if not m:
                out.append(_wrap_paragraph(entry, width, indent_str))
                continue
            marker = m.group(1) + ' '
            body = m.group(2)
            out.append(_wrap_field_or_bullet(entry, width, indent_str,
                                              marker, body, '    '))
        return '\n'.join(out)

    # Bullet list: split by lines starting with "- " / "* ".
    if _BULLET_RE.match(first_stripped):
        entries = []
        current = []
        for ln in body_lines:
            if _BULLET_RE.match(ln) and current:
                entries.append(current)
                current = [ln]
            else:
                current.append(ln)
        if current:
            entries.append(current)
        out = []
        for entry in entries:
            m = _BULLET_RE.match(entry[0])
            if not m:
                out.append(_wrap_paragraph(entry, width, indent_str))
                continue
            marker = m.group(1) + ' '
            body = m.group(2)
            out.append(_wrap_field_or_bullet(entry, width, indent_str,
                                              marker, body, '  '))
        return '\n'.join(out)

    # Plain paragraph (possibly indented under a directive).
    return _wrap_paragraph(body_lines, width, indent_str)


def _wrap_rst_docstring(rst: str, available_width: int) -> str:
    """Wrap an RST docstring to fit ``available_width`` chars per line.

    The input is split on blank-line boundaries and each block is wrapped according to
    its kind. A block immediately following a paragraph ending with bare ``::`` (the
    literal-block sentinel — distinct from an explicit ``.. directive::`` whose content
    is prose) is preserved verbatim.
    """
    blocks = re.split(r'\n[ \t]*\n', rst.rstrip())
    out_blocks = []
    prev_ends_literal = False
    for block in blocks:
        out_blocks.append(_wrap_block(block, available_width,
                                       is_literal=prev_ends_literal))
        last_lines = [l for l in out_blocks[-1].split('\n') if l.strip()]
        if last_lines:
            last = last_lines[-1].rstrip()
            # ``::`` at end is a literal-block sentinel ONLY when not part of a
            # ``.. directive::`` line. Directive content following is prose.
            prev_ends_literal = (
                last.endswith('::')
                and not _DIRECTIVE_RE.match(last_lines[-1].lstrip())
            )
        else:
            prev_ends_literal = False
    return '\n\n'.join(out_blocks)


def _format_docstring(rst: str, indent: int = 4) -> str:
    """Wrap an RST string as an indented docstring, enforcing the 120-char line cap."""
    if not rst.strip():
        return ''
    available = max(40, MAX_LINE_LENGTH - indent)
    # Escape backslashes for the Python source BEFORE wrapping so the wrap width
    # measures against the bytes that actually land on disk (each ``\`` becomes
    # ``\\`` and would otherwise push the line one column over).
    escaped = rst.replace('\\', '\\\\')
    wrapped_rst = _wrap_rst_docstring(escaped, available)
    prefix = ' ' * indent
    lines = ['"""']
    for line in wrapped_rst.rstrip().splitlines():
        lines.append(line)
    lines.append('"""')
    return textwrap.indent('\n'.join(lines), prefix)


def _needs_optional(params: list[Param]) -> bool:
    return any(p.default is not None for p in params)


def _build_signature(func: FunctionDef, module: str,
                     typedefs: Optional[dict] = None,
                     is_method: bool = False,
                     def_indent: int = 0,
                     name_len: int = 0) -> tuple[str, set[str], set[str]]:
    """Build a Python function signature string and collect typing imports.

    Returns ``(signature_str, typing_imports, external_modules)`` — external
    modules are other ``xbmc*`` stub modules referenced by the annotations,
    which the caller emits inside an ``if TYPE_CHECKING:`` block.

    ``def_indent`` is the column at which the ``def`` keyword starts (0 for a
    module-level function, 4 for a method). ``name_len`` is the function name
    length. They're used to decide whether the one-line signature would push the
    full ``def …:`` line past ``MAX_LINE_LENGTH``; if so, parameters are split,
    one per indented line.
    """
    typing_imports: set[str] = set()
    external_modules: set[str] = set()
    parts = []
    if is_method:
        parts.append('self')
    for param in func.params:
        py_type, ti, ext = map_type(param.cpp_type, module, typedefs)
        typing_imports |= ti
        external_modules |= ext
        if param.default is not None:
            py_default = map_default_value(param.default)
            if py_default == 'None' and not py_type.startswith('Optional'):
                py_type = f'Optional[{py_type}]'
                typing_imports.add('Optional')
            parts.append(f'{param.name}: {py_type} = {py_default}')
        else:
            parts.append(f'{param.name}: {py_type}')

    py_ret, ti, ext = map_type(func.cpp_return_type, module, typedefs)
    typing_imports |= ti
    external_modules |= ext

    if func.is_constructor:
        return_ann = ' -> None'
    elif py_ret == 'None':
        return_ann = ' -> None'
    else:
        return_ann = f' -> {py_ret}'

    params_str = ', '.join(parts)
    one_line = f'({params_str}){return_ann}'
    # The full source line is: <def_indent spaces>def <name><sig>:
    full_len = def_indent + len('def ') + name_len + len(one_line) + 1
    if full_len <= MAX_LINE_LENGTH or not parts:
        return one_line, typing_imports, external_modules

    # One-line is too long: emit one parameter per indented line.
    inner_indent = ' ' * (def_indent + 4)
    close_indent = ' ' * def_indent
    rendered = '(\n'
    for p in parts:
        rendered += f'{inner_indent}{p},\n'
    rendered += f'{close_indent}){return_ann}'
    return rendered, typing_imports, external_modules


# ──────────────────────────────────────────────────────────────────────────────
# Function / method generation
# ──────────────────────────────────────────────────────────────────────────────

def _generate_function(func: FunctionDef, module: str,
                       dox: DoxygenIndex,
                       typedefs: Optional[dict] = None,
                       class_name: Optional[str] = None,
                       indent: int = 0) -> tuple[str, set[str], set[str]]:
    """Generate a Python function/method definition string.

    Returns ``(code, typing_imports, external_modules)``.
    """
    typing_imports: set[str] = set()
    external_modules: set[str] = set()
    prefix = ' ' * indent
    lines = []

    func_name = func.name
    sig, ti, ext = _build_signature(func, module, typedefs,
                                    is_method=class_name is not None,
                                    def_indent=indent,
                                    name_len=len(func_name))
    typing_imports |= ti
    external_modules |= ext

    py_ret, _, _ = map_type(func.cpp_return_type, module, typedefs)
    body_stmt = default_return(py_ret)

    lines.append(f'{prefix}def {func_name}{sig}:')

    # Docstring
    memberdef = get_member_doc(dox, func_name, class_name)
    if memberdef is not None:
        rst = member_to_rst(memberdef)
    else:
        rst = ''

    if rst.strip():
        lines.append(_format_docstring(rst, indent + 4))

    # Body (may span multiple lines, e.g. a local import + return)
    for stmt in body_stmt.split('\n'):
        lines.append(f'{prefix}    {stmt}')

    return '\n'.join(lines), typing_imports, external_modules


# ──────────────────────────────────────────────────────────────────────────────
# Class generation
# ──────────────────────────────────────────────────────────────────────────────

def _generate_class(cls: ClassDef, module: str,
                    dox: DoxygenIndex, xml_dir: str,
                    typedefs: Optional[dict] = None) -> tuple[str, set[str], set[str]]:
    """Generate a Python class definition string.

    Returns ``(code, typing_imports, external_modules)``.
    """
    typing_imports: set[str] = set()
    external_modules: set[str] = set()
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
        mdef, ti, ext = _generate_function(
            method, module, dox,
            typedefs=typedefs,
            class_name=cls.name,
            indent=4,
        )
        typing_imports |= ti
        external_modules |= ext
        lines.append('')
        lines.append(mdef)
        has_methods = True

    if not has_methods:
        lines.append('')
        lines.append('    pass')

    return '\n'.join(lines), typing_imports, external_modules


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
    external_modules: set[str] = set()

    # Build sections as (kind, text) tuples. ``kind`` controls PEP-8 spacing:
    #   - top-level class/function definitions ('def') are surrounded by two blank
    #     lines (i.e. preceded and followed by ``\n\n\n`` joiners);
    #   - everything else ('stmt') is separated by a single blank line.
    sections: list[tuple[str, str]] = []

    # ── Module docstring ──────────────────────────────────────────────────────
    module_rst = ''
    if dox.top_compound is not None:
        has_inner_class = bool(dox.top_compound.findall('innerclass'))
        module_rst = group_module_to_rst(dox.top_compound, has_inner_class)
    if module_rst.strip():
        wrapped_rst = _wrap_rst_docstring(module_rst, MAX_LINE_LENGTH)
        escaped = '\n'.join(line.replace('\\', '\\\\') for line in wrapped_rst.splitlines())
        sections.append(('stmt', f'"""\n{escaped}\n"""'))
    else:
        sections.append(('stmt', f'"""\n**{module} module**\n"""'))

    # ── Imports (filled in below once typing usage is known) ──────────────────
    sections.append(('imports', '<<IMPORTS>>'))

    # ── Sentinel ─────────────────────────────────────────────────────────────
    sections.append(('stmt', '__kodistubs__ = True'))

    # ── Constants ────────────────────────────────────────────────────────────
    if constants:
        const_lines = []
        for name in sorted(constants.keys()):
            val = constants[name]
            if isinstance(val, str):
                const_lines.append(f'{name} = {val!r}')
            else:
                const_lines.append(f'{name} = {val}')
        sections.append(('stmt', '\n'.join(const_lines)))

    # ── Classes ──────────────────────────────────────────────────────────────
    for cls in api.classes:
        cls_code, ti, ext = _generate_class(cls, module, dox, xml_dir, api.typedefs)
        typing_imports |= ti
        external_modules |= ext
        sections.append(('def', cls_code))

    # ── Module-level functions ────────────────────────────────────────────────
    for func in api.functions:
        func_code, ti, ext = _generate_function(func, module, dox,
                                                typedefs=api.typedefs, indent=0)
        typing_imports |= ti
        external_modules |= ext
        sections.append(('def', func_code))

    # ── Assemble imports ──────────────────────────────────────────────────────
    needs_optional = _check_needs_optional(api)
    if needs_optional:
        typing_imports.add('Optional')

    # Don't import the current module from itself (defensive — should never happen
    # since same-module refs are emitted unqualified).
    external_modules.discard(module)

    # ``TYPE_CHECKING`` is only needed if there are cross-module class refs.
    if external_modules:
        typing_imports.add('TYPE_CHECKING')

    import_block_lines: list[str] = ['from __future__ import annotations']
    if typing_imports:
        import_block_lines.append(
            f'from typing import {", ".join(sorted(typing_imports))}'
        )
    if external_modules:
        import_block_lines.append('')
        import_block_lines.append('if TYPE_CHECKING:')
        for mod in sorted(external_modules):
            import_block_lines.append(f'    import {mod}')
    import_block = '\n'.join(import_block_lines)

    # ── Final assembly ────────────────────────────────────────────────────────
    header = (
        '# This file is generated from Kodi source code and post-edited\n'
        '# to correct code style and docstrings formatting.\n'
        '# License: GPL v.3 <https://www.gnu.org/licenses/gpl-3.0.en.html>'
    )

    final_sections: list[tuple[str, str]] = [('stmt', header)]
    for kind, text in sections:
        if kind == 'imports':
            final_sections.append(('stmt', import_block))
        else:
            final_sections.append((kind, text))

    content = _join_with_pep8_spacing(final_sections) + '\n'

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


def _join_with_pep8_spacing(sections: list[tuple[str, str]]) -> str:
    """Join ``(kind, text)`` sections with PEP 8 vertical whitespace.

    A boundary that touches a top-level ``'def'`` section (class or function) gets
    two blank lines between it and its neighbour; all other boundaries get one
    blank line. Method definitions inside classes are produced with their own
    single-blank-line separators by ``_generate_class`` and untouched here.
    """
    parts: list[str] = []
    for i, (kind, text) in enumerate(sections):
        if i == 0:
            parts.append(text)
            continue
        prev_kind = sections[i - 1][0]
        sep = '\n\n\n' if 'def' in (kind, prev_kind) else '\n\n'
        parts.append(sep + text)
    return ''.join(parts)


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
