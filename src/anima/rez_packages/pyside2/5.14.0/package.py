# -*- coding: utf-8 -*-

name = "pyside2"

version = "5.14.0"

author = ["Erkan Ozgur Yilmaz"]

uuid = "6e88b9f8666a4524a388c8e0b6640f1a"

description = "PySide2 Package"

requires = [
    "python",
]

variants = [
    [".python-2.7"],
]

build_command = "python3 {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    # Set QT_API env var for anima
    env.QT_API.set("pyside2")
    py_libs_path = "$HOME/Documents/development/pylibs"
    env.PYTHONPATH.append(
        "{}/py{}.{}/lib/python/site-packages__extras__".format(
            py_libs_path,
            env.REZ_PYTHON_MAJOR_VERSION,
            env.REZ_PYTHON_MINOR_VERSION,
        )
    )
