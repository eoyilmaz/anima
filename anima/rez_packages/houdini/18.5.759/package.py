# -*- coding: utf-8 -*-

name = "houdini"

version = "18.5.759"

author = ["Erkan Ozgur Yilmaz"]

uuid = "e412cb9626164151b088f2bf4a66fe31"

description = "Houdini package"

requires = [
    ".python-3.7",
    "qLib"
]

build_command = "python3 {root}/../build.py {install}"

with scope("config") as c:
    # c.release_packages_path = "/shots/fx/home/software/packages"
    # c.plugins.release_hook.emailer.recipients = []
    c.plugins.release_vcs.git.allow_no_upstream = True


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")
    major = env.REZ_HOUDINI_MAJOR_VERSION
    minor = env.REZ_HOUDINI_MINOR_VERSION
    patch = env.REZ_HOUDINI_PATCH_VERSION

    if system.platform == "osx":
        env.PATH.append(
            f"/Applications/Houdini/Houdini{major}.{minor}.{patch}/"
            f"Houdini FX {major}.{minor}.{patch}.app/Contents/MacOS"
        )
        env.PATH.append(
            f"/Applications/Houdini/Houdini{major}.{minor}.{patch}/"
            f"Houdini Indie {major}.{minor}.{patch}.app/Contents/MacOS"
        )
        env.PATH.append(
            f"/Applications/Houdini/Houdini{major}.{minor}.{patch}/"
            f"Houdini Core {major}.{minor}.{patch}.app/Contents/MacOS"
        )
        env.PATH.append(
            f"/Applications/Houdini/Houdini{major}.{minor}.{patch}/"
            f"Frameworks/Houdini.framework/Versions/{major}.{minor}/"
            f"Resources/bin/"
        )
    elif system.platform == "windows":
        env.PATH.append(
            f"C:/Program Files/Side Effects Software/"
            f"Houdini {major}.{minor}.{patch}/bin"
        )
    else:
        # default to Linux
        env.PATH.append(f"/opt/hfs{major}.{minor}.{patch}/bin")
        env.LD_PRELOAD = "/lib64/libc_malloc_debug.so.0"
        env.LD_LIBRARY_PATH.append("$HFS/dsolib")

    if "&" not in env.PATH.value():
        env.PATH.append("&")

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

    if "HOUDINI_DSO_PATH" not in env.keys():
        env.HOUDINI_DSO_PATH = "&"
    elif "&" not in env.HOUDINI_DSO_PATH.value():
        env.HOUDINI_DSO_PATH.append("&")

    if "HOUDINI_PYTHON_PANEL_PATH" not in env.keys():
        env.HOUDINI_PYTHON_PANEL_PATH = "&"
    elif "&" not in env.HOUDINI_PYTHON_PANEL_PATH.value():
        env.HOUDINI_PYTHON_PANEL_PATH.append("&")

    if "HOUDINI_MENU_PATH" not in env.keys():
        env.HOUDINI_MENU_PATH = "&"
    elif "&" not in env.HOUDINI_MENU_PATH.value():
        env.HOUDINI_MENU_PATH.append("&")

    env.HOUDINI_DSO_ERROR = 2
    env.HOUDINI_ACCESS_METHOD = 2
