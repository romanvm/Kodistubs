"""Entry point: python -m kodistubs_generator [module1,module2,...]"""
from __future__ import annotations
import argparse
import os
import sys


ALL_MODULES = ['xbmc', 'xbmcaddon', 'xbmcgui', 'xbmcplugin', 'xbmcvfs', 'xbmcdrm']


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

    # Load settings
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from . import settings  # noqa: E402

    swig_dir = os.path.normpath(
        os.path.join(project_root, settings.KODI_SWIG_DIR)
    )
    xml_dir = os.path.join(project_root, 'doxygen', 'xml')
    output_dir = os.path.join(project_root, 'src')

    # Derive kodi source root from swig_dir
    # KODI_SWIG_DIR = '../xbmc/build/build/swig'  → kodi_src = '../xbmc'
    kodi_src = os.path.normpath(os.path.join(
        project_root,
        os.path.join(os.path.dirname(settings.KODI_SWIG_DIR), '..', '..')
    ))

    from .swig_parser import parse_module
    from .doxy_parser import load_module_docs
    from .const_resolver import load_constants
    from .code_generator import generate_module

    for module in modules:
        print(f'Generating {module}...', flush=True)
        try:
            api = parse_module(module, swig_dir)
            dox = load_module_docs(module, xml_dir)
            constants = load_constants(module, swig_dir, kodi_src)
            generate_module(api, dox, constants, xml_dir, output_dir)
            print(f'  → src/{module}/__init__.py')
        except Exception as exc:
            print(f'  ERROR: {exc}', file=sys.stderr)
            import traceback
            traceback.print_exc()

    print('Done.')


if __name__ == '__main__':
    main()
