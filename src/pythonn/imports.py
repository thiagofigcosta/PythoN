from __future__ import annotations

import os
import re

from .errors import PythoNError
from .scanner import LineScan, code_text, scan

_IMPORT = re.compile(r"^import\s+(?P<names>.+)$")
_FROM = re.compile(r"^from\s+(?P<module>\.*[\w.]*)\s+import\s")


def logical_code_lines(scans: tuple[LineScan, ...]) -> tuple[tuple[int, str], ...]:
    grouped: dict[int, list[str]] = {}
    order = []
    for line in scans:
        start = line.logical_line_start
        if start not in grouped:
            grouped[start] = []
            order.append(start)
        grouped[start].append(code_text(line).strip())
    return tuple(
        (start, " ".join(part for part in grouped[start] if part)) for start in order
    )


def module_names(code: str) -> tuple[str, ...]:
    text = code.strip()
    match = _FROM.match(text)
    if match:
        module = match.group("module")
        return (module,) if module else ()
    match = _IMPORT.match(text)
    if match is None:
        return ()
    names = []
    for part in match.group("names").split(","):
        name = part.strip().split(" as ")[0].strip()
        if re.match(r"^\.*[\w.]+$", name):
            names.append(name)
    return tuple(names)


def resolve(module: str, base_dir: str) -> str | None:
    if module.startswith(".."):
        return None
    relative = module[1:] if module.startswith(".") else module
    # A dotted module name never legally contains a path separator or is absolute;
    # os.path.join silently DISCARDS base_dir on an absolute component, so this
    # guards the same escape mirror_path already guards against '..' for.
    if os.sep in relative or (os.altsep and os.altsep in relative) or os.path.isabs(
        relative
    ):
        return None
    parts = [part for part in relative.split(".") if part]
    if not parts:
        candidate = os.path.join(base_dir, "__init__.py")
        return os.path.abspath(candidate) if os.path.isfile(candidate) else None
    stem = os.path.join(base_dir, *parts)
    for candidate in (stem + ".py", os.path.join(stem, "__init__.py")):
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)
    return None


def read_source(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except UnicodeDecodeError:
        raise PythoNError("not valid UTF-8", path) from None
    except OSError as error:
        raise PythoNError(error.strerror or "cannot be read", path) from None


def collect(entry_path: str) -> tuple[str, ...]:
    entry = os.path.abspath(entry_path)
    ordered = [entry]
    seen = {entry}
    queue = [entry]

    while queue:
        current = queue.pop(0)
        base_dir = os.path.dirname(current)
        scans = scan(read_source(current))
        for _, code in logical_code_lines(scans):
            for module in module_names(code):
                resolved = resolve(module, base_dir)
                if resolved is not None and resolved not in seen:
                    seen.add(resolved)
                    ordered.append(resolved)
                    queue.append(resolved)

    return tuple(ordered)
