"""Parse Doxygen XML files to extract API documentation."""
from __future__ import annotations
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


_MODULE_GROUP: dict[str, str] = {
    'xbmc': 'group__python__xbmc',
    'xbmcaddon': 'group__python__xbmcaddon',
    'xbmcgui': 'group__python__xbmcgui',
    'xbmcplugin': 'group__python__xbmcplugin',
    'xbmcvfs': 'group__python__xbmcvfs',
    'xbmcdrm': 'group__python__xbmcdrm',
}


@dataclass
class DoxygenIndex:
    """All parsed Doxygen documentation for a single Kodi Python module."""
    # group_id → compounddef element
    groups: dict[str, ET.Element] = field(default_factory=dict)
    # function name → list of memberdef elements (may have duplicates across groups)
    members: dict[str, list[ET.Element]] = field(default_factory=dict)
    # class refid → compounddef element of the *group* that documents it
    class_group: dict[str, ET.Element] = field(default_factory=dict)
    # class short name → compounddef element
    class_group_by_name: dict[str, ET.Element] = field(default_factory=dict)
    # top-level compounddef (the module-level group)
    top_compound: Optional[ET.Element] = None


def _load_xml(xml_dir: str, group_id: str) -> Optional[ET.Element]:
    path = os.path.join(xml_dir, f'{group_id}.xml')
    if not os.path.exists(path):
        return None
    tree = ET.parse(path)
    root = tree.getroot()
    return root.find('.//compounddef')


def _index_group(compound: ET.Element, idx: DoxygenIndex, xml_dir: str,
                 visited: set[str]) -> None:
    """Recursively load a group and all its inner groups."""
    gid = compound.get('id', '')
    if gid in visited:
        return
    visited.add(gid)
    idx.groups[gid] = compound

    # Index memberdef elements
    for memberdef in compound.findall('.//memberdef'):
        name = memberdef.findtext('name', '')
        if name:
            idx.members.setdefault(name, []).append(memberdef)

    # Map class refids to this group
    for innerclass in compound.findall('innerclass'):
        refid = innerclass.get('refid', '')
        # Load class compound to get short name for lookup
        cls_compound = _load_xml(xml_dir, refid)
        if cls_compound is not None:
            # Extract short class name from compoundname
            cpp_name = cls_compound.findtext('compoundname', '')
            short_name = cpp_name.split('::')[-1]
            idx.class_group[refid] = compound
            idx.class_group_by_name[short_name] = compound

    # Follow inner groups recursively
    for innergroup in compound.findall('innergroup'):
        refid = innergroup.get('refid', '')
        if refid and refid not in visited:
            sub = _load_xml(xml_dir, refid)
            if sub is not None:
                # Check if this subgroup documents a class
                for ic in sub.findall('innerclass'):
                    ic_refid = ic.get('refid', '')
                    cls_c = _load_xml(xml_dir, ic_refid)
                    if cls_c is not None:
                        cpp_name = cls_c.findtext('compoundname', '')
                        short_name = cpp_name.split('::')[-1]
                        idx.class_group[ic_refid] = sub
                        idx.class_group_by_name[short_name] = sub
                _index_group(sub, idx, xml_dir, visited)


def load_module_docs(module: str, xml_dir: str) -> DoxygenIndex:
    """Load all Doxygen documentation for a Kodi Python module."""
    idx = DoxygenIndex()
    group_id = _MODULE_GROUP.get(module)
    if not group_id:
        return idx
    compound = _load_xml(xml_dir, group_id)
    if compound is None:
        return idx
    idx.top_compound = compound
    _index_group(compound, idx, xml_dir, set())
    return idx


def get_member_doc(idx: DoxygenIndex, func_name: str,
                   class_name: Optional[str] = None) -> Optional[ET.Element]:
    """Find the best matching memberdef for a function/method.

    Optionally filter by qualified C++ class name (e.g. 'Addon').
    """
    candidates = idx.members.get(func_name, [])
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    if class_name:
        # Try to match by definition field containing class name
        for m in candidates:
            defn = m.findtext('definition', '') or m.findtext('qualifiedname', '')
            if class_name in defn:
                return m
    # Return the one with most documentation
    def doc_score(m: ET.Element) -> int:
        brief = m.findtext('briefdescription', '') or ''
        detail = ET.tostring(m.find('detaileddescription') or ET.Element('x'),
                             encoding='unicode')
        return len(brief) + len(detail)

    return max(candidates, key=doc_score)


def get_class_doc(idx: DoxygenIndex, class_name: str) -> Optional[ET.Element]:
    """Get the compounddef of the group that documents the class."""
    return idx.class_group_by_name.get(class_name)


def get_class_inheritance(xml_dir: str, module: str, class_name: str) -> Optional[str]:
    """Return the Python base class name for a given C++ class, if any."""
    # Find the class compound XML
    # Try common refid patterns
    sanitized_mod = module.replace('xbmc', 'xbmc')
    candidates = [
        f'classXBMCAddon_1_1{module}_1_1{class_name}',
    ]
    for cid in candidates:
        compound = _load_xml(xml_dir, cid)
        if compound is not None:
            for base in compound.findall('basecompoundref'):
                prot = base.get('prot', '')
                if prot != 'public':
                    continue
                base_text = base.text or ''
                # Extract short class name
                base_class = base_text.split('::')[-1]
                # Only return if base class is within the same module
                if f'::{module}::' in base_text or base_text.startswith(f'XBMCAddon::{module}'):
                    return base_class
    return None
