# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

Kodistubs are Python stub modules that re-create the Kodi (XBMC) Media Center Python API. They exist purely to enable
IDE autocompletion, type checking, and docstring access when developing Kodi addons. Every method body is a stub — it
returns an empty/default value and does nothing else. The package is published to PyPI as `Kodistubs`.

The six stub modules map directly to Kodi's Python API namespaces:
- `xbmc.py` — general Kodi functions and classes (player, monitor, playlists, dialogs)
- `xbmcaddon.py` — addon settings and localization (`Addon` class)
- `xbmcgui.py` — GUI widgets, windows, dialogs, list items
- `xbmcplugin.py` — plugin (virtual filesystem) functions for content providers
- `xbmcvfs.py` — virtual filesystem access (file I/O, directory operations)
- `xbmcdrm.py` — DRM/crypto session support (`CryptoSession` class)

Each module sets `__kodistubs__ = True` at module level as a sentinel. All functions and methods carry PEP-484 type
annotations and reStructuredText docstrings sourced from Kodi's own documentation.

## Versioning

Major version tracks the Kodi version (e.g., `22.0.0` = Kodi 22). Update `version` in `setup.cfg` when bumping.

## Build and Packaging

```bash
# Install build deps (one-time)
pip install build

# Build sdist + wheel
python -m build

# Install locally from source
pip install -e .
```

## Documentation

Docs use Sphinx with the `autodoc` extension — it imports the stubs to extract docstrings.

```bash
# Install Sphinx (one-time)
pip install -r requirements.txt

# Build HTML docs
cd docs && make html
```

Output goes to `docs/_build/html/`. The `docs/conf.py` reads version and author from `setup.cfg` automatically.

## Authoring Stubs

When adding or updating stub content:

1. Method bodies must be minimal stubs: `pass` for `None`-returning methods, `return ""` / `return 0` / `return []` /
   `return {}` for typed returns, matching the declared return type.
2. Docstrings use reStructuredText with `:param name:`, `:type name:`, `:return:`, `:rtype:` fields and fenced
   `Example::` blocks.
3. Version notes follow the `@python_vXX` convention already used throughout (e.g., `@python_v20 New class added.`).
4. All parameters should have type annotations; use `typing` imports (`Union`, `List`, `Dict`, `Tuple`, `Optional`) —
   the project targets Python 3.6+.
5. Constants are bare module-level assignments with integer or string literals.

## Branches

- `master` — current stable stubs (Kodi Matrix/Nexus/Omega era, Python 3)
- `piers` — next Kodi version stubs (active development)
- `legacy` — archived stubs for older Kodi releases
- `python2` — archived stubs for Kodi versions that used Python 2

## General Rules

- Do not commit anything go Git without explicit confirmation.
