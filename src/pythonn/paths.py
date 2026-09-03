from __future__ import annotations

import os


def common_root(paths: tuple[str, ...]) -> str:
    directories = [os.path.dirname(os.path.abspath(path)) for path in paths]
    if not directories:
        return os.getcwd()
    if len(directories) == 1:
        return directories[0]
    return os.path.commonpath(directories)


def mirror_path(path: str, root: str, temp_root: str) -> str:
    relative = os.path.relpath(os.path.abspath(path), root)
    # relpath answers with a `..` prefix when root does not contain path, and the caller
    # writes a file to whatever comes back - so an unguarded join escapes the build tree.
    if relative == os.pardir or relative.startswith(os.pardir + os.sep):
        raise ValueError("{} is not inside {}".format(path, root))
    return os.path.join(temp_root, relative)
