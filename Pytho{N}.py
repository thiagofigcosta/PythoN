#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Pytho{\} - a curly-brace pre-compiler for Python.

GENERATED FILE - do not edit.
Edit src/pythonn/*.py and run: python3 scripts/build_vendor.py
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile


class PythoNError(Exception):
    """A fault in the Pytho{\\} source, reported against its real position."""

    def __init__(
        self,
        message: str,
        path: str = "",
        line: int = 0,
        column: int = 0,
        source_line: str = "",
    ) -> None:
        super().__init__(message)
        self.message = message
        self.path = path
        self.line = line
        self.column = column
        self.source_line = source_line

    def render(self) -> str:
        if self.line == 0:
            head = "{}: error: {}".format(self.path, self.message)
        else:
            head = "{}:{}:{}: error: {}".format(
                self.path, self.line, self.column, self.message
            )
        if not self.source_line:
            return head
        caret = " " * max(0, self.column - 1) + "^"
        return "{}\n{}\n{}".format(head, self.source_line, caret)


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


def common_root(paths: tuple[str, ...]) -> str:
    directories = [os.path.dirname(os.path.abspath(path)) for path in paths]
    if not directories:
        return os.getcwd()
    if len(directories) == 1:
        return directories[0]
    return os.path.commonpath(directories)


def mirror_path(path: str, root: str, temp_root: str) -> str:
    relative = os.path.relpath(os.path.abspath(path), root)
    # relpath answers with a `..` prefix when root does not contain path, and the caller
    # writes a file to whatever comes back - so an unguarded join escapes the build tree.
    if relative == os.pardir or relative.startswith(os.pardir + os.sep):
        raise ValueError("{} is not inside {}".format(path, root))
    return os.path.join(temp_root, relative)


def build_command(python_version: str, entry: str, args: tuple[str, ...]) -> list[str]:
    command = ["python{}".format(python_version)]
    if entry:
        command.append(entry)
    command.extend(args)
    return command


def run(command: list[str], show_cmd: bool = False) -> int:
    if show_cmd:
        print(" ".join(shlex.quote(part) for part in command) + "\n")
    try:
        return subprocess.run(command).returncode
    except FileNotFoundError:
        raise PythoNError("interpreter not found", path=command[0]) from None


def _split_at_program(argv: list[str]) -> int | None:
    """Index of the first token that hands argv over to the target program:
    a literal '--', or the first '.py' source file - whichever comes first.
    None means the whole argv is still ours (interactive-shell case)."""
    for index, item in enumerate(argv):
        if item == "--" or item.endswith(".py"):
            return index
    return None


def parse_args(argv: list[str]) -> tuple[argparse.Namespace, str, tuple[str, ...]]:
    parser = argparse.ArgumentParser(
        prog="Pytho{N}.py",
        description="Run Python written with curly brackets instead of indentation.",
    )
    parser.add_argument("-v", "--version", dest="python_version", default="3")
    parser.add_argument("--show-cmd", action="store_true")
    parser.add_argument("--print-output", action="store_true")
    parser.add_argument("--keep-temp", action="store_true")

    split = _split_at_program(argv)
    if split is None:
        # No '.py' and no '--': the whole line might still be ours (e.g. a bare
        # `-v 2`), so let argparse read everything, exactly as before.
        options, rest = parser.parse_known_args(argv)
        source = ""
        program_args = []
        for item in rest:
            if not source and item.endswith(".py"):
                source = item
                continue
            program_args.append(item)
        return options, source, tuple(program_args)

    # Only OUR flags precede the split point - a program flag that collides with one
    # of ours (e.g. `app.py -v`) must never reach argparse, or it gets consumed.
    options, _ = parser.parse_known_args(argv[:split])
    if argv[split] == "--":
        return options, "", tuple(argv[split + 1:])
    return options, argv[split], tuple(argv[split + 1:])


def compile_tree(source_path: str, temp_root: str, print_output: bool = False) -> str:
    entry_path = os.path.abspath(source_path)
    files = collect(source_path)
    root = common_root(files)

    for path in files:
        content = read_source(path)
        result = transpile(content, path=path)
        target = mirror_path(path, root, temp_root)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(result.code)
        if print_output:
            print(result.code)

    # Derived from the entry's own path, not from collect()'s iteration order -
    # which file gets executed no longer rides on an incidental "collect() always
    # returns the entry first" guarantee.
    return mirror_path(entry_path, root, temp_root)


def main(argv: list[str]) -> int:
    options, source, program_args = parse_args(argv)

    if not source:
        command = build_command(options.python_version, "", program_args)
        try:
            return run(command, options.show_cmd)
        except PythoNError as error:
            sys.stderr.write(error.render() + "\n")
            return 2

    temp_root = tempfile.mkdtemp(prefix="pythoN-")
    try:
        try:
            entry = compile_tree(source, temp_root, options.print_output)
            command = build_command(options.python_version, entry, program_args)
            return run(command, options.show_cmd)
        except PythoNError as error:
            sys.stderr.write(error.render() + "\n")
            return 2
    finally:
        # One finally covering every exit path. Cleaning up only after PythoNError left
        # the build tree behind for any other failure in the pipeline.
        if options.keep_temp:
            sys.stderr.write("kept build tree: {}\n".format(temp_root))
        else:
            shutil.rmtree(temp_root, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
