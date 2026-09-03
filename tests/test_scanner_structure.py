from __future__ import annotations

from pythonn.scanner import scan


def test_round_brackets_carry_depth_across_lines():
    lines = scan("f(\n  1,\n)")
    assert lines[0].bracket_depth_after == 1
    assert lines[1].bracket_depth_before == 1
    assert lines[2].bracket_depth_after == 0


def test_curly_braces_are_recorded_with_column_and_depth():
    line = scan("if x {")[0]
    assert [(b.column, b.opening, b.bracket_depth) for b in line.braces] == [
        (5, True, 0)
    ]


def test_a_curly_brace_does_not_change_bracket_depth():
    line = scan("d = {1: 2}")[0]
    assert line.bracket_depth_after == 0


def test_a_brace_inside_a_string_is_not_recorded():
    line = scan("x = '{ }'")[0]
    assert line.braces == ()


def test_a_brace_inside_a_comment_is_not_recorded():
    line = scan("x = 1  # }")[0]
    assert line.braces == ()


def test_a_brace_inside_round_brackets_records_the_depth():
    line = scan("f({'a': 1})")[0]
    assert line.braces[0].bracket_depth == 1


def test_a_wrapped_header_shares_one_logical_line():
    lines = scan("if (a and\n    b) {\n    pass\n}")
    assert lines[0].logical_line_start == 0
    assert lines[1].logical_line_start == 0
    assert lines[2].logical_line_start == 2


def test_a_backslash_continues_the_logical_line():
    lines = scan("x = 1 + \\\n    2\ny = 3")
    assert lines[1].logical_line_start == 0
    assert lines[2].logical_line_start == 2


def test_an_even_run_of_trailing_backslashes_does_not_continue_the_line():
    # The line ends `x = 1 \\` - an escaped backslash, not a continuation marker.
    # Testing endswith("\\") instead of counting the run gets this exact case wrong.
    lines = scan("x = 1 \\\\\ny = 3")
    assert lines[1].logical_line_start == 1


def test_lines_inside_a_triple_quoted_string_belong_to_its_logical_line():
    lines = scan('x = """\na\n"""\ny = 1')
    assert lines[1].logical_line_start == 0
    assert lines[3].logical_line_start == 3
