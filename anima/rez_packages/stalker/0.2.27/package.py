# -*- coding: utf-8 -*-

name = "stalker"

version = "0.2.27"

author = [
    "Erkan Ozgur Yilmaz"
]

uuid = "4f67b7696af4423e8b340d2f965c092f"

description = "Stalker package"

requires = [
    "python"
]

variants = [
    ["python-2.7"],
    ["python-3.6"],
    ["python-3.7"],
    ["python-3.8"],
    ["python-3.9"],
    ["python-3.10"],
]

build_command = "python {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")
    env.STALKER_PATH = "/mnt/NAS/Users/eoyilmaz/Stalker_Projects"
