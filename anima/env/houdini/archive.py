# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
from anima.utils.archive import ArchiverBase


class Archiver(ArchiverBase):
    """Archives the current scene with all the necessary inputs
    """

    default_project_structure = """assets
    Outputs
    Outputs/geo
    Outputs/geo/cache
    """

    def _extract_references(self):
        """Extract referenced files from the current scene.

        This could be:

          - Geometry caches (File, DopIO)
          - Alembic caches (Alembic)
          - Redshift Proxies (s@instancefile point attr)
          - Textures (RSTexture, Texture)
          - Any spare input that is a file path

        :return:
        """
        raise NotImplementedError("Method is not implemented yet")

    def _move_file_and_fix_references(self, path, project_path, scenes_folder='', refs_folder=''):
        """Moves the given file to the given project path and moves any references of it too

        :param str path: The path of the scene file
        :param str project_path: The project path
        :param str scenes_folder: The scenes folder to store the original scene.
        :param str refs_folder: The references folder to replace reference paths with.
        :return list: returns a list of paths
        """
        raise NotImplementedError("Method is not implemented yet")