from __future__ import annotations

import glob
import os
import pathlib
import shutil
import tempfile

from pythonn.cli import main, parse_args
from tests.conftest import run_new


def test_it_defaults_to_python_three():
    options, source, args = parse_args(["x.py"])
    assert (options.python_version, source, args) == ("3", "x.py", ())


def test_the_version_flag_is_read():
    options, _, _ = parse_args(["-v", "2", "x.py"])
    assert options.python_version == "2"


def test_arguments_after_the_source_are_passed_through_in_order():
    _, source, args = parse_args(["x.py", "--argument", "to", "file"])
    assert (source, args) == ("x.py", ("--argument", "to", "file"))


def test_the_first_py_argument_is_the_source():
    _, source, args = parse_args(["a.py", "b.py"])
    assert (source, args) == ("a.py", ("b.py",))


def test_no_source_means_the_interactive_shell():
    _, source, _ = parse_args([])
    assert source == ""


def test_the_flags_are_recognised():
    options, _, _ = parse_args(["--show-cmd", "--print-output", "--keep-temp", "x.py"])
    assert options.show_cmd and options.print_output and options.keep_temp


def test_a_program_flag_colliding_with_a_tool_flag_reaches_the_program():
    options, source, args = parse_args(["app.py", "-v"])
    assert (options.python_version, source, args) == ("3", "app.py", ("-v",))


def test_a_program_help_flag_reaches_the_program_untouched():
    options, source, args = parse_args(["app.py", "-h"])
    assert (source, args) == ("app.py", ("-h",))


def test_a_tool_flag_before_the_source_still_sets_the_interpreter():
    options, source, args = parse_args(["-v", "3", "app.py", "x"])
    assert (options.python_version, source, args) == ("3", "app.py", ("x",))


def test_a_tool_flag_before_the_source_is_honoured_with_empty_program_args():
    options, source, args = parse_args(["--show-cmd", "app.py"])
    assert (options.show_cmd, source, args) == (True, "app.py", ())


def test_a_program_flag_shaped_like_a_tool_flag_after_the_source_is_untouched():
    options, source, args = parse_args(["app.py", "--show-cmd"])
    assert (options.show_cmd, source, args) == (False, "app.py", ("--show-cmd",))


def test_a_literal_dash_dash_hands_everything_after_it_to_the_program():
    options, source, args = parse_args(["--show-cmd", "--", "--print-output", "app.py"])
    assert (options.show_cmd, source, args) == (
        True,
        "",
        ("--print-output", "app.py"),
    )


def test_it_runs_a_program_and_returns_its_output(tmp_path: pathlib.Path):
    source = tmp_path / "hello.py"
    source.write_text("if True {\n    print('hi')\n}\n")
    result = run_new(str(source))
    assert result.returncode == 0
    assert result.stdout == "hi\n"


def test_a_failing_program_propagates_its_exit_code(tmp_path: pathlib.Path):
    source = tmp_path / "boom.py"
    source.write_text("import sys\nif True {\n    sys.exit(7)\n}\n")
    assert run_new(str(source)).returncode == 7


def test_print_output_prints_the_transpiled_source(tmp_path: pathlib.Path):
    source = tmp_path / "hello.py"
    source.write_text("if True {\n    print('hi')\n}\n")
    result = run_new(str(source), tool_flags=("--print-output",))
    # The distinctive shape of a transpile: a `{`-braced header comes back `:`-terminated.
    # (The child program's own "hi" can land before or after it - the parent's print()
    # is block-buffered while piped, so ordering between the two processes isn't fixed.)
    assert "if True:\n    print('hi')" in result.stdout
    assert "hi" in result.stdout.splitlines()


def test_show_cmd_prints_the_command_it_is_about_to_run(tmp_path: pathlib.Path):
    source = tmp_path / "hello.py"
    source.write_text("print('hi')\n")
    result = run_new(str(source), tool_flags=("--show-cmd",))
    assert "python3" in result.stdout
    # The printed command names the TRANSPILED entry (mirrored into the build tree),
    # not the original source path.
    assert str(source) not in result.stdout
    assert source.name in result.stdout


def test_a_brace_error_is_reported_against_the_source(tmp_path: pathlib.Path):
    source = tmp_path / "bad.py"
    source.write_text("x = 1\n}\n")
    result = run_new(str(source))
    assert result.returncode == 2
    assert "bad.py:2:1: error: unmatched '}'" in result.stderr


def test_a_missing_interpreter_is_reported_not_traced(tmp_path: pathlib.Path, capsys):
    # run_new always places the source right after the entry point, so a `-v` passed
    # to it lands AFTER the source and is (correctly, per the argv split) a program
    # arg, not ours - call main() in-process to put the tool flag where it belongs.
    source = tmp_path / "hello.py"
    source.write_text("print('hi')\n")
    code = main(["-v", "987654-does-not-exist", str(source)])
    captured = capsys.readouterr()
    assert code == 2
    assert "interpreter not found" in captured.err
    assert "Traceback" not in captured.err


def test_a_local_import_is_transpiled_too(tmp_path: pathlib.Path):
    (tmp_path / "helper.py").write_text("def hi() {\n    print('from helper')\n}\n")
    source = tmp_path / "main.py"
    source.write_text("import helper\nhelper.hi()\n")
    result = run_new(str(source))
    assert result.stdout == "from helper\n"


def test_the_build_tree_is_removed(tmp_path: pathlib.Path):
    source = tmp_path / "hello.py"
    source.write_text("print('hi')\n")
    # Asserting against the legacy `.tmp_pythoN` name would pass even with cleanup
    # deleted, because mkdtemp never writes there. Watch the real temp dir instead.
    pattern = os.path.join(tempfile.gettempdir(), "pythoN-*")
    before = set(glob.glob(pattern))
    run_new(str(source))
    assert set(glob.glob(pattern)) == before


def test_two_runs_do_not_share_a_build_tree(tmp_path: pathlib.Path):
    source = tmp_path / "where.py"
    source.write_text("print(__file__)\n")
    first = run_new(str(source), tool_flags=("--keep-temp",)).stdout
    second = run_new(str(source), tool_flags=("--keep-temp",)).stdout
    assert first != second
    for kept in (first, second):
        shutil.rmtree(pathlib.Path(kept.strip()).parent, ignore_errors=True)
