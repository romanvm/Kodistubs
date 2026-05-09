---
name: create-kodistubs
description: Regenerate the Kodi (XBMC) Python API stub packages under `src/` from SWIG XML and Doxygen XML sources 
  by running the `kodistubs_generator` tool and post-processing its output. Use this skill whenever the user asks 
  to (re)generate Kodistubs, rebuild the `xbmc*` stub modules, refresh stubs from upstream Kodi sources, or fix issues 
  in already-generated stubs while improving `kodistubs_generator`. 
  Trigger on phrases like "regenerate the stubs", "update kodistubs", "rebuild the xbmc stub modules", 
  "run the kodistubs generator", or any request that involves consuming `AddonModule*.i.xml` or the `doxygen/xml` tree.
---

# Creating Kodistubs

Use this skill to (re)generate the six Python stub packages under `src/` that re-create the Kodi Python API:
`xbmc`, `xbmcaddon`, `xbmcgui`, `xbmcdrm`, `xbmcplugin`, `xbmcvfs`. The packages are built from upstream Kodi sources
via the in-repo `kodistubs_generator` tool, then audited and fixed by you.

The output must be valid Python, render cleanly through Sphinx, and faithfully expose every constant, function, class,
and method that Kodi makes available to Python addons.

## Inputs

- **SWIG definitions** — `../xbmc/build/build/swig` (relative to the project root) contains:
  - `AddonModule*.i.xml` — SWIG XML with call signatures and return types for each `xbmc*` module.
  - `AddonModule*.i.cpp` — generated C++ for those modules; consult when SWIG XML alone is ambiguous.
  - Ignore `xbmcwsgi` files — they are not part of this project's stubs.
- **Doxygen documentation** — `doxygen/xml/` (relative to the project root) holds the docstring source. The top-level
  group files are:
  - `group__python__xbmc.xml`
  - `group__python__xbmcaddon.xml`
  - `group__python__xbmcgui.xml`
  - `group__python__xbmcplugin.xml`
  - `group__python__xbmcvfs.xml`
  - `group__python__xbmcdrm.xml`
- **Kodi C++ source tree** — `../xbmc/` (relative to the project root) is the upstream Kodi checkout. Use it as the
  source of truth when resolving constant values, enum members, `#define`s, or anything else the SWIG/Doxygen output
  references but does not directly contain. Relevant entry points include `xbmc/interfaces/legacy/Module*.cpp`
  (`getNAME()` accessor implementations), `xbmc/commons/ilog.h`, `xbmc/playlists/PlayListTypes.h`,
  `xbmc/storage/discs/IDiscDriveHandler.h`, `xbmc/utils/LangCodeExpander.h`, `xbmc/network/NetworkServices.h`,
  `xbmc/guilib/GUIControl.h`, `xbmc/guilib/GUIEditControl.h`, `xbmc/guilib/GUIListItem.h`,
  `xbmc/dialogs/GUIDialogBoxBase.h`, and `xbmc/interfaces/legacy/Dialog.h`.

If Doxygen XML files are missing, `cd` to `doxygen` directory and run `doxygen kodi.doxy`.

## Workflow

1. Run `python3 -m kodistubs_generator` from the project root to produce the raw stub packages. The generator writes
   into `src/`, overwriting existing content.
2. Audit the generated output module by module against the rules below and fix issues directly in the generated files.
3. When a problem is systemic (affects multiple files or would recur on the next regeneration), fix it in
   `kodistubs_generator/` instead of patching the output, then regenerate.
4. Build the Sphinx docs (`cd docs && make html`) and resolve every warning and error before considering the work
   complete.
5. Do **not** commit anything to Git without explicit confirmation from the user.

## Output rules

### Coverage

- Include every Python module-level constant, function, class, and method that Kodi exposes to Python code.
- Carry across the documentation for each of those objects in valid reStructuredText compatible with Sphinx.

### Module-level constant values

`ALL_CAPS` module-level constants must carry their **real** values from Kodi sources, not placeholder zeros or empty
strings. The SWIG `.i.cpp` exposes them as either an integer literal, a `getNAME()` accessor call, a
`Class::MEMBER` reference, or a `static_cast<int>(EXPR)` wrapper — chase each one through to its actual definition in
the Kodi C++ tree (`../xbmc/`) before accepting a value.

- `getNAME()` accessors live in `xbmc/interfaces/legacy/Module*.cpp`. Read the accessor body and recurse on the
  expression it returns.
- Enum members may be in `enum class` blocks (scoped: `Class::Enum::MEMBER`), plain `enum` blocks (unscoped),
  or nested inside namespaces or classes. Traverse the enclosing scopes.
- `#define`s and `constexpr int NAME = N;` / `constexpr int NAME{N};` lines may live in any header. `#define`s can
  also reference other identifiers and use arithmetic (e.g. `CONTROL_CHOICES_START + 1`) — evaluate the expression.
- A constant whose *real* value is `0` (e.g. the first member of an enum) is fine; the goal is correctness, not
  avoiding zero. Verify each suspected zero by reading the Kodi source rather than assuming.

Resolution belongs in `kodistubs_generator/const_resolver.py`. If a constant comes out wrong, extend the resolver
(add the relevant header to its scan list, fix a parser, or expand the expression evaluator) rather than hand-editing
the generated stub.

### Code formatting

- Follow PEP 8, but allow lines up to **120 characters**. Wrap longer lines without breaking Python syntax.
- Follow PEP 257 for docstrings, again allowing 120-character lines. Wrap without breaking reStructuredText markup or
  the Python syntax inside literal/example blocks.
- Follow Sphinx reStructuredText conventions throughout.

### Signatures and bodies

- Every function, class, and method must carry a complete call signature with type annotations.
- Method bodies must be minimal stubs that satisfy the declared return type:
  - `pass` for functions/methods that return `None`.
  - A minimal instance of the declared type otherwise — `""` for `str`, `0` for `int`, `[]` for `list`, `{}` for `dict`,
    `MyClass()` for a class with a no-arg constructor, etc.
- Resolve C++ `Namespace::Type` references in annotations to their Python equivalents. Never leave `::`-separated names
  in the generated Python.

### Cross-module references

- Use `from __future__ import annotations` at the beginning of the generated stub files.
- Fix unresolved references to classes that live in other stub modules. Import the necessary stub module(s)
  to resolve the reference and guard it with `if TYPE_CHECKING:` so it is only visible to type checkers.

### Docstrings

- Source docstring content from the Doxygen XML for each object.
- Convert Doxygen XML markup into the corresponding reStructuredText: text styles, `:param:`/`:type:`/`:return:`/
  `:rtype:` fields, tables, admonition blocks, code/example blocks, etc. Preserve the semantic meaning rather than the
  literal markup.

### `@python_v<version>` markers

These tags indicate the Kodi Python API version that introduced a feature. They have no special syntactic meaning —
treat them as plain text, but apply these conventions:

- Wrap the marker in reStructuredText bold formatting.
- Place the marker at the start of its own paragraph; the comment it introduces belongs in that paragraph.
- If a single source paragraph contains multiple `@python_v<version>` markers, split it into one paragraph per marker,
  each starting with the respective tag.

## Verification

The job isn't done until both of these hold:

- The generated packages are importable and free of Python syntax errors.
- `cd docs && make html` produces clean output — fix every warning and error Sphinx reports.

## Improving `kodistubs_generator`

Treat each round of fixes as feedback for the generator. If you find yourself making the same kind of correction in
several files, push the fix into `kodistubs_generator/` (parser, type mapper, doc converter, code generator — whichever
is responsible) and regenerate, rather than maintaining the patch by hand in `src/`.
