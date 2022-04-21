# -*- coding: utf-8 -*-

name = "3DE4"

version = "6.b3.0"

author = [
    "Erkan Ozgur Yilmaz",
]

uuid = "fc2910d27b3247ca935e7dde7f7b1835"

description = "3DEqualizer4 Package"

requires = [
    "python-2.7",
]

build_command = "python {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")
    env.TDE4_ROOT = "/opt/3DE4_r{}{}".format(
        env.REZ_3DE4_MAJOR_VERSION,
        env.REZ_3DE4_MINOR_VERSION,
    )
    env.PATH.append("/opt/3DE4_r{}{}/bin".format(
            env.REZ_3DE4_MAJOR_VERSION,
            env.REZ_3DE4_MINOR_VERSION,
        )
    )
