# -*- coding: utf-8 -*-

name = "houdini"

version = "19.0.383"

author = ["Erkan Ozgur Yilmaz"]

uuid = "e412cb9626164151b088f2bf4a66fe31"

description = "Houdini package"

requires = [
    "python-3.7",
    "qlib"
]

build_command = "python {root}/../build.py {install}"

with scope("config") as c:
    # c.release_packages_path = "/shots/fx/home/software/packages"
    # c.plugins.release_hook.emailer.recipients = []
    c.plugins.release_vcs.git.allow_no_upstream = True


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")
    env.PATH.append(
        "/opt/hfs{}.{}.{}/bin".format(
            env.REZ_HOUDINI_MAJOR_VERSION,
            env.REZ_HOUDINI_MINOR_VERSION,
            env.REZ_HOUDINI_PATCH_VERSION
        )
    )
    if "&" not in env.PATH.value():
        env.PATH.append("&")

    env.LD_PRELOAD = "/lib64/libc_malloc_debug.so.0"
    env.LD_LIBRARY_PATH.append("$HFS/dsolib")

    if "&" not in env.LD_LIBRARY_PATH.value():
        env.LD_LIBRARY_PATH.append("&")

    if "HOUDINI_PATH" not in env.keys():
        env.HOUDINI_PATH = "&"
    elif "&" not in env.HOUDINI_PATH.value():
        env.HOUDINI_PATH.append("&")

    if "HOUDINI_OTLSCAN_PATH" not in env.keys():
        env.HOUDINI_OTLSCAN_PATH = "&"
    elif "&" not in env.HOUDINI_OTLSCAN_PATH.value():
        env.HOUDINI_OTLSCAN_PATH.append("&")

    if "HOUDINI_MENU_PATH" not in env.keys():
        env.HOUDINI_MENU_PATH = "&"
    elif "&" not in env.HOUDINI_MENU_PATH.value():
        env.HOUDINI_MENU_PATH.append("&")

    env.HOUDINI_DSO_ERROR = 2
    env.HOUDINI_ACCESS_METHOD = 2
