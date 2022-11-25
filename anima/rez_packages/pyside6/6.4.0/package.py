# -*- coding: utf-8 -*-

name = "pyside6"

version = "6.4.0"

author = [
    "Erkan Ozgur Yilmaz",
]

uuid = "f61b1afcf035408db2f9921226ee0891"

description = "PySide6 Package"

requires = [
    "python",
]

variants = [
    [".python-3.8"],
    [".python-3.9"],
    [".python-3.10"],
    [".python-3.11"],
]

build_command = "python3 {root}/../build.py {install}"


def commands():
    import os
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")
    py_libs_path = os.path.expanduser("$HOME/Documents/development/pylibs")
    env.PYTHONPATH.append("{}/py{}.{}/__extras__".format(
            py_libs_path,
            env.REZ_PYTHON_MAJOR_VERSION,
            env.REZ_PYTHON_MINOR_VERSION,
        )
    )
