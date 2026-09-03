from __future__ import annotations

import pytest

from pythonn.errors import PythoNError
from pythonn.transpiler import transpile


def out(source: str) -> str:
    return transpile(source).code


def test_a_block_becomes_a_colon_and_four_spaces():
    assert out("if x {\n    pass\n}") == "if x:\n    pass\n"


def test_source_indentation_is_discarded():
    assert out("if x {\n            pass\n}") == "if x:\n    pass\n"


def test_nested_blocks_nest_the_indentation():
    source = "if a {\nif b {\npass\n}\n}"
    assert out(source) == "if a:\n    if b:\n        pass\n\n"


def test_else_on_the_closing_line_keeps_the_outer_depth():
    source = "if a {\n    x()\n} else {\n    y()\n}"
    assert out(source) == "if a:\n    x()\nelse:\n    y()\n"


def test_an_inline_block_becomes_two_lines():
    assert out("if x { pass }") == "if x:\n    pass"


def test_an_inline_block_keeps_its_trailing_comment_on_the_header():
    assert out("if x { pass }  # note") == "if x:  # note\n    pass"


def test_a_comment_containing_a_brace_does_not_close_a_block():
    source = "if True {\n    # a } here\n    x()\n}"
    assert out(source) == "if True:\n    # a } here\n    x()\n"


def test_braces_inside_a_triple_quoted_string_are_untouched():
    source = 'x = """\n} braces { inside\n"""\nif True {\n    pass\n}'
    assert out(source) == 'x = """\n} braces { inside\n"""\nif True:\n    pass\n'


def test_a_nested_multiline_dict_survives():
    source = 'd = {\n    "a": {\n        "b": 1\n    }\n}\nif d {\n    pass\n}'
    assert out(source) == (
        'd = {\n"a": {\n"b": 1\n}\n}\nif d:\n    pass\n'
    )


def test_a_lambda_returning_a_dict_survives():
    source = 'f = lambda: {"k": "v"}\nif f() {\n    pass\n}'
    assert out(source) == 'f = lambda: {"k": "v"}\nif f():\n    pass\n'


def test_an_ignored_file_is_returned_byte_for_byte():
    source = "if x:\n    pass  # }{\n" + r"# Pytho{\}: Ignore file" + "\n"
    assert out(source) == source


def test_a_verbatim_region_is_emitted_untouched():
    source = "\n".join(
        [
            r"# Pytho{\}: Start regular Python",
            "for i in range(2):",
            "    print(i)",
            r"# Pytho{\}: End regular Python",
        ]
    )
    assert out(source) == source


def test_a_verbatim_region_inside_a_block_is_an_error():
    source = "\n".join(
        [
            "if x {",
            r"# Pytho{\}: Start regular Python",
            "pass",
            r"# Pytho{\}: End regular Python",
            "}",
        ]
    )
    with pytest.raises(PythoNError, match="cannot start inside a block"):
        transpile(source, path="a.py")


def test_nested_inline_blocks_are_rejected_with_a_position():
    with pytest.raises(PythoNError) as caught:
        transpile("if a { if b { pass } }", path="a.py")
    assert "nested inline" in caught.value.message
    assert (caught.value.line, caught.value.column) == (1, 6)


def test_an_inline_body_continued_with_a_backslash_is_rejected_clearly():
    with pytest.raises(PythoNError) as caught:
        transpile("if a { pass \\\n}", path="a.py")
    assert "continued onto another line" in caught.value.message
    assert (caught.value.line, caught.value.column) == (1, 6)


def test_a_continued_condition_is_fine_when_the_braces_share_a_line():
    assert out("if a and \\\n   b { x = 1 }") == "if a and \\\nb:\n    x = 1"


def test_an_inline_block_may_still_contain_a_dict_literal():
    assert out("if x { d = {'a': 1} }") == "if x:\n    d = {'a': 1}"


def test_the_line_map_is_one_to_one_without_inline_blocks():
    result = transpile("if x {\n    pass\n}")
    assert result.line_map == (1, 2, 3)


def test_the_line_map_repeats_the_source_line_for_an_inline_block():
    result = transpile("if x { pass }")
    assert result.line_map == (1, 1)


def test_output_indentation_is_spaces_not_tabs():
    assert "\t" not in out("if x {\n    pass\n}")
