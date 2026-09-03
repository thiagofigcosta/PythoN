from __future__ import annotations

import pathlib

import pytest

from pythonn.errors import PythoNError
from pythonn.imports import collect, logical_code_lines, module_names, resolve
from pythonn.scanner import scan


def test_it_reads_a_plain_import():
    assert module_names("import math") == ("math",)


def test_it_reads_a_comma_separated_import():
    assert module_names("import math, sys") == ("math", "sys")


def test_it_strips_an_alias():
    assert module_names("import basic_external_file as ext") == (
        "basic_external_file",
    )


def test_it_reads_a_dotted_from_import():
    assert module_names("from a.b import c") == ("a.b",)


def test_it_reads_a_relative_from_import():
    assert module_names("from .x import y") == (".x",)


def test_a_bare_name_is_not_an_import():
    assert module_names("important = 1") == ()


def test_a_parenthesised_import_joins_into_one_logical_line():
    scans = scan("from a import (\n    b,\n    c,\n)")
    joined = logical_code_lines(scans)
    assert joined[0][1].startswith("from a import (")
    assert module_names(joined[0][1]) == ("a",)


def test_resolve_finds_a_module_file(tmp_path: pathlib.Path):
    (tmp_path / "helper.py").write_text("x = 1")
    assert resolve("helper", str(tmp_path)) == str(tmp_path / "helper.py")


def test_resolve_finds_a_package_init(tmp_path: pathlib.Path):
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "__init__.py").write_text("x = 1")
    assert resolve("pkg", str(tmp_path)) == str(package / "__init__.py")


def test_resolve_returns_none_for_an_installed_module(tmp_path: pathlib.Path):
    assert resolve("math", str(tmp_path)) is None


def test_resolve_refuses_to_walk_upward(tmp_path: pathlib.Path):
    inner = tmp_path / "inner"
    inner.mkdir()
    (tmp_path / "outer.py").write_text("x = 1")
    assert resolve("..outer", str(inner)) is None


def test_collect_returns_the_entry_first_then_its_imports(tmp_path: pathlib.Path):
    (tmp_path / "helper.py").write_text("y = 2")
    entry = tmp_path / "main.py"
    entry.write_text("import helper\nimport math")
    assert collect(str(entry)) == (str(entry), str(tmp_path / "helper.py"))


def test_collect_visits_each_file_once_even_in_a_cycle(tmp_path: pathlib.Path):
    (tmp_path / "a.py").write_text("import b")
    (tmp_path / "b.py").write_text("import a")
    entry = tmp_path / "a.py"
    assert collect(str(entry)) == (str(entry), str(tmp_path / "b.py"))


def test_a_file_that_is_not_utf8_is_reported_as_a_diagnostic(tmp_path: pathlib.Path):
    entry = tmp_path / "main.py"
    entry.write_bytes(b'x = "caf\xe9"\n')
    with pytest.raises(PythoNError) as caught:
        collect(str(entry))
    assert caught.value.path == str(entry)
    assert "UTF-8" in caught.value.message


def test_a_missing_file_is_reported_as_a_diagnostic(tmp_path: pathlib.Path):
    with pytest.raises(PythoNError):
        collect(str(tmp_path / "nope.py"))


def test_collect_ignores_a_module_named_only_inside_a_string(tmp_path: pathlib.Path):
    (tmp_path / "helper.py").write_text("y = 2")
    entry = tmp_path / "main.py"
    entry.write_text("text = 'import helper'")
    assert collect(str(entry)) == (str(entry),)
