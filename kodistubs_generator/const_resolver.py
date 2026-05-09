"""Resolve Kodi Python API constant values from .i.cpp and C++ source.

The flow is:

1. ``EnumResolver`` scans a curated set of Kodi headers and ``Module*.cpp``
   accessor files at construction time, building two indexes — ``_known``
   (identifier or scoped identifier → integer/string value) and ``_getters``
   (``getNAME`` → its raw return expression).
2. ``parse_constants_from_cpp`` reads the SWIG-generated ``.i.cpp`` and finds
   every ``PyModule_Add{Int,String}Constant`` call, extracting ``(name, expr)``.
3. Each ``expr`` is fed to ``EnumResolver.resolve``, which understands integer
   literals, ``static_cast`` wrappers, getter calls (looked up via ``_getters``
   and resolved transitively), scoped/unqualified identifiers, and arithmetic
   expressions (recursively substituted, then evaluated via a restricted AST
   walk).
"""
from __future__ import annotations

import ast
import operator
import os
import re
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# Source files scanned for constants
# ──────────────────────────────────────────────────────────────────────────────

# Headers that define enums, constexpr ints, and ``#define`` constants used by
# Python-facing accessors.
_HEADER_FILES: tuple[str, ...] = (
    'xbmc/commons/ilog.h',
    'xbmc/network/NetworkServices.h',
    'xbmc/playlists/PlayListTypes.h',
    'xbmc/storage/discs/IDiscDriveHandler.h',
    'xbmc/utils/LangCodeExpander.h',
    'xbmc/SortFileItem.h',
    'xbmc/guilib/GUIControl.h',
    'xbmc/guilib/GUIEditControl.h',
    'xbmc/guilib/GUIListItem.h',
    'xbmc/dialogs/GUIDialogBoxBase.h',
    'xbmc/interfaces/legacy/Dialog.h',
    'xbmc/input/Key.h',
)

# ``Module*.cpp`` files: source of ``getNAME() { return EXPR; }`` accessors and
# of ``#define NAME "string"`` string constants exposed via SWIG.
_MODULE_CPP_FILES: tuple[str, ...] = (
    'xbmc/interfaces/legacy/ModuleXbmc.cpp',
    'xbmc/interfaces/legacy/ModuleXbmcgui.cpp',
    'xbmc/interfaces/legacy/ModuleXbmcplugin.cpp',
    'xbmc/interfaces/legacy/ModuleXbmcvfs.cpp',
)


# ──────────────────────────────────────────────────────────────────────────────
# Brace matching helper
# ──────────────────────────────────────────────────────────────────────────────

def _matching_brace_end(text: str, open_pos: int) -> int:
    """Return the index of the ``}`` matching the ``{`` at ``open_pos``.

    Tracks nested braces. Strings and line/block comments are treated as opaque
    so braces inside them are ignored. Returns ``-1`` if no match is found.
    """
    assert text[open_pos] == '{'
    depth = 0
    i = open_pos
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == '/' and i + 1 < n:
            nxt = text[i + 1]
            if nxt == '/':
                nl = text.find('\n', i)
                i = n if nl == -1 else nl + 1
                continue
            if nxt == '*':
                end = text.find('*/', i + 2)
                i = n if end == -1 else end + 2
                continue
        if ch in '"\'':
            # Skip string literal
            quote = ch
            i += 1
            while i < n:
                if text[i] == '\\':
                    i += 2
                    continue
                if text[i] == quote:
                    i += 1
                    break
                i += 1
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


# ──────────────────────────────────────────────────────────────────────────────
# Arithmetic expression evaluator (safe AST walk)
# ──────────────────────────────────────────────────────────────────────────────

_BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.FloorDiv: operator.floordiv,
    ast.Div: operator.floordiv, ast.Mod: operator.mod,
    ast.LShift: operator.lshift, ast.RShift: operator.rshift,
    ast.BitOr: operator.or_, ast.BitAnd: operator.and_,
    ast.BitXor: operator.xor,
}
_UNARY_OPS = {
    ast.USub: operator.neg, ast.UAdd: operator.pos,
    ast.Invert: operator.invert,
}


def _eval_ast(node: ast.AST) -> int:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f'unsupported binary op: {type(node.op).__name__}')
        return op(_eval_ast(node.left), _eval_ast(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f'unsupported unary op: {type(node.op).__name__}')
        return op(_eval_ast(node.operand))
    raise ValueError(f'unsupported AST node: {type(node).__name__}')


# ──────────────────────────────────────────────────────────────────────────────
# Resolver
# ──────────────────────────────────────────────────────────────────────────────

# C++ identifier or scoped identifier: ``Foo``, ``Foo::Bar``, ``A::B::C``.
_TOKEN_RE = re.compile(r'[A-Za-z_]\w*(?:::[A-Za-z_]\w*)*')


class EnumResolver:
    """Resolves C++ enum/constant expressions to integer or string values."""

    def __init__(self, kodi_src: str) -> None:
        self.kodi_src = kodi_src
        self._cache: dict[str, Optional[object]] = {}
        # Identifier (or scoped identifier) → integer or string value.
        self._known: dict[str, object] = {}
        # Getter function name (e.g. ``getLOGDEBUG``) → raw return expression.
        self._getters: dict[str, str] = {}
        # Track active resolution stack to avoid infinite recursion.
        self._resolving: set[str] = set()
        self._scan_all()

    # ── Scanning ──────────────────────────────────────────────────────────────

    def _scan_all(self) -> None:
        for rel in _HEADER_FILES:
            self._scan_header(os.path.join(self.kodi_src, rel))
        for rel in _MODULE_CPP_FILES:
            self._scan_module_cpp(os.path.join(self.kodi_src, rel))

    def _scan_header(self, path: str) -> None:
        if not os.path.exists(path):
            return
        with open(path, encoding='utf-8', errors='replace') as f:
            text = f.read()
        text = self._strip_comments(text)
        self._scan_scope(text, scopes=[])

    def _strip_comments(self, text: str) -> str:
        """Remove ``//`` and ``/* */`` comments without affecting line offsets."""
        out: list[str] = []
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if ch == '/' and i + 1 < n:
                if text[i + 1] == '/':
                    nl = text.find('\n', i)
                    if nl == -1:
                        return ''.join(out)
                    out.append(' ' * (nl - i))
                    i = nl
                    continue
                if text[i + 1] == '*':
                    end = text.find('*/', i + 2)
                    if end == -1:
                        return ''.join(out)
                    block = text[i:end + 2]
                    # Preserve newlines so line numbers stay aligned.
                    out.append(''.join('\n' if c == '\n' else ' ' for c in block))
                    i = end + 2
                    continue
            out.append(ch)
            i += 1
        return ''.join(out)

    def _scan_scope(self, text: str, scopes: list[str]) -> None:
        """Recurse into ``namespace`` / ``class`` / ``struct`` / ``enum`` blocks.

        Anonymous namespaces are flattened into the surrounding scope.
        """
        # File-scope ``#define`` constants.
        for m in re.finditer(
            r'^\s*#\s*define\s+([A-Za-z_]\w*)\s+(.+?)\s*$', text, re.M
        ):
            name, val = m.group(1), m.group(2).strip()
            self._add_define(name, val, scopes)

        # ``constexpr int NAME = V;`` and ``constexpr int NAME{V};``
        for m in re.finditer(
            r'(?:constexpr|const)\s+int\s+(\w+)\s*(?:=\s*(-?\d+)|\{\s*(-?\d+)\s*\})\s*[;,]',
            text,
        ):
            name = m.group(1)
            val_str = m.group(2) if m.group(2) is not None else m.group(3)
            try:
                self._add_value(name, int(val_str), scopes)
            except (TypeError, ValueError):
                pass

        # ``enum [class|struct] NAME [: type] { ... };`` (anywhere).
        for m in re.finditer(
            r'\benum\s+(class|struct)?\s*(\w+)?\s*(?::\s*\w[\w\s:]*?)?\s*(\{)',
            text,
        ):
            brace_pos = m.start(3)
            end = _matching_brace_end(text, brace_pos)
            if end < 0:
                continue
            body = text[brace_pos + 1:end]
            enum_name = m.group(2) or ''
            enum_scopes = scopes + ([enum_name] if enum_name else [])
            self._parse_enum_body(body, enum_scopes)

        # ``namespace NAME[, NS, ...] { ... }``  — including nested ``A::B``.
        for m in re.finditer(r'\bnamespace\s+([\w:]+)?\s*(\{)', text):
            ns = m.group(1) or ''
            brace_pos = m.start(2)
            end = _matching_brace_end(text, brace_pos)
            if end < 0:
                continue
            body = text[brace_pos + 1:end]
            inner_scopes = scopes + ([s for s in ns.split('::') if s] if ns else [])
            self._scan_scope(body, inner_scopes)

        # ``class|struct CLASSNAME ... { ... };``
        for m in re.finditer(
            r'\b(?:class|struct)\s+(\w+)\b[^{;]*?(\{)', text
        ):
            class_name = m.group(1)
            brace_pos = m.start(2)
            end = _matching_brace_end(text, brace_pos)
            if end < 0:
                continue
            body = text[brace_pos + 1:end]
            self._scan_scope(body, scopes + [class_name])

    def _parse_enum_body(self, body: str, scopes: list[str]) -> None:
        """Walk an enum body, assigning sequential values respecting ``= EXPR``."""
        current = 0
        # Each member: NAME, NAME = EXPR, NAME = EXPR (trailing comma optional).
        for m in re.finditer(
            r'([A-Za-z_]\w*)\s*(?:=\s*([^,}]+?))?\s*(?:,|$|(?=}))',
            body,
        ):
            name = m.group(1)
            val_str = m.group(2)
            if val_str is not None:
                val_str = val_str.strip()
                try:
                    current = int(val_str, 0)
                except ValueError:
                    # Try resolving via existing ``_known`` (e.g. enum member
                    # references another).
                    resolved = self._eval_with_substitution(val_str)
                    if isinstance(resolved, int):
                        current = resolved
                    # else: keep the previous ``current`` value
            self._add_value(name, current, scopes)
            current += 1

    def _scan_module_cpp(self, path: str) -> None:
        """Parse accessor return expressions and ``#define`` string constants."""
        if not os.path.exists(path):
            return
        with open(path, encoding='utf-8', errors='replace') as f:
            text = f.read()
        text = self._strip_comments(text)

        # ``int|long|String|const char* getNAME() { return EXPR; }``
        for m in re.finditer(
            r'(?:int|long|String|const\s+char\s*\*)\s+(get[A-Za-z_]\w*)\s*\(\s*\)\s*\{(.*?)\}',
            text, re.DOTALL,
        ):
            name = m.group(1)
            body = m.group(2)
            ret = re.search(r'\breturn\s+(.+?);', body, re.DOTALL)
            if ret:
                expr = ret.group(1).strip()
                # Strip trailing ``.c_str()`` (returns plain string token).
                expr = re.sub(r'\.c_str\(\)\s*$', '', expr)
                self._getters[name] = expr

        # File-scope ``#define NAME "value"`` (string constants).
        for m in re.finditer(
            r'^\s*#\s*define\s+([A-Za-z_]\w*)\s+"([^"]*)"\s*$', text, re.M
        ):
            self._add_value(m.group(1), m.group(2), [])

        # File-scope ``#define NAME VALUE`` (numeric / expression).
        for m in re.finditer(
            r'^\s*#\s*define\s+([A-Za-z_]\w*)\s+(.+?)\s*$', text, re.M
        ):
            name, val = m.group(1), m.group(2).strip()
            if val.startswith('"'):
                continue  # already handled
            self._add_define(name, val, [])

    # ── Index builders ────────────────────────────────────────────────────────

    def _add_value(self, name: str, value: object, scopes: list[str]) -> None:
        """Store a value under all useful suffix combinations of its scope.

        For ``KODI::PLAYLIST::Id::TYPE_MUSIC = 0`` (scopes = [KODI, PLAYLIST, Id])
        we store ``TYPE_MUSIC``, ``Id::TYPE_MUSIC``, ``PLAYLIST::Id::TYPE_MUSIC``,
        and ``KODI::PLAYLIST::Id::TYPE_MUSIC`` so callers can look up by any
        natural form. Earlier definitions win on collision (more specific scopes
        still resolve correctly via their fully-qualified key).
        """
        keys = [name]
        for n in range(1, len(scopes) + 1):
            keys.append('::'.join(scopes[-n:]) + '::' + name)
        for key in keys:
            self._known.setdefault(key, value)

    def _add_define(self, name: str, raw_value: str, scopes: list[str]) -> None:
        """Store a ``#define`` value (numeric, identifier, or expression)."""
        # Try int first.
        try:
            self._add_value(name, int(raw_value, 0), scopes)
            return
        except ValueError:
            pass
        # Resolve symbolically (later, when all known values are loaded).
        # Stash as a getter-like alias so ``resolve`` can chase it.
        self._getters[name] = raw_value

    # ── Resolution ────────────────────────────────────────────────────────────

    def resolve(self, raw_val: str) -> Optional[object]:
        """Resolve a raw C++ constant expression to a Python value.

        Returns ``int``, ``str``, or ``None`` if resolution fails.
        """
        raw_val = raw_val.strip()
        if raw_val in self._cache:
            return self._cache[raw_val]
        result = self._try_resolve(raw_val)
        self._cache[raw_val] = result
        return result

    def _try_resolve(self, expr: str) -> Optional[object]:
        expr = expr.strip()
        if not expr:
            return None

        # Direct integer literal.
        try:
            return int(expr, 0)
        except ValueError:
            pass

        # Direct string literal: "..." (single-line, no escapes outside basic).
        m = re.fullmatch(r'"((?:[^"\\]|\\.)*)"', expr)
        if m:
            return self._unescape_c_string(m.group(1))

        # ``static_cast<TYPE>(EXPR)`` — strip and recurse.
        m = re.fullmatch(r'static_cast<[^<>]+>\s*\((.*)\)', expr, re.DOTALL)
        if m:
            return self._try_resolve(m.group(1))

        # Direct lookup (handles fully-qualified ``A::B::C``).
        if expr in self._known:
            return self._known[expr]

        # Getter call ``getNAME()`` — chase the cached return expression.
        m = re.fullmatch(r'(get[A-Za-z_]\w*)\s*\(\s*\)', expr)
        if m:
            getter = m.group(1)
            if getter in self._resolving:
                return None  # cycle
            body = self._getters.get(getter)
            if body is not None:
                self._resolving.add(getter)
                try:
                    return self._try_resolve(body)
                finally:
                    self._resolving.discard(getter)
            # Fall back to direct name lookup (``getLOGDEBUG`` → ``LOGDEBUG``).
            tail = getter[3:]
            if tail in self._known:
                return self._known[tail]
            return None

        # Plain identifier alias chase (``CONTROL_NO_BUTTON`` → ``CONTROL_CHOICES_START``).
        if re.fullmatch(r'[A-Za-z_]\w*', expr):
            if expr in self._getters:
                if expr in self._resolving:
                    return None
                self._resolving.add(expr)
                try:
                    return self._try_resolve(self._getters[expr])
                finally:
                    self._resolving.discard(expr)
            return None

        # Arithmetic / scoped identifier expression.
        return self._eval_with_substitution(expr)

    def _eval_with_substitution(self, expr: str) -> Optional[int]:
        """Substitute identifiers with known integer values, then eval as Python."""
        unresolved: list[str] = []

        def replace(m: re.Match[str]) -> str:
            token = m.group(0)
            val = self._known.get(token)
            if val is None and '::' in token:
                # Try shorter suffixes.
                parts = token.split('::')
                for i in range(1, len(parts)):
                    suffix = '::'.join(parts[i:])
                    if suffix in self._known:
                        val = self._known[suffix]
                        break
            if val is None and token in self._getters:
                val = self._try_resolve(self._getters[token])
            if isinstance(val, int):
                return str(val)
            unresolved.append(token)
            return token

        sub = _TOKEN_RE.sub(replace, expr)
        if unresolved:
            return None
        # Strip trailing ``;`` if any sneaks in.
        sub = sub.rstrip(';').strip()
        try:
            tree = ast.parse(sub, mode='eval')
            return _eval_ast(tree.body)
        except (SyntaxError, ValueError):
            return None

    @staticmethod
    def _unescape_c_string(s: str) -> str:
        """Minimal C-string unescape (sufficient for known constants)."""
        return (s
                .replace('\\\\', '\\')
                .replace('\\n', '\n')
                .replace('\\t', '\t')
                .replace('\\"', '"')
                .replace("\\'", "'"))


# ──────────────────────────────────────────────────────────────────────────────
# .i.cpp parser
# ──────────────────────────────────────────────────────────────────────────────

_META_CONSTANTS = frozenset({
    '__author__', '__date__', '__version__', '__credits__', '__platform__',
})


def parse_constants_from_cpp(cpp_path: str,
                              resolver: EnumResolver) -> dict[str, object]:
    """Parse ``PyModule_Add{Int,String}Constant`` calls from a ``.i.cpp`` file.

    Returns a dict mapping constant name → Python value (``int`` or ``str``).
    Constants that can't be resolved are emitted with a typed-zero placeholder
    (``0`` for ints, ``''`` for strings) — better to ship a syntactically valid
    stub than crash the whole pipeline.
    """
    if not os.path.exists(cpp_path):
        return {}
    with open(cpp_path, encoding='utf-8', errors='replace') as f:
        text = f.read()

    result: dict[str, object] = {}

    # Integer constants.
    for m in re.finditer(
        r'PyModule_AddIntConstant\s*\(\s*\w+\s*,\s*"(\w+)"\s*,\s*(.+?)\s*\)\s*;',
        text,
    ):
        name, val_expr = m.group(1), m.group(2).strip()
        if name in _META_CONSTANTS:
            continue
        resolved = resolver.resolve(val_expr)
        if isinstance(resolved, int):
            result[name] = resolved
        else:
            result[name] = 0  # placeholder

    # String constants (literal ``"..."``).
    for m in re.finditer(
        r'PyModule_AddStringConstant\s*\(\s*\w+\s*,\s*"(\w+)"\s*,\s*"([^"]*)"\s*\)\s*;',
        text,
    ):
        name, val = m.group(1), m.group(2)
        if name in _META_CONSTANTS:
            continue
        result[name] = val

    # String constants via getter (``getNAME()``) or arbitrary expression.
    # The non-greedy ``(.+?)`` plus ``\)\s*;`` anchor handles nested parens
    # in the value expression (e.g. ``getXXX()`` or ``foo().c_str()``).
    for m in re.finditer(
        r'PyModule_AddStringConstant\s*\(\s*\w+\s*,\s*"(\w+)"\s*,\s*(.+?)\s*\)\s*;',
        text,
    ):
        name, val_expr = m.group(1), m.group(2).strip()
        if name in _META_CONSTANTS:
            continue
        if name in result:
            continue  # already parsed as a literal above
        if val_expr.startswith('"'):
            continue  # literal already handled
        resolved = resolver.resolve(val_expr)
        if isinstance(resolved, str):
            result[name] = resolved
        else:
            result[name] = ''  # placeholder

    return result


def load_constants(module: str, swig_dir: str, kodi_src: str) -> dict[str, object]:
    """Load all constants for a module from its ``.i.cpp`` file."""
    cpp_name_map = {
        'xbmc': 'AddonModuleXbmc',
        'xbmcaddon': 'AddonModuleXbmcaddon',
        'xbmcgui': 'AddonModuleXbmcgui',
        'xbmcplugin': 'AddonModuleXbmcplugin',
        'xbmcvfs': 'AddonModuleXbmcvfs',
        'xbmcdrm': 'AddonModuleXbmcdrm',
    }
    base = cpp_name_map.get(module, f'AddonModule{module.capitalize()}')
    cpp_path = os.path.join(swig_dir, f'{base}.i.cpp')
    resolver = EnumResolver(kodi_src)
    constants = parse_constants_from_cpp(cpp_path, resolver)
    return {k: v for k, v in constants.items() if k not in _META_CONSTANTS}
