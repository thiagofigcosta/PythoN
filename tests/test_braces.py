from __future__ import annotations

import contextlib
import io

import pytest

from pythonn.braces import BraceKind, classify, head_keyword
from pythonn.errors import PythoNError
from pythonn.scanner import scan
from pythonn.transpiler import transpile


def kinds(source: str):
    return [(e.opening, e.kind) for e in classify(scan(source))]


def test_a_compound_header_ending_in_a_brace_opens_a_block():
    assert kinds("if x {\n    pass\n}") == [
        (True, BraceKind.BLOCK),
        (False, BraceKind.BLOCK),
    ]


def test_an_assignment_brace_is_a_literal():
    assert kinds("d = {'a': 1}") == [
        (True, BraceKind.LITERAL),
        (False, BraceKind.LITERAL),
    ]


def test_a_lambda_returning_a_dict_is_a_literal():
    assert kinds('f = lambda: {"k": "v"}') == [
        (True, BraceKind.LITERAL),
        (False, BraceKind.LITERAL),
    ]


def test_a_nested_multiline_dict_is_all_literal():
    source = 'd = {\n    "a": {\n        "b": 1\n    }\n}'
    assert {kind for _, kind in kinds(source)} == {BraceKind.LITERAL}


def test_a_brace_inside_round_brackets_is_a_literal():
    assert kinds("f({'a': 1})") == [
        (True, BraceKind.LITERAL),
        (False, BraceKind.LITERAL),
    ]


def test_a_dict_inside_a_block_stays_literal_while_the_block_stays_block():
    source = "if x {\n    d = {'a': 1}\n}"
    assert kinds(source) == [
        (True, BraceKind.BLOCK),
        (True, BraceKind.LITERAL),
        (False, BraceKind.LITERAL),
        (False, BraceKind.BLOCK),
    ]


def test_a_wrapped_header_still_opens_a_block():
    assert kinds("if (a and\n    b) {\n    pass\n}")[0] == (True, BraceKind.BLOCK)


def test_every_compound_keyword_opens_a_block():
    for keyword, header in [
        ("if", "if x {"),
        ("elif", "elif x {"),
        ("else", "else {"),
        ("for", "for i in y {"),
        ("while", "while x {"),
        ("def", "def f() {"),
        ("class", "class A {"),
        ("try", "try {"),
        ("except", "except E {"),
        ("finally", "finally {"),
        ("with", "with a as b {"),
        ("match", "match x {"),
        ("case", "case 1 {"),
    ]:
        assert kinds(header + "\n    pass\n}")[0] == (
            True,
            BraceKind.BLOCK,
        ), keyword


def test_async_def_opens_a_block():
    assert kinds("async def f() {\n    pass\n}")[0] == (True, BraceKind.BLOCK)


def test_head_keyword_reads_the_logical_line_start():
    scans = scan("if (a and\n    b) {")
    assert head_keyword(scans, scans[1].logical_line_start) == "if"


def test_an_inline_block_is_marked_inline():
    events = classify(scan("if x { pass }"))
    assert events[0].kind is BraceKind.BLOCK
    assert events[0].inline is True


def test_a_closing_brace_before_elif_does_not_hide_the_keyword():
    # examples/basic_external_file.py ships both spacings of this form.
    for header in ("}elif x {", "}   elif x {"):
        events = classify(scan("if a {\n    pass\n" + header + "\n    pass\n}"))
        assert events[2].kind is BraceKind.BLOCK, header


def test_a_trailing_comment_does_not_stop_a_block_open():
    assert kinds("if x {  # note\n    pass\n}")[0] == (True, BraceKind.BLOCK)


def test_an_unmatched_close_is_reported_with_a_position():
    with pytest.raises(PythoNError) as caught:
        classify(scan("x = 1\n}"), path="a.py")
    assert (caught.value.line, caught.value.column) == (2, 1)


def test_an_unclosed_open_is_reported_with_a_position():
    with pytest.raises(PythoNError) as caught:
        classify(scan("if x {\n    pass"), path="a.py")
    assert (caught.value.line, caught.value.column) == (1, 6)


@pytest.mark.parametrize(
    "source",
    [
        'match = {"a": 1}',
        "match[k] = {}",
        "match.attr = {}",
        "match, y = {1}, 2",
        "match == {}",
    ],
)
def test_match_used_as_an_identifier_is_not_a_block_header(source):
    # match/case are SOFT keywords - unlike every other name in BLOCK_KEYWORDS they
    # can legally be a variable, so each of these must read as a plain literal brace.
    # NOTE: "match(x) { pass }" used to live in this list, expecting LITERAL. It was
    # wrong: real Python parses `match(x):` as a match statement over the parenthesized
    # subject `(x)`, not a call (verified against CPython) - `(` can't be a reject
    # char. See test_soft_keyword_rule_table below for the corrected rule.
    assert kinds(source)[0] == (True, BraceKind.LITERAL)


def test_match_and_case_still_open_a_block_as_statements():
    assert kinds("match value {\n    pass\n}")[0] == (True, BraceKind.BLOCK)
    assert kinds("case 1 {\n    pass\n}")[0] == (True, BraceKind.BLOCK)


def test_an_identifier_named_match_inside_an_inline_block_does_not_raise():
    # Regression: `match`'s hard-keyword misclassification made the reclassified
    # inline body read `match = {}` as its own nested block, so this used to raise
    # "nested inline blocks are not supported".
    result = transpile("if x { match = {} }\n")
    assert result.code == "if x:\n    match = {}\n"


@pytest.mark.parametrize(
    "source, expected",
    [
        ('match = {"a": 1}', BraceKind.LITERAL),
        ("case = {1: 2}", BraceKind.LITERAL),
        ("match == {}", BraceKind.LITERAL),
        ("match.attr = {}", BraceKind.LITERAL),
        ("match, y = 1, {}", BraceKind.LITERAL),
        ("match[k] = {}", BraceKind.LITERAL),
        ("match v {", BraceKind.BLOCK),
        ("case 1 {", BraceKind.BLOCK),
        ("case [a, b] {", BraceKind.BLOCK),
        ("match (a, b) {", BraceKind.BLOCK),
        ("case x if x == 1 {", BraceKind.BLOCK),
        ('match d["k"] {', BraceKind.BLOCK),
    ],
)
def test_soft_keyword_rule_table(source, expected):
    # The corrected rule (see the SOFT_KEYWORDS comment in braces.py): the keyword
    # reads as a statement head unless the text between it and the block brace is
    # empty, starts with an operator, or holds a bracket-depth-zero assignment.
    if expected is BraceKind.BLOCK:
        source = source + "\n    pass\n}"
    assert kinds(source)[0] == (True, expected), source


def test_a_list_pattern_case_transpiles_and_runs():
    # The regression this whole table exists to pin: the old rule rejected `[` and
    # `(` outright, so `case [a, b] {` (one of the most common match shapes) raised
    # a SyntaxError instead of transpiling.
    source = (
        "v = [1, 2]\n"
        "match v {\n"
        "    case [a, b] {\n"
        '        print("list pattern ok", a, b)\n'
        "    }\n"
        "}\n"
    )
    result = transpile(source)
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        exec(compile(result.code, "<test>", "exec"), {})
    assert captured.getvalue() == "list pattern ok 1 2\n"
