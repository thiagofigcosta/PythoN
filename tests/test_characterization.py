from __future__ import annotations

import pathlib

from tests.conftest import normalize, run_vendored

GOLDEN = pathlib.Path(__file__).parent / "golden" / "examples_basic.stdout.txt"


def test_examples_basic_output_is_unchanged():
    result = run_vendored("examples/basic.py")
    assert result.returncode == 0
    assert normalize(result.stdout) == normalize(GOLDEN.read_text())


def test_the_new_pipeline_matches_the_captured_baseline():
    from tests.conftest import run_new

    result = run_new("examples/basic.py")
    assert result.returncode == 0, result.stderr
    assert normalize(result.stdout) == normalize(GOLDEN.read_text())
