from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .errors import PythoNError
from .scanner import Brace, LineScan, code_text

BLOCK_KEYWORDS = frozenset(
    {
        "if",
        "elif",
        "else",
        "for",
        "while",
        "def",
        "class",
        "try",
        "except",
        "finally",
        "with",
        "match",
        "case",
    }
)

_HEAD = re.compile(r"^[\s}]*(?:async\s+)?([A-Za-z_]\w*)")

# match/case are SOFT keywords in real Python - unlike every other name in
# BLOCK_KEYWORDS, they can legally be identifiers. `(` and `[` cannot be excluded
# here: a parenthesized/tupled subject (`match (a, b) {`) and a list pattern
# (`case [a, b] {`) are ordinary statement heads, not identifier uses - only an
# operator lead-in or a real assignment marks the keyword as a plain name instead.
SOFT_KEYWORDS = frozenset({"match", "case"})
_SOFT_KEYWORD_LEADING_OPERATORS = frozenset("=<>!+-*/%&|^@~,.")
_ASSIGNMENT_GUARD_CHARS = frozenset("=!<>")


class BraceKind(Enum):
    BLOCK = "block"
    LITERAL = "literal"


@dataclass(frozen=True)
class BraceEvent:
    line: int
    column: int
    opening: bool
    kind: BraceKind
    inline: bool = False


def head_keyword(scans: tuple[LineScan, ...], logical_start: int) -> str:
    match = _HEAD.match(code_text(scans[logical_start]))
    return match.group(1) if match else ""


def _code_slice(line: LineScan, start_column: int, end_column: int) -> str:
    parts = []
    for span in line.code_spans:
        start = max(span.start, start_column)
        end = min(span.end, end_column)
        if start < end:
            parts.append(line.text[start:end])
    return "".join(parts)


def _code_between(
    scans: tuple[LineScan, ...],
    start_line: int,
    start_column: int,
    end_line: int,
    end_column: int,
) -> str:
    """Code text strictly between two positions, possibly across physical lines of
    one wrapped logical line (e.g. `match (a and\\n    b) {`)."""
    if start_line == end_line:
        return _code_slice(scans[start_line], start_column, end_column)
    parts = [_code_slice(scans[start_line], start_column, len(scans[start_line].text))]
    for index in range(start_line + 1, end_line):
        parts.append(_code_slice(scans[index], 0, len(scans[index].text)))
    parts.append(_code_slice(scans[end_line], 0, end_column))
    return "".join(parts)


def _has_bracket_depth_zero_assignment(text: str) -> bool:
    """An `=` counts as an assignment only outside brackets and only when it is not
    half of `==`, `!=`, `<=`, `>=` (checking one neighbour on each side is enough -
    a real assignment can never itself be adjacent to one of those guard chars)."""
    depth = 0
    length = len(text)
    for index, char in enumerate(text):
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)
        elif char == "=" and depth == 0:
            previous_char = text[index - 1] if index > 0 else ""
            next_char = text[index + 1] if index + 1 < length else ""
            if previous_char not in _ASSIGNMENT_GUARD_CHARS and next_char != "=":
                return True
    return False


def _reads_as_soft_keyword(
    scans: tuple[LineScan, ...], logical_start: int, brace_line: int, brace_column: int
) -> bool:
    keyword_line = scans[logical_start]
    head_match = _HEAD.match(keyword_line.text)
    keyword_end = head_match.end() if head_match else 0
    between = _code_between(scans, logical_start, keyword_end, brace_line, brace_column)
    between = between.strip()
    if not between or between[0] in _SOFT_KEYWORD_LEADING_OPERATORS:
        return False
    return not _has_bracket_depth_zero_assignment(between)


def _code_after(line: LineScan, column: int) -> str:
    parts = []
    for span in line.code_spans:
        start = max(span.start, column + 1)
        if start < span.end:
            parts.append(line.text[start:span.end])
    return "".join(parts)


def _is_last_significant(line: LineScan, column: int) -> bool:
    return _code_after(line, column).strip() == ""


def _closes_inline(
    flat: list[tuple[int, Brace]], position: int, scans: tuple[LineScan, ...]
) -> bool:
    """True when this '{' has its matching '}' on the same logical line, last."""
    opener_line = scans[flat[position][0]]
    depth = 1
    for line_index, brace in flat[position + 1:]:
        depth += 1 if brace.opening else -1
        if depth == 0:
            closer_line = scans[line_index]
            same_logical = (
                closer_line.logical_line_start == opener_line.logical_line_start
            )
            return same_logical and _is_last_significant(closer_line, brace.column)
    return False


def _open_kind(
    flat: list[tuple[int, Brace]],
    position: int,
    scans: tuple[LineScan, ...],
    stack: list[tuple[BraceKind, int, int]],
) -> tuple[BraceKind, bool]:
    line_index, brace = flat[position]
    line = scans[line_index]
    if any(kind is BraceKind.LITERAL for kind, _, _ in stack):
        return BraceKind.LITERAL, False
    if brace.bracket_depth > 0:
        return BraceKind.LITERAL, False
    keyword = head_keyword(scans, line.logical_line_start)
    if keyword not in BLOCK_KEYWORDS:
        return BraceKind.LITERAL, False
    if keyword in SOFT_KEYWORDS and not _reads_as_soft_keyword(
        scans, line.logical_line_start, line_index, brace.column
    ):
        return BraceKind.LITERAL, False
    if _is_last_significant(line, brace.column):
        return BraceKind.BLOCK, False
    if _closes_inline(flat, position, scans):
        return BraceKind.BLOCK, True
    return BraceKind.LITERAL, False


def classify(scans: tuple[LineScan, ...], path: str = "<source>") -> tuple[BraceEvent, ...]:
    flat = [(line.index, brace) for line in scans for brace in line.braces]
    events = []
    stack = []

    for position, (line_index, brace) in enumerate(flat):
        line = scans[line_index]
        if not brace.opening:
            if not stack:
                raise PythoNError(
                    "unmatched '}'",
                    path,
                    line_index + 1,
                    brace.column + 1,
                    line.text,
                )
            kind, _, _ = stack.pop()
            events.append(BraceEvent(line_index, brace.column, False, kind))
            continue
        kind, inline = _open_kind(flat, position, scans, stack)
        stack.append((kind, line_index, brace.column))
        events.append(BraceEvent(line_index, brace.column, True, kind, inline))

    if stack:
        _, line_index, column = stack[-1]
        raise PythoNError(
            "unclosed '{'",
            path,
            line_index + 1,
            column + 1,
            scans[line_index].text,
        )

    return tuple(events)
