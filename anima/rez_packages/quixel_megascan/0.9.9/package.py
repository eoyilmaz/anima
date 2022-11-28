# -*- coding: utf-8 -*-

name = "quixel_megascan"

version = "0.9.9"

author = ["Erkan Ozgur Yilmaz"]

uuid = "e2f583d1a3ab41ef91431a5362bf1937"

description = "Quixel Megascan Package"

variants = [
    ["blender"],
    ["maya"],
    ["houdini"],
]

build_command = "python3 {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    env.MEGASCAN_LIBRARY_PATH = (
        "/mnt/NAS/Users/eoyilmaz/Stalker_Projects/Resources/Quixel/"
    )

    if "blender" in this.root:
        pass

    if "maya" in this.root:
        env.PYTHONPATH.append(
            "$MEGASCAN_LIBRARY_PATH/support/plugins/maya/6.8/MSLiveLink/"
        )

    if "houdini" in this.root:
        env.HOUDINI_PATH.prepend(
            "$MEGASCAN_LIBRARY_PATH/support/plugins/houdini/4.5/MSLiveLink/"
        )
