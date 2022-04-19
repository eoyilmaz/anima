# -*- coding: utf-8 -*-

name = "pyside2"

version = "5.15.2"

author = [
    "Erkan Ozgur Yilmaz",
]

uuid = "6e88b9f8666a4524a388c8e0b6640f1a"

description = "PySide2 Package"

requires = [
    "python",
]

variants = [
    ["python-3.7"],
    ["python-3.9"],
    ["python-3.10"],
]

build_command = "python {root}/../build.py {install}"


def commands():
    import os
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")
    anima_lib_path = os.path.expanduser("$HOME/Documents/development/anima")
    env.PYTHONPATH.append("{}/extra_libraries/py{}.{}/__extras__".format(
            anima_lib_path,
            env.REZ_PYTHON_MAJOR_VERSION,
            env.REZ_PYTHON_MINOR_VERSION,
        )
    )
