from __future__ import annotations

import os
import pathlib

import pytest

from pythonn.paths import common_root, mirror_path


def test_a_single_file_roots_at_its_own_directory(tmp_path: pathlib.Path):
    entry = tmp_path / "main.py"
    assert common_root((str(entry),)) == str(tmp_path)


def test_two_files_root_at_their_shared_parent(tmp_path: pathlib.Path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    paths = (str(tmp_path / "a" / "x.py"), str(tmp_path / "b" / "y.py"))
    assert common_root(paths) == str(tmp_path)


def test_mirror_preserves_the_relative_layout(tmp_path: pathlib.Path):
    root = str(tmp_path)
    source = str(tmp_path / "examples" / "basic.py")
    assert mirror_path(source, root, "/tmp/build") == os.path.join(
        "/tmp/build", "examples", "basic.py"
    )


def test_mirror_handles_an_absolute_source(tmp_path: pathlib.Path):
    root = str(tmp_path)
    source = str(tmp_path / "main.py")
    assert mirror_path(source, root, "/tmp/build") == os.path.join(
        "/tmp/build", "main.py"
    )


def test_mirror_refuses_a_path_outside_the_root(tmp_path: pathlib.Path):
    outside = tmp_path / "elsewhere" / "main.py"
    with pytest.raises(ValueError):
        mirror_path(str(outside), str(tmp_path / "root"), "/tmp/build")


def test_mirror_normalises_a_dot_dot_component(tmp_path: pathlib.Path):
    inner = tmp_path / "inner"
    inner.mkdir()
    source = str(inner / ".." / "main.py")
    assert mirror_path(source, str(tmp_path), "/tmp/build") == os.path.join(
        "/tmp/build", "main.py"
    )
