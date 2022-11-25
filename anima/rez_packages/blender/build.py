#!/usr/bin/env python
import os
import sys
import pathlib


def build(source_path, build_path, install_path, targets):
    source_path = pathlib.Path(source_path)
    build_path = pathlib.Path(build_path)
    install_path = pathlib.Path(install_path)
    print(f"source_path : {source_path}")
    print(f"build_path  : {build_path}")
    print(f"install_path: {install_path}")
    print(f"targets     : {targets}")

    major, minor, patch = os.environ["REZ_BUILD_PROJECT_VERSION"].split(".")
    print(f"major: {major}")
    print(f"minor: {minor}")
    print(f"patch: {patch}")

    # create custom start_blender command to the install_path
    start_blender_command_path = pathlib.Path(install_path) / "bin" / "blender"

    start_blender_command_content = ""
    if sys.platform.startswith("linux"):
        start_blender_command_content = f"""#!/usr/bin/sh
/opt/blender-{major}.{minor}.{patch}/blender --python-use-system-env "$@"
"""
    elif sys.platform.startswith("darwin"):
        start_blender_command_content = f"""#!/bin/zsh
/Applications/Blender-{major}.{minor}.{patch}.app/Contents/MacOS/blender --python-use-system-env "$@"
"""

    os.makedirs(start_blender_command_path.parent.absolute(), exist_ok=True)
    # create the file and write down the content
    with open(start_blender_command_path, "w+") as f:
        f.write(start_blender_command_content)
    # make it executable
    os.chmod(start_blender_command_path, 0o777)


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
