"""Convert Doxygen XML elements to reStructuredText docstrings."""
from __future__ import annotations

import re
import textwrap
import xml.etree.ElementTree as ET
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# Inline element conversion (returns text WITHOUT elem.tail)
# ──────────────────────────────────────────────────────────────────────────────

_LONE_STAR_RE = re.compile(r'(?<![A-Za-z0-9_])\*(?![A-Za-z0-9_])')


def _escape_rst_inline(text: str) -> str:
    """Escape characters with special RST inline meaning that appear in plain text.

    Doxygen represents bold/emphasis with explicit ``<bold>`` / ``<emphasis>`` elements;
    we add ``**...**`` / ``*...*`` markup ourselves from those. Raw text content from
    ``elem.text`` / ``elem.tail`` therefore contains no intentional inline markup, but
    a stray ``*`` (e.g. ``(default format: *)``) at an emphasis start-string position
    or any ``|`` (substitution-reference marker, e.g. ``"|68,69,59|..."``) would be
    mis-parsed by docutils. Pipes are always escaped; asterisks only when they sit at
    a position where RST would otherwise treat them as emphasis start (i.e. not
    adjacent to a word character on either side — ``SERVER_*`` is left alone).
    """
    text = text.replace('|', r'\|')
    text = _LONE_STAR_RE.sub(r'\\*', text)
    return text


def _inner_text(elem: ET.Element) -> str:
    """Concatenate text and recursively converted children (no tail)."""
    parts = []
    if elem.text:
        parts.append(_escape_rst_inline(elem.text))
    for child in elem:
        parts.append(_inline(child))   # includes child.tail
    return ''.join(parts)


def _inline(elem: ET.Element) -> str:
    """Convert an inline Doxygen element to RST, including elem.tail."""
    tag = elem.tag
    inner = _inner_text(elem)
    tail = _escape_rst_inline(elem.tail) if elem.tail else ''

    if tag == 'bold':
        # Split multi-sentence bold runs into separate **...** segments so that
        # Sphinx's autosummary, which truncates at the first ". ", does not leave a
        # ``**`` unclosed (upstream Sphinx bug in ``extract_summary``).
        if re.search(r'\.\s+\S', inner):
            segments = [s.strip() for s in re.split(r'(?<=\.)\s+', inner) if s.strip()]
            return ' '.join(f'**{s}**' for s in segments) + tail
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
    """Return the inline text of a <para>, stripping block children.

    Collapses whitespace (including stray newlines from XML formatting) into single
    spaces so the result is a clean single-line string suitable for inline RST contexts
    like bullet items, parameter descriptions, and table cells.
    """
    parts = []
    if para.text:
        parts.append(_escape_rst_inline(para.text))
    for child in para:
        # For inline collection we skip block-level children entirely
        if child.tag in ('parameterlist', 'simplesect', 'programlisting',
                         'table', 'sect2', 'sect3', 'orderedlist', 'itemizedlist'):
            if child.tail:
                parts.append(_escape_rst_inline(child.tail))
        else:
            parts.append(_inline(child))
    return re.sub(r'\s+', ' ', ''.join(parts)).strip()


def _extract_block_children(para: ET.Element,
                            tags: tuple = ('table',)) -> list[ET.Element]:
    """Return block-level child elements of ``<para>`` matching ``tags``.

    Used to pull out tables (and other block content) embedded inside a
    ``<parameterdescription>`` so they can be re-emitted after the RST field list
    rather than silently dropped by ``_para_inline``.
    """
    return [c for c in para if c.tag in tags]


def _clean_python_marker(text: str) -> str:
    r"""Strip \python_func{...} and \python_class{...} markers."""
    text = re.sub(r'\\python_func\{[^}]*\}\s*', '', text)
    text = re.sub(r'\\python_class\{[^}]*\}\s*', '', text)
    return text.strip()


# ──────────────────────────────────────────────────────────────────────────────
# Table → RST
# ──────────────────────────────────────────────────────────────────────────────

_TABLE_TARGET_WIDTH = 110   # leave headroom under the 120-char limit after indent


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
    natural = [max(len(cell_data[r][c]) for r in range(len(cell_data)))
               for c in range(num_cols)]
    natural = [max(w, 1) for w in natural]

    # Simple-table cost = sum(widths) + (num_cols - 1) spaces.
    if sum(natural) + (num_cols - 1) <= _TABLE_TARGET_WIDTH:
        sep = ' '.join('=' * w for w in natural)
        lines = [sep]
        for i, row in enumerate(cell_data):
            line = ' '.join(c.ljust(natural[j]) for j, c in enumerate(row))
            lines.append(line)
            if i == 0 and len(cell_data) > 1:
                lines.append(sep)
        lines.append(sep)
        return '\n' + '\n'.join(lines) + '\n'

    # Too wide for a simple table — emit a grid table with capped columns and
    # cells wrapped to fit. Grid-table overhead = 1 + 3 * num_cols.
    overhead = 1 + 3 * num_cols
    budget = max(num_cols * 8, _TABLE_TARGET_WIDTH - overhead)
    widths = _shrink_columns(natural, budget)
    return '\n' + _render_grid_table(cell_data, widths) + '\n'


def _shrink_columns(natural: list[int], budget: int) -> list[int]:
    """Shrink column widths down so their sum fits ``budget``, repeatedly trimming the
    widest column until the total fits."""
    widths = list(natural)
    while sum(widths) > budget:
        i = max(range(len(widths)), key=lambda k: widths[k])
        if widths[i] <= 8:
            break
        widths[i] -= 1
    return widths


def _wrap_cell(text: str, width: int) -> list[str]:
    if not text:
        return ['']
    wrapped = textwrap.wrap(text, width=width,
                            break_long_words=False,
                            break_on_hyphens=False)
    return wrapped or [text]


def _render_grid_table(cell_data: list[list[str]], widths: list[int]) -> str:
    sep = '+' + '+'.join('-' * (w + 2) for w in widths) + '+'
    head_sep = '+' + '+'.join('=' * (w + 2) for w in widths) + '+'
    out = [sep]
    for i, row in enumerate(cell_data):
        wrapped_cells = [_wrap_cell(cell, widths[c]) for c, cell in enumerate(row)]
        height = max(len(c) for c in wrapped_cells)
        for c in wrapped_cells:
            while len(c) < height:
                c.append('')
        for line_idx in range(height):
            parts = ['|']
            for c, w in zip(wrapped_cells, widths):
                parts.append(' ' + c[line_idx].ljust(w) + ' |')
            out.append(''.join(parts))
        out.append(head_sep if i == 0 and len(cell_data) > 1 else sep)
    return '\n'.join(out)


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
# List item rendering
# ──────────────────────────────────────────────────────────────────────────────


def _listitem_to_rst(listitem: ET.Element) -> str:
    """Render a Doxygen ``<listitem>`` as an RST bullet entry.

    The inline text of the item's ``<para>`` children appears after ``- `` on the
    bullet line. Any block-level children nested inside those paragraphs (tables,
    code listings, nested lists) are emitted as 2-space-indented continuations so
    they remain part of the same list item under RST's indentation rules. Without
    this, ``_para_inline``'s aggressive block-stripping would silently drop tables
    embedded in list items (e.g. ``InfoTagVideo.setUniqueIDs``).
    """
    inline_parts: list[str] = []
    block_parts: list[str] = []
    for p in listitem.findall('para'):
        text = _para_inline(p)
        if text:
            inline_parts.append(text)
        for child in p:
            if child.tag == 'table':
                tbl = _table_to_rst(child).strip()
                if tbl:
                    block_parts.append(tbl)
            elif child.tag == 'programlisting':
                listing = _listing_to_rst(child).strip()
                if listing:
                    block_parts.append(listing)
            elif child.tag in ('orderedlist', 'itemizedlist'):
                nested = []
                for inner in child.findall('listitem'):
                    rendered = _listitem_to_rst(inner)
                    if rendered:
                        nested.append(rendered)
                if nested:
                    block_parts.append('\n'.join(nested))
    inline_text = ' '.join(inline_parts).strip()
    if not block_parts:
        return f'- {inline_text}' if inline_text else ''
    bullet_line = f'- {inline_text}' if inline_text else '-'
    indented = '\n\n'.join(textwrap.indent(b, '  ') for b in block_parts)
    return f'{bullet_line}\n\n{indented}'


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
        inline_buf.append(_escape_rst_inline(para.text))

    for child in para:
        tag = child.tag
        tail = _escape_rst_inline(child.tail) if child.tail else ''

        if tag == 'parameterlist':
            flush_inline()
            kind = child.get('kind', 'param')
            trailing_tables: list[str] = []
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
                        for tbl in _extract_block_children(p, ('table',)):
                            t_rst = _table_to_rst(tbl).strip()
                            if t_rst:
                                trailing_tables.append(t_rst)
                    desc = ' '.join(parts).strip()
                if kind == 'param':
                    sections.append(f':param {name_str}: {desc}')
                elif kind == 'exception':
                    sections.append(f':raises {name_str}: {desc}')
            for t_rst in trailing_tables:
                sections.append(t_rst)
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
                rendered = _listitem_to_rst(listitem)
                if rendered:
                    sections.append(rendered)
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
    # Tracks whether any block-level child has been processed yet. Inline text
    # accumulated before the first block is the leading description (→ desc_parts);
    # inline text between/after blocks is a preamble or trailing note (→ note_parts).
    state = {'seen_block': False}

    def flush_inline() -> None:
        inline_text = ''.join(inline_buf).strip()
        inline_buf.clear()
        cleaned = _clean_python_marker(inline_text)
        if not cleaned:
            return
        if state['seen_block']:
            note_parts.append(cleaned)
        else:
            desc_parts.append(cleaned)

    if para.text:
        inline_buf.append(_escape_rst_inline(para.text))

    for child in para:
        tag = child.tag
        tail = _escape_rst_inline(child.tail) if child.tail else ''

        if tag == 'parameterlist':
            flush_inline()
            state['seen_block'] = True
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
                embedded_tables: list[str] = []
                if desc_elem is not None:
                    parts = []
                    for p in desc_elem.findall('para'):
                        parts.append(_para_inline(p))
                        for tbl in _extract_block_children(p, ('table',)):
                            t_rst = _table_to_rst(tbl).strip()
                            if t_rst:
                                embedded_tables.append(t_rst)
                    desc = ' '.join(parts).strip()
                if kind == 'param':
                    param_parts.append(f':param {name_str}: {desc}')
                elif kind == 'exception':
                    raise_parts.append(f':raises {name_str}: {desc}')
                # Tables embedded in a parameterdescription are emitted as
                # standalone blocks after the field list (per the source: such
                # parameter desc usually says "see table below").
                for t_rst in embedded_tables:
                    note_parts.append(t_rst)
            if tail:
                inline_buf.append(tail)

        elif tag == 'simplesect':
            flush_inline()
            state['seen_block'] = True
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
            # Special-case: drop a bare "Example:" label before a code listing,
            # but keep any other preamble text as a normal paragraph.
            inline_text = ''.join(inline_buf).strip()
            inline_buf.clear()
            cleaned = _clean_python_marker(inline_text)
            if cleaned and not _EXAMPLE_PAT.match(cleaned):
                if state['seen_block']:
                    note_parts.append(cleaned)
                else:
                    desc_parts.append(cleaned)
            state['seen_block'] = True
            example_parts.append(_listing_to_rst(child))
            if tail:
                inline_buf.append(tail)

        elif tag == 'table':
            flush_inline()
            state['seen_block'] = True
            table_rst = _table_to_rst(child)
            if table_rst.strip():
                note_parts.append(table_rst)
            if tail:
                inline_buf.append(tail)

        elif tag in ('orderedlist', 'itemizedlist'):
            flush_inline()
            state['seen_block'] = True
            items = []
            for listitem in child.findall('listitem'):
                rendered = _listitem_to_rst(listitem)
                if rendered:
                    items.append(rendered)
            if items:
                note_parts.append('\n'.join(items))
            if tail:
                inline_buf.append(tail)

        elif tag in ('sect2', 'sect3'):
            flush_inline()
            state['seen_block'] = True
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


def _flatten_detail_paras(detail: ET.Element) -> list[ET.Element]:
    """Return the effective ``<para>`` children of a ``<detaileddescription>``.

    Some Doxygen output (notably ``xbmcplugin.addSortMethod``) wraps the entire
    detailed description in a ``<sect2>`` whose ``<title>`` carries the brief and
    whose ``<para>`` children carry params/notes/examples. This helper unwraps a
    single top-level ``<sect2>``/``<sect3>`` so its inner ``<para>`` elements are
    treated as if they were direct children of detaileddescription.
    """
    direct_paras = detail.findall('para')
    sect_children = [c for c in detail
                     if c.tag in ('sect1', 'sect2', 'sect3', 'sect4')]
    if not direct_paras and len(sect_children) == 1:
        return sect_children[0].findall('para')
    return direct_paras


def _detail_brief_from_sect_title(detail: ET.Element) -> str:
    """If detaileddescription contains a single sect with a meaningful title, return
    that title (cleaned of ``@brief`` and ``\\python_func{...}`` markers) for use as
    a brief description. Returns '' otherwise."""
    sect_children = [c for c in detail
                     if c.tag in ('sect1', 'sect2', 'sect3', 'sect4')]
    if len(sect_children) != 1:
        return ''
    title = sect_children[0].find('title')
    if title is None:
        return ''
    text = (title.text or '').strip()
    text = re.sub(r'^@brief\s*', '', text)
    text = _clean_python_marker(text)
    return text.strip()


def description_to_rst(brief: Optional[ET.Element],
                        detail: Optional[ET.Element],
                        include_detail: bool = True) -> str:
    """Merge brief + detailed descriptions into a single RST string."""
    sections: list[str] = []

    # --- Brief ---
    brief_text = ''
    if brief is not None:
        brief_parts = []
        for para in brief.findall('para'):
            text = _para_inline(para)
            text = _clean_python_marker(text)
            if text:
                brief_parts.append(text)
        brief_text = ' '.join(brief_parts).strip()

    # If brief is empty, fall back to a single sect's <title> (Doxygen quirk).
    if not brief_text and detail is not None:
        brief_text = _detail_brief_from_sect_title(detail)

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

    for para in _flatten_detail_paras(detail):
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
        if not vp:
            continue
        # Per spec: each @python_v<num> note must be its own paragraph.
        for split_vp in re.split(r'\s+(?=@python_v\d+\b)', vp):
            split_vp = split_vp.strip()
            if split_vp:
                sections.append(split_vp)
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
