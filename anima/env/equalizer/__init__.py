# -*- coding: utf-8 -*-

import tde4
from anima.env.base import EnvironmentBase


class Equalizer(EnvironmentBase):

    name = '3DEqualizer4'

    def save_as(self, version, run_pre_publishers=True):
        """runs when saving a document

        :param version:
        :param run_pre_publishers:
        :return:
        """

        tde4.setProjectPath(version.absolute_full_path)
        tde4.saveProject(version.absolute_full_path)

    def open(self, version, force=False, representation=None,
             reference_depth=0, skip_update_check=False):
        """

        :param version:
        :param force:
        :param representation:
        :param reference_depth:
        :param skip_update_check:
        :return:
        """

        from stalker import Version
        assert isinstance(version, Version)
        td4.loadProject(version.absolute_full_path)
