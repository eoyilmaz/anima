#!/usr/bin/env python
import os
import shutil
import subprocess
import sys
import pathlib
import zipfile


def build(source_path, build_path, install_path, targets):
    source_path = pathlib.Path(source_path)
    build_path = pathlib.Path(build_path)
    install_path = pathlib.Path(install_path)

    print(f"source_path : {source_path}")
    print(f"build_path  : {build_path}")
    print(f"install_path: {install_path}")
    print(f"targets     : {targets}")

    major, minor, patch = os.environ["REZ_BUILD_PROJECT_VERSION"].split(".")
    zip_file_name = f"v{major}.{minor}.{patch}.zip"
    zip_full_path = build_path / zip_file_name
    download_url = (
        f"https://github.com/qLab/qLib/archive/refs/tags/{zip_file_name}"
    )
    print(f"download_url: {download_url}")
    # don't download if the file already exists
    os.chdir(build_path)

    if not zip_full_path.exists():
        print("Downloading installer!")
        process = subprocess.Popen(
            ["curl", "-OL", download_url], stdout=subprocess.PIPE
        )
        stdout_buffer = []
        while True:
            stdout = process.stdout.readline()
            if not isinstance(stdout, str):
                stdout = stdout.decode("utf-8", "replace")

            if stdout == "" and process.poll() is not None:
                break

            if stdout != "":
                stdout_buffer.append(stdout)
                print(stdout)
    else:
        print(f"ZIP file exists: {zip_full_path}")
        print("Skipping download!")

    # copy qlib folder to installation path
    qlib_folder_name = f"qLib-{major}.{minor}.{patch}"
    qlib_build_path = build_path / qlib_folder_name
    qlib_install_path = install_path / qlib_folder_name

    # don't extract again if unzipped folder exist
    if not qlib_build_path.exists():
        print("ZIP file content already extracted!")
        print("removing content!")
        shutil.rmtree(qlib_build_path, ignore_errors=True)

    # extract ZIP file content
    print(f"extracting ZIP file content to {qlib_build_path}")
    with zipfile.ZipFile(zip_full_path) as z:
        z.extractall()

    # remove previous installation if exist
    if qlib_install_path.exists():
        print(f"removing previous install at {qlib_install_path}")
        shutil.rmtree(qlib_install_path, ignore_errors=True)

    # finally move the extracted content in to place
    print(f"moving build folder in to install path: {qlib_install_path}")
    shutil.move(f"./{qlib_folder_name}", install_path)


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:]
    )
