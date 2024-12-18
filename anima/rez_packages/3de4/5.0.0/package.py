# -*- coding: utf-8 -*-

name = "3de4"

version = "5.0.0"

author = ["Erkan Ozgur Yilmaz"]

uuid = "fc2910d27b3247ca935e7dde7f7b1835"

description = "3DE4 Package"

requires = [
    ".python-2.7",
]

build_command = "python3 {root}/../build.py {install}"


def commands():
    # env.PATH.append("{root}/bin")
    major = env.REZ_3DE4_MAJOR_VERSION
    minor = env.REZ_3DE4_MINOR_VERSION
    if system.platform == "linux":
        env.TDE4_ROOT = f"/opt/3DE4_r{major}{minor}"
        env.QT_API = "pyside2"
    elif system.platform == "osx":
        env.TDE4_ROOT = f"/Applications/3DE4_r{major}{minor}/Contents/MacOS/3DE4"
        env.QT_API = "pyside6"
    elif system.platform == "windows":
        env.TDE4_ROOT = f"C:/Program Files/3DE4_r{major}{minor}"
        env.QT_API = "pyside2"
    env.PATH.append("${TDE4_ROOT}/bin")
    env.PYTHONPATH.append("{root}/lib/python")
    env.PYTHON_CUSTOM_SCRIPTS_3DE4.append("{root}/lib/python")
