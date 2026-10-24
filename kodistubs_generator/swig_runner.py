"""Run SWIG on Kodi's ``AddonModule*.i`` files to produce SWIG XML parse trees.

Kodi no longer ships SWIG XML, so the generator runs SWIG itself with the same
arguments as ``generate_file()`` in ``xbmc/interfaces/swig/CMakeLists.txt`` plus
``-xmlout``. SWIG is taken from the ``swig`` PyPI package (see
``requirements-generator.txt``) unless ``settings.SWIG_EXECUTABLE`` overrides it.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sysconfig
from typing import Optional

MIN_SWIG_VERSION = (4, 5, 0)

# Mirrors SWIG_ARGS in xbmc/interfaces/swig/CMakeLists.txt.
_SWIG_WARNINGS = '-w401,389,514,362,302'


def find_swig(configured: Optional[str] = None) -> str:
    """Return the path to a SWIG executable that is new enough for Kodi's interface files."""
    if configured:
        candidate: Optional[str] = configured
    else:
        # The swig wheel installs its launcher next to the running interpreter,
        # which may not be on PATH if the venv is not activated.
        candidate = (shutil.which('swig', path=sysconfig.get_path('scripts'))
                     or shutil.which('swig'))
    if candidate is None:
        raise FileNotFoundError(
            'SWIG not found. Install it with "pip install -r requirements-generator.txt" '
            'or set SWIG_EXECUTABLE in kodistubs_generator/settings.py.'
        )
    version = swig_version(candidate)
    if version < MIN_SWIG_VERSION:
        raise RuntimeError(
            f'{candidate} is SWIG {".".join(map(str, version))}; '
            f'{".".join(map(str, MIN_SWIG_VERSION))} or newer is required.'
        )
    return candidate


def swig_version(swig: str) -> tuple[int, ...]:
    """Return the version reported by ``swig -version``."""
    output = subprocess.run([swig, '-version'], capture_output=True, text=True, check=True).stdout
    match = re.search(r'SWIG Version (\d+(?:\.\d+)*)', output)
    if match is None:
        raise RuntimeError(f'Cannot determine SWIG version from: {output.strip()}')
    return tuple(int(part) for part in match.group(1).split('.'))


def _module_basename(module: str) -> str:
    """``xbmcgui`` → ``AddonModuleXbmcgui``."""
    return f'AddonModule{module.capitalize()}'


def _read_depfile(path: str) -> list[str]:
    """Return the prerequisites listed in a Makefile-style depfile written by ``swig -MMD``."""
    with open(path, encoding='utf-8') as f:
        text = f.read().replace('\\\n', ' ')
    _, _, prerequisites = text.partition(': ')
    return prerequisites.split()


def _is_up_to_date(xml_path: str, depfile: str, base_dir: str) -> bool:
    """Check the XML against its depfile; relative depfile entries are relative to ``base_dir``."""
    if not (os.path.exists(xml_path) and os.path.exists(depfile)):
        return False
    xml_mtime = os.path.getmtime(xml_path)
    for dependency in _read_depfile(depfile):
        dependency = os.path.join(base_dir, dependency)
        if not os.path.exists(dependency) or os.path.getmtime(dependency) > xml_mtime:
            return False
    return True


def run_swig(module: str, kodi_src: str, work_dir: str, swig: str, force: bool = False) -> str:
    """Generate ``AddonModule*.i.xml`` (plus ``.i.cpp`` and ``.pyi``) for a module into ``work_dir``.

    SWIG is skipped when the existing XML is newer than every file listed in its
    depfile. Returns the path to the XML file.
    """
    basename = _module_basename(module)
    swig_src_dir = os.path.join(kodi_src, 'xbmc', 'interfaces', 'swig')
    interface_file = os.path.join(swig_src_dir, f'{basename}.i')
    if not os.path.exists(interface_file):
        raise FileNotFoundError(f'SWIG interface file not found: {interface_file}')

    os.makedirs(work_dir, exist_ok=True)
    xml_path = os.path.join(work_dir, f'{basename}.i.xml')
    cpp_path = os.path.join(work_dir, f'{basename}.i.cpp')
    depfile = f'{cpp_path}.d'
    if not force and _is_up_to_date(xml_path, depfile, swig_src_dir):
        return xml_path

    args = [
        swig, '-python', '-c++', '-builtin', '-interface', module, '-pyi', _SWIG_WARNINGS,
        '-xmlout', os.path.abspath(xml_path),
        '-o', os.path.abspath(cpp_path),
        '-MMD', '-MF', os.path.abspath(depfile),
        '-I' + os.path.abspath(os.path.join(kodi_src, 'xbmc')),
        os.path.abspath(interface_file),
    ]
    # SWIG writes the kodi_*.i entries of the depfile relative to its working
    # directory; a fixed one lets _is_up_to_date resolve them.
    result = subprocess.run(args, cwd=swig_src_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f'SWIG failed for {module}:\n{result.stderr.strip()}')
    return xml_path
