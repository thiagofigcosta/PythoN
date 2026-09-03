from __future__ import annotations

from pythonn.pragmas import (
    END_REGULAR,
    IGNORE_FILE,
    START_REGULAR,
    directive,
    is_ignored,
    verbatim_lines,
)
from pythonn.scanner import scan


def test_it_recognises_the_ignore_directive():
    assert directive(scan(r"# Pytho{\}: Ignore file")[0]) == IGNORE_FILE


def test_it_is_case_and_whitespace_insensitive():
    assert directive(scan(r"   #   pytho{\}  :  IGNORE FILE  ")[0]) == IGNORE_FILE


def test_it_recognises_the_region_markers():
    assert directive(scan(r"# Pytho{\}: Start regular Python")[0]) == START_REGULAR
    assert directive(scan(r"# Pytho{\}: End regular Python")[0]) == END_REGULAR


def test_a_plain_comment_is_not_a_directive():
    assert directive(scan("# just a comment")[0]) is None


def test_a_directive_after_code_is_not_a_directive():
    assert directive(scan(r"x = 1  # Pytho{\}: Ignore file")[0]) is None


def test_a_directive_inside_a_string_is_not_a_directive():
    assert directive(scan(r"x = '# Pytho{\}: Ignore file'")[0]) is None


def test_is_ignored_finds_the_directive_anywhere_in_the_file():
    assert is_ignored(scan("x = 1\n" + r"# Pytho{\}: Ignore file")) is True
    assert is_ignored(scan("x = 1")) is False


def test_verbatim_lines_covers_the_region_and_its_markers():
    source = "\n".join(
        [
            "a = 1",
            r"# Pytho{\}: Start regular Python",
            "for i in range(2):",
            "    print(i)",
            r"# Pytho{\}: End regular Python",
            "b = 2",
        ]
    )
    assert verbatim_lines(scan(source)) == frozenset({1, 2, 3, 4})


def test_an_unterminated_region_runs_to_the_end_of_the_file():
    source = "a = 1\n" + r"# Pytho{\}: Start regular Python" + "\nb = 2"
    assert verbatim_lines(scan(source)) == frozenset({1, 2})
