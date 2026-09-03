from __future__ import annotations

import pathlib
import sys
import warnings

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_vendor import build  # noqa: E402

VENDORED = REPO_ROOT / "Pytho{N}.py"


def test_the_vendored_file_is_up_to_date():
    assert VENDORED.read_text() == build(REPO_ROOT / "src" / "pythonn"), (
        "Pytho{N}.py is stale - run: python3 scripts/build_vendor.py"
    )


def test_the_vendored_file_compiles_without_warnings():
    # The docstring names the language `Pytho{\}`, so the header must be a RAW string:
    # a plain one makes every run of the shipped file emit a SyntaxWarning, and a future
    # Python turns that into a hard SyntaxError.
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        compile(VENDORED.read_text(), str(VENDORED), "exec")


@pytest.mark.skipif(sys.version_info < (3, 10), reason="needs sys.stdlib_module_names")
def test_the_vendored_file_has_no_third_party_imports():
    text = VENDORED.read_text()
    for line in text.splitlines():
        if line.startswith("import ") or line.startswith("from "):
            module = line.split()[1].split(".")[0]
            assert module in sys.stdlib_module_names or module == "__future__", module
