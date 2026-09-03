from __future__ import annotations

import sys

import pytest

from pythonn.errors import PythoNError
from pythonn.runner import build_command, run


def test_it_builds_an_argument_list_not_a_shell_string():
    command = build_command("3", "/tmp/a b.py", ("--flag", "value"))
    assert command == ["python3", "/tmp/a b.py", "--flag", "value"]


def test_an_empty_entry_builds_the_interactive_command():
    assert build_command("3", "", ()) == ["python3"]


def test_the_version_suffix_is_honoured():
    assert build_command("2", "x.py", ())[0] == "python2"


def test_it_returns_the_child_exit_code(tmp_path):
    script = tmp_path / "fail.py"
    script.write_text("import sys\nsys.exit(7)\n")
    assert run([sys.executable, str(script)]) == 7


def test_it_returns_zero_on_success(tmp_path):
    script = tmp_path / "ok.py"
    script.write_text("print('hi')\n")
    assert run([sys.executable, str(script)]) == 0


def test_show_cmd_prints_a_quoted_command(tmp_path, capsys):
    script = tmp_path / "ok.py"
    script.write_text("pass\n")
    run([sys.executable, str(script), "a b"], show_cmd=True)
    assert "'a b'" in capsys.readouterr().out


def test_a_missing_interpreter_is_reported_as_a_diagnostic_not_a_traceback():
    with pytest.raises(PythoNError) as caught:
        run(["pythoN-interpreter-that-does-not-exist"])
    assert caught.value.message == "interpreter not found"
    assert caught.value.path == "pythoN-interpreter-that-does-not-exist"
