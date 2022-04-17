# -*- coding: utf-8 -*-

name = "fusion"

version = "17.3.1"

author = [
    "Erkan Ozgur Yilmaz"
]

uuid = "59a8d4cd31414e888b4f859ef14b0fb7"

description = "Fusion package"

requires = [
    "python"
]

variants = [
    ["python-2"],
    ["python-3"]
]

build_command = "python {root}/../build.py {install}"


def commands():
    env.PYTHONPATH.append("{root}/python")
    env.PATH.append("{root}/bin")
    env.PATH.append(
        "/opt/BlackmagicDesign/Fusion{}/".format(env.REZ_FUSION_MAJOR_VERSION)
    )
