#!/usr/bin/env python
import os
import pathlib
import sys
import subprocess


def build(source_path, build_path, install_path, targets):
    source_path = pathlib.Path(source_path)
    build_path = pathlib.Path(build_path)
    install_path = pathlib.Path(install_path)

    print(f"source_path : {source_path}")
    print(f"build_path  : {build_path}")
    print(f"install_path: {install_path}")
    print(f"targets     : {targets}")

    major, minor, patch = os.environ["REZ_BUILD_PROJECT_VERSION"].split(".")

    # crate a symlink to the original python interpreter
    os.chdir(install_path)
    os.makedirs(install_path / "bin", exist_ok=True)
    os.chdir(install_path / "bin")
    # get system python path
    proc = subprocess.Popen(["which", f"python{major}.{minor}"], stdout=subprocess.PIPE)
    python_path = proc.stdout.readline().strip().decode("utf-8")
    print(f"python_path: {python_path}")
    proc = subprocess.Popen(["ln", "-sf", python_path, "python"])


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
