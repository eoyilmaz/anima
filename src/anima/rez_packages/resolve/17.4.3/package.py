# -*- coding: utf-8 -*-

name = "resolve"

version = "17.4.3"

author = ["Erkan Ozgur Yilmaz"]

uuid = "86791641abc04a189b2177f4eff55327"

description = "DaVinci Resolve package"

requires = [
    "anima",
]

variants = [
    [".python-3"],
]

build_command = "python3 {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/../python")
    env.PATH.append("{root}/bin")

    # Set Qt API
    env.QT_API = "pyside2"

    if system.platform == "linux":
        env.PATH.append("/opt/resolve/")
        env.RESOLVE_SCRIPT_API = "/opt/resolve/Developer/Scripting/"
        env.RESOLVE_SCRIPT_LIB = "/opt/resolve/libs/Fusion/fusionscript.so"
        env.PYTHONPATH.append("$RESOLVE_SCRIPT_API/Modules/")
    elif system.platform == "osx":
        env.PATH.append("/Applications/DaVinci Resolve/DaVinci Resolve.app/")
        env.RESOLVE_SCRIPT_API = (
            "/Applications/DaVinci Resolve/DaVinci Resolve.app/Developer/Scripting/"
        )
        env.RESOLVE_SCRIPT_LIB = (
            "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/"
            "Fusion/fusionscript.so"
        )
        env.PYTHONPATH.append("$RESOLVE_SCRIPT_API/Modules/")
