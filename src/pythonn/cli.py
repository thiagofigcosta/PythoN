from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile

from .errors import PythoNError
from .imports import collect, read_source
from .paths import common_root, mirror_path
from .runner import build_command, run
from .transpiler import transpile


def _split_at_program(argv: list[str]) -> int | None:
    """Index of the first token that hands argv over to the target program:
    a literal '--', or the first '.py' source file - whichever comes first.
    None means the whole argv is still ours (interactive-shell case)."""
    for index, item in enumerate(argv):
        if item == "--" or item.endswith(".py"):
            return index
    return None


def parse_args(argv: list[str]) -> tuple[argparse.Namespace, str, tuple[str, ...]]:
    parser = argparse.ArgumentParser(
        prog="Pytho{N}.py",
        description="Run Python written with curly brackets instead of indentation.",
    )
    parser.add_argument("-v", "--version", dest="python_version", default="3")
    parser.add_argument("--show-cmd", action="store_true")
    parser.add_argument("--print-output", action="store_true")
    parser.add_argument("--keep-temp", action="store_true")

    split = _split_at_program(argv)
    if split is None:
        # No '.py' and no '--': the whole line might still be ours (e.g. a bare
        # `-v 2`), so let argparse read everything, exactly as before.
        options, rest = parser.parse_known_args(argv)
        source = ""
        program_args = []
        for item in rest:
            if not source and item.endswith(".py"):
                source = item
                continue
            program_args.append(item)
        return options, source, tuple(program_args)

    # Only OUR flags precede the split point - a program flag that collides with one
    # of ours (e.g. `app.py -v`) must never reach argparse, or it gets consumed.
    options, _ = parser.parse_known_args(argv[:split])
    if argv[split] == "--":
        return options, "", tuple(argv[split + 1:])
    return options, argv[split], tuple(argv[split + 1:])


def compile_tree(source_path: str, temp_root: str, print_output: bool = False) -> str:
    entry_path = os.path.abspath(source_path)
    files = collect(source_path)
    root = common_root(files)

    for path in files:
        content = read_source(path)
        result = transpile(content, path=path)
        target = mirror_path(path, root, temp_root)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(result.code)
        if print_output:
            print(result.code)

    # Derived from the entry's own path, not from collect()'s iteration order -
    # which file gets executed no longer rides on an incidental "collect() always
    # returns the entry first" guarantee.
    return mirror_path(entry_path, root, temp_root)


def main(argv: list[str]) -> int:
    options, source, program_args = parse_args(argv)

    if not source:
        command = build_command(options.python_version, "", program_args)
        try:
            return run(command, options.show_cmd)
        except PythoNError as error:
            sys.stderr.write(error.render() + "\n")
            return 2

    temp_root = tempfile.mkdtemp(prefix="pythoN-")
    try:
        try:
            entry = compile_tree(source, temp_root, options.print_output)
            command = build_command(options.python_version, entry, program_args)
            return run(command, options.show_cmd)
        except PythoNError as error:
            sys.stderr.write(error.render() + "\n")
            return 2
    finally:
        # One finally covering every exit path. Cleaning up only after PythoNError left
        # the build tree behind for any other failure in the pipeline.
        if options.keep_temp:
            sys.stderr.write("kept build tree: {}\n".format(temp_root))
        else:
            shutil.rmtree(temp_root, ignore_errors=True)
