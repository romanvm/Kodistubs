"""Convert Doxygen XML elements to reStructuredText docstrings."""
from __future__ import annotations
import re
import textwrap
import xml.etree.ElementTree as ET
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# Inline element conversion (returns text WITHOUT elem.tail)
# ──────────────────────────────────────────────────────────────────────────────

def _inner_text(elem: ET.Element) -> str:
    """Concatenate text and recursively converted children (no tail)."""
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        parts.append(_inline(child))   # includes child.tail
    return ''.join(parts)


def _inline(elem: ET.Element) -> str:
    """Convert an inline Doxygen element to RST, including elem.tail."""
    tag = elem.tag
    inner = _inner_text(elem)
    tail = elem.tail or ''

    if tag == 'bold':
        return f'**{inner}**' + tail
    if tag == 'emphasis':
        return f'*{inner}*' + tail
    if tag == 'computeroutput':
        return f'``{inner}``' + tail
    if tag == 'ref':
        return inner + tail
    if tag == 'ulink':
        url = elem.get('url', '')
        if url:
            return f'`{inner} <{url}>`_' + tail
        return inner + tail
    if tag == 'sp':
        return ' ' + tail
    if tag == 'linebreak':
        return '\n' + tail
    if tag in ('hruler', 'ndash', 'mdash'):
        return ('' if tag == 'hruler' else ('--' if tag == 'ndash' else '---')) + tail
    # Block-level children (handled elsewhere): return only tail
    if tag in ('parameterlist', 'simplesect', 'programlisting',
                'table', 'sect2', 'sect3', 'orderedlist', 'itemizedlist'):
        return tail
    # Fallback: inner text
    return inner + tail


def _para_inline(para: ET.Element) -> str:
    """Return the inline text of a <para>, stripping block children."""
    parts = []
    if para.text:
        parts.append(para.text)
    for child in para:
        # For inline collection we skip block-level children entirely
        if child.tag in ('parameterlist', 'simplesect', 'programlisting',
                         'table', 'sect2', 'sect3', 'orderedlist', 'itemizedlist'):
            if child.tail:
                parts.append(child.tail)
        else:
            parts.append(_inline(child))
    return ''.join(parts).strip()


def _clean_python_marker(text: str) -> str:
    r"""Strip \python_func{...} and \python_class{...} markers."""
    text = re.sub(r'\\python_func\{[^}]*\}\s*', '', text)
    text = re.sub(r'\\python_class\{[^}]*\}\s*', '', text)
    return text.strip()


# ──────────────────────────────────────────────────────────────────────────────
# Table → RST
# ──────────────────────────────────────────────────────────────────────────────

def _table_to_rst(elem: ET.Element) -> str:
    rows = elem.findall('row')
    if not rows:
        return ''
    cell_data = []
    for row in rows:
        cell_data.append([_para_inline(c) if c.find('para') is not None
                          else (c.text or '').strip()
                          for c in row.findall('entry')])
    if not cell_data:
        return ''
    num_cols = max(len(r) for r in cell_data)
    for row in cell_data:
        while len(row) < num_cols:
            row.append('')
    widths = [max(len(cell_data[r][c]) for r in range(len(cell_data)))
              for c in range(num_cols)]
    widths = [max(w, 1) for w in widths]
    sep = ' '.join('=' * w for w in widths)
    lines = [sep]
    for i, row in enumerate(cell_data):
        line = ' '.join(c.ljust(widths[j]) for j, c in enumerate(row))
        lines.append(line)
        if i == 0 and len(cell_data) > 1:
            lines.append(sep)
    lines.append(sep)
    return '\n' + '\n'.join(lines) + '\n'


# ──────────────────────────────────────────────────────────────────────────────
# Code block → RST
# ──────────────────────────────────────────────────────────────────────────────

def _listing_to_rst(elem: ET.Element) -> str:
    lines = []
    for codeline in elem.findall('codeline'):
        parts = []
        for hl in codeline.findall('highlight'):
            if hl.text:
                parts.append(hl.text)
            for child in hl:
                if child.tag == 'sp':
                    parts.append(' ')
                    if child.tail:
                        parts.append(child.tail)
                elif child.tag == 'ref':
                    parts.append(_inner_text(child))
                    if child.tail:
                        parts.append(child.tail)
                else:
                    if child.text:
                        parts.append(child.text)
                    if child.tail:
                        parts.append(child.tail)
            if hl.tail:
                parts.append(hl.tail)
        lines.append(''.join(parts))
    code_lines = '\n'.join(lines)
    result = '\nExample::\n\n'
    for line in code_lines.splitlines():
        result += f'    {line}\n'
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Block-level para conversion (used for simple/nested paras)
# ──────────────────────────────────────────────────────────────────────────────

def _para_to_rst(para: ET.Element) -> str:
    """Convert a <para> to RST, handling both inline and block children."""
    sections: list[str] = []
    inline_buf: list[str] = []

    def flush_inline() -> None:
        text = ''.join(inline_buf).strip()
        inline_buf.clear()
        if text:
            text = _clean_python_marker(text)
            if text:
                sections.append(text)

    if para.text:
        inline_buf.append(para.text)

    for child in para:
        tag = child.tag
        tail = child.tail or ''

        if tag == 'parameterlist':
            flush_inline()
            kind = child.get('kind', 'param')
            for item in child.findall('parameteritem'):
                names = []
                for nameelem in item.findall('.//parametername'):
                    n = _para_inline(nameelem) if nameelem.find('para') is not None \
                        else (nameelem.text or '').strip()
                    if n:
                        names.append(n)
                name_str = ', '.join(names)
                desc_elem = item.find('parameterdescription')
                desc = ''
                if desc_elem is not None:
                    parts = []
                    for p in desc_elem.findall('para'):
                        parts.append(_para_inline(p))
                    desc = ' '.join(parts).strip()
                if kind == 'param':
                    sections.append(f':param {name_str}: {desc}')
                elif kind == 'exception':
                    sections.append(f':raises {name_str}: {desc}')
            if tail:
                inline_buf.append(tail)

        elif tag == 'simplesect':
            flush_inline()
            kind = child.get('kind', '')
            content_parts = []
            for p in child.findall('para'):
                content_parts.append(_para_inline(p))
            content = ' '.join(content_parts).strip()
            if kind == 'return':
                sections.append(f':return: {content}')
            elif kind == 'rtype':
                sections.append(f':rtype: {content}')
            elif kind in ('note', 'attention', 'warning'):
                if content:
                    directive = {'note': '.. note::', 'attention': '.. attention::',
                                 'warning': '.. warning::'}[kind]
                    indented = textwrap.indent(content, '    ')
                    sections.append(f'{directive}\n\n{indented}')
            else:
                if content:
                    sections.append(content)
            if tail:
                inline_buf.append(tail)

        elif tag == 'programlisting':
            # Discard any inline text that is just an "Example:" label
            inline_text = ''.join(inline_buf).strip()
            inline_buf.clear()
            cleaned = _clean_python_marker(inline_text)
            _example_pat = re.compile(r'^\*{0,2}Example:?\*{0,2}$', re.I)
            if cleaned and not _example_pat.match(cleaned.strip()):
                sections.append(cleaned)
            sections.append(_listing_to_rst(child))
            if tail:
                inline_buf.append(tail)

        elif tag == 'table':
            flush_inline()
            sections.append(_table_to_rst(child))
            if tail:
                inline_buf.append(tail)

        elif tag == 'hruler':
            # Skip — just keep the tail
            if tail:
                inline_buf.append(tail)

        elif tag in ('orderedlist', 'itemizedlist'):
            flush_inline()
            for listitem in child.findall('listitem'):
                item_parts = []
                for p in listitem.findall('para'):
                    item_parts.append(_para_inline(p))
                sections.append('- ' + ' '.join(item_parts).strip())
            if tail:
                inline_buf.append(tail)

        elif tag in ('sect2', 'sect3'):
            flush_inline()
            for p in child.findall('para'):
                rst = _para_to_rst(p)
                if rst:
                    sections.append(rst)
            if tail:
                inline_buf.append(tail)

        else:
            # Inline element — use _inline() which includes its tail
            inline_buf.append(_inline(child))
            # _inline already appended tail, so don't double-add

    flush_inline()
    return '\n\n'.join(s for s in sections if s.strip())


# ──────────────────────────────────────────────────────────────────────────────
# Top-level converters
# ──────────────────────────────────────────────────────────────────────────────

_BLOCK_TAGS = frozenset({
    'parameterlist', 'simplesect', 'programlisting',
    'table', 'orderedlist', 'itemizedlist', 'sect2', 'sect3',
})

_EXAMPLE_PAT = re.compile(r'^\*{0,2}Example:?\*{0,2}$', re.I)

_DIRECTIVES = {
    'note': '.. note::',
    'attention': '.. attention::',
    'warning': '.. warning::',
}


def _process_detail_para(
    para: ET.Element,
    desc_parts: list[str],
    param_parts: list[str],
    return_parts: list[str],
    raise_parts: list[str],
    note_parts: list[str],
    version_parts: list[str],
    example_parts: list[str],
) -> None:
    """Process one <para> from a detaileddescription into the appropriate buckets."""
    children_tags = {child.tag for child in para}
    has_block = bool(children_tags & _BLOCK_TAGS)

    if not has_block:
        raw_xml = ET.tostring(para, encoding='unicode')
        rst = _para_to_rst(para).strip()
        rst = _clean_python_marker(rst)
        if rst:
            if '@python_v' in raw_xml:
                version_parts.append(rst)
            else:
                desc_parts.append(rst)
        return

    # Para has block children — process each child individually
    inline_buf: list[str] = []
    if para.text:
        inline_buf.append(para.text)

    for child in para:
        tag = child.tag
        tail = child.tail or ''

        if tag == 'parameterlist':
            kind = child.get('kind', 'param')
            for item in child.findall('parameteritem'):
                names = []
                for nameelem in item.findall('.//parametername'):
                    n = (nameelem.text or '').strip()
                    if n:
                        names.append(n)
                name_str = ', '.join(names)
                desc_elem = item.find('parameterdescription')
                desc = ''
                if desc_elem is not None:
                    parts = [_para_inline(p) for p in desc_elem.findall('para')]
                    desc = ' '.join(parts).strip()
                if kind == 'param':
                    param_parts.append(f':param {name_str}: {desc}')
                elif kind == 'exception':
                    raise_parts.append(f':raises {name_str}: {desc}')
            if tail:
                inline_buf.append(tail)

        elif tag == 'simplesect':
            kind = child.get('kind', '')
            content = ' '.join(_para_inline(p) for p in child.findall('para')).strip()
            if kind == 'return':
                return_parts.append(f':return: {content}')
            elif kind == 'rtype':
                return_parts.append(f':rtype: {content}')
            elif kind in _DIRECTIVES:
                if content:
                    directive = _DIRECTIVES[kind]
                    indented = textwrap.indent(content, '    ')
                    note_parts.append(f'{directive}\n\n{indented}')
            else:
                if content:
                    note_parts.append(content)
            if tail:
                inline_buf.append(tail)

        elif tag == 'programlisting':
            inline_text = ''.join(inline_buf).strip()
            inline_buf.clear()
            cleaned = _clean_python_marker(inline_text)
            if cleaned and not _EXAMPLE_PAT.match(cleaned):
                desc_parts.append(cleaned)
            example_parts.append(_listing_to_rst(child))
            if tail:
                inline_buf.append(tail)

        elif tag == 'table':
            table_rst = _table_to_rst(child)
            if table_rst.strip():
                note_parts.append(table_rst)
            if tail:
                inline_buf.append(tail)

        elif tag in ('orderedlist', 'itemizedlist'):
            items = []
            for listitem in child.findall('listitem'):
                item_parts = [_para_inline(p) for p in listitem.findall('para')]
                items.append('- ' + ' '.join(item_parts).strip())
            if items:
                note_parts.append('\n'.join(items))
            if tail:
                inline_buf.append(tail)

        elif tag in ('sect2', 'sect3'):
            for p in child.findall('para'):
                rst = _para_to_rst(p)
                if rst:
                    note_parts.append(rst)
            if tail:
                inline_buf.append(tail)

        elif tag == 'hruler':
            if tail:
                inline_buf.append(tail)

        else:
            # inline element — _inline() includes tail
            inline_buf.append(_inline(child))

    # Classify accumulated inline content
    inline_text = ''.join(inline_buf).strip()
    inline_text = _clean_python_marker(inline_text)
    if inline_text:
        raw_xml = ET.tostring(para, encoding='unicode')
        if '@python_v' in raw_xml:
            version_parts.append(inline_text)
        # else: trailing inline after block — discard (usually noise)


def description_to_rst(brief: Optional[ET.Element],
                        detail: Optional[ET.Element],
                        include_detail: bool = True) -> str:
    """Merge brief + detailed descriptions into a single RST string."""
    sections: list[str] = []

    # --- Brief ---
    if brief is not None:
        brief_parts = []
        for para in brief.findall('para'):
            text = _para_inline(para)
            text = _clean_python_marker(text)
            if text:
                brief_parts.append(text)
        brief_text = ' '.join(brief_parts).strip()
        if brief_text:
            sections.append(brief_text)

    if not include_detail or detail is None:
        return '\n\n'.join(sections)

    # --- Detailed ---
    desc_parts: list[str] = []
    param_parts: list[str] = []
    return_parts: list[str] = []
    raise_parts: list[str] = []
    note_parts: list[str] = []
    version_parts: list[str] = []
    example_parts: list[str] = []

    for para in detail.findall('para'):
        # Skip pure \python_class / \python_func marker paragraphs
        raw_inline = _para_inline(para)
        if re.match(r'^\\python_(class|func)\{', raw_inline):
            continue

        _process_detail_para(
            para,
            desc_parts, param_parts, return_parts, raise_parts,
            note_parts, version_parts, example_parts,
        )

    if desc_parts:
        sections.append('\n\n'.join(desc_parts))
    if param_parts:
        sections.append('\n'.join(param_parts))
    if return_parts:
        sections.append('\n'.join(return_parts))
    if raise_parts:
        sections.append('\n'.join(raise_parts))
    if note_parts:
        sections.append('\n\n'.join(note_parts))
    for vp in version_parts:
        if vp:
            sections.append(vp)
    for ep in example_parts:
        ep = ep.strip()
        if ep:
            sections.append(ep)

    return '\n\n'.join(s for s in sections if s.strip())


def member_to_rst(memberdef: ET.Element) -> str:
    """Extract RST docstring content from a Doxygen memberdef element."""
    brief = memberdef.find('briefdescription')
    detail = memberdef.find('detaileddescription')
    return description_to_rst(brief, detail, include_detail=True)


def group_class_to_rst(compounddef: ET.Element) -> str:
    """Extract class docstring from the group that documents it (brief + detail)."""
    brief = compounddef.find('briefdescription')
    detail = compounddef.find('detaileddescription')
    return description_to_rst(brief, detail, include_detail=True)


def group_module_to_rst(compounddef: ET.Element, has_inner_class: bool = False) -> str:
    """Extract module docstring from a group.

    When the group primarily describes a class (has_inner_class=True), only the
    brief description is used for the module-level docstring.
    """
    brief = compounddef.find('briefdescription')
    detail = compounddef.find('detaileddescription')
    return description_to_rst(brief, detail, include_detail=not has_inner_class)
