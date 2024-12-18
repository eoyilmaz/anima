#!/usr/bin/env python
import os
import pathlib
import shutil
import subprocess
import sys


def build_linux(source_path, build_path, install_path, targets):
    """Build for Linux.

    Args:
        source_path (src): The source path.
        build_path (src): The build path.
        install_path (src): The install path.
        targets (List[str]): The list of targets.
    """
    source_path = pathlib.Path(source_path)
    build_path = pathlib.Path(build_path)
    install_path = pathlib.Path(install_path)

    print(f"source_path : {source_path}")
    print(f"build_path  : {build_path}")
    print(f"install_path: {install_path}")
    print(f"targets     : {targets}")

    maya_usd_version = os.environ["REZ_BUILD_PROJECT_VERSION"]
    (
        maya_usd_major_version,
        maya_usd_minor_version,
        maya_usd_patch_version,
    ) = maya_usd_version.split(".")

    print(f"maya_usd_version      : {maya_usd_version}")
    print(f"maya_usd_major_version: {maya_usd_major_version}")
    print(f"maya_usd_minor_version: {maya_usd_minor_version}")
    print(f"maya_usd_patch_version: {maya_usd_patch_version}")

    variant_index = int(os.environ["REZ_BUILD_VARIANT_INDEX"])
    variant_lut = [
        "maya-2020",
        "maya-2022",
    ]
    print(f"variant_index: {variant_index}")

    maya_version_name_lut = {
        "maya-2020": "Maya2020.4",
        "maya-2022": "Maya2022.3",
    }
    module_folder_lut = {
        "maya-2020": "maya2020",
        "maya-2022": "maya2022",
    }
    maya_version_name = maya_version_name_lut[variant_lut[variant_index]]
    print(f"maya_version_name: {maya_version_name}")

    module_folder_name = module_folder_lut[variant_lut[variant_index]]
    print(f"module_folder_name: f{module_folder_name}")

    os.chdir(build_path)
    installer_script_file_name = (
        f"MayaUSD_{maya_usd_version}_{maya_version_name}_Linux.run"
    )
    tar_ball_file_name = f"MayaUSD_{maya_usd_version}_{maya_version_name}_Linux.tar.gz"
    installer_script_file_full_path = build_path / installer_script_file_name
    tar_ball_file_full_path = build_path / tar_ball_file_name

    download_url = (
        f"https://github.com/Autodesk/maya-usd/releases/download/"
        f"v{maya_usd_version}/{installer_script_file_name}"
    )
    print(f"download_url: {download_url}")
    # don't download if the file already exists
    if not installer_script_file_full_path.exists():
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
        print(f"Installer exists: {installer_script_file_full_path}")
        print("Skipping download!")

    if not tar_ball_file_full_path.exists():
        print("Tarball doesn't exist!")
        print("Extracting!")
        # extract the content of the installer
        # the run file is a script that contains the tar.gz of the rpm file after a certain
        # offset
        # find the offset
        with open(installer_script_file_full_path, "rb") as f:
            data = f.readlines()

        search_byte = b"eval $finish; exit $res"
        offset = -1
        for i, line in enumerate(data):
            if search_byte in line:
                offset = i
                break
        if offset == -1:
            RuntimeError("Cannot find data offset!")

        installer_data = data[offset + 1 :]
        with open(tar_ball_file_full_path, "wb") as f:
            f.writelines(installer_data)
    else:
        print("Tarball exists, not extracting!")

    # extract tarball content
    process = subprocess.Popen(
        ["tar", "-xvzf", tar_ball_file_full_path], stdout=subprocess.PIPE
    )
    process.wait()

    # find the RPM file
    rpm_file_full_path = None
    for f in build_path.glob("*.rpm"):
        rpm_file_full_path = f
        break
    print(rpm_file_full_path)

    # extract the rpm file
    rpm2cpio_process = subprocess.Popen(
        ["rpm2cpio", str(rpm_file_full_path)], stdout=subprocess.PIPE
    )
    cpio_process = subprocess.Popen(["cpio", "-idmv"], stdin=rpm2cpio_process.stdout)
    rpm2cpio_process.wait()

    # now we should have the RPM file content extracted to ./usr/autodesk
    # find the mayausd folder and mayausd.mod file under
    # ./usr/autodesk/mayausd/maya2022/0.19.0_*-*/ folder
    content_folder = build_path / "usr" / "autodesk" / "mayausd" / module_folder_name

    mayausd_folder_path = None
    mayausd_mod_file_path = None
    for f in content_folder.glob(f"{maya_usd_version}_*-*"):
        for fd in f.glob("*"):
            if fd.name == "mayausd":
                mayausd_folder_path = fd
            elif fd.name == "mayausd.mod":
                mayausd_mod_file_path = fd

    print(f"mayausd_folder_path  : {mayausd_folder_path}")
    print(f"mayausd_mod_file_path: {mayausd_mod_file_path}")

    # update the mayausd.mod file and replace <PLUGIN_DIR> with install_path/maya_usd
    with open(mayausd_mod_file_path, "r") as f:
        data = f.readlines()

    for i, line in enumerate(data):
        if "<PLUGIN_DIR>" in line:
            data[i] = line.replace("<PLUGIN_DIR>", "maya_usd")

    with open(mayausd_mod_file_path, "w") as f:
        f.writelines(data)

    shutil.move(str(mayausd_folder_path), str(install_path.joinpath("maya_usd")))
    shutil.move(str(mayausd_mod_file_path), str(install_path.joinpath("mayausd.mod")))


def build_osx(source_path, build_path, install_path, targets):
    raise NotImplementedError("macOS build is not implemented yet!")


if __name__ == "__main__":
    if system.platform == "linux":
        build_linux(
            source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
            build_path=os.environ["REZ_BUILD_PATH"],
            install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
            targets=sys.argv[1:],
        )
    elif system.platform == "osx":
        build_osx(
            source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
            build_path=os.environ["REZ_BUILD_PATH"],
            install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
            targets=sys.argv[1:],
        )
