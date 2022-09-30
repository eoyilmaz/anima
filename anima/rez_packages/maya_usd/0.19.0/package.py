# -*- coding: utf-8 -*-

name = 'maya_usd'

version = '0.19.0'

author = ['Erkan Ozgur Yilmaz']

uuid = '821275f80a914b8eb4b690810192c235'

description = 'Maya USD'

requires = []

variants = [
    ["maya-2020"],
    ["maya-2022"],
]

build_command = "python {root}/build.py {install}"

with scope("config") as c:
    # c.release_packages_path = "/shots/fx/home/software/packages"
    # c.plugins.release_hook.emailer.recipients = []
    c.plugins.release_vcs.git.allow_no_upstream = True


def commands():
    env.MAYA_MODULE_PATH.prepend("{root}")
