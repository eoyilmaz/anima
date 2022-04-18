# -*- coding: utf-8 -*-

name = "blender"

version = "3.1.2"

author = [
    "Erkan Ozgur Yilmaz",
]

uuid = "edf2e1216f1744e286dbfc5becd985e5"

description = "Blender Package"

requires = [
    "aces",
    "python-3.10",
]

build_command = "python {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    env.PATH.prepend("{root}/bin")
