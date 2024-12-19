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
    install_path_bin = install_path / "bin"
    os.makedirs(install_path_bin, exist_ok=True)
    os.chdir(install_path_bin)
    print(f"install_path_bin: {install_path_bin}")
    # get system python path
    proc = subprocess.Popen(["which", f"python{major}.{minor}"], stdout=subprocess.PIPE)
    python_path = proc.stdout.readline().strip().decode("utf-8")
    print(f"python_path: {python_path}")
    proc = subprocess.Popen(["ln", "-sf", python_path, "python"])
    proc = subprocess.Popen(["ln", "-sf", python_path, f"python{major}"])
    proc = subprocess.Popen(["ln", "-sf", python_path, f"python{major}.{minor}"])


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
