# Paths are relative to the project root.
KODI_SRC_DIR = '../xbmc'
# None: the swig installed next to the running Python (requirements.txt), then swig on PATH.
SWIG_EXECUTABLE = None
SWIG_WORK_DIR = 'build/swig'
# Doxygen XML is produced from KODI_SRC_DIR/xbmc/interfaces/legacy by ``doxygen kodi.doxy`` in doxygen/,
# whose INPUT must point at the same checkout.
DOXYGEN_XML_DIR = 'doxygen/xml'
