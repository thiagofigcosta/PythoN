from __future__ import annotations

import pathlib

import pytest

from tests.conftest import run_vendored

EXAMPLES = sorted((pathlib.Path(__file__).parent.parent / "examples").glob("*.py"))


def test_the_examples_directory_is_not_empty():
    # Guards the parametrisation below: a bad glob would silently collect nothing
    # and every example test would vanish while the suite still reported green.
    assert len(EXAMPLES) >= 10


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.name)
def test_every_example_runs(example: pathlib.Path):
    result = run_vendored("examples/{}".format(example.name))
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.name)
def test_no_example_emits_a_warning(example: pathlib.Path):
    result = run_vendored("examples/{}".format(example.name))
    assert "Warning" not in result.stderr, result.stderr
