# -*- coding: utf-8 -*-

name = "python"

version = "3.13.0"

author = ["Erkan Ozgur Yilmaz"]

uuid = "f86b5f3700054e94ae2566b81c5a7433"

description = "Python package"

variants = [[".python-3.13"]]

build_command = "python3 {root}/../build.py {install}"

with scope("config") as c:
    # c.release_packages_path = "/shots/fx/home/software/packages"
    # c.plugins.release_hook.emailer.recipients = []
    c.plugins.release_vcs.git.allow_no_upstream = True


def commands():
    # env.PYTHONPATH.append("{root}/python")
    env.PATH.prepend("{root}/bin")
    pass
