#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

import os
import sys


def submit_export_alembics(path):
    """creates a afanasy job that exports the alembics on a given scene

    :param str path: Path to a maya file
    """
    import af
    import afcommon

    block = af.Block(
        "Alembic Export",
        'maya',
    )

    command = [
        "mayapy",
        "-c",
        "\"import pymel.core as pm; from anima.env.mayaEnv import afanasy_publisher;afanasy_publisher.export_alembics('%s');\"" % path
    ]

    block.setCommand(" ".join(command))
    block.setNumeric(1, 1, 1, 1)

    job = af.Job('Test - Alembic Export')
    job.blocks = [block]
    status, data = job.send()

    # restore job name
    if not status:
        RuntimeError('Something went wrong!')


def export_alembics(path):
    """This does all the work needed

    :param str path: The path of the file version
    :return:
    """
    from anima.env import mayaEnv
    m = mayaEnv.Maya()
    m.use_progress_window = False  # Maya sets that automatically but let's be sure!
    v = m.get_version_from_full_path(path)
    if not v:
        raise RuntimeError("version not found!")

    m.open(v, force=True, skip_update_check=True, prompt=False)

    from anima.env.mayaEnv import auxiliary
    auxiliary.export_alembic_from_cache_node(handles=1)
