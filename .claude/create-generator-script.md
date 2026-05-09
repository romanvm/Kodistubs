# Instructions for creating Kodistubs generator script

You need to create a Python script that generates Python stub packages for Kodi-Python API according to the following
specs:

- The script should be placed in `kodistubs_generator` subdirectory relative to the project directory. The subdirectory
  should contain `__init__.py` file.
- The script may contain several Python modules depending on the needs.
- The script entrypoint should be located in `__main__.py` file.
- The script should be run as `python -m kodistubs_generator` from the project root.
- The script must accept an optional parameter that is a comma-separated list of Kodi-Python API modules that
  you need to generate stub packages for, e.g. `python -m kodistubs_generator xbmc` or
  `python -m kodistubs_generator xbmc,xbmcgui,xbmcvfs`. If the parameter is missing, generate all stubs.
- The script package should include `settings.py` file that contains `KODI_SWIG_DIR = '../xbmc/build/build/swig'` 
  variable that is a relative path to SWIG definitions of Kodi-Python API modules. This variable is used to access
  the necessary input files.
- `KODI_SWIG_DIR` contains `AddonModule*.i.*` files that are definitions for xbmc, xbmcaddon, xbmcgui, xbmcdrm, xbmcplugin,
  and xbmcvfs modules respectively. Ignore files for xbmcwsgi module, they are not relevant to the task.
  The `AddonModule*.i.xml` files are SWIG XML definitions for call signatures and return types of Kodi Python API modules
  written in C++ using Python-C API. The `AddonModule*.i.cpp` files are generated C++ files for those modules.
- The `doxugen/xml` subdirectory from the project root contains Doxygen documentation for xbmc* modules of Kodi-Python API.
  The top level XML files for xbmc* modules documentations are:
  *  group__python__xbmc.xml
  *  group__python__xbmcaddon.xml
  *  group__python__xbmcgui.xml
  *  group__python__xbmcplugin.xml
  *  group__python__xbmcvfs.xml
  *  group__python__xbmcdrm.xml
- The generated stub packages must include all Python module-level constants, functions, classes, and methods exposed
  by Kodi to Python code and the respective documentation in valid reStructuredText format compatible with Sphinx 
  documentation generator.
- Use existing src/xbmc* stub packages as an example of the output.
- Functions, classes, and methods must include call signatures with type annotations and minimal
  code not to raise syntax errors according to the following rules:
  * If a function or a method does not return anything, use `pass` operator.
  * If a function or a method returns a type, use a minimal instance of this type, e.g, an emty string for `str` type,
    and empty list for `list` type, `0` for `int` type, an instance of a class without parameters, etc.
- Dostrings content for modules, classes, methods, and functions should be taken from Doxygen XML files for the respective
  objects. Convert XML markup into the respective reStructuredText markup to preserve the semantical meaning of docstring
  elements: text style, parameters and return values descriptions, tables, admonition blocks, etc.
- Fix unresolved references in type annotations and Python code to objects located in other stub packages.
- Generated stub packages should be placed in `src` subdirectory overwriting the existing content. 
  Do not commit anything to Git without an explicit confirmation.
- The Generated stub packages must produce correct Shphinx HTML documentation using the configuration in `docs`
  subdirectory. Fix all possible errors and warnings produced by Sphinx when generating docs.
