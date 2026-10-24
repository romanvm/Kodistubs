"""Entry point: python -m kodistubs_generator [module1,module2,...]"""
from __future__ import annotations
import argparse
import os
import sys


ALL_MODULES = ['xbmc', 'xbmcaddon', 'xbmcgui', 'xbmcplugin', 'xbmcvfs', 'xbmcdrm']


def _report_undocumented(undocumented: list[str]) -> None:
    """Report API members without Doxygen documentation.

    Constructors are listed separately: Kodi documents them in the class description.
    A non-constructor gap usually means stale or changed Doxygen output.
    """
    constructors = [n for n in undocumented if n.endswith('.__init__')]
    others = [n for n in undocumented if not n.endswith('.__init__')]
    if others:
        print(f'  WARNING: {len(others)} member(s) without documentation: {", ".join(others)}', file=sys.stderr)
    if constructors:
        print(f'  note: {len(constructors)} constructor(s) without own documentation', flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate Kodi Python API stub packages.',
    )
    parser.add_argument(
        'modules',
        nargs='?',
        default='',
        help='Comma-separated list of modules to generate (default: all).',
    )
    args = parser.parse_args()

    if args.modules:
        modules = [m.strip() for m in args.modules.split(',') if m.strip()]
        unknown = [m for m in modules if m not in ALL_MODULES]
        if unknown:
            print(f'Unknown module(s): {", ".join(unknown)}', file=sys.stderr)
            print(f'Available: {", ".join(ALL_MODULES)}', file=sys.stderr)
            sys.exit(1)
    else:
        modules = ALL_MODULES

    # Locate project root (the directory containing this package)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    from . import settings
    from .code_generator import generate_module
    from .const_resolver import load_constants
    from .doxy_parser import load_module_docs
    from .doxygen_runner import ensure_doxygen_xml
    from .swig_parser import parse_module
    from .swig_runner import find_swig, run_swig

    kodi_src = os.path.normpath(os.path.join(project_root, settings.KODI_SRC_DIR))
    work_dir = os.path.join(project_root, settings.SWIG_WORK_DIR)
    xml_dir = os.path.join(project_root, settings.DOXYGEN_XML_DIR)
    output_dir = os.path.join(project_root, 'src')

    try:
        swig = find_swig(settings.SWIG_EXECUTABLE)
        ensure_doxygen_xml(project_root, kodi_src, xml_dir)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)

    for module in modules:
        print(f'Generating {module}...', flush=True)
        try:
            swig_xml = run_swig(module, kodi_src, work_dir, swig)
            api = parse_module(module, swig_xml)
            dox = load_module_docs(module, xml_dir)
            constants = load_constants(api, kodi_src)
            undocumented = generate_module(api, dox, constants, xml_dir, output_dir)
            print(f'  → src/{module}/__init__.py')
            _report_undocumented(undocumented)
        except Exception as exc:
            print(f'  ERROR: {exc}', file=sys.stderr)
            import traceback
            traceback.print_exc()

    print('Done.')


if __name__ == '__main__':
    main()
