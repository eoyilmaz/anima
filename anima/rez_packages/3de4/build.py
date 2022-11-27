#!/usr/bin/env python
import os
import shutil
import sys


def build(source_path, build_path, install_path, targets):
    print(f"source_path : {source_path}")
    print(f"build_path  : {build_path}")
    print(f"install_path: {install_path}")
    print(f"targets     : {targets}")
    # copy the lib folder
    shutil.copytree(
        os.path.join(source_path, "..", "lib"),
        os.path.join(install_path, "lib"),
        dirs_exist_ok=True,
    )


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
