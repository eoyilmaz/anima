# -*- coding: utf-8 -*-

name = "pymel"

version = "1.5.0"

author = ["Erkan Ozgur Yilmaz"]

uuid = "fdc7e1bc441d493db7e31d28530df675"

description = "PyMEL"

build_command = "python3 {root}/../../github_project_builder.py --owner=lumapictures --repo=pymel"


def commands():
    env.PYTHONPATH.append(
        "$REZ_PYMEL_ROOT/pymel-$REZ_PYMEL_MAJOR_VERSION.$REZ_PYMEL_MINOR_VERSION.$REZ_PYMEL_PATCH_VERSION"
    )
