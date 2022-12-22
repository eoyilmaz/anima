# -*- coding: utf-8 -*-

name = "anima"

version = "0.7.0"

author = ["Erkan Ozgur Yilmaz"]

uuid = "7ac53aa7e70c4014a5695f476f992d02"

description = "Anima Pipeline Package"

requires = [
    "stalker",
]

variants = [
    ["python"],  # pure python variant
    ["blender"],
    ["fusion"],
    ["houdini"],
    ["maya"],
    ["3de4"],
]

build_command = "python3 {root}/build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    import os

    # find python major and minor version
    python_major = -1
    python_minor = 0
    for p in str(env.REZ_USED_EPH_RESOLVE).split(" "):
        if "python" not in p:
            continue
        python_major, python_minor = p.strip().split("-")[1].split(".")[0:2]

    env.ANIMA_LIB_PATH = "${HOME}/Documents/development"
    env.ANIMA_DEV_PATH = "${HOME}/Documents/DEV"
    env.ANIMA_PATH = os.path.expanduser("${ANIMA_LIB_PATH}/anima")

    env.PYTHONPATH.append("${ANIMA_LIB_PATH}/anima")

    if "maya" not in this.root and "houdini" not in this.root:
        # default PYTHONPATH
        pylibs_base_path = "{}/pylibs/py{}.{}{}".format(
            "${ANIMA_LIB_PATH}",
            python_major,
            python_minor,
            "",
        )
        env.PATH.append("{}/bin".format(pylibs_base_path))
        env.PYTHONPATH.append("{}/lib/python/site-packages".format(pylibs_base_path))

    if "maya" in this.root:
        # Maya
        # PYTHONPATH
        pylibs_base_path = "{}/pylibs/py{}.{}{}".format(
            "${ANIMA_LIB_PATH}",
            python_major,
            python_minor,
            # maya=<2023 uses x86 under macOS
            "_x86"
            if system.platform == "osx"  # and int(env.REZ_MAYA_MAJOR_VERSION) <= 2023
            else "",
        )
        env.PATH.append("{}/bin".format(pylibs_base_path))
        env.PYTHONPATH.append("{}/lib/python/site-packages".format(pylibs_base_path))
        env.PYTHONPATH.append("${ANIMA_LIB_PATH}/anima/anima/dcc/mayaEnv/config")
        env.PYTHONPATH.append(
            "${ANIMA_LIB_PATH}/anima/anima/dcc/mayaEnv/config/${REZ_MAYA_MAJOR_VERSION}"
        )
        env.PYTHONPATH.append("${ANIMA_DEV_PATH}/maya/scripts")

        # MAYA_SCRIPT_PATH
        env.MAYA_SCRIPT_PATH.append("${ANIMA_LIB_PATH}/anima/anima/dcc/mayaEnv/config")
        env.MAYA_SCRIPT_PATH.append(
            "${ANIMA_LIB_PATH}/anima/anima/dcc/mayaEnv/config/${REZ_MAYA_MAJOR_VERSION}"
        )

        env.MAYA_PLUG_IN_PATH.append(
            "${ANIMA_LIB_PATH}/anima/anima/dcc/mayaEnv/plugins"
        )
        env.MAYA_PLUG_IN_PATH.append("${ANIMA_DEV_PATH}/maya/plugins")
        env.MAYA_PLUG_IN_PATH.append(
            "${ANIMA_DEV_PATH}/maya/plugins/${REZ_MAYA_MAJOR_VERSION}"
        )

        env.MAYA_PLUG_IN_PATH.append(
            "${ANIMA_LIB_PATH}/anima/anima/dcc/mayaEnv/plugins/${REZ_MAYA_MAJOR_VERSION}"
        )

        # XMBLANGPATH
        if system.platform == "linux":
            env.XBMLANGPATH.append("${ANIMA_DEV_PATH}/maya/icons/%B")
            env.XBMLANGPATH.append("${ANIMA_DEV_PATH}/maya/icons/CustomIcons/%B")
        else:
            env.XBMLANGPATH.append("${ANIMA_DEV_PATH}/maya/icons/")
            env.XBMLANGPATH.append("${ANIMA_DEV_PATH}/maya/icons/CustomIcons/")

        # MAYA_PRESET_PATH
        env.MAYA_PRESET_PATH.append("${ANIMA_DEV_PATH}/maya/presets")

        # ANIMA MAYA SHELVES PATH
        env.ANIMA_MAYA_SHELVES_PATH = "${ANIMA_DEV_PATH}/maya/shelves"

    if "houdini" in this.root:
        # Houdini
        # PYTHONPATH
        pylibs_base_path = "{}/pylibs/py{}.{}{}".format(
            "${ANIMA_LIB_PATH}",
            python_major,
            python_minor,
            # Houdini uses x86 under macOS
            "_x86"
            if system.platform == "osx"  # and int(env.REZ_MAYA_MAJOR_VERSION) <= 2023
            else "",
        )
        env.PATH.append("{}/bin".format(pylibs_base_path))
        env.PYTHONPATH.append("{}/lib/python/site-packages".format(pylibs_base_path))

        env.HOUDINI_SHORT_VERSION = (
            "${REZ_HOUDINI_MAJOR_VERSION}.${REZ_HOUDINI_MINOR_VERSION}"
        )
        anima_otl_path = "${ANIMA_DEV_PATH}/houdini/otls/${HOUDINI_SHORT_VERSION}"
        anima_dso_path = "${ANIMA_DEV_PATH}/houdini/dso/${HOUDINI_SHORT_VERSION}"

        env.HOUDINI_OTLSCAN_PATH.prepend(anima_otl_path)
        env.HOUDINI_DSO_PATH.prepend(anima_dso_path)
        env.HOUDINI_PYTHON_PANEL_PATH.prepend(
            "${ANIMA_LIB_PATH}/anima/anima/dcc/houdini/python_panels/"
        )
        env.HOUDINI_MENU_PATH.prepend(
            "${ANIMA_LIB_PATH}/anima/anima/dcc/houdini/menus/"
        )

    # Blender
    if "blender" in this.root:
        # Blender cannot use multiple paths in BLENDER_USER_SCRIPTS
        # so, instead of append/prepend directly set to a value
        env.BLENDER_USER_SCRIPTS = "${ANIMA_DEV_PATH}/blender"
