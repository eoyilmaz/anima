# -*- coding: utf-8 -*-

name = 'maya'

version = '2020.4.0'

author = ['Erkan Ozgur Yilmaz']

uuid = '926ca70831554917977883498363a94e'

description = 'Maya package'

requires = ['python-2.7.11']

build_command = "python3 {root}/../build.py {install}"

with scope("config") as c:
    # c.release_packages_path = "/shots/fx/home/software/packages"
    # c.plugins.release_hook.emailer.recipients = []
    c.plugins.release_vcs.git.allow_no_upstream = True


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")
    env.PATH.append("/usr/autodesk/maya{}/bin".format(env.REZ_MAYA_MAJOR_VERSION))
    env.MAYA_DISABLE_CIP = 1
    env.MAYA_DISABLE_CER = 1


