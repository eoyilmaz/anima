# -*- coding: utf-8 -*-

name = "agx"

version = "12.3.0"

author = ["Erkan Ozgur Yilmaz"]

uuid = "59d10c2d4a634336ae8675f11b6b1345"

description = "AgX Package"

build_command = "python3 {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    env.OCIO.append(
        "$HOME/Documents/development/"
        "AgX/"
        "config.ocio"
    )
