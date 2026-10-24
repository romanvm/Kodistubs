"""Keep the Doxygen XML (docstring source) in sync with Kodi's ``interfaces/legacy`` headers."""
from __future__ import annotations

import glob
import os
import shutil
import subprocess


def ensure_doxygen_xml(project_root: str, kodi_src: str, xml_dir: str) -> None:
    """Run ``doxygen kodi.doxy`` if the XML is missing or older than any legacy header.

    Stale XML silently drops the documentation of newly added API members.
    """
    headers = glob.glob(os.path.join(kodi_src, 'xbmc', 'interfaces', 'legacy', '*.h'))
    index = os.path.join(xml_dir, 'index.xml')
    if os.path.exists(index) and headers:
        if os.path.getmtime(index) >= max(os.path.getmtime(h) for h in headers):
            return

    doxygen = shutil.which('doxygen')
    if doxygen is None:
        raise FileNotFoundError('doxygen not found; it is needed to (re)generate doxygen/xml.')
    print('  Doxygen XML is missing or outdated, running doxygen...', flush=True)
    result = subprocess.run([doxygen, 'kodi.doxy'], cwd=os.path.join(project_root, 'doxygen'),
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f'doxygen failed:\n{result.stderr.strip()}')
