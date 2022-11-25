# -*- coding: utf-8 -*-

name = "blender"

version = "3.0.1"

author = [
    "Erkan Ozgur Yilmaz",
]

uuid = "edf2e1216f1744e286dbfc5becd985e5"

description = "Blender Package"

requires = [
    "aces",
]

variants = [
    [".python-3.9"],
]

build_command = "python3 {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    env.PATH.prepend("{root}/bin")

    major = env.REZ_BLENDER_MAJOR_VERSION,
    minor = env.REZ_BLENDER_MINOR_VERSION,
    patch = env.REZ_BLENDER_PATCH_VERSION,
    if system.platform == "osx":
        # env.PATH.append(
        #     f"/Applications/Blender-{major}.{minor}.{patch}.app/Contents/MacOS"
        # )
        env.PYTHONHOME.set(
            f"/Applications/Blender-{major}.{minor}.{patch}.app/Contents/"
            f"Resources/{major}.{minor}/python"
        )
