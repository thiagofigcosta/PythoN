from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
VENDORED_SCRIPT = REPO_ROOT / "Pytho{N}.py"


@pytest.fixture(scope="session")
def repo_root() -> pathlib.Path:
    return REPO_ROOT


def run_vendored(source_path: str, *args: str) -> subprocess.CompletedProcess:
    """Run the checked-in, generated Pytho{N}.py - there is no legacy code left
    after Task 12; this is the characterization baseline for the vendored build."""
    return subprocess.run(
        [sys.executable, str(VENDORED_SCRIPT), source_path, *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def run_new(
    source_path: str, *args: str, tool_flags: tuple = ()
) -> subprocess.CompletedProcess:
    """Run the package entry point, independent of the vendored root file.

    `tool_flags` are inserted BEFORE the source path, landing on Pytho{N}'s own
    side of the argv split (see cli.parse_args); `*args` land after the source,
    where they belong to the target program instead.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "pythonn", *tool_flags, source_path, *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
    )


_VERSION_LINE = re.compile(r"^Running over Python \S+$", re.MULTILINE)


def normalize(output: str) -> str:
    """examples/basic.py prints the running interpreter's version.

    Comparing it verbatim would pin the whole suite to one CPython build, so
    that single line is masked on both sides; every other line stays exact.
    """
    return _VERSION_LINE.sub("Running over Python <version>", output)
