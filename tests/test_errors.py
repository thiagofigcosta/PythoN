from __future__ import annotations

import pytest

from pythonn.errors import PythoNError


def test_render_without_source_line_is_one_line():
    err = PythoNError("unmatched '}'", path="a.py", line=3, column=1)
    assert err.render() == "a.py:3:1: error: unmatched '}'"


def test_render_places_the_caret_under_the_column():
    err = PythoNError(
        "unmatched '}'", path="a.py", line=3, column=5, source_line="    }"
    )
    assert err.render() == "a.py:3:5: error: unmatched '}'\n    }\n    ^"


def test_it_is_an_exception_and_carries_its_message():
    with pytest.raises(PythoNError, match="boom"):
        raise PythoNError("boom")


def test_a_file_level_fault_renders_without_a_fake_position():
    err = PythoNError("not valid UTF-8", path="a.py")
    assert err.render() == "a.py: error: not valid UTF-8"
