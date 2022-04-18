# -*- coding: utf-8 -*-

name = "aces"

version = "1.0.3"

author = [
    "Erkan Ozgur Yilmaz",
]

uuid = "5d2cff05093e444c899608b842df8ca5"

description = "ACES Package"

build_command = "python {root}/../build.py {install}"


def commands():
    env.PYTHONPATH.append("{root}/python")
    env.PATH.append("{root}/bin")
    env.OCIO.append(
        "$HOME/Documents/development/OpenColorIO-Configs/aces_{}.{}.{}/config.ocio".format(
            env.REZ_ACES_MAJOR_VERSION,
            env.REZ_ACES_MINOR_VERSION,
            env.REZ_ACES_PATCH_VERSION,
        )
    )
