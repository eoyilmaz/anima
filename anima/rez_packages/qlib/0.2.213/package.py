# -*- coding: utf-8 -*-

name = "qlib"

version = "0.2.213"

author = [
    "qLab",
]

uuid = "742b691df8324d9a90b072da4cc8d8f0"

description = "qLib Package"

build_command = "python3 {root}/../build.py {install}"


def commands():
    env.QLIB = "$REZ_QLIB_ROOT/qLib-$REZ_QLIB_MAJOR_VERSION.$REZ_QLIB_MINOR_VERSION.$REZ_QLIB_PATCH_VERSION"
    env.QOTL = "$QLIB/otls"
    env.HOUDINI_OTLSCAN_PATH.prepend(
        "$QOTL/base:$QOTL/future:$QOTL/experimental"
    )
    env.HOUDINI_PATH.prepend("$QLIB")
