#!/usr/bin/env python
import argparse
import pathlib
import os
import shutil
import subprocess
import sys
import zipfile


def build(owner="", repo="", tag_prefix=""):
    """Build the given project.

    Args:
        owner (str): The owner of the repository.
        repo (str): The repo name.
        tag_prefix (str): Sometimes projects give tags with a "v" in front of
            the version number (i.e. v0.2.213), set ``tag_prefix="v"`` in that
            case.
    """
    source_path = pathlib.Path(os.environ["REZ_BUILD_SOURCE_PATH"])
    build_path = pathlib.Path(os.environ["REZ_BUILD_PATH"])
    install_path = pathlib.Path(os.environ["REZ_BUILD_INSTALL_PATH"])

    print(f"source_path : {source_path}")
    print(f"build_path  : {build_path}")
    print(f"install_path: {install_path}")

    project_name = os.environ["REZ_BUILD_PROJECT_NAME"]
    major, minor, patch = os.environ["REZ_BUILD_PROJECT_VERSION"].split(".")
    zip_file_name = f"{tag_prefix}{major}.{minor}.{patch}.zip"
    variant_subpath = os.environ["REZ_BUILD_VARIANT_SUBPATH"]
    print(f"variant_subpath: {variant_subpath}")
    if variant_subpath == "":
        # no variant, store directly in to the build_path
        zip_full_path = build_path / zip_file_name
    else:
        # there are variants store in parent path
        zip_full_path = build_path.parent / zip_file_name

    download_url = (
        f"https://github.com/{owner}/{repo}/archive/refs/tags/{zip_file_name}"
    )
    print(f"download_url: {download_url}")
    # don't download if the file already exists
    os.chdir(build_path)

    if not zip_full_path.exists():
        print("Downloading installer!")
        curl_command = ["curl", "-OL", download_url, "--output-dir", str(zip_full_path.parent)]
        print("curl_command: {}".format(" ".join(curl_command)))
        process = subprocess.Popen(
            curl_command, stdout=subprocess.PIPE
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
    lib_folder_name = f"{project_name}-{major}.{minor}.{patch}"
    lib_build_path = build_path / lib_folder_name
    lib_install_path = install_path / lib_folder_name

    # don't extract again if unzipped folder exist
    if not lib_build_path.exists():
        print("ZIP file content already extracted!")
        print("removing content!")
        shutil.rmtree(lib_build_path, ignore_errors=True)

    # extract ZIP file content
    print(f"extracting ZIP file content to {lib_build_path}")
    with zipfile.ZipFile(zip_full_path) as z:
        z.extractall()

    # remove previous installation if exist
    if lib_install_path.exists():
        print(f"removing previous install at {lib_install_path}")
        shutil.rmtree(lib_install_path, ignore_errors=True)

    # finally move the extracted content in to place
    print(f"moving build folder in to install path: {lib_install_path}")
    shutil.move(f"./{lib_folder_name}", install_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Build GitHub Projects.'
    )
    parser.add_argument(
        '-o', '--owner', required=True,
        help="The repo owner (eoyilmaz)"
    )
    parser.add_argument(
        '-r', '--repo', required=True,
        help="The repo name (anima)"
    )
    parser.add_argument(
        '-t', '--tag-prefix', required=False, default=""
    )
    args = parser.parse_args()
    build(
        owner=args.owner,
        repo=args.repo,
        tag_prefix=args.tag_prefix
    )
