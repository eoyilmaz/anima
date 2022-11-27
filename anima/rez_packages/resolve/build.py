#!/usr/bin/env python
import os
import shutil
import sys
import pathlib


def build(source_path, build_path, install_path, targets):
    print(f"source_path : {source_path}")
    print(f"build_path  : {build_path}")
    print(f"install_path: {install_path}")
    print(f"targets     : {targets}")

    # copy the bin folder content to the install_path
    for dir in ["bin"]:
        shutil.rmtree(pathlib.Path(install_path) / dir, ignore_errors=True)
        os.makedirs(install_path, exist_ok=True)
        shutil.copytree(
            pathlib.Path(source_path) / ".." / dir,
            pathlib.Path(install_path) / dir,
        )


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
