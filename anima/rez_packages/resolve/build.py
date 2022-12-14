#!/usr/bin/env python
import os
import re
import shutil
import sys
import pathlib


shebang_regex = re.compile("(#!\{shebang)(\.)([\w]+)(})")


def build(source_path, build_path, install_path, targets):
    print(f"source_path : {source_path}")
    print(f"build_path  : {build_path}")
    print(f"install_path: {install_path}")
    print(f"targets     : {targets}")

    source_path = pathlib.Path(source_path)
    install_path = pathlib.Path(install_path)

    # copy the bin folder content to the install_path
    for dir in ["bin"]:
        shutil.rmtree(install_path / dir, ignore_errors=True)
        os.makedirs(install_path, exist_ok=True)
        shutil.copytree(
            source_path / ".." / dir,
            install_path / dir,
        )

    # Fix shebangs
    for file_path in (install_path / dir).glob("*"):
        fix_shebang(file_path)


def fix_shebang(file_path):
    """Fix the shebang of the given file according to the current os.

    Args:
        file_path (Union[str, Path]: Path of the file to be fixed.
    """
    shebangs = {
        "win32": None,
        "linux": {
            "sh": "/usr/bin/sh"
        },
        "darwin": {
            "sh": "/bin/sh"
        },
    }
    if sys.platform == "win32":
        return

    with open(file_path, "r") as f:
        data = f.readlines()

    # fix the shebang at the first line
    match = shebang_regex.match(data[0])
    if not match:
        return

    exec = match.groups()[2]
    exec_path = shebangs[sys.platform].get(exec)
    if not exec_path:
        return

    data[0] = "#!{}".format(exec_path)

    with open(file_path, "w") as f:
        f.writelines(data)


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
