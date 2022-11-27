# -*- coding: utf-8 -*-

name = "fusion"

version = "18.0.4"

author = ["Erkan Ozgur Yilmaz"]

uuid = "59a8d4cd31414e888b4f859ef14b0fb7"

description = "Fusion package"

requires = []

variants = [[".python-2"], [".python-3"]]

build_command = "python3 {root}/../build.py {install}"


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")

    major = env.REZ_FUSION_MAJOR_VERSION
    if system.platform == "linux":
        env.PATH.append(f"/opt/BlackmagicDesign/Fusion{major}/")
        env.PATH.append(f"/opt/BlackmagicDesign/FusionRenderNode{major}/")
        env.PYTHONPATH.append(f"/opt/BlackmagicDesign/Fusion{major}/")
    if system.platform == "osx":
        env.PATH.append(
            f"/Applications/Blackmagic Fusion {major}/Fusion.app/Contents/MacOS/"
        )
        env.PATH.append(
            f"/Applications/Blackmagic Fusion {major} Render Node/Fusion Render Node.app/Contents/MacOS/"
        )
        env.PYTHONPATH.append(
            f"/Applications/Blackmagic Fusion {major}/Fusion.app/Contents/MacOS/"
        )
