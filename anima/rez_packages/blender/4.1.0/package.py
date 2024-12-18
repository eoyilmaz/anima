# -*- coding: utf-8 -*-

name = "blender"

version = "4.1.0"

author = ["Erkan Ozgur Yilmaz"]

uuid = "edf2e1216f1744e286dbfc5becd985e5"

description = "Blender Package"

requires = [
    "ocio-2",
    "aces",
    ".python-3.11",
]

build_command = "python3 {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    env.PATH.prepend("{root}/bin")
