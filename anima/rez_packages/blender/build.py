#!/usr/bin/env python
import os
import sys
import pathlib


def build(source_path, build_path, install_path, targets):
    print(f"source_path : {source_path}")
    print(f"build_path  : {build_path}")
    print(f"install_path: {install_path}")
    print(f"targets     : {targets}")

    version_str = os.path.split(source_path)[-1]
    major_version, minor_version, patch_version = version_str.split(".")
    print(f"major_version: {major_version}")
    print(f"minor_version: {minor_version}")
    print(f"patch_version: {patch_version}")

    # create custom start_blender command to the install path
    start_blender_command_path = pathlib.Path(install_path) / "bin" / "blender"
    start_blender_command_content = """#!/usr/bin/sh
$HOME/.local/bin/blender-{}.{}.{}/blender --python-use-system-env "$@"
""".format(
        major_version, minor_version, patch_version
    )

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
