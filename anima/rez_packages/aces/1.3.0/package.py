# -*- coding: utf-8 -*-

name = "aces"

version = "1.3.0"

author = ["Erkan Ozgur Yilmaz"]

uuid = "5d2cff05093e444c899608b842df8ca5"

description = "ACES Package"

build_command = "python3 {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    env.OCIO.append(
        "$HOME/Documents/development/"
        "OpenColorIO-Config-ACES-build/"
        "cg-config-v2.2.0_"
        f"aces-v{env.REZ_ACES_MAJOR_VERSION}.{env.REZ_ACES_MINOR_VERSION}_"
        f"ocio-v{env.REZ_OCIO_MAJOR_VERSION}.{env.REZ_OCIO_MINOR_VERSION}"
        ".ocio"
    )
