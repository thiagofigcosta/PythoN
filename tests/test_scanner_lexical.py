from __future__ import annotations

from pythonn.scanner import code_text, scan


def scan_one(text: str):
    return scan(text)[0]


def test_a_plain_code_line_is_all_code():
    line = scan_one("x = 1")
    assert code_text(line) == "x = 1"
    assert line.trailing_comment is None


def test_a_string_body_is_not_code():
    line = scan_one("x = 'hello'")
    assert code_text(line) == "x = "


def test_a_comment_is_not_code_and_is_reported():
    line = scan_one("x = 1  # note")
    assert code_text(line) == "x = 1  "
    assert line.text[line.trailing_comment.start:] == "# note"


def test_a_hash_inside_a_string_is_not_a_comment():
    line = scan_one("x = '# not a comment'")
    assert line.trailing_comment is None


def test_a_brace_inside_a_comment_is_not_code():
    line = scan_one("if True:  # a } here")
    assert "}" not in code_text(line)


def test_a_triple_quoted_string_spans_lines():
    lines = scan('x = """\n} braces { inside\n"""\ny = 1')
    assert lines[1].in_string_before is True
    assert code_text(lines[1]) == ""
    assert lines[3].in_string_before is False
    assert code_text(lines[3]) == "y = 1"


def test_an_escaped_quote_does_not_end_a_string():
    line = scan_one("x = 'it\\'s'  # after")
    assert line.text[line.trailing_comment.start:] == "# after"


def test_a_raw_string_backslash_does_not_escape():
    line = scan_one("x = r'a\\'  # after")
    assert line.text[line.trailing_comment.start:] == "# after"


def test_an_fstring_prefix_is_code_but_its_body_is_not():
    line = scan_one('x = f"{a}{b}"')
    # The `f` is part of the expression, so it stays code; everything from the
    # opening quote on, braces included, does not.
    assert code_text(line) == "x = f"
    assert "{" not in code_text(line)


def test_an_unterminated_single_quote_does_not_leak_to_the_next_line():
    lines = scan("x = 'oops\ny = 1")
    assert lines[1].in_string_before is False
    assert code_text(lines[1]) == "y = 1"
