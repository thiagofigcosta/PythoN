from __future__ import annotations

import shlex
import subprocess

from .errors import PythoNError


def build_command(python_version: str, entry: str, args: tuple[str, ...]) -> list[str]:
    command = ["python{}".format(python_version)]
    if entry:
        command.append(entry)
    command.extend(args)
    return command


def run(command: list[str], show_cmd: bool = False) -> int:
    if show_cmd:
        print(" ".join(shlex.quote(part) for part in command) + "\n")
    try:
        return subprocess.run(command).returncode
    except FileNotFoundError:
        raise PythoNError("interpreter not found", path=command[0]) from None
