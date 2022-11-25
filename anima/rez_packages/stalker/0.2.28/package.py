# -*- coding: utf-8 -*-

name = "stalker"

version = "0.2.28"

author = [
    "Erkan Ozgur Yilmaz"
]

uuid = "4f67b7696af4423e8b340d2f965c092f"

description = "Stalker package"

requires = []

variants = [
    [".python-2.7"],
    [".python-3.6"],
    [".python-3.7"],
    [".python-3.8"],
    [".python-3.9"],
    [".python-3.10"],
    [".python-3.11"],
]

build_command = "python3 {root}/../../github_project_builder.py --owner=eoyilmaz --repo=stalker"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")
    env.STALKER_PATH = "$HOME/Stalker_Config"
    env.PYTHONPATH.append(
        "$REZ_STALKER_ROOT/stalker-$REZ_STALKER_MAJOR_VERSION.$REZ_STALKER_MINOR_VERSION.$REZ_STALKER_PATCH_VERSION"
    )
