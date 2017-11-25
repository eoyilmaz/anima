# -*- coding: utf-8 -*-
"""Installs photoshop scripts
"""

from _winreg import OpenKey, EnumKey, HKEY_LOCAL_MACHINE, QueryValue
import os
import shutil


def install_scripts():
    """installs javascripts for python
    """
    # find photoshop install dir
    reg_key_path = r"SOFTWARE\Adobe\Photoshop"
    with OpenKey(HKEY_LOCAL_MACHINE, reg_key_path) as k:
        version_sub_key_name = EnumKey(k, 0)
        version_sub_key = OpenKey(k, version_sub_key_name)
        install_path = QueryValue(version_sub_key, "ApplicationPath")

    # now copy all the files under scripts folder to
    # photoshop/Presets/Scripts path
    photoshop_scripts_path = os.path.normpath(
        os.path.join(
            install_path, 'Presets', 'Scripts'
        )
    )
    print(photoshop_scripts_path)

    here = os.path.dirname(__file__)
    scripts_folder = os.path.join(here, 'scripts')

    for root, dirs, files in os.walk(scripts_folder):
        for file_ in files:
            file_path = os.path.join(root, file_)
            shutil.copy(
                os.path.normpath(file_path),
                photoshop_scripts_path + '\\'
            )


if __name__ == "__main__":
    install_scripts()
    input('Press ENTER To Continue')
