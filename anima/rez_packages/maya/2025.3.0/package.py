# -*- coding: utf-8 -*-

name = "maya"

version = "2025.3.0"

author = ["Erkan Ozgur Yilmaz"]

uuid = "926ca70831554917977883498363a94e"

description = "Maya package"

requires = [
    ".python-3.11",
    "pymel-1.5.0",
    "ocio-2.3",
]

build_command = "python3 {root}/../build.py {install}"

with scope("config") as c:
    # c.release_packages_path = "/shots/fx/home/software/packages"
    # c.plugins.release_hook.emailer.recipients = []
    c.plugins.release_vcs.git.allow_no_upstream = True


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    major = env.REZ_MAYA_MAJOR_VERSION
    if system.platform == "linux":
        env.PATH.append(f"/usr/autodesk/maya{major}/bin")
    elif system.platform == "osx":
        env.PATH.append(f"/Applications/Autodesk/maya{major}/Maya.app/Contents/bin")
        env.PATH.append(f"/Applications/Autodesk/maya{major}/Maya.app/Contents/MacOS")

    env.MAYA_DISABLE_CIP = 1
    env.MAYA_DISABLE_CER = 1
