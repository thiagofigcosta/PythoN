from __future__ import annotations

import re

from .scanner import LineScan, code_text

IGNORE_FILE = "ignore file"
START_REGULAR = "start regular python"
END_REGULAR = "end regular python"

_DIRECTIVE = re.compile(
    r"^\s*#\s*Pytho\{\\\}\s*:\s*"
    r"(?P<verb>ignore\s+file|start\s+regular\s+python|end\s+regular\s+python)\s*$",
    re.IGNORECASE,
)


def directive(line: LineScan) -> str | None:
    if line.trailing_comment is None:
        return None
    if code_text(line).strip():
        return None
    match = _DIRECTIVE.match(line.text[line.trailing_comment.start:])
    if match is None:
        return None
    return re.sub(r"\s+", " ", match.group("verb")).strip().lower()


def is_ignored(scans: tuple[LineScan, ...]) -> bool:
    return any(directive(line) == IGNORE_FILE for line in scans)


def verbatim_lines(scans: tuple[LineScan, ...]) -> frozenset[int]:
    inside = False
    marked = set()
    for line in scans:
        verb = directive(line)
        if verb == START_REGULAR:
            inside = True
            marked.add(line.index)
        elif verb == END_REGULAR:
            inside = False
            marked.add(line.index)
        elif inside:
            marked.add(line.index)
    return frozenset(marked)
