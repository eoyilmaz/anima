# -*- coding: utf-8 -*-

name = 'python'

version = '3.10.0'

author = [
    'Erkan Ozgur Yilmaz'
]

uuid = 'f86b5f3700054e94ae2566b81c5a7433'

description = 'Python package'

build_command = "python {root}/../build.py {install}"

with scope("config") as c:
    # c.release_packages_path = "/shots/fx/home/software/packages"
    # c.plugins.release_hook.emailer.recipients = []
    c.plugins.release_vcs.git.allow_no_upstream = True


def commands():
    # env.PYTHONPATH.append("{root}/python")
    # env.PATH.append("{root}/bin")
    pass
