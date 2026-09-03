from __future__ import annotations

import pathlib

import pytest

from pythonn.transpiler import transpile
from tests.conftest import run_new

FIXTURES = sorted(p for p in (pathlib.Path(__file__).parent / "fixtures").iterdir() if p.is_dir())


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.name)
def test_the_transpiled_source_matches(fixture: pathlib.Path):
    source = (fixture / "input.py").read_text()
    expected = (fixture / "expected.py").read_text()
    assert transpile(source, path=str(fixture / "input.py")).code == expected


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.name)
def test_the_executed_output_matches(fixture: pathlib.Path):
    result = run_new(str(fixture / "input.py"))
    assert result.returncode == 0, result.stderr
    assert result.stdout == (fixture / "expected_stdout.txt").read_text()
