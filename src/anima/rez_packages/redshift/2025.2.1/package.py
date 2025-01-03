# -*- coding: utf-8 -*-

name = "redshift"

version = "2025.2.1"

author = ["Erkan Ozgur Yilmaz"]

uuid = "949dbed5cb0247e4b94445f6ef3a0539"

description = "Redshift package"

variants = [
    ["maya-2025"],
    ["houdini-20.5.410"],
]

build_command = "python3 {root}/../build.py {install}"

with scope("config") as c:
    # c.release_packages_path = "/shots/fx/home/software/packages"
    # c.plugins.release_hook.emailer.recipients = []
    c.plugins.release_vcs.git.allow_no_upstream = True


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    if system.platform == "linux":
        env.REDSHIFT_LOCATION = "/usr/redshift-{}.{}.{}".format(
            env.REZ_REDSHIFT_MAJOR_VERSION,
            env.REZ_REDSHIFT_MINOR_VERSION,
            env.REZ_REDSHIFT_PATCH_VERSION,
        )
        env.REDSHIFT_COREDATAPATH = env.REDSHIFT_LOCATION
    elif system.platform == "osx":
        env.REDSHIFT_LOCATION = "/Applications/redshift-{}.{}.{}".format(
            env.REZ_REDSHIFT_MAJOR_VERSION,
            env.REZ_REDSHIFT_MINOR_VERSION,
            env.REZ_REDSHIFT_PATCH_VERSION,
        )
        env.REDSHIFT_COREDATAPATH = env.REDSHIFT_LOCATION
        env.PATH.append("/usr/sbin/")

    if "maya" in this.root:
        env.REDSHIFT_PLUG_IN_PATH = "$REDSHIFT_COREDATAPATH/redshift4maya/{}".format(
            env.REZ_MAYA_MAJOR_VERSION
        )
        env.REDSHIFT_SCRIPT_PATH = "$REDSHIFT_COREDATAPATH/redshift4maya/common/scripts"
        env.REDSHIFT_XBMLANGPATH = "$REDSHIFT_COREDATAPATH/redshift4maya/common/icons"
        env.REDSHIFT_RENDER_DESC_PATH = (
            "$REDSHIFT_COREDATAPATH/redshift4maya/common/rendererDesc"
        )
        env.REDSHIFT_CUSTOM_TEMPLATE_PATH = (
            "$REDSHIFT_COREDATAPATH/redshift4maya/common/scripts/NETemplates"
        )
        env.REDSHIFT_MAYAEXTENSIONSPATH = "$REDSHIFT_PLUG_IN_PATH/extensions"
        env.REDSHIFT_PROCEDURALSPATH = "$REDSHIFT_COREDATAPATH/procedurals"

        env.MAYA_PLUG_IN_PATH.append(env.REDSHIFT_PLUG_IN_PATH)
        env.MAYA_SCRIPT_PATH.append(env.REDSHIFT_SCRIPT_PATH)
        env.PYTHONPATH.append(env.REDSHIFT_SCRIPT_PATH)
        env.XBMLANGPATH.append(env.REDSHIFT_XBMLANGPATH)
        env.MAYA_RENDER_DESC_PATH.append(env.REDSHIFT_RENDER_DESC_PATH)
        env.MAYA_CUSTOM_TEMPLATE_PATH.append(env.REDSHIFT_CUSTOM_TEMPLATE_PATH)

        env.PATH.append("{}/bin".format(env.REDSHIFT_COREDATAPATH))

        # create a link under /Applications to redshift
        # import os

        # try:
        #     os.remove("/Applications/redshift")
        # except FileNotFoundError:
        #     pass
        # os.symlink(str(env.REDSHIFT_LOCATION), "/Applications/redshift")

    if "houdini" in this.root:
        env.HOUDINI_DSO_ERROR = 2
        env.PATH.prepend("{}/bin".format(env.REDSHIFT_LOCATION))

        houdini_version_tuple = (
            env.REZ_HOUDINI_MAJOR_VERSION,
            env.REZ_HOUDINI_MINOR_VERSION,
            env.REZ_HOUDINI_PATCH_VERSION,
        )

        env.HOUDINI_PATH.prepend(
            "{}/redshift4houdini/{}.{}.{}{}".format(
                env.REDSHIFT_LOCATION,
                houdini_version_tuple[0],
                houdini_version_tuple[1],
                houdini_version_tuple[2],
                "" if system.arch == "x86_64" else f"_{system.arch}"
            )
        )
        env.REDSHIFT_RV_OPEN_ONLY = 1
        env.REDSHIFT_RV_ALWAYSONTOP = 0
        env.PXR_PLUGINPATH_NAME.append(
            "{}/redshift4solaris/{}.{}.{}".format(
                env.REDSHIFT_LOCATION,
                houdini_version_tuple[0],
                houdini_version_tuple[1],
                houdini_version_tuple[2],
            )
        )
