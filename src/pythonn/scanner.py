from __future__ import annotations

from dataclasses import dataclass

TRIPLE_DELIMITERS = ("'''", '"""')
QUOTES = "\"'"


@dataclass(frozen=True)
class Span:
    start: int
    end: int


@dataclass(frozen=True)
class Brace:
    column: int
    opening: bool
    bracket_depth: int


@dataclass(frozen=True)
class LineScan:
    index: int
    text: str
    code_spans: tuple[Span, ...]
    trailing_comment: Span | None
    braces: tuple[Brace, ...]
    bracket_depth_before: int
    bracket_depth_after: int
    in_string_before: bool
    in_string_after: bool
    logical_line_start: int


def code_text(line: LineScan) -> str:
    return "".join(line.text[s.start:s.end] for s in line.code_spans)


def _prefix_is_raw(text: str, quote_index: int) -> bool:
    index = quote_index - 1
    prefix = ""
    while index >= 0 and text[index].isalpha():
        prefix = text[index] + prefix
        index -= 1
    return "r" in prefix.lower()


def scan(source: str) -> tuple[LineScan, ...]:
    lines = source.split("\n")
    scans = []
    delimiter = ""
    raw = False
    depth = 0
    logical_start = 0
    pending_continuation = False

    for index, text in enumerate(lines):
        in_string_before = bool(delimiter)
        depth_before = depth
        continued = pending_continuation or in_string_before or depth_before > 0
        if not continued:
            logical_start = index
        pending_continuation = False
        braces = []
        spans = []
        comment = None
        span_start = None if in_string_before else 0
        escaped_eol = False
        position = 0
        length = len(text)

        while position < length:
            char = text[position]

            if delimiter:
                if not raw and char == "\\":
                    escaped_eol = position + 1 >= length
                    position += 2
                    continue
                if text.startswith(delimiter, position):
                    position += len(delimiter)
                    delimiter = ""
                    raw = False
                    span_start = position
                    continue
                position += 1
                continue

            if char == "#":
                if span_start is not None and position > span_start:
                    spans.append(Span(span_start, position))
                span_start = None
                comment = Span(position, length)
                break

            if char in QUOTES:
                if span_start is not None and position > span_start:
                    spans.append(Span(span_start, position))
                span_start = None
                triple = next(
                    (t for t in TRIPLE_DELIMITERS if text.startswith(t, position)), ""
                )
                delimiter = triple or char
                raw = _prefix_is_raw(text, position)
                position += len(delimiter)
                continue

            if char in "([":
                depth += 1
            elif char in ")]":
                depth = max(0, depth - 1)
            elif char in "{}":
                braces.append(Brace(position, char == "{", depth))

            position += 1

        if span_start is not None and span_start < length:
            spans.append(Span(span_start, length))

        # A single-quoted string cannot cross a newline unless the newline itself was
        # escaped; without this reset one unterminated quote would swallow the file.
        if delimiter and len(delimiter) == 1 and not escaped_eol:
            delimiter = ""
            raw = False

        if not delimiter and comment is None:
            trailing = len(text) - len(text.rstrip("\\"))
            pending_continuation = trailing % 2 == 1

        scans.append(
            LineScan(
                index=index,
                text=text,
                code_spans=tuple(spans),
                trailing_comment=comment,
                braces=tuple(braces),
                bracket_depth_before=depth_before,
                bracket_depth_after=depth,
                in_string_before=in_string_before,
                in_string_after=bool(delimiter),
                logical_line_start=logical_start,
            )
        )

    return tuple(scans)
