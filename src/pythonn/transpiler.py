from __future__ import annotations

from dataclasses import dataclass

from .braces import BraceEvent, BraceKind, classify
from .errors import PythoNError
from .pragmas import START_REGULAR, directive, is_ignored, verbatim_lines
from .scanner import LineScan, scan

DEFAULT_INDENT = "    "


@dataclass(frozen=True)
class TranspileResult:
    code: str
    line_map: tuple[int, ...]


def _strip_range(line: LineScan, events: list[BraceEvent], start: int, end: int) -> str:
    parts = []
    previous = start
    for event in events:
        head = line.text[previous:event.column].rstrip()
        parts.append(head + ":" if event.opening else head)
        previous = event.column + 1
    parts.append(line.text[previous:end])
    return "".join(parts).strip()


def _emit_inline(
    line: LineScan, block_events: list[BraceEvent], path: str
) -> tuple[str, str]:
    opener = next(event for event in block_events if event.inline)
    closer = next(
        (
            event
            for event in block_events
            if not event.opening and event.column > opener.column
        ),
        None,
    )
    # classify() only marks an opener inline when it found a closer on the same LOGICAL
    # line, while block_events is grouped by PHYSICAL line - so a missing closer here
    # means exactly one thing: the body was continued with a backslash.
    if closer is None:
        raise PythoNError(
            "an inline block body cannot be continued onto another line",
            path,
            line.index + 1,
            opener.column + 1,
            line.text,
        )
    body = _strip_range(line, [], opener.column + 1, closer.column)
    # The inner pair of `if a { if b { pass } }` classifies as LITERAL - its closer is
    # not last-significant, because the outer `}` still follows - so inspecting this
    # line's own events cannot see it. Re-classifying the body as source of its own
    # does, and leaves `if x { d = {'a': 1} }` alone, whose body holds no block brace.
    if "{" in body and any(
        event.kind is BraceKind.BLOCK for event in classify(scan(body), path)
    ):
        raise PythoNError(
            "nested inline blocks are not supported",
            path,
            line.index + 1,
            opener.column + 1,
            line.text,
        )

    leading = [event for event in block_events if event.column < opener.column]
    header = _strip_range(line, leading + [opener], 0, opener.column + 1)
    tail = line.text[closer.column + 1:].strip()
    if tail:
        header = header + "  " + tail
    return header, body


def transpile(
    source: str, path: str = "<source>", indent: str = DEFAULT_INDENT
) -> TranspileResult:
    scans = scan(source)
    if is_ignored(scans):
        return TranspileResult(source, tuple(range(1, len(scans) + 1)))

    events = classify(scans, path)
    verbatim = verbatim_lines(scans)

    by_line: dict[int, list[BraceEvent]] = {}
    for event in events:
        if event.kind is BraceKind.BLOCK:
            by_line.setdefault(event.line, []).append(event)

    depth = 0
    emitted = []
    line_map = []

    for line in scans:
        block_events = sorted(by_line.get(line.index, ()), key=lambda e: e.column)

        if line.index in verbatim:
            if depth != 0 and directive(line) == START_REGULAR:
                raise PythoNError(
                    "a regular Python region cannot start inside a block",
                    path,
                    line.index + 1,
                    1,
                    line.text,
                )
            if block_events:
                raise PythoNError(
                    "braces are not processed inside a regular Python region",
                    path,
                    line.index + 1,
                    block_events[0].column + 1,
                    line.text,
                )
            emitted.append(line.text)
            line_map.append(line.index + 1)
            continue

        if line.in_string_before:
            # This line is the CONTENT of a triple-quoted string opened on an earlier
            # line (the opener itself is code and falls through to the normal path
            # below) - strip-and-reindent would rewrite the user's string data.
            emitted.append(line.text)
            line_map.append(line.index + 1)
            continue

        line_depth = depth
        for event in block_events:
            if event.opening:
                depth += 1
            else:
                depth -= 1
                line_depth = min(line_depth, depth)

        if any(event.inline for event in block_events):
            header, body = _emit_inline(line, block_events, path)
            emitted.append(indent * line_depth + header)
            line_map.append(line.index + 1)
            emitted.append(indent * (line_depth + 1) + body)
            line_map.append(line.index + 1)
            continue

        text = _strip_range(line, block_events, 0, len(line.text))
        emitted.append(indent * line_depth + text if text else "")
        line_map.append(line.index + 1)

    return TranspileResult("\n".join(emitted), tuple(line_map))
