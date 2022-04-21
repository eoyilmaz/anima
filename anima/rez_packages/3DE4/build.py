#!/usr/bin/env python
import os
import sys


def build(source_path, build_path, install_path, targets):
    print(f"source_path : {source_path}")
    print(f"build_path  : {build_path}")
    print(f"install_path: {install_path}")
    print(f"targets     : {targets}")


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:]
    )
