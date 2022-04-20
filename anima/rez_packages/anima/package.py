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
]

build_command = "python {root}/build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    import os

    anima_lib_path = os.path.expanduser("$HOME/Documents/development/anima")
    anima_dev_path = os.path.expanduser("$HOME/Documents/DEV")

    env.ANIMA_LIB_PATH = anima_lib_path
    env.ANIMA_DEV_PATH = anima_dev_path
    env.ANIMA_PATH = os.path.expanduser("{}/anima".format(anima_lib_path))

    env.PYTHONPATH.append("{}/anima".format(anima_lib_path))
    env.PYTHONPATH.append(
        "{}/extra_libraries/py{}.{}".format(
            anima_lib_path,
            env.REZ_PYTHON_MAJOR_VERSION,
            env.REZ_PYTHON_MINOR_VERSION,
        )
    )

    # Maya
    if "maya" in this.root:
        # PYTHONPATH
        env.PYTHONPATH.append(
            "{}/anima/anima/dcc/mayaEnv/config".format(anima_lib_path)
        )
        env.PYTHONPATH.append(
            "{}/anima/anima/dcc/mayaEnv/config/{}".format(
                anima_lib_path, env.REZ_MAYA_MAJOR_VERSION
            )
        )
        env.PYTHONPATH.append("{}/maya/scripts".format(anima_dev_path))

        # MAYA_SCRIPT_PATH
        env.MAYA_SCRIPT_PATH.append(
            "{}/anima/anima/dcc/mayaEnv/config".format(anima_lib_path)
        )
        env.MAYA_SCRIPT_PATH.append(
            "{}/anima/anima/dcc/mayaEnv/config/{}".format(
                anima_lib_path, env.REZ_MAYA_MAJOR_VERSION
            )
        )

        env.MAYA_PLUG_IN_PATH.append(
            "{}/anima/anima/dcc/mayaEnv/plugins".format(anima_lib_path)
        )
        env.MAYA_PLUG_IN_PATH.append(
            "{}/anima/anima/dcc/mayaEnv/plugins/{}".format(
                anima_lib_path, env.REZ_MAYA_MAJOR_VERSION
            )
        )

        # XMBLANGPATH
        env.XBMLANGPATH.append("{}/maya/icons/%B".format(anima_dev_path))
        env.XBMLANGPATH.append("{}/maya/icons/CustomIcons/%B".format(anima_dev_path))

        # MAYA_PRESET_PATH
        env.MAYA_PRESET_PATH.append("{}/maya/presets".format(anima_dev_path))

        # ANIMA MAYA SHELVES PATH
        env.ANIMA_MAYA_SHELVES_PATH = "{}/maya/shelves".format(anima_dev_path)

    # Houdini
    if "houdini" in this.root:
        houdini_short_version = "{}.{}".format(
            env.REZ_HOUDINI_MAJOR_VERSION, env.REZ_HOUDINI_MINOR_VERSION
        )
        anima_otl_path = "{}/houdini/otls/{}".format(
            anima_dev_path, houdini_short_version
        )
        anima_dso_path = "{}/houdini/dso/{}".format(
            anima_dev_path, houdini_short_version
        )

        env.HOUDINI_OTLSCAN_PATH.append(anima_otl_path)
        if "&" not in env.HOUDINI_OTLSCAN_PATH.value():
            env.HOUDINI_OTLSCAN_PATH.append("&")

        env.HOUDINI_DSO_PATH.append(anima_dso_path)
        if "&" not in env.HOUDINI_DSO_PATH.value():
            env.HOUDINI_DSO_PATH.append("&")

        env.HOUDINI_PYTHON_PANEL_PATH.append(
            "{}/anima/anima/dcc/houdini/python_panels/".format(anima_lib_path)
        )
        if "&" not in env.HOUDINI_PYTHON_PANEL_PATH.value():
            env.HOUDINI_PYTHON_PANEL_PATH.append("&")

        env.HOUDINI_MENU_PATH.append(
            "{}/anima/anima/dcc/houdini/menus/".format(anima_lib_path)
        )
        if "&" not in env.HOUDINI_MENU_PATH.value():
            env.HOUDINI_MENU_PATH.append("&")

    # Blender
    if "blender" in this.root:
        # Blender cannot use multiple paths in BLENDER_USER_SCRIPTS
        # so, instead of append/prepend directly set to a value
        env.BLENDER_USER_SCRIPTS = "{}/blender".format(anima_dev_path)
        # Add extra libraries like PySide2

