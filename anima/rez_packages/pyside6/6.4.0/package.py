# -*- coding: utf-8 -*-

name = "pyside6"

version = "6.4.0"

author = ["Erkan Ozgur Yilmaz"]

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
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    # Set QT_LIB env var for anima
    env.QT_LIB.set("PySide6")
    py_libs_path = "$HOME/Documents/development/pylibs"
    env.PYTHONPATH.append(
        "{}/py{}.{}/lib/python/site_packages__extras__".format(
            py_libs_path,
            env.REZ_PYTHON_MAJOR_VERSION,
            env.REZ_PYTHON_MINOR_VERSION,
        )
    )
