#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import sys

MODULE_ORDER = (
    "errors",
    "scanner",
    "braces",
    "pragmas",
    "transpiler",
    "imports",
    "paths",
    "runner",
    "cli",
)

HEADER = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Pytho{\\} - a curly-brace pre-compiler for Python.

GENERATED FILE - do not edit.
Edit src/pythonn/*.py and run: python3 scripts/build_vendor.py
"""
from __future__ import annotations

'''

FOOTER = '''

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''

# These patterns assume every module keeps its imports single-line, at column zero, with
# no module-level docstring. An indented import inside a function, a parenthesised
# multi-line import, or a docstring line starting with `from` would be hoisted or stripped
# wrongly - and the drift test would report a mismatch without explaining why.
_RELATIVE_IMPORT = re.compile(r"^from\s+\.")
_FUTURE_IMPORT = re.compile(r"^from\s+__future__\s+import")
_ABSOLUTE_IMPORT = re.compile(r"^(import\s+\w|from\s+\w)")


def build(source_dir: pathlib.Path) -> str:
    stdlib_imports = set()
    bodies = []

    for name in MODULE_ORDER:
        lines = (source_dir / (name + ".py")).read_text().splitlines()
        kept = []
        for line in lines:
            if _FUTURE_IMPORT.match(line) or _RELATIVE_IMPORT.match(line):
                continue
            if _ABSOLUTE_IMPORT.match(line):
                stdlib_imports.add(line)
                continue
            kept.append(line)
        bodies.append("\n".join(kept).strip("\n"))

    imports_block = "\n".join(sorted(stdlib_imports))
    body = "\n\n\n".join(bodies)
    return HEADER + imports_block + "\n\n\n" + body + FOOTER


def main() -> int:
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    target = repo_root / "Pytho{N}.py"
    target.write_text(build(repo_root / "src" / "pythonn"))
    target.chmod(0o755)
    return 0


if __name__ == "__main__":
    sys.exit(main())
