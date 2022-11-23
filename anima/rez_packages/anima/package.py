# -*- coding: utf-8 -*-

name = "anima"

version = "0.7.0"

author = [
    "Erkan Ozgur Yilmaz",
]

uuid = "7ac53aa7e70c4014a5695f476f992d02"

description = "Anima Pipeline Package"

requires = [
    "stalker",
]

variants = [
    ["blender"],
    ["fusion"],
    ["houdini"],
    ["maya"],
    ["3de4"]
]

build_command = "python3 {root}/build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    import os

    env.ANIMA_LIB_PATH = "${HOME}/Documents/development/anima"
    env.ANIMA_DEV_PATH = "${HOME}/Documents/DEV"
    env.ANIMA_PATH = os.path.expanduser("${ANIMA_LIB_PATH}/anima")

    env.PYTHONPATH.append("${ANIMA_LIB_PATH}/anima")
    env.PYTHONPATH.append(
        "${ANIMA_LIB_PATH}/extra_libraries/"
        "py${REZ_PYTHON_MAJOR_VERSION}.${REZ_PYTHON_MINOR_VERSION}"
    )

    # Maya
    if "maya" in this.root:
        # PYTHONPATH
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
        env.XBMLANGPATH.append("${ANIMA_DEV_PATH}/maya/icons/%B")
        env.XBMLANGPATH.append("${ANIMA_DEV_PATH}/maya/icons/CustomIcons/%B")

        # MAYA_PRESET_PATH
        env.MAYA_PRESET_PATH.append("${ANIMA_DEV_PATH}/maya/presets")

        # ANIMA MAYA SHELVES PATH
        env.ANIMA_MAYA_SHELVES_PATH = "${ANIMA_DEV_PATH}/maya/shelves"

    # Houdini
    if "houdini" in this.root:
        env.HOUDINI_SHORT_VERSION = \
            "${REZ_HOUDINI_MAJOR_VERSION}.${REZ_HOUDINI_MINOR_VERSION}"
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

    # 3DE4
    if "3de4" in this.root:
        pass
