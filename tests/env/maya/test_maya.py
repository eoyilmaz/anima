# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import shutil
import tempfile

import unittest2
import pymel

from stalker import (db, Project, Repository, StatusList, Status, Asset, Shot,
                     Task, Sequence, Version, User, Type, Structure,
                     FilenameTemplate, ImageFormat)

from anima import utils
from anima.env.mayaEnv import Maya
from anima.env.mayaEnv import ProgressWindowManager, ProgressCaller
from anima.utils import walk_version_hierarchy


class MayaTestBase(unittest2.TestCase):

    """The base class for Maya Tests
    """

    def create_version(self, task, take_name):
        """A helper method for creating a new version

        :param task: the task
        :param take_name: the take_name name
        :return: the version
        """
        # just renew the scene
        pymel.core.newFile(force=True)

        v = Version(task=task, take_name=take_name)
        db.DBSession.add(v)
        self.maya_env.save_as(v)

        return v


    @classmethod
    def setUpClass(cls):
        """setup in class level
        """
        import logging
        logger = logging.getLogger('anima.env.maya')
        logger.setLevel(logging.DEBUG)

    def setUp(self):
        """setup the tests
        """
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        database_url = "sqlite:///:memory:"
        db.setup({'sqlalchemy.url': database_url})
        db.init()

        self.temp_repo_path = tempfile.mkdtemp()

        self.user1 = User(
            name='User 1',
            login='user1',
            email='user1@users.com',
            password='12345'
        )

        self.repo1 = Repository(
            name='Test Project Repository',
            linux_path=self.temp_repo_path,
            windows_path=self.temp_repo_path,
            osx_path=self.temp_repo_path
        )

        self.status_new = Status.query.filter_by(code='NEW').first()
        self.status_wip = Status.query.filter_by(code='WIP').first()
        self.status_comp = Status.query.filter_by(code='CMPL').first()

        self.task_template = FilenameTemplate(
            name='Task Template',
            target_entity_type='Task',
            path='{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.asset_template = FilenameTemplate(
            name='Asset Template',
            target_entity_type='Asset',
            path='{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.shot_template = FilenameTemplate(
            name='Shot Template',
            target_entity_type='Shot',
            path='{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.sequence_template = FilenameTemplate(
            name='Sequence Template',
            target_entity_type='Sequence',
            path='{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.structure = Structure(
            name='Project Struture',
            templates=[self.task_template, self.asset_template,
                       self.shot_template, self.sequence_template]
        )

        self.project_status_list = StatusList(
            name='Project Statuses',
            target_entity_type='Project',
            statuses=[self.status_new, self.status_wip, self.status_comp]
        )

        self.image_format = ImageFormat(
            name='HD 1080',
            width=1920,
            height=1080,
            pixel_aspect=1.0
        )

        # create a test project
        self.project = Project(
            name='Test Project',
            code='TP',
            repository=self.repo1,
            status_list=self.project_status_list,
            structure=self.structure,
            image_format=self.image_format
        )

        self.task_status_list =\
            StatusList.query.filter_by(target_entity_type='Task').first()
        self.asset_status_list =\
            StatusList.query.filter_by(target_entity_type='Asset').first()
        self.shot_status_list =\
            StatusList.query.filter_by(target_entity_type='Shot').first()
        self.sequence_status_list =\
            StatusList.query.filter_by(target_entity_type='Sequence').first()

        self.character_type = Type(
            name='Character',
            code='CHAR',
            target_entity_type='Asset'
        )

        # create a test series of root task
        self.task1 = Task(
            name='Test Task 1',
            project=self.project
        )
        self.task2 = Task(
            name='Test Task 2',
            project=self.project
        )
        self.task3 = Task(
            name='Test Task 3',
            project=self.project
        )

        # then a couple of child tasks
        self.task4 = Task(
            name='Test Task 4',
            parent=self.task1
        )
        self.task5 = Task(
            name='Test Task 5',
            parent=self.task1
        )
        self.task6 = Task(
            name='Test Task 6',
            parent=self.task1
        )

        # create a root asset
        self.asset1 = Asset(
            name='Asset 1',
            code='asset1',
            type=self.character_type,
            project=self.project
        )

        # create a child asset
        self.asset2 = Asset(
            name='Asset 2',
            code='asset2',
            type=self.character_type,
            parent=self.task4
        )

        # create a root Sequence
        self.sequence1 = Sequence(
            name='Sequence1',
            code='SEQ1',
            project=self.project
        )

        # create a child Sequence
        self.sequence2 = Sequence(
            name='Sequence2',
            code='SEQ2',
            parent=self.task2
        )

        # create a root Shot
        self.shot1 = Shot(
            code='SH001',
            project=self.project
        )

        # create a child Shot (child of a Sequence)
        self.shot2 = Shot(
            code='SH002',
            parent=self.sequence1
        )

        # create a child Shot (child of a child Sequence)
        self.shot3 = Shot(
            code='SH003',
            parent=self.sequence2
        )

        # commit everything
        db.DBSession.add_all([
            self.repo1, self.status_new, self.status_wip, self.status_comp,
            self.project_status_list, self.project, self.task_status_list,
            self.asset_status_list, self.shot_status_list,
            self.sequence_status_list, self.task1, self.task2, self.task3,
            self.task4, self.task5, self.task6, self.asset1, self.asset2,
            self.shot1, self.shot2, self.shot3, self.sequence1, self.sequence2,
            self.task_template, self.asset_template, self.shot_template,
            self.sequence_template
        ])
        db.DBSession.commit()

        # create the environment instance
        self.maya_env = Maya()

        # asset2
        self.version1 = self.create_version(self.asset2, 'Main')
        self.version2 = self.create_version(self.asset2, 'Main')
        self.version3 = self.create_version(self.asset2, 'Main')

        self.version4 = self.create_version(self.asset2, 'Take1')
        self.version5 = self.create_version(self.asset2, 'Take1')
        self.version6 = self.create_version(self.asset2, 'Take1')

        # task5
        self.version7 = self.create_version(self.task5, 'Main')
        self.version8 = self.create_version(self.task5, 'Main')
        self.version9 = self.create_version(self.task5, 'Main')

        self.version10 = self.create_version(self.task5, 'Take1')
        self.version11 = self.create_version(self.task5, 'Take1')
        self.version12 = self.create_version(self.task5, 'Take1')

        # task6
        self.version13 = self.create_version(self.task6, 'Main')
        self.version14 = self.create_version(self.task6, 'Main')
        self.version15 = self.create_version(self.task6, 'Main')

        self.version16 = self.create_version(self.task6, 'Take1')
        self.version17 = self.create_version(self.task6, 'Take1')
        self.version18 = self.create_version(self.task6, 'Take1')

        # shot3
        self.version19 = self.create_version(self.shot3, 'Main')
        self.version20 = self.create_version(self.shot3, 'Main')
        self.version21 = self.create_version(self.shot3, 'Main')

        self.version22 = self.create_version(self.shot3, 'Take1')
        self.version23 = self.create_version(self.shot3, 'Take1')
        self.version24 = self.create_version(self.shot3, 'Take1')

        # task3
        self.version25 = self.create_version(self.task3, 'Main')
        self.version26 = self.create_version(self.task3, 'Main')
        self.version27 = self.create_version(self.task3, 'Main')

        self.version28 = self.create_version(self.task3, 'Take1')
        self.version29 = self.create_version(self.task3, 'Take1')
        self.version30 = self.create_version(self.task3, 'Take1')

        # asset1
        self.version31 = self.create_version(self.asset1, 'Main')
        self.version32 = self.create_version(self.asset1, 'Main')
        self.version33 = self.create_version(self.asset1, 'Main')

        self.version34 = self.create_version(self.asset1, 'Take1')
        self.version35 = self.create_version(self.asset1, 'Take1')
        self.version36 = self.create_version(self.asset1, 'Take1')

        # shot2
        self.version37 = self.create_version(self.shot2, 'Main')
        self.version38 = self.create_version(self.shot2, 'Main')
        self.version39 = self.create_version(self.shot2, 'Main')

        self.version40 = self.create_version(self.shot2, 'Take1')
        self.version41 = self.create_version(self.shot2, 'Take1')
        self.version42 = self.create_version(self.shot2, 'Take1')

        # shot1
        self.version43 = self.create_version(self.shot1, 'Main')
        self.version44 = self.create_version(self.shot1, 'Main')
        self.version45 = self.create_version(self.shot1, 'Main')

        self.version46 = self.create_version(self.shot1, 'Take1')
        self.version47 = self.create_version(self.shot1, 'Take1')
        self.version48 = self.create_version(self.shot1, 'Take1')

        # +- task1
        # |  |
        # |  +- task4
        # |  |  |
        # |  |  +- asset2
        # |  |     +- Main
        # |  |     |  +- version1
        # |  |     |  +- version2 (P)
        # |  |     |  +- version3 (P)
        # |  |     +- Take1
        # |  |        +- version4 (P)
        # |  |        +- version5
        # |  |        +- version6 (P)
        # |  |
        # |  +- task5
        # |  |  +- Main
        # |  |  |  +- version7
        # |  |  |  +- version8
        # |  |  |  +- version9
        # |  |  +- Take1
        # |  |     +- version10
        # |  |     +- version11
        # |  |     +- version12 (P)
        # |  |
        # |  +- task6
        # |     +- Main
        # |     |  +- version13
        # |     |  +- version14
        # |     |  +- version15
        # |     +- Take1
        # |        +- version16 (P)
        # |        +- version17
        # |        +- version18 (P)
        # |
        # +- task2
        # |  |
        # |  +- sequence2
        # |     |
        # |     +- shot3
        # |        +- Main
        # |        |  +- version19
        # |        |  +- version20
        # |        |  +- version21
        # |        +- Take1
        # |           +- version22
        # |           +- version23
        # |           +- version24
        # |
        # +- task3
        # |  +- Main
        # |  |  +- version25
        # |  |  +- version26
        # |  |  +- version27
        # |  +- Take1
        # |     +- version28
        # |     +- version29
        # |     +- version30
        # |
        # +- asset1
        # |  +- Main
        # |  |  +- version31
        # |  |  +- version32
        # |  |  +- version33
        # |  +- Take1
        # |     +- version34
        # |     +- version35
        # |     +- version36
        # |
        # +- sequence1
        # |  |
        # |  +- shot2
        # |     +- Main
        # |     |  +- version37
        # |     |  +- version38
        # |     |  +- version39
        # |     +- Take1
        # |        +- version40
        # |        +- version41
        # |        +- version42
        # |
        # +- shot1
        #    +- Main
        #    |  +- version43
        #    |  +- version44
        #    |  +- version45
        #    +- Take1
        #       +- version46
        #       +- version47
        #       +- version48

        # just renew the scene
        pymel.core.newFile(force=True)

        # create a buffer for extra created files, which are to be removed
        self.remove_these_files_buffer = []

    def tearDown(self):
        """cleanup the test
        """
        # set the db.session to None
        db.DBSession.remove()

        # delete the temp folder
        # shutil.rmtree(self.temp_repo_path, ignore_errors=True)

        for f in self.remove_these_files_buffer:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f, True)

    @classmethod
    def tearDownClass(cls):
        # quit maya
        pymel.core.runtime.Quit()


class MayaTestCase(MayaTestBase):
    """tests the maya.Maya
    """

    def test_save_as_creates_a_maya_file_at_version_absolute_full_path(self):
        """testing if the save_as creates a maya file at the Version.full_path
        """
        version1 = Version(task=self.task6)
        version1.extension = '.ma'
        version1.update_paths()

        # check the version file doesn't exists
        self.assertFalse(os.path.exists(version1.absolute_full_path))

        # save the version
        self.maya_env.save_as(version1)

        # check the file exists
        self.assertTrue(os.path.exists(version1.absolute_full_path))

    def test_save_as_sets_the_version_extension_to_ma(self):
        """testing if the save_as method sets the version extension to ma
        """
        version1 = Version(task=self.task6)
        version1.extension = '.ma'
        version1.update_paths()

        version1.extension = ""
        self.maya_env.save_as(version1)
        self.assertEqual(version1.extension, ".ma")

    def test_save_as_sets_the_render_version_string(self):
        """testing if the save_as method sets the version string in the render
        settings
        """
        version1 = Version(
            task=self.task1
        )
        version1.extension = '.ma'
        version1.update_paths()
        db.DBSession.add(version1)
        db.DBSession.commit()

        self.maya_env.save_as(version1)

        # now check if the render settings version is the same with the
        # version.version_number

        render_version =\
            pymel.core.getAttr("defaultRenderGlobals.renderVersion")
        self.assertEqual(render_version,
                         "v%03d" % version1.version_number)

    def test_save_as_sets_the_render_format_to_exr_for_mentalray(self):
        """testing if the save_as method sets the render format to exr
        """
        # load mayatomr plugin
        try:
            pymel.core.loadPlugin("Mayatomr")
        except RuntimeError:
            # no Mayatomr plugin
            # so pass the test
            return

        # set the current renderer to mentalray
        dRG = pymel.core.PyNode("defaultRenderGlobals")

        dRG.setAttr('currentRenderer', 'mentalRay')

        # dirty little maya tricks
        pymel.core.mel.miCreateDefaultNodes()

        mrG = pymel.core.PyNode("mentalrayGlobals")

        version1 = Version(
            task=self.task1
        )
        version1.extension = '.ma'
        version1.update_paths()
        db.DBSession.add(version1)
        db.DBSession.commit()
        self.maya_env.save_as(version1)

        # now check if the render format is correctly set to exr with zip
        # compression
        self.assertEqual(dRG.getAttr("imageFormat"), 51)
        self.assertEqual(dRG.getAttr("imfkey"), "exr")
        self.assertEqual(mrG.getAttr("imageCompression"), 4)

    def test_save_as_sets_the_render_format_to_exr_for_arnold(self):
        """testing if the save_as method sets the render format to exr when the
        renderer is arnold
        """
        # load mtoa plugin
        try:
            pymel.core.loadPlugin("mtoa")
        except RuntimeError:
            # no mtoa plugin
            # pass the test
            return

        # set the current renderer to arnold
        dRG = pymel.core.PyNode("defaultRenderGlobals")
        dRG.setAttr('currentRenderer', 'arnold')

        # dirty little maya tricks: do a render to create arnold globals
        from mtoa.cmds.arnoldRender import arnoldRender
        arnoldRender(10, 10, False, False,
                     'perspShape', ' -layer defaultRenderLayer')

        dAD = pymel.core.PyNode("defaultArnoldDriver")

        version1 = Version(
            task=self.task1
        )
        version1.extension = '.ma'
        version1.update_paths()
        db.DBSession.add(version1)
        db.DBSession.commit()
        self.maya_env.save_as(version1)

        # now check if the render format is correctly set to exr with zip
        # compression
        self.assertEqual(dRG.getAttr("imageFormat"), 51)
        self.assertEqual(dAD.exrCompression.get(), 2)  # zips
        self.assertEqual(dAD.halfPrecision.get(), 1)  # half
        self.assertEqual(dAD.tiled.get(), 0)  # not tiled
        self.assertEqual(dAD.autocrop.get(), 1)  # auto crop

    def test_save_as_sets_the_render_file_name_for_Assets(self):
        """testing if the save_as sets the render file name correctly
        """
        version1 = Version(task=self.task6)
        version1.extension = '.ma'
        version1.update_paths()

        self.maya_env.save_as(version1)

        # check if the path equals to
        expected_path = \
            '../../Outputs/<RenderLayer>/' \
            '%(project_code)s_%(version_nice_name)s_v%(version_number)s' \
            '_<RenderLayer>_<RenderPass>' % {
                'project_code': version1.task.project.code,
                'version_nice_name': version1.nice_name,
                'version_number': ('%s' % version1.version_number).zfill(3)
            }

        image_path = os.path.join(
            pymel.core.workspace.path,
            pymel.core.workspace.fileRules['image']
        ).replace("\\", "/")

        expected_path = utils.relpath(
            image_path,
            expected_path,
        )

        dRG = pymel.core.PyNode("defaultRenderGlobals")

        self.assertEqual(
            expected_path,
            dRG.getAttr("imageFilePrefix")
        )

    def test_save_as_sets_the_render_file_name_for_Shots(self):
        """testing if the save_as sets the render file name correctly
        """
        version1 = Version(task=self.task6)
        version1.extension = '.ma'
        version1.update_paths()

        self.maya_env.save_as(version1)

        # check if the path equals to
        expected_path = \
            '../../Outputs/<RenderLayer>/' \
            '%(project_code)s_%(version_nice_name)s_v%(version_number)s' \
            '_<RenderLayer>_<RenderPass>' % {
                'project_code': version1.task.project.code,
                'version_nice_name': version1.nice_name,
                'version_number': ('%s' % version1.version_number).zfill(3)
            }

        image_path = os.path.join(
            pymel.core.workspace.path,
            pymel.core.workspace.fileRules['image']
        ).replace("\\", "/")

        expected_path = utils.relpath(
            image_path,
            expected_path,
        )

        dRG = pymel.core.PyNode("defaultRenderGlobals")

        print expected_path
        print dRG.getAttr("imageFilePrefix")

        self.assertEqual(
            expected_path,
            dRG.getAttr("imageFilePrefix")
        )

    # def test_save_as_replaces_file_image_paths(self):
    #     """testing if save_as method replaces image paths with REPO relative
    #     path
    #     """
    #     self.maya_env.save_as(self.version1)
    # 
    #     # create file node
    #     file_node = pymel.core.createNode("file")
    # 
    #     # set it to a path in the workspace
    #     texture_path = os.path.join(
    #         pymel.core.workspace.path, ".maya_files/textures/test.jpg"
    #     )
    #     file_node.fileTextureName.set(texture_path)
    # 
    #     # save a newer version
    #     version2 = Version(**self.kwargs)
    #     version2.save()
    # 
    #     self.maya_env.save_as(version2)
    # 
    #     # now check if the file nodes fileTextureName is converted to a
    #     # relative path to the current workspace
    # 
    #     expected_path = texture_path.replace(os.environ["REPO"], "$REPO")
    # 
    #     self.assertEqual(
    #         file_node.getAttr("fileTextureName"),
    #         expected_path
    #     )

    def test_save_as_sets_the_resolution(self):
        """testing if save_as sets the render resolution for the current scene
        """
        version1 = Version(
            task=self.task1
        )
        version1.extension = '.ma'
        version1.update_paths()
        db.DBSession.add(version1)
        db.DBSession.commit()

        width = self.project.image_format.width
        height = self.project.image_format.height
        pixel_aspect = self.project.image_format.pixel_aspect

        # save the scene
        self.maya_env.save_as(version1)

        # check the resolutions
        dRes = pymel.core.PyNode("defaultResolution")
        self.assertEqual(dRes.width.get(), width)
        self.assertEqual(dRes.height.get(), height)
        self.assertEqual(dRes.pixelAspect.get(), pixel_aspect)

    def test_save_as_sets_the_resolution_only_for_first_version(self):
        """testing if save_as sets the render resolution for the current scene
        but only for the first version of the asset
        """
        version1 = Version(
            task=self.task1
        )
        version1.extension = '.ma'
        version1.update_paths()
        db.DBSession.add(version1)
        db.DBSession.commit()

        width = self.project.image_format.width
        height = self.project.image_format.height
        pixel_aspect = self.project.image_format.pixel_aspect

        # save the scene
        self.maya_env.save_as(version1)

        # check the resolutions
        dRes = pymel.core.PyNode("defaultResolution")
        self.assertEqual(dRes.width.get(), width)
        self.assertEqual(dRes.height.get(), height)
        self.assertEqual(dRes.pixelAspect.get(), pixel_aspect)

        new_width = 1280
        new_height = 720
        new_pixel_aspect = 1.0
        dRes.width.set(new_width)
        dRes.height.set(new_height)
        dRes.pixelAspect.set(new_pixel_aspect)

        # save the version again
        new_version = Version(
            task=self.task1
        )
        new_version.extension = '.ma'
        new_version.update_paths()
        db.DBSession.add(new_version)
        db.DBSession.commit()

        self.maya_env.save_as(new_version)

        # test if the resolution is not changed
        self.assertEqual(dRes.width.get(), new_width)
        self.assertEqual(dRes.height.get(), new_height)
        self.assertEqual(dRes.pixelAspect.get(), new_pixel_aspect)

    def test_save_as_fills_the_referenced_versions_list(self):
        """testing if the save_as method updates the Version.inputs list with
        the current references list from the Maya
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        versionBase = Version(task=self.task6)
        db.DBSession.add(versionBase)
        db.DBSession.commit()

        # change the take name
        version1 = Version(
            task=self.task6,
            take_name="Take1"
        )
        db.DBSession.add(version1)
        db.DBSession.commit()

        version2 = Version(
            task=self.task6,
            take_name="Take2"
        )
        db.DBSession.add(version2)
        db.DBSession.commit()

        version3 = Version(
            task=self.task6,
            take_name="Take3"
        )
        db.DBSession.add(version3)
        db.DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version

        # create a new scene
        pymel.core.newFile(force=True)

        # check if the versionBase.inputs is an empty list
        self.assertTrue(versionBase.inputs == [])

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # save it as versionBase
        self.maya_env.save_as(versionBase)

        # now check if versionBase.references is updated
        self.assertTrue(len(versionBase.inputs) == 2)

        self.assertItemsEqual(versionBase.inputs, [version1, version2])

    def test_save_as_of_a_scene_with_two_references_to_the_same_version(self):
        """testing if the case where the current maya scene has two references
        to the same file is gracefully handled by assigning the version only
        once
        """
        # create a version for an asset
        vers1 = Version(task=self.asset1)

        # save it
        self.maya_env.save_as(vers1)

        # new scene
        pymel.core.newFile(force=True)

        # create another version with different type
        vers2 = Version(task=self.asset1)

        # reference the other version twice
        self.maya_env.reference(vers1)
        self.maya_env.reference(vers1)

        # save it and expect no InvalidRequestError
        self.maya_env.save_as(vers2)

        # reference again
        self.maya_env.reference(vers1)

        # save as another version
        vers3 = Version(task=self.asset1)
        self.maya_env.save_as(vers3)

    def test_save_as_move_external_files_to_project_folder(self):
        """testing if save_as will move all the external files to project
        folder under the "external_files" folder
        """
        # create a texture file with local path
        new_texture_file = pymel.core.nt.File()
        # generate a local path
        local_file_full_path = os.path.join(
            tempfile.gettempdir(),
            "temp.png"
        )
        # touch the file
        with open(local_file_full_path, 'w'):
            pass

        self.remove_these_files_buffer.append(local_file_full_path)
        new_texture_file.fileTextureName.set(local_file_full_path)

        # now save it as a new version
        version1 = Version(task=self.task1)
        db.DBSession.add(version1)
        db.DBSession.commit()

        self.maya_env.save_as(version1)

        # and expect the fileTexture has been moved to workspace/external_files
        # folder
        expected_path =\
            os.path.join(version1.absolute_path, 'external_files', 'Textures',
                         'temp.png')

        self.assertEqual(
            expected_path,
            new_texture_file.fileTextureName.get()
        )

    def test_open_updates_the_referenced_versions_list(self):
        """testing if the open method updates the Version.inputs list with the
        current references list from the Maya
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        versionBase = Version(task=self.task1)
        db.DBSession.add(versionBase)
        db.DBSession.commit()

        # change the take name
        version1 = Version(task=self.task1, take_name="Take1")
        db.DBSession.add(version1)
        db.DBSession.commit()

        version2 = Version(task=self.task1, take_name="Take2")
        db.DBSession.add(version2)
        db.DBSession.commit()

        version3 = Version(task=self.task1, take_name="Take3")
        db.DBSession.add(version2)
        db.DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version

        # create a new scene
        pymel.core.newFile(force=True)

        # check if the versionBase.references is an empty list
        self.assertEqual([], versionBase.inputs)

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # save it as versionBase
        self.maya_env.save_as(versionBase)

        # now check if versionBase.inputs is updated
        # this part is already tested in save_as
        self.assertEqual(2, len(versionBase.inputs))
        self.assertItemsEqual(versionBase.inputs, [version1, version2])

        # now remove references
        for ref_node in pymel.core.listReferences():
            ref_node.remove()

        # do a save (not save_as)
        pymel.core.saveFile()

        # clean scene
        pymel.core.newFile(force=True)

        # open the same version
        self.maya_env.open(versionBase, force=True)

        # and check the references is updated
        self.assertEqual(0, len(versionBase.inputs))
        self.assertEqual(versionBase.inputs, [])

    def test_open_does_not_load_unloaded_references(self):
        """testing if the open method doesn't load unloaded references
        """
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        version_base = Version(task=self.task1)
        db.DBSession.add(version_base)
        db.DBSession.commit()

        # change the take name
        version1 = Version(task=self.task1, take_name="Take1")
        db.DBSession.add(version1)
        db.DBSession.commit()

        version2 = Version(task=self.task1, take_name="Take2")
        db.DBSession.add(version2)
        db.DBSession.commit()

        version3 = Version(task=self.task1, take_name="Take3")
        db.DBSession.add(version3)
        db.DBSession.commit()

        # now create scenes with these files
        self.maya_env.save_as(version1)
        self.maya_env.save_as(version2)
        self.maya_env.save_as(version3)  # this is the dummy version

        # create a new scene
        pymel.core.newFile(force=True)

        # reference the given versions
        self.maya_env.reference(version1)
        self.maya_env.reference(version2)

        # unload a couple of them
        refs = pymel.core.listReferences()
        refs[0].unload()
        print refs[0].path
        print refs[1].path
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # save it as versionBase
        self.maya_env.save_as(version_base)
        self.assertFalse(refs[0].isLoaded())
        self.assertTrue(refs[1].isLoaded())

        # clean scene
        pymel.core.newFile(force=True)

        # re-open the file
        self.maya_env.open(version_base, force=True)

        # check if the references are loaded
        refs = pymel.core.listReferences()
        self.assertTrue(refs[1].isLoaded())
        self.assertFalse(refs[0].isLoaded())

    def test_save_as_in_another_project_updates_paths_correctly(self):
        """testing if the external paths are updated correctly if the document
        is created in one maya project but it is saved under another one.
        """
        # create a new scene
        # save it under one Asset Version with name Asset1

        asset1 = Asset(
            name='Asset1',
            code='Ass1',
            type=self.character_type,
            project=self.project
        )
        db.DBSession.add(asset1)
        db.DBSession.commit()

        version1 = Version(task=asset1)
        db.DBSession.add(version1)
        db.DBSession.commit()

        version_ref1 = Version(
            task=asset1,
            take_name="References1"
        )
        db.DBSession.add(version_ref1)
        db.DBSession.commit()

        version_ref2 = Version(
            task=asset1,
            take_name="References2"
        )
        db.DBSession.add(version_ref2)
        db.DBSession.commit()

        # save a maya file with this references
        pymel.core.newFile(f=True)
        self.maya_env.save_as(version_ref1)
        self.maya_env.save_as(version_ref2)

        # save the original version
        self.maya_env.save_as(version1)

        # create a couple of file textures
        file_texture1 = pymel.core.createNode("file")
        file_texture2 = pymel.core.createNode("file")

        path1 = os.path.join(
            version1.absolute_path, ".maya_files/TEXTURES/a.jpg"
        )
        path2 = os.path.join(
            version1.absolute_path, ".maya_files/TEXTURES/b.jpg"
        )

        # set them to some relative paths
        file_texture1.fileTextureName.set(path1)
        file_texture2.fileTextureName.set(path2)

        # create a couple of references in the same project
        self.maya_env.reference(version_ref1)
        self.maya_env.reference(version_ref2)

        # save again
        self.maya_env.save_as(version1)

        # then save it under another Asset with name Asset2
        # because with this new system all the Assets folders are a maya
        # project, the references should be updated correctly
        asset2 = Asset(
            name='Asset2',
            code='Ass2',
            type=self.character_type,
            project=self.project
        )
        db.DBSession.add(asset2)
        db.DBSession.commit()

        # create a new Version for Asset 2
        version2 = Version(task=asset2)

        # now save it under that asset
        self.maya_env.save_as(version2)

        # check the file paths they should stay intact
        # because they are already under the repository so no need to change
        # the path
        self.assertEqual(file_texture1.fileTextureName.get(), path1)
        self.assertEqual(file_texture2.fileTextureName.get(), path2)

    def test_save_as_sets_the_fps(self):
        """testing if the save_as method sets the fps value correctly
        """
        # create two projects with different fps values
        # first create a new scene and save it under the first project
        # and then save it under the other project
        # and check if the fps follows the project values

        project1 = Project(
            name="FPS Test Project 1",
            code='FTP1',
            status_list=self.project_status_list,
            structure=self.structure,
            repository=self.repo1,
            fps=24,
            image_format=self.image_format
        )
        db.DBSession.add(project1)

        project2 = Project(
            name="FPS Test Project 2",
            code='FTP2',
            status_list=self.project_status_list,
            structure=self.structure,
            repository=self.repo1,
            fps=30,
            image_format=self.image_format
        )
        db.DBSession.add(project2)

        # create assets
        asset1 = Asset(
            name="Test Asset 1",
            code='TA1',
            project=project1,
            type=self.character_type
        )
        db.DBSession.add(asset1)

        asset2 = Asset(
            name="Test Asset 2",
            code='TA2',
            project=project2,
            type=self.character_type
        )
        db.DBSession.add(asset2)
        db.DBSession.commit()

        # create versions
        version1 = Version(
            task=asset1,
            created_by=self.user1
        )
        db.DBSession.add(version1)
        db.DBSession.commit()

        version2 = Version(
            task=asset2,
            created_by=self.user1
        )
        db.DBSession.add(version2)
        db.DBSession.commit()

        # save the current scene for asset1
        self.maya_env.save_as(version1)

        # check the fps value
        self.assertEqual(
            self.maya_env.get_fps(),
            24
        )

        # now save it for asset2
        self.maya_env.save_as(version2)

        # check the fps value
        self.assertEqual(
            self.maya_env.get_fps(),
            30
        )

    def test_reference_creates_references_with_absolute_paths(self):
        """testing if reference method creates references with unresolved paths
        are absolute paths
        """
        vers1 = Version(task=self.asset1, created_by=self.user1)
        db.DBSession.add(vers1)
        db.DBSession.commit()

        vers2 = Version(task=self.asset1, created_by=self.user1)
        db.DBSession.add(vers2)
        db.DBSession.commit()

        self.maya_env.save_as(vers1)

        pymel.core.newFile(force=True)
        self.maya_env.save_as(vers2)

        # reference vers1 to vers2
        self.maya_env.reference(vers1)

        # now check if the referenced files unresolved path is equal to
        # ver2.absolute_full_path
        refs = pymel.core.listReferences()

        # there should be only one reference
        self.assertEqual(len(refs), 1)

        # the unresolved path should be an absolute path
        self.assertEqual(
            vers1.absolute_full_path,
            refs[0].unresolvedPath()
        )

        self.assertTrue(refs[0].isLoaded())

    # def test_save_as_replaces_imagePlane_filename_with_env_variable(self):
    #     """testing if save_as replaces the imagePlane filename with repository
    #     environment variable
    #     """
    #     # create a camera
    #     # create an image plane
    #     # set it to something
    #     # save the scene
    #     # check if the path is replaced with repository environment variable
    # 
    #     self.fail("test is not implemented yet")

    def test_save_as_creates_the_workspace_mel_file_in_the_given_path(self):
        """testing if save_as creates the workspace.mel file in the Asset or
        Shot root
        """
        task6 = Task(
            name='Test Task 6 - New',
            parent=self.task1
        )
        db.DBSession.add(task6)
        db.DBSession.commit()

        version1 = Version(task=task6)
        version1.extension = '.ma'
        version1.update_paths()

        # check if the workspace.mel file does not exist yet
        workspace_mel_full_path = os.path.join(
            version1.absolute_path,
            'workspace.mel'
        )
        self.assertFalse(os.path.exists(workspace_mel_full_path))
        self.maya_env.save_as(version1)
        self.assertTrue(os.path.exists(workspace_mel_full_path))

    def test_save_as_creates_the_workspace_fileRule_folders(self):
        """testing if save_as creates the fileRule folders
        """
        task6 = Task(
            name='Test Task 6 - New',
            parent=self.task1
        )
        db.DBSession.add(task6)
        db.DBSession.commit()

        version1 = Version(task=task6)
        version1.extension = '.ma'
        version1.update_paths()

        # first prove that the folders doesn't exist
        for key in pymel.core.workspace.fileRules.keys():
            file_rule_partial_path = pymel.core.workspace.fileRules[key]
            file_rule_full_path = os.path.join(
                version1.absolute_path,
                file_rule_partial_path
            )
            self.assertFalse(os.path.exists(file_rule_full_path))

        self.maya_env.save_as(version1)

        # save_as and now expect the folders to be created
        for key in pymel.core.workspace.fileRules.keys():
            file_rule_partial_path = pymel.core.workspace.fileRules[key]
            file_rule_full_path = os.path.join(
                version1.absolute_path,
                file_rule_partial_path
            )
            print file_rule_full_path
            self.assertTrue(os.path.exists(file_rule_full_path))

    def test_is_in_repo_working_properly(self):
        """testing if Maya.is_in_repo() is working properly
        """
        repo_path = self.repo1.path

        self.assertTrue(
            self.maya_env.is_in_repo(repo_path)
        )
        self.assertTrue(
            self.maya_env.is_in_repo(
                os.path.join(repo_path, 'a.txt')
            )
        )
        self.assertFalse(
            self.maya_env.is_in_repo(
                os.path.normpath(
                    os.path.join(repo_path, '../a.txt')
                )
            )
        )

    def test_move_to_local_is_working_properly(self):
        """testing if Maya.move_to_local is working properly
        """
        # create a couple of files in some other directories than repo
        another_tmp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(another_tmp_dir, 'test.png')

        with open(temp_file_path, 'w'):
            pass

        # add the file to be cleaned up list
        self.remove_these_files_buffer.append(temp_file_path)
        self.remove_these_files_buffer.append(another_tmp_dir)

        # now create a version and move the file to the local path of this
        # version
        version = Version(task=self.task1)
        version.extension = '.ma'
        version.update_paths()
        db.DBSession.add(version)
        db.DBSession.commit()

        new_path =\
            self.maya_env.move_to_local(version, temp_file_path, 'Textures')
        self.remove_these_files_buffer.append(new_path)

        # check if the file is there
        self.assertTrue(
            os.path.exists(new_path)
        )

    def test_update_first_level_versions_does_not_update_namespaces(self):
        """testing if update_first_level_versions method does not updates
        namespaces
        """
        vers1 = Version(task=self.asset1, created_by=self.user1)
        db.DBSession.add(vers1)
        db.DBSession.commit()

        vers2 = Version(task=self.asset1, created_by=self.user1, take_name='A')
        vers2.is_published = True
        db.DBSession.add(vers2)
        db.DBSession.commit()

        vers3 = Version(task=self.asset1, created_by=self.user1, take_name='A')
        vers3.is_published = True
        db.DBSession.add(vers3)
        db.DBSession.commit()

        pymel.core.newFile(force=True)
        self.maya_env.save_as(vers2)

        pymel.core.newFile(force=True)
        self.maya_env.save_as(vers3)

        self.maya_env.save_as(vers1)

        # reference vers2 to vers1
        self.maya_env.reference(vers2)

        # now check if the referenced files unresolved path is equal to
        # ver2.absolute_full_path
        refs = pymel.core.listReferences()

        # there should be only one reference
        self.assertEqual(len(refs), 1)

        # the unresolved path should be an absolute path
        self.assertEqual(
            vers2.absolute_full_path,
            refs[0].unresolvedPath()
        )

        self.assertTrue(refs[0].isLoaded())

        # update version to latest published version
        reference_resolution = {
            'root': [vers2],
            'create': [vers1],
            'update': [vers2],
            'leave': []
        }
        self.maya_env.update_first_level_versions(reference_resolution)

        # now check if the reference is updated and the namespace is set
        # correctly
        refs = pymel.core.listReferences()
        self.assertEqual(
            vers3.absolute_full_path,
            refs[0].unresolvedPath()
        )
        self.assertEqual(
            refs[0].namespace,
            vers2.nice_name
        )


class MayaReferenceUpdateTestCase(MayaTestBase):
    """tests the maya.Maya reference updates
    """

    def test_update_versions_is_working_properly_case_1(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version12
          version5
            version2 -> has new published version (version3)

        Expected Result:

        version12 (no new version based on version12)
          version5 (no new version based on version5)
            version2 (do not update version2)
        """
        # create a deep relation
        self.version2.is_published = True

        # new scene
        # version5 references version2
        self.maya_env.open(self.version5)
        self.maya_env.reference(self.version2)
        pymel.core.saveFile()
        self.version5.is_published = True
        pymel.core.newFile(force=True)

        # version12 references version5
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version5)
        pymel.core.saveFile()
        self.version12.is_published = True
        pymel.core.newFile(force=True)

        # version3 set published
        self.version3.is_published = True

        print "version2  : %s" % self.version2
        print "version3  : %s" % self.version3
        print "version5  : %s" % self.version5
        print "version12 : %s" % self.version12

        # check the setup
        visited_versions = []
        for v in walk_version_hierarchy(self.version12):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version12, self.version5, self.version2]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        reference_resolution = self.maya_env.open(self.version12)
        updated_versions = \
            self.maya_env.update_versions(reference_resolution)

        print 'updated_versions: %s' % updated_versions

        # we should be still in version12 scene
        self.assertEqual(
            self.version12,
            self.maya_env.get_current_version()
        )

        # check references
        # we shouldn't have a new version5 referenced
        refs = pymel.core.listReferences()
        self.assertEqual(
            self.version5,
            self.maya_env.get_version_from_full_path(refs[0].path)
        )

        # and it should still have referencing version2
        refs = pymel.core.listReferences(refs[0])
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(refs[0].path)
        )

    def test_update_versions_is_working_properly_case_2(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version6 -> new version of version5 is already referencing version6
          version3 (so version6 is already using version3 and both are
                    published)

        version12
          version5 -> has new published version (version6)
            version2 -> has new published version (version3)

        Expected Final Result
        version12
          version6 -> 1st level reference is updated correctly
            version3
        """
        # create a deep relation
        self.version2.is_published = True

        # new scene
        # version5 references version2
        self.maya_env.open(self.version5)
        self.maya_env.reference(self.version2)
        pymel.core.saveFile()
        self.version5.is_published = True
        pymel.core.newFile(force=True)

        # version6 references version3
        self.maya_env.open(self.version6)
        self.maya_env.reference(self.version3)
        pymel.core.saveFile()
        self.version6.is_published = True
        pymel.core.newFile(force=True)

        # version12 references version5
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version5)
        pymel.core.saveFile()
        self.version12.is_published = True
        pymel.core.newFile(force=True)

        # version3 set published
        self.version3.is_published = True
        self.version6.is_published = True

        print "version2  : %s" % self.version2
        print "version3  : %s" % self.version3
        print "version5  : %s" % self.version5
        print "version6  : %s" % self.version6
        print "version12 : %s" % self.version12

        # check the setup
        visited_versions = []
        for v in walk_version_hierarchy(self.version12):
            visited_versions.append(v)

        expected_visited_versions = \
            [self.version12, self.version5, self.version2]

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        reference_resolution = self.maya_env.open(self.version12)
        created_versions = \
            self.maya_env.update_versions(reference_resolution)

        print 'created_versions: %s' % created_versions

        # no new versions should have been created
        self.assertEqual(0, len(created_versions))

        # check if we are still in version12 scene
        self.assertEqual(
            self.version12,
            self.maya_env.get_current_version()
        )

        # and expect maya have the updated references
        refs = pymel.core.listReferences()
        self.assertEqual(
            self.version6,
            self.maya_env.get_version_from_full_path(refs[0].path)
        )

        # and it should have referenced version3
        refs = pymel.core.listReferences(refs[0])
        self.assertEqual(
            self.version3,
            self.maya_env.get_version_from_full_path(refs[0].path)
        )

    def test_update_versions_is_working_properly_case_3(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version15
          version12
            version5
              version2 -> has new published version (version3)
          version12 -> referenced a second time
            version5
              version2 -> has new published version (version3)

        Expected Final Result
        version15
          version12
            version5
              version2 -> it is not a 1st level reference, nothing is updated
          version12
            version5
              version2 -> nothing is updated
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # new scene
        # version5 references version2
        self.maya_env.open(self.version5)
        self.maya_env.reference(self.version2)
        pymel.core.saveFile()
        self.version5.is_published = True
        pymel.core.newFile(force=True)

        # version12 references version5
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version5)
        pymel.core.saveFile()
        self.version12.is_published = True
        pymel.core.newFile(force=True)

        # version15 references version12 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version12)
        self.maya_env.reference(self.version12)
        pymel.core.saveFile()
        pymel.core.newFile(force=True)

        print "version2  : %s" % self.version2
        print "version5  : %s" % self.version5
        print "version12 : %s" % self.version12
        print "version15 : %s" % self.version15

        # check the setup
        visited_versions = []
        for v in walk_version_hierarchy(self.version15):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version12, self.version5, self.version2]

        print expected_visited_versions
        print visited_versions

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )
        reference_resolution = self.maya_env.open(self.version15)

        # check reference resolution
        self.assertItemsEqual(
            reference_resolution['root'],
            [self.version12]
        )
        self.assertItemsEqual(
            reference_resolution['create'],
            [self.version5, self.version12]
        )
        self.assertItemsEqual(
            reference_resolution['update'],
            [self.version2]
        )
        self.assertItemsEqual(
            reference_resolution['leave'],
            []
        )

        updated_versions = \
            self.maya_env.update_versions(reference_resolution)

        print 'updated_versions: %s' % updated_versions
        self.assertEqual(0, len(updated_versions))

        # check if we are still in version15 scene
        self.assertEqual(
            self.version15,
            self.maya_env.get_current_version()
        )

        # and expect maya have the updated references
        refs_level1 = pymel.core.listReferences()
        self.assertEqual(
            self.version12,
            self.maya_env.get_version_from_full_path(refs_level1[0].path)
        )
        self.assertEqual(
            self.version12,
            self.maya_env.get_version_from_full_path(refs_level1[1].path)
        )

        # and it should have referenced version5A
        refs_level2 = pymel.core.listReferences(refs_level1[0])
        self.assertEqual(
            self.version5,
            self.maya_env.get_version_from_full_path(refs_level2[0].path)
        )

        # and it should have referenced version5A
        refs_level3 = pymel.core.listReferences(refs_level2[0])
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(refs_level3[0].path)
        )

        # the other version5A
        refs_level2 = pymel.core.listReferences(refs_level1[1])
        self.assertEqual(
            self.version5,
            self.maya_env.get_version_from_full_path(refs_level2[0].path)
        )

        # and it should have referenced version5A
        refs_level3 = pymel.core.listReferences(refs_level2[0])
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(refs_level3[0].path)
        )

    def test_update_versions_is_working_properly_case_4(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version15
          version12
            version5
              version2 -> has new published version (version3)
            version5 -> Referenced a second time
              version2 -> has new published version (version3)
          version12 -> Referenced a second time
            version5
              version2 -> has new published version (version3)
            version5
              version2 -> has new published version (version3)

        Expected Final Result
        version15
          version12
            version5
              version2 -> nothing is updated
            version5
              version2 -> nothing is updated
          version12
            version5
              version2 -> nothing is updated
            version5
              version2 -> nothing is updated
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # new scene
        # version5 references version2
        self.maya_env.open(self.version5)
        self.maya_env.reference(self.version2)
        pymel.core.saveFile()
        self.version5.is_published = True
        pymel.core.newFile(force=True)

        # version12 references version5
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version5)
        self.maya_env.reference(self.version5)  # reference a second time
        pymel.core.saveFile()
        self.version12.is_published = True
        pymel.core.newFile(force=True)

        # version15 references version12 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version12)
        self.maya_env.reference(self.version12)
        pymel.core.saveFile()
        pymel.core.newFile(force=True)

        print "version2  : %s" % self.version2
        print "version5  : %s" % self.version5
        print "version12 : %s" % self.version12
        print "version15 : %s" % self.version15

        # check the setup
        visited_versions = []
        for v in walk_version_hierarchy(self.version15):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version12, self.version5, self.version2]

        print expected_visited_versions
        print visited_versions

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        reference_resolution = self.maya_env.open(self.version15)
        updated_versions = \
            self.maya_env.update_versions(reference_resolution)

        print 'updated_versions: %s' % updated_versions

        self.assertEqual(0, len(updated_versions))

        # check if we are still in version15 scene
        self.assertEqual(
            self.version15,
            self.maya_env.get_current_version()
        )

        # and expect maya have the updated references
        refs = pymel.core.listReferences()
        version12_ref1 = refs[0]
        version12_ref2 = refs[1]

        refs = pymel.core.listReferences(version12_ref1)
        version5_ref1 = refs[0]
        version5_ref2 = refs[1]

        refs = pymel.core.listReferences(version12_ref2)
        version5_ref3 = refs[0]
        version5_ref4 = refs[1]

        version2_ref1 = pymel.core.listReferences(version5_ref1)[0]
        version2_ref2 = pymel.core.listReferences(version5_ref2)[0]
        version2_ref3 = pymel.core.listReferences(version5_ref3)[0]
        version2_ref4 = pymel.core.listReferences(version5_ref4)[0]

        # Version12
        published_version = self.version12
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version12_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version12_ref2.path)
        )

        # Version5
        published_version = self.version5
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version5_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version5_ref2.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version5_ref3.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version5_ref4.path)
        )

        # Version2
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(version2_ref1.path)
        )
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(version2_ref2.path)
        )
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(version2_ref3.path)
        )
        self.assertEqual(
            self.version2,
            self.maya_env.get_version_from_full_path(version2_ref4.path)
        )

    def test_update_versions_is_working_properly_case_5(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version15
          version11 -> has a new version already using version6 (version12)
            version4 -> has a new published version (version6) using version3
              version2 -> has new published version (version3)
            version4 -> Referenced a second time
              version2 -> has new published version (version3)
          version11 -> Referenced a second time
            version4
              version2
            version4
              version2

        Expected Final Result (generates only one new version)
        version15 -> no new version based on version15
          version12
            version6
              version3
            version6
              version3
          version12
            version6
              version3
            version6
              version3
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # version4 references version2
        self.maya_env.open(self.version4)
        self.maya_env.reference(self.version2)
        pymel.core.saveFile()
        self.version4.is_published = True
        pymel.core.newFile(force=True)

        # version6 references version3
        self.maya_env.open(self.version6)
        self.maya_env.reference(self.version3)
        pymel.core.saveFile()
        self.version6.is_published = True
        pymel.core.newFile(force=True)

        # version11 references version5
        self.maya_env.open(self.version11)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)  # reference a second time
        pymel.core.saveFile()
        self.version11.is_published = True
        pymel.core.newFile(force=True)

        # version12 references version6
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version6)
        self.maya_env.reference(self.version6)  # reference a second time
        pymel.core.saveFile()
        self.version12.is_published = True
        pymel.core.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)
        self.maya_env.reference(self.version11)
        pymel.core.saveFile()
        pymel.core.newFile(force=True)

        print "version2  : %s" % self.version2
        print "version3  : %s" % self.version3
        print "version4  : %s" % self.version4
        print "version5  : %s" % self.version5
        print "version6  : %s" % self.version6
        print "version11 : %s" % self.version11
        print "version12 : %s" % self.version12
        print "version15 : %s" % self.version15

        # check the setup
        visited_versions = []
        for v in walk_version_hierarchy(self.version15):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version11, self.version4, self.version2]

        print expected_visited_versions
        print visited_versions

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        reference_resolution = self.maya_env.open(self.version15)
        updated_versions = \
            self.maya_env.update_versions(reference_resolution)

        print 'updated_versions: %s' % updated_versions
        self.assertEqual(0, len(updated_versions))

        # check if we are still in version15 scene
        self.assertEqual(
            self.version15,
            self.maya_env.get_current_version()
        )

        # and expect maya have the updated references
        refs = pymel.core.listReferences()
        version12_ref1 = refs[0]
        version12_ref2 = refs[1]

        refs = pymel.core.listReferences(version12_ref1)
        version6_ref1 = refs[0]
        version6_ref2 = refs[1]

        refs = pymel.core.listReferences(version12_ref2)
        version6_ref3 = refs[0]
        version6_ref4 = refs[1]

        version3_ref1 = pymel.core.listReferences(version6_ref1)[0]
        version3_ref2 = pymel.core.listReferences(version6_ref2)[0]
        version3_ref3 = pymel.core.listReferences(version6_ref3)[0]
        version3_ref4 = pymel.core.listReferences(version6_ref4)[0]

        # Version12
        published_version = self.version12.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version12_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version12_ref2.path)
        )

        # Version5
        published_version = self.version5.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref2.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref3.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref4.path)
        )

        # Version2
        published_version = self.version2.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref2.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref3.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref4.path)
        )

    def test_update_versions_is_working_properly_case_6(self):
        """testing if update_versions is working properly in following
        condition:

        Start Condition:

        version15
          version11 -> has a new version already using version6 (version12)
            version4 -> has a new published version (version6) using version3
              version2 -> has new published version (version3)
            version4 -> Referenced a second time
              version3 -> shallow updated before (let see what happens)

        Expected Final Result (generates only one new version)
        version15
          version12
            version6
              version3
            version6
              version3
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # version4 references version2
        self.maya_env.open(self.version4)
        self.maya_env.reference(self.version2)
        pymel.core.saveFile()
        self.version4.is_published = True
        pymel.core.newFile(force=True)

        # version6 references version3
        self.maya_env.open(self.version6)
        self.maya_env.reference(self.version3)
        pymel.core.saveFile()
        self.version6.is_published = True
        pymel.core.newFile(force=True)

        # version11 references version5
        self.maya_env.open(self.version11)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)  # reference a second time
        pymel.core.saveFile()
        self.version11.is_published = True
        pymel.core.newFile(force=True)

        # version12 references version6
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version6)
        self.maya_env.reference(self.version6)  # reference a second time
        pymel.core.saveFile()
        self.version12.is_published = True
        pymel.core.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)

        # now simulate a shallow update on version2 -> version3 while under
        # in version4
        refs = pymel.core.listReferences(recursive=1)
        # we should have all the references
        print refs
        self.assertEqual(self.version2.absolute_full_path, refs[-1].path)
        refs[-1].replaceWith(self.version3.absolute_full_path)

        pymel.core.saveFile()
        pymel.core.newFile(force=True)

        print "version2  : %s" % self.version2
        print "version3  : %s" % self.version3
        print "version4  : %s" % self.version4
        print "version5  : %s" % self.version5
        print "version6  : %s" % self.version6
        print "version11 : %s" % self.version11
        print "version12 : %s" % self.version12
        print "version15 : %s" % self.version15

        # check the setup
        visited_versions = []
        for v in walk_version_hierarchy(self.version15):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version11, self.version4, self.version2]

        print expected_visited_versions
        print visited_versions

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        reference_resolution = self.maya_env.open(self.version15)
        updated_versions = \
            self.maya_env.update_versions(reference_resolution)

        print 'updated_versions: %s' % updated_versions
        self.assertEqual(0, len(updated_versions))

        # check if we are still in version15 scene
        self.assertEqual(
            self.version15,
            self.maya_env.get_current_version()
        )

        # and expect maya have the updated references
        refs = pymel.core.listReferences()
        version12_ref1 = refs[0]

        refs = pymel.core.listReferences(version12_ref1)
        version6_ref1 = refs[0]
        version6_ref2 = refs[1]

        version3_ref1 = pymel.core.listReferences(version6_ref1)[0]
        version3_ref2 = pymel.core.listReferences(version6_ref2)[0]

        # Version12
        published_version = self.version12.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version12_ref1.path)
        )

        # Version5
        published_version = self.version5.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version6_ref2.path)
        )

        # Version2
        published_version = self.version2.latest_published_version
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref1.path)
        )
        self.assertEqual(
            published_version,
            self.maya_env.get_version_from_full_path(version3_ref2.path)
        )

    def test_reference_updates_version_inputs_attribute(self):
        """testing if Maya.reference updates Version.inputs attribute
        """
        # create references to various versions
        self.maya_env.open(self.version6)

        self.maya_env.reference(self.version5)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version3)

        # at this point we should have self.version6.inputs filled correctly
        self.assertItemsEqual(
            [self.version5, self.version4, self.version3],
            self.version6.inputs
        )

    def test_get_referenced_versions_returns_a_list_of_Version_instances(self):
        """testing if Maya.get_referenced_versions returns a list of Versions
        instances referenced in the current scene
        """
        # create references to various versions
        self.maya_env.open(self.version6)

        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version5)
        self.maya_env.reference(self.version5)  # duplicate refs
        self.maya_env.reference(self.version4)  # duplicate refs
        self.maya_env.reference(self.version3)

        # now try to get the referenced versions
        referenced_versions = self.maya_env.get_referenced_versions()

        self.assertItemsEqual(
            referenced_versions,
            [self.version3, self.version4, self.version5]
        )

    def test_get_referenced_versions_returns_a_list_of_Version_instances_referenced_under_the_given_reference(self):
        """testing if Maya.get_referenced_versions returns a list of Versions
        referenced in the current scene under the given reference
        """
        # create references to various versions
        self.maya_env.open(self.version6)

        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version5)
        self.maya_env.reference(self.version5)  # duplicate refs
        self.maya_env.reference(self.version4)  # duplicate refs
        self.maya_env.reference(self.version3)

        # save the scene and start
        pymel.core.saveFile()

        # open version7 and reference version6 to it
        self.maya_env.open(self.version7)
        self.maya_env.reference(self.version6)

        # now try to get the referenced versions
        versions = self.maya_env.get_referenced_versions()

        self.assertItemsEqual(versions, [self.version6])

        # and get a deeper one
        versions = \
            self.maya_env.get_referenced_versions(
                pymel.core.listReferences()[0]
            )

        self.assertItemsEqual(
            versions,
            [self.version3, self.version4, self.version5]
        )

    def test_update_version_inputs_method_updates_the_inputs_of_the_open_version(self):
        """testing if Maya.update_version_inputs() returns updates the inputs
        attribute of the current open version by looking to the referenced
        versions
        """
        # do not use maya_env to open and reference files
        # create references to various versions
        def open_(version):
            new_workspace = version.absolute_path
            pymel.core.workspace.open(new_workspace)
            pymel.core.openFile(version.absolute_full_path, f=True,)

        # create references
        def reference(version):
            namespace = os.path.basename(version.filename)
            namespace = namespace.replace('.', '_')
            ref = pymel.core.createReference(
                version.absolute_full_path,
                gl=True,
                namespace=namespace,
                options='v=0'
            )

        open_(self.version6)
        reference(self.version4)
        reference(self.version5)
        reference(self.version5)  # duplicate refs
        reference(self.version4)  # duplicate refs
        reference(self.version3)

        # save the scene and start
        pymel.core.saveFile()

        # the version6.inputs should be an empty list
        self.assertEqual(self.version6.inputs, [])

        # open version7 and reference version6 to it
        open_(self.version7)
        reference(self.version6)

        # version7.inputs should be an empty list
        self.assertEqual(self.version7.inputs, [])

        # now try to update referenced versions
        self.maya_env.update_version_inputs()

        self.assertItemsEqual(
            [self.version6],
            self.version7.inputs
        )

        # now get the version6.inputs right
        refs = pymel.core.listReferences()
        self.maya_env.update_version_inputs(refs[0])

        self.assertItemsEqual(
            [self.version3, self.version4, self.version5],
            self.version6.inputs
        )

    def test_reference_method_updates_the_inputs_of_the_referenced_version(self):
        """testing if Maya.reference() method updates the Version.inputs of the
        referenced version
        """
        # create a new version
        self.maya_env.open(self.version6)

        # check prior to referencing
        self.assertTrue(self.version5 not in self.version6.inputs)

        # reference something and let Maya to update the inputs
        self.maya_env.reference(self.version5)

        # check if version5 is in version6.inputs
        self.assertTrue(self.version5 in self.version6.inputs)

        # remove the reference and save the file (do not saveAs)
        pymel.core.listReferences()[0].remove()

        # save the file over itself
        pymel.core.saveFile()

        # check if version5 still in version6.inputs
        self.assertTrue(self.version5 in self.version6.inputs)

        # create a new scene and reference the previous version and check if
        pymel.core.newFile(f=True)
        self.maya_env.reference(self.version6)

        # the Version.inputs is updated correctly
        self.assertTrue(self.version5 not in self.version6.inputs)

    def test_check_referenced_versions_is_working_properly(self):
        """testing if check_referenced_versions will return a list of tuples
        holding info like which ref needs to be updated or which reference
        needs a new version, what is the corresponding Version instance and
        what is the final action

        Start Condition:

        version15
          version11 -> has a new version already using version6 (version12)
            version4 -> has a new published version (version6) using version3
              version2 -> has new published version (version3)
            version4 -> Referenced a second time
              version2 -> has new published version (version3)
          version11 -> Referenced a second time
            version4
              version2
            version4
              version2
          version21
            version16 -> has a new published version version18
          version38 -> no update
            version27 -> no update

        Expected Final Result (generates only one new version)
        version15 -> same version of version15
          version12
            version6
              version3
            version6
              version3
          version12
            version6
              version3
            version6
              version3
          version21 -> same version of version21
            version18
          version38 -> no update
            version27 -> no update
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # version4 references version2
        self.maya_env.open(self.version4)
        self.maya_env.reference(self.version2)
        pymel.core.saveFile()
        self.version4.is_published = True
        pymel.core.newFile(force=True)

        # version6 references version3
        self.maya_env.open(self.version6)
        self.maya_env.reference(self.version3)
        pymel.core.saveFile()
        self.version6.is_published = True
        pymel.core.newFile(force=True)

        # version11 references version5
        self.maya_env.open(self.version11)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)  # reference a second time
        pymel.core.saveFile()
        self.version11.is_published = True
        pymel.core.newFile(force=True)

        # version12 references version6
        self.maya_env.open(self.version12)
        self.maya_env.reference(self.version6)
        self.maya_env.reference(self.version6)  # reference a second time
        pymel.core.saveFile()
        self.version12.is_published = True
        pymel.core.newFile(force=True)

        # version21 references version16
        self.maya_env.open(self.version21)
        self.maya_env.reference(self.version16)
        pymel.core.saveFile()
        self.version16.is_published = True
        self.version18.is_published = True
        self.version21.is_published = True
        pymel.core.newFile(force=True)

        # version38 references version27
        self.maya_env.open(self.version38)
        self.maya_env.reference(self.version27)
        pymel.core.saveFile()
        self.version38.is_published = True
        self.version27.is_published = True
        pymel.core.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)
        self.maya_env.reference(self.version11)
        self.maya_env.reference(self.version21)
        self.maya_env.reference(self.version38)
        pymel.core.saveFile()
        #pymel.core.newFile(force=True)
        db.DBSession.commit()

        # check the setup
        visited_versions = []
        for v in walk_version_hierarchy(self.version15):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version11, self.version4, self.version2,
             self.version21, self.version16, self.version38, self.version27]

        print expected_visited_versions
        print visited_versions

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        root_refs = pymel.core.listReferences()

        version11_ref_1 = root_refs[0]
        version4_ref_1 = pymel.core.listReferences(version11_ref_1)[0]
        version2_ref_1 = pymel.core.listReferences(version4_ref_1)[0]
        version4_ref_2 = pymel.core.listReferences(version11_ref_1)[1]
        version2_ref_2 = pymel.core.listReferences(version4_ref_2)[0]

        version11_ref_2 = root_refs[1]
        version4_ref_3 = pymel.core.listReferences(version11_ref_2)[0]
        version2_ref_3 = pymel.core.listReferences(version4_ref_3)[0]
        version4_ref_4 = pymel.core.listReferences(version11_ref_2)[1]
        version2_ref_4 = pymel.core.listReferences(version4_ref_4)[0]

        version21_ref = root_refs[2]
        version16_ref = pymel.core.listReferences(version21_ref)[0]

        version38_ref = root_refs[3]
        version27_ref = pymel.core.listReferences(version38_ref)[0]

        self.assertFalse(self.version2.is_latest_published_version())

        expected_reference_resolution = {
            'root': [
                self.version38,
                self.version11,
                self.version21
            ],
            'leave': [
                self.version27,
                self.version38
            ],
            'update': [
                self.version16,
                self.version2,
                self.version4,
                self.version11
            ],
            'create': [
                self.version21
            ]
        }

        result = \
            self.maya_env.check_referenced_versions()

        print 'self.version27: %s' % self.version27
        print 'self.version38: %s' % self.version38
        print 'self.version16: %s' % self.version16
        print 'self.version21: %s' % self.version21
        print 'self.version2 : %s' % self.version2
        print 'self.version4 : %s' % self.version4
        print 'self.version11: %s' % self.version11
        print 'self.version15: %s' % self.version15

        print expected_reference_resolution
        print '--------------------------'
        print result

        self.assertItemsEqual(
            expected_reference_resolution['root'],
            result['root']
        )
        self.assertItemsEqual(
            expected_reference_resolution['leave'],
            result['leave']
        )
        self.assertItemsEqual(
            expected_reference_resolution['update'],
            result['update']
        )
        self.assertItemsEqual(
            expected_reference_resolution['create'],
            result['create']
        )

    def test_check_referenced_versions_is_working_properly_case_2(self):
        """testing if check_referenced_versions will return a dictionary holding
        info like which ref needs to be updated or which reference needs a new
        version, what is the corresponding Version instance and what is the
        final action, even if the 2nd level of references has an update

        Start Condition:

        version15 -> has no new version
          version11 -> has no new version
            version4 -> has no new version
              version2 -> has new published version (version3)

        Expected Final Result (generates only one new version)
        version15 -> create
          version11 -> create
            version4 -> create
              version2 -> update
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # version4 references version2
        self.maya_env.open(self.version4)
        self.maya_env.reference(self.version2)
        pymel.core.saveFile()
        self.version4.is_published = True
        pymel.core.newFile(force=True)

        # version11 references version4
        self.maya_env.open(self.version11)
        self.maya_env.reference(self.version4)
        pymel.core.saveFile()
        self.version11.is_published = True
        pymel.core.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)
        pymel.core.saveFile()

        db.DBSession.commit()

        # check the setup
        visited_versions = []
        for v in walk_version_hierarchy(self.version15):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version11, self.version4, self.version2]

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        expected_reference_resolution = {
            'root': [self.version11],
            'leave': [],
            'update': [self.version2],
            'create': [self.version4, self.version11]
        }

        result = \
            self.maya_env.check_referenced_versions()

        print 'self.version15.id: %s' % self.version15.id
        print 'self.version11.id: %s' % self.version11.id
        print 'self.version4.id : %s' % self.version4.id
        print 'self.version2.id : %s' % self.version2.id

        print expected_reference_resolution
        print '--------------------------'
        print result

        self.assertItemsEqual(
            expected_reference_resolution['root'],
            result['root']
        )
        self.assertItemsEqual(
            expected_reference_resolution['leave'],
            result['leave']
        )
        self.assertItemsEqual(
            expected_reference_resolution['update'],
            result['update']
        )
        self.assertItemsEqual(
            expected_reference_resolution['create'],
            result['create']
        )


class MayaFixReferenceNamespaceTestCase(MayaTestBase):
    """Tests Maya.fix_reference_namespace() method
    """

    def test_fix_reference_namespace_is_working_properly(self):
        """testing if the fix_reference_namespace method is working properly

        version15 -> has no new version
          version11 -> has no new version
            version4 -> has no new version
              version2 -> has no new version

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pymel.core.spaceLocator()
        loc.t.set(0, 0, 0)
        pymel.core.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # lookdev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pymel.core.saveFile()

        pymel.core.newFile(force=True)
        # version11 references version4
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        version4_ref_node = refs[0]
        version4_ref_node.namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there is only one locator in the current scene
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(1, 0, 0)
        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(version4_ref_node)[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pymel.core.saveFile()
        pymel.core.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version11.filename.replace('.', '_')
        pymel.core.saveFile()

        db.DBSession.commit()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        self.maya_env.fix_reference_namespaces()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, scs=1)),
            1
        )

        # and check if the locator is in 1, 0, 0
        loc = pymel.core.ls(type=pymel.core.nt.Transform)[0]
        self.assertEqual(loc.tx.get(), 1.0)
        self.assertEqual(loc.ty.get(), 0.0)
        self.assertEqual(loc.tz.get(), 0.0)
        pymel.core.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_duplicate_refs(self):
        """testing if the fix_reference_namespace method is working properly
        with duplicate references

        version15 -> has no new version
          version11 -> has no new version
            version4 -> has no new version
              version2 -> has no new version
          version11 -> has no new version
            version4 -> has no new version
              version2 -> has no new version

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pymel.core.spaceLocator()
        loc.t.set(0, 0, 0)
        pymel.core.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # lookdev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pymel.core.saveFile()

        # version11 references version4
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        version4_ref_node = refs[0]
        version4_ref_node.namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be two locators in the current scene
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(1, 0, 0)

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(version4_ref_node)[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pymel.core.saveFile()
        pymel.core.newFile(force=True)

        # version15 references version11 two times
        self.maya_env.open(self.version15)
        self.maya_env.reference(self.version11)
        self.maya_env.reference(self.version11)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version11.filename.replace('.', '_')
        refs[1].namespace = self.version11.filename.replace('.', '_')
        pymel.core.saveFile()

        db.DBSession.commit()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # the second copy
        self.assertEqual(
            all_refs[3].namespace,
            '%s1' % self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[4].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[5].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        self.maya_env.fix_reference_namespaces()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[3].namespace,
            'Test_Task_1_Test_Task_5_Take2'
        )

        self.assertEqual(
            all_refs[4].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[5].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # now check we don't have any failed edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[3], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[4], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[5], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, scs=1)),
            1
        )

        # and we have all successful edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[3], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[4], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[5], es=1, scs=1)),
            1
        )

        # and check if the locator is in 1, 0, 0
        locs = pymel.core.ls(type=pymel.core.nt.Transform)
        self.assertEqual(locs[0].tx.get(), 1.0)
        self.assertEqual(locs[0].ty.get(), 0.0)
        self.assertEqual(locs[0].tz.get(), 0.0)

        # the second locator
        self.assertEqual(locs[1].tx.get(), 1.0)
        self.assertEqual(locs[1].ty.get(), 0.0)
        self.assertEqual(locs[1].tz.get(), 0.0)
        pymel.core.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_shallower_duplicate_refs(self):
        """testing if the fix_reference_namespace method is working properly
        with duplicate references

          version11 -> has no new version ->Layout
            version4 -> has no new version -> LookDev
              version2 -> has no new version -> Model
            version4 -> has no new version
              version2 -> has no new version
            version4 -> has no new version
              version2 -> has no new version
            version4 -> has no new version
              version2 -> has no new version

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pymel.core.spaceLocator()
        loc.t.set(0, 0, 0)
        pymel.core.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pymel.core.saveFile()

        # version11 references version4 four times
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        refs[1].namespace = self.version4.filename.replace('.', '_')
        refs[2].namespace = self.version4.filename.replace('.', '_')
        refs[3].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be four locators in the current scene
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(1, 0, 0)
        loc[1].t.set(2, 0, 0)
        loc[2].t.set(3, 0, 0)
        loc[3].t.set(4, 0, 0)

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        version2_ref_node = pymel.core.listReferences(refs[1])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        version2_ref_node = pymel.core.listReferences(refs[2])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        version2_ref_node = pymel.core.listReferences(refs[3])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pymel.core.saveFile()
        print 'self.version11.absolute_full_path: %s' % \
              self.version11.absolute_full_path
        db.DBSession.commit()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # the second copy
        self.assertEqual(
            all_refs[2].namespace,
            '%s%s' % (self.version4.filename.replace('.', '_'),
                      all_refs[2].copyNumberList()[1])
        )

        self.assertEqual(
            all_refs[3].namespace,
            self.version2.filename.replace('.', '_')
        )

        # the third copy
        self.assertEqual(
            all_refs[4].namespace,
            '%s%s' % (self.version4.filename.replace('.', '_'),
                      all_refs[4].copyNumberList()[2])
        )

        self.assertEqual(
            all_refs[5].namespace,
            self.version2.filename.replace('.', '_')
        )

        # the forth copy
        self.assertEqual(
            all_refs[6].namespace,
            '%s%s' % (self.version4.filename.replace('.', '_'),
                      all_refs[6].copyNumberList()[3])
        )

        self.assertEqual(
            all_refs[7].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.latest_published_version.nice_name
        )

        # second copy
        self.assertEqual(
            all_refs[2].namespace,
            'Asset_2_Take2'
        )

        self.assertEqual(
            all_refs[3].namespace,
            self.version2.latest_published_version.nice_name
        )

        # third copy
        self.assertEqual(
            all_refs[4].namespace,
            'Asset_2_Take3'
        )

        self.assertEqual(
            all_refs[5].namespace,
            self.version2.latest_published_version.nice_name
        )

        # forth copy
        self.assertEqual(
            all_refs[6].namespace,
            'Asset_2_Take4'
        )

        self.assertEqual(
            all_refs[7].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        # second copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[3], es=1, fld=1)),
            0
        )

        # third copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[4], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[5], es=1, fld=1)),
            0
        )

        # forth copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[6], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[7], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        # second copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[3], es=1, scs=1)),
            1
        )

        # third copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[4], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[5], es=1, scs=1)),
            1
        )

        # forth copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[6], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[7], es=1, scs=1)),
            1
        )

        # and check if the locator are where they should be
        locs = pymel.core.ls(type=pymel.core.nt.Transform)
        self.assertTrue(locs[0].tx.get() > 0.5)
        self.assertTrue(locs[1].tx.get() > 0.5)
        self.assertTrue(locs[2].tx.get() > 0.5)
        self.assertTrue(locs[3].tx.get() > 0.5)
        pymel.core.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_refs_with_new_versions(self):
        """testing if the fix_reference_namespace method is working properly
        with references which has new versions

          version11 -> has no new version ->Layout
            version4 -> has no new version -> LookDev
              version2 -> has no new version -> Model -> has a new version3

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version3.is_published = True

        self.version4.is_published = True
        self.version11.is_published = True
        db.DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pymel.core.spaceLocator()
        loc.t.set(0, 0, 0)
        pymel.core.saveFile()

        # save as version3
        self.maya_env.save_as(self.version3)

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pymel.core.saveFile()

        # version11 references version4 four times
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be four locators in the current scene
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(1, 0, 0)

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pymel.core.saveFile()
        print 'self.version11.absolute_full_path: %s' % \
              self.version11.absolute_full_path
        db.DBSession.commit()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.latest_published_version.nice_name
        )

        # check if the reference is created from version2
        self.assertEqual(
            self.maya_env.get_version_from_full_path(all_refs[1].path).parent,
            self.version2
        )

        # and it is version3
        self.assertEqual(
            self.maya_env.get_version_from_full_path(all_refs[1].path),
            self.version3
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        # and check if the locator are where they should be
        locs = pymel.core.ls(type=pymel.core.nt.Transform)
        self.assertEqual(1.0, locs[0].tx.get())
        pymel.core.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_refs_updated_in_a_previous_scene(self):
        """testing if the fix_reference_namespace method is working properly
        with references which are updated in another scene

          version11 -> has no new version ->Layout
            version4 -> has no new version -> LookDev
              version2 -> has no new version -> Model

          version15 -> another scene which is referencing version4
            version4
              version2

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        db.DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pymel.core.spaceLocator()
        loc.t.set(0, 0, 0)
        pymel.core.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pymel.core.saveFile()

        # version11 references version4
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(1, 0, 0)

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pymel.core.saveFile()
        print 'self.version11.absolute_full_path: %s' % \
              self.version11.absolute_full_path
        db.DBSession.commit()

        # version15 also references version4
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version15)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(0, 1, 0)
        pymel.core.saveFile()

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)
        db.DBSession.commit()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now fix the namespaces in version15 let it be fixed
        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        version15_version4_path = all_refs[0].path
        version15_version2_path = all_refs[1].path

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        # and check if the locator are where they should be
        locs = pymel.core.ls(type=pymel.core.nt.Transform)
        self.assertEqual(1.0, locs[0].ty.get())
        pymel.core.saveFile()

        # now open version11 and try to fix it also there
        self.maya_env.open(self.version11)

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        version11_version4_path = all_refs[0].path
        version11_version2_path = all_refs[1].path

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        # and check if the locator are where they should be
        locs = pymel.core.ls(type=pymel.core.nt.Transform)
        self.assertEqual(1.0, locs[0].tx.get())
        pymel.core.saveFile()

        # check if the two scenes are using the same assets
        self.assertEqual(
            version15_version4_path,
            version11_version4_path
        )
        self.assertEqual(
            version15_version2_path,
            version11_version2_path
        )

    def test_fix_reference_namespace_is_working_properly_with_refs_updated_in_a_previous_scene_deeper(self):
        """testing if the fix_reference_namespace method is working properly
        with references which are updated in another scene

        version15 -> Bigger Layout
          version11 -> Layout
            version4 -> LookDev
              version2 -> Model

          version23 -> Another Bigger Layout
            version18 -> Another Layout referencing version4
              version4 -> LookDev
                version2 -> Model

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True
        self.version18.is_published = True
        self.version23.is_published = True
        db.DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pymel.core.spaceLocator()
        loc.t.set(0, 0, 0)
        pymel.core.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pymel.core.saveFile()

        # version11 references version4
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(1, 0, 0)
        pymel.core.saveFile()

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version15 references version11
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version15)  # bigger layout
        self.maya_env.reference(self.version11)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version11.filename.replace('.', '_')
        # now do some other edits here
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(0, 1, 0)
        pymel.core.saveFile()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # version18 references version4
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version18)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(0, 0, 1)
        pymel.core.saveFile()

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version23 references version18
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version23)  # bigger layout
        self.maya_env.reference(self.version18)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version18.filename.replace('.', '_')
        # now do some other edits here
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(0, 0, 2)
        pymel.core.saveFile()

        db.DBSession.commit()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version18.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # check edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, scs=1)),
            2
        )

        # now fix the namespaces in version23 let it be fixed
        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        version23_version4_path = all_refs[1].path
        version23_version2_path = all_refs[2].path

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version18.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, scs=1)),
            2
        )

        # and check if the locator are where they should be
        locs = pymel.core.ls(type=pymel.core.nt.Transform)
        self.assertEqual(2.0, locs[0].tz.get())
        pymel.core.saveFile()

        # now open version11 and try to fix it also there
        self.maya_env.open(self.version15)

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        version15_version4_path = all_refs[1].path
        version15_version2_path = all_refs[2].path

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, scs=1)),
            2
        )

        # and check if the locator are where they should be
        locs = pymel.core.ls(type=pymel.core.nt.Transform)
        self.assertEqual(1.0, locs[0].ty.get())
        pymel.core.saveFile()

        # check if the two scenes are using the same assets
        self.assertEqual(
            version15_version4_path,
            version23_version4_path
        )
        self.assertEqual(
            version15_version2_path,
            version23_version2_path
        )

    def test_fix_reference_namespace_returns_a_list_of_newly_created_versions(self):
        """testing if the fix_reference_namespace method will return newly
        created version instances in a list.

          version11 -> has no new version ->Layout
            version4 -> has no new version -> LookDev
              version2 -> has no new version -> Model -> has a new version3

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version3.is_published = True

        self.version4.is_published = True
        self.version11.is_published = True
        db.DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pymel.core.spaceLocator()
        loc.t.set(0, 0, 0)
        pymel.core.saveFile()

        # save as version3
        self.maya_env.save_as(self.version3)

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pymel.core.saveFile()

        # version11 references version4 four times
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be four locators in the current scene
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(1, 0, 0)

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pymel.core.saveFile()
        print 'self.version11.absolute_full_path: %s' % \
              self.version11.absolute_full_path
        db.DBSession.commit()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        list_of_versions = self.maya_env.fix_reference_namespaces()

        self.assertItemsEqual(
            list_of_versions,
            [self.version4.latest_published_version]
        )

    def test_fix_reference_namespace_returned_versions_have_correct_description(self):
        """testing if the fix_reference_namespace method will return newly
        created version instances in a list.

          version11 -> has no new version ->Layout
            version4 -> has no new version -> LookDev
              version2 -> has no new version -> Model -> has a new version3

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version3.is_published = True

        self.version4.is_published = True
        self.version11.is_published = True
        db.DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        loc = pymel.core.spaceLocator()
        loc.t.set(0, 0, 0)
        pymel.core.saveFile()

        # save as version3
        self.maya_env.save_as(self.version3)

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        pymel.core.saveFile()

        # version11 references version4 four times
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be four locators in the current scene
        loc = pymel.core.ls(type=pymel.core.nt.Transform)
        loc[0].t.set(1, 0, 0)

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        pymel.core.saveFile()
        print 'self.version11.absolute_full_path: %s' % \
              self.version11.absolute_full_path
        db.DBSession.commit()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # now let it be fixed
        list_of_versions = self.maya_env.fix_reference_namespaces()

        self.assertEqual(
            'Automatically created with Fix Reference Namespace',
            self.version4.latest_published_version.description
        )

    def test_fix_reference_namespace_is_working_properly_with_complex_edits(self):
        """testing if the fix_reference_namespace method is working properly
        with references which are updated in another scene

        version15 -> Bigger Layout -> Move the parent
          version11 -> Layout -> Parent it under a group
            version4 -> LookDev -> Assign new Material
              version2 -> Model

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True
        db.DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        cube = pymel.core.polyCube(name='test_cube')
        cube[0].t.set(0, 0, 0)
        pymel.core.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        # assign a new material
        cube = pymel.core.ls('*:test_cube', type=pymel.core.nt.Transform)[0]
        blinn, blinnSG = pymel.core.createSurfaceShader('blinn')
        pymel.core.sets(blinnSG, e=True, fe=[cube])
        pymel.core.saveFile()

        # version11 references version4
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        cube = pymel.core.ls('*:*:test_cube', type=pymel.core.nt.Transform)[0]
        # parent it to something else
        group = pymel.core.group(cube, name='test_group')
        cube.t.set(1, 0, 0)
        pymel.core.saveFile()

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version15 references version11
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version15)  # bigger layout
        self.maya_env.reference(self.version11)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version11.filename.replace('.', '_')
        # now do some other edits here
        group = pymel.core.ls(
            '*:test_group',
            type=pymel.core.nt.Transform
        )[0]
        # move the one with no parent to somewhere in the scene
        group.t.set(10, 0, 0)
        pymel.core.saveFile()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            2
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, scs=1)),
            4
        )

        # and check if the locator are where they should be
        group = pymel.core.ls('*:test_group', type=pymel.core.nt.Transform)[0]
        self.assertEqual(10.0, group.tx.get())
        pymel.core.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_references_with_no_namespaces(self):
        """testing if the fix_reference_namespace method is working properly
        with references which are not using namespaces

        version15 -> Bigger Layout -> Move the parent / Uses no namespaces
          version11 -> Layout -> Parent it under a group
            version4 -> LookDev -> Assign new Material
              version2 -> Model

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True
        db.DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        cube = pymel.core.polyCube(name='test_cube')
        cube[0].t.set(0, 0, 0)
        pymel.core.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        # assign a new material
        cube = pymel.core.ls('*:test_cube', type=pymel.core.nt.Transform)[0]
        blinn, blinnSG = pymel.core.createSurfaceShader('blinn')
        pymel.core.sets(blinnSG, e=True, fe=[cube])
        pymel.core.saveFile()

        # version11 references version4
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use old namespace style
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version4.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        cube = pymel.core.ls('*:*:test_cube', type=pymel.core.nt.Transform)[0]
        # parent it to something else
        group = pymel.core.group(cube, name='test_group')
        # pymel.core.parent(cube, group)
        cube.t.set(1, 0, 0)
        pymel.core.saveFile()

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version15 references version11
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version15)  # bigger layout
        self.maya_env.reference(self.version11, use_namespace=False)
        # use no namespace for version11 (so do not edit to old version)
        # now do some other edits here
        group = pymel.core.ls(
            'test_group',
            type=pymel.core.nt.Transform
        )[0]
        # move the one with no parent to somewhere in the scene
        group.t.set(10, 0, 0)
        pymel.core.saveFile()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.split('.')[0]  # maya uses filename
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.split('.')[0]  # still using filename
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.split('.')[0]
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.latest_published_version.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.latest_published_version.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # # and we have all successful edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            2
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, scs=1)),
            4
        )

        # and check if the locator are where they should be
        group = pymel.core.ls('test_group', type=pymel.core.nt.Transform)[0]
        self.assertEqual(10.0, group.tx.get())
        pymel.core.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_references_with_same_namespaces_with_its_children_ref(self):
        """testing if the fix_reference_namespace method is working properly
        with references that has the same namespace with its children

        version15 -> Bigger Layout -> Move the parent
          version11 -> Layout -> Parent it under a group
            version4 -> LookDev -> Assign new Material / using the same
                        namespace with its child
              version2 -> Model

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True
        db.DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        cube = pymel.core.polyCube(name='test_cube')
        cube[0].t.set(0, 0, 0)
        pymel.core.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        # assign a new material
        cube = pymel.core.ls('*:test_cube', type=pymel.core.nt.Transform)[0]
        blinn, blinnSG = pymel.core.createSurfaceShader('blinn')
        pymel.core.sets(blinnSG, e=True, fe=[cube])
        pymel.core.saveFile()

        # version11 references version4
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use version2 namespace in version4
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version2.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        cube = pymel.core.ls('*:*:test_cube', type=pymel.core.nt.Transform)[0]
        # parent it to something else
        group = pymel.core.group(cube, name='test_group')
        # pymel.core.parent(cube, group)
        cube.t.set(1, 0, 0)
        pymel.core.saveFile()

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version15 references version11
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version15)  # bigger layout
        self.maya_env.reference(self.version11)
        # use old style namespace here
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version11.filename.replace('.', '_')
        # now do some other edits here
        group = pymel.core.ls(
            '*:test_group',
            type=pymel.core.nt.Transform
        )[0]
        # move the one with no parent to somewhere in the scene
        group.t.set(10, 0, 0)
        pymel.core.saveFile()

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        # version4 is using version2 namespace
        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.filename.replace('.', '_')
        )

        # version4 is using version2 filename
        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            2
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, scs=1)),
            4
        )

        # and check if the locator are where they should be
        group = pymel.core.ls('*:test_group', type=pymel.core.nt.Transform)[0]
        self.assertEqual(10.0, group.tx.get())
        pymel.core.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_references_with_same_namespaces_with_its_children_ref_in_a_shallower_setup(self):
        """testing if the fix_reference_namespace method is working properly
        with references that has the same namespace with its children in a
        shallower setup

        version11 -> Layout -> Parent it under a group
          version4 -> LookDev -> Assign new Material / using the same
                      namespace with its child
            version2 -> Model

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        db.DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        cube = pymel.core.polyCube(name='test_cube')
        cube[0].t.set(0, 0, 0)
        pymel.core.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        # assign a new material
        cube = pymel.core.ls('*:test_cube', type=pymel.core.nt.Transform)[0]
        blinn, blinnSG = pymel.core.createSurfaceShader('blinn')
        pymel.core.sets(blinnSG, e=True, fe=[cube])
        pymel.core.saveFile()

        # version11 references version4
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use version2 namespace in version4
        refs = pymel.core.listReferences()
        refs[0].namespace = self.version2.filename.replace('.', '_')
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        cube = pymel.core.ls('*:*:test_cube', type=pymel.core.nt.Transform)[0]
        # parent it to something else
        group = pymel.core.group(cube, name='test_group')
        cube.t.set(1, 0, 0)
        pymel.core.saveFile()

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # check namespaces
        all_refs = pymel.core.listReferences(recursive=1)

        # version4 is using version2 namespace
        self.assertEqual(
            all_refs[0].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        # check namespaces
        # version4 is using version2 filename
        self.assertEqual(
            all_refs[0].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version4.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version2.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            1
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            4
        )

        # and check if the locator are where they should be
        pymel.core.saveFile()

    def test_fix_reference_namespace_is_working_properly_with_references_with_correct_namespaces_but_has_wrong_namespace_children(self):
        """testing if the fix_reference_namespace method is working properly
        with references that has the same namespace with its children

        version15 -> Bigger Layout
          version11 -> Layout -> uses correct namespace
            version4 -> LookDev -> uses correct namespace
              version2 -> Model -> uses wrong namespace

        All uses wrong namespaces
        """
        # create deep reference
        self.version2.is_published = True
        self.version4.is_published = True
        self.version11.is_published = True
        self.version15.is_published = True
        db.DBSession.commit()

        # open version2 and create a locator
        self.maya_env.open(self.version2)  # model
        cube = pymel.core.polyCube(name='test_cube')
        cube[0].t.set(0, 0, 0)
        pymel.core.saveFile()

        # version4 references version2
        self.maya_env.open(self.version4)  # look dev
        self.maya_env.reference(self.version2)
        # change the namespace to old one
        refs = pymel.core.listReferences()
        ref = refs[0]
        isinstance(ref, pymel.core.system.FileReference)
        ref.namespace = self.version2.filename.replace('.', '_')
        # assign a new material
        cube = pymel.core.ls('*:test_cube', type=pymel.core.nt.Transform)[0]
        blinn, blinnSG = pymel.core.createSurfaceShader('blinn')
        pymel.core.sets(blinnSG, e=True, fe=[cube])
        pymel.core.saveFile()

        # version11 references version4
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version11)  # layout
        self.maya_env.reference(self.version4)
        # use version2 namespace in version4
        refs = pymel.core.listReferences()
        # refs[0].namespace = self.version4.nice_name
        # now do the edits here
        # we need to do some edits
        # there should be only one locator in the current scene
        cube = pymel.core.ls('*:*:test_cube', type=pymel.core.nt.Transform)[0]
        # parent it to something else
        group = pymel.core.group(cube, name='test_group')
        cube.t.set(1, 0, 0)
        pymel.core.saveFile()

        # we should have created an edit
        version2_ref_node = pymel.core.listReferences(refs[0])[0]
        edits = pymel.core.referenceQuery(version2_ref_node, es=1)
        self.assertTrue(len(edits) > 0)

        # version15 references version11
        pymel.core.newFile(force=True)
        self.maya_env.open(self.version15)  # bigger layout
        self.maya_env.reference(self.version11)
        # use old style namespace here
        refs = pymel.core.listReferences()
        # refs[0].namespace = self.version11.nice_name
        # now do some other edits here
        group = pymel.core.ls(
            '*:test_group',
            type=pymel.core.nt.Transform
        )[0]
        # move the one with no parent to somewhere in the scene
        group.t.set(10, 0, 0)
        pymel.core.saveFile()

        # check namespaces
        # version11 is using correct namespace
        all_refs = pymel.core.listReferences(recursive=1)
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.nice_name
        )

        # version4 is using correct namespace
        self.assertEqual(
            all_refs[1].namespace,
            self.version4.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.filename.replace('.', '_')
        )

        self.maya_env.fix_reference_namespaces()
        pymel.core.saveFile()

        # check if the namespaces are fixed
        all_refs = pymel.core.listReferences(recursive=1)

        # first copy
        self.assertEqual(
            all_refs[0].namespace,
            self.version11.nice_name
        )

        self.assertEqual(
            all_refs[1].namespace,
            self.version4.nice_name
        )

        self.assertEqual(
            all_refs[2].namespace,
            self.version2.nice_name
        )

        # now check we don't have any failed edits
        # first copy
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, fld=1)),
            0
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, fld=1)),
            0
        )

        # and we have all successful edits
        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[0], es=1, scs=1)),
            2
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[1], es=1, scs=1)),
            1
        )

        self.assertEqual(
            len(pymel.core.referenceQuery(all_refs[2], es=1, scs=1)),
            4
        )

        # and check if the locator are where they should be
        group = pymel.core.ls('*:test_group', type=pymel.core.nt.Transform)[0]
        self.assertEqual(10.0, group.tx.get())
        pymel.core.saveFile()


class ReferenceToAssTestCase(MayaTestBase):
    """tests the reference file to ass integration
    """

    def setUp(self):
        """additional setup
        """
        # call the supers setUp first
        super(ReferenceToAssTestCase, self).setUp()

        # now do your addition
        # create ass take for asset2
        self.ass_version1 = self.create_version(self.asset2, 'Main_ASS')
        self.ass_version2 = self.create_version(self.asset2, 'Main_ASS')
        self.ass_version3 = self.create_version(self.asset2, 'Main_ASS')

        self.ass_version4 = self.create_version(self.asset2, 'Take1_ASS')
        self.ass_version5 = self.create_version(self.asset2, 'Take1_ASS')
        self.ass_version6 = self.create_version(self.asset2, 'Take1_ASS')

        self.ass_version3.is_published = True
        self.version1.is_published = True
        self.version3.is_published = True

        self.ass_version6.is_published = True
        db.DBSession.commit()

        pymel.core.newFile(force=True)

    def test_FileReference_class_has_to_ass_method(self):
        """testing if FileReference has a to_ass() method
        """
        from pymel.core.system import FileReference
        self.assertTrue(hasattr(FileReference, 'to_ass'))

    def test_FileReference_class_has_to_original_method(self):
        """testing if FileReference has a to_original() method
        """
        from pymel.core.system import FileReference
        self.assertTrue(hasattr(FileReference, 'to_original'))

    def test_to_ass_is_working_properly(self):
        """testing if FileReference.to_ass() is working properly
        """
        # reference version1 to the scene
        ref = self.maya_env.reference(self.version1)

        self.assertEqual(ref.path, self.version1.absolute_full_path)
        # now invoke to_ass on the FileReference node
        ref.to_ass()

        # and expect its path to be replaced with self.ass_version3
        self.assertEqual(ref.path, self.ass_version3.absolute_full_path)

    def test_to_original_is_working_properly(self):
        """testing if FileReference.to_original() is working properly
        """
        # reference version1 to the scene
        ref = self.maya_env.reference(self.ass_version1)

        self.assertEqual(ref.path, self.ass_version1.absolute_full_path)
        # now invoke to_ass on the FileReference node
        ref.to_original()

        # and expect its path to be replaced with self.ass_version3
        self.assertEqual(ref.path, self.version3.absolute_full_path)

    def test_has_ass_is_working_properly(self):
        """testing if FileReference.has_ass() is working properly
        """
        # reference version1 to the scene
        ref1 = self.maya_env.reference(self.version1)
        ref2 = self.maya_env.reference(self.version40)  # which has no ASS
        self.assertEqual(ref1.path, self.version1.absolute_full_path)

        # now check has_ass
        self.assertTrue(ref1.has_ass())
        self.assertFalse(ref2.has_ass())

    def test_is_ass_is_working_properly(self):
        """testing if FileReference.is_ass() is working properly
        """
        # reference version1 to the scene
        ref1 = self.maya_env.reference(self.version1)
        ref2 = self.maya_env.reference(self.version40)  # which has no ASS
        self.assertEqual(ref1.path, self.version1.absolute_full_path)

        self.assertFalse(ref1.is_ass())
        self.assertFalse(ref2.is_ass())

        ref1.to_ass()
        ref2.to_ass()

        self.assertTrue(ref1.is_ass())
        self.assertFalse(ref2.is_ass())


class PatchedProgressWindow(object):
    """A dummy class for patching pymel.core.progressWindow
    """

    def __init__(self):
        self.call_info = {}

    def __call__(self, *args, **kwargs):
        """mock version of the pymel.core.progressWindow command

        :return:
        """
        self.call_info.update(kwargs)


class ProgressWindowManagerTestCase(unittest2.TestCase):
    """tests the maya.ProgressWindowManager class
    """

    progress_window = None

    @classmethod
    def setUpClass(cls):
        """set up tests in class level
        """
        # patch pymel.core.
        cls.progress_window = pymel.core.progressWindow
        cls.mock_progress_window = PatchedProgressWindow()
        pymel.core.progressWindow = cls.mock_progress_window

    @classmethod
    def tearDownClass(cls):
        """clean up tests in class level
        """
        # restore the progressWindow
        pymel.core.progressWindow = cls.progress_window

    def test_singletonness(self):
        """testing if the ProgressWindowManager is a Singleton class.
        """
        pm1 = ProgressWindowManager()
        pm2 = ProgressWindowManager()
        self.assertEqual(id(pm1), id(pm2))

    def test_register_will_return_a_ProgerssCaller_instance(self):
        """testing if the ProgressWindowManager.register() method will return a
        ProgressCaller instance
        """
        pm = ProgressWindowManager()
        caller = pm.register('test', 10)
        self.assertIsInstance(caller, ProgressCaller)

        self.assertEqual(caller.name, 'test')
        self.assertEqual(caller.max_iterations, 10)
        self.assertEqual(caller.current_step, 0)

    def test_register_will_store_the_given_caller_name_in_callers_dictionary(self):
        """testing if ProgressWindow.register() method will store the given
        name as a key in the ProgressWindow.callers dictionary
        """
        pm = ProgressWindowManager()
        caller = pm.register('update_references', 100)
        self.assertIn(caller, pm.callers)

    def test_register_will_set_the_manager_to_in_progress(self):
        """testing if ProgressWindow.register() method will set the system to
        "in_progress" mode True
        """
        pm = ProgressWindowManager()
        self.assertFalse(pm.in_progress)
        pm.register('update_references', 100)
        self.assertTrue(pm.in_progress)

    def test_register_will_create_the_window_if_it_is_not_created_yet(self):
        """testing if the register method will create the progressWindow if it
        is not created yet
        """
        pm = ProgressWindowManager()
        self.assertFalse(pm.in_progress)
        caller = pm.register('test', 5)
        self.assertTrue(pm.in_progress)

    def test_step_method_will_increment_the_call_count_of_the_given_caller(self):
        """testing if the step method will increment the step of the caller
        """
        pm = ProgressWindowManager()
        caller = pm.register('test', 100)
        self.assertEqual(caller.current_step, 0)

        pm.step(caller)
        self.assertEqual(caller.current_step, 1)

        pm.step(caller)
        self.assertEqual(caller.current_step, 2)

    def test_step_automatically_removes_the_given_caller_if_it_reached_to_its_maximum(self):
        """testing if the step method will automatically remove the caller from
        the list if the caller reached to its maximum
        """
        pm = ProgressWindowManager()
        self.assertFalse(pm.in_progress)
        caller = pm.register('test', 5)
        self.assertTrue(pm.in_progress)
        self.assertEqual(caller.current_step, 0)
        self.assertTrue(pm.in_progress)
        self.assertIn(caller, pm.callers)

        for i in range(5):
            caller.step()

        self.assertNotIn(caller, pm.callers)
        self.assertFalse(pm.in_progress)

    def test_step_will_step_the_progressWindow(self):
        """testing if the step method will call pymel.core.progressWindow
        properly
        """
        pm = ProgressWindowManager()
        caller = pm.register('test', 5)
        pm.step(caller, 2)

        self.assertIn('step', self.mock_progress_window.call_info)

        # check the value
        self.assertEqual(self.mock_progress_window.call_info['step'], 2)

    def test_end_progress_method_removes_the_given_caller_from_list(self):
        """testing if the end_progress method will remove the given caller from
        the callers list
        """
        pm = ProgressWindowManager()
        caller = pm.register('test', 5)
        caller.step()
        self.assertIn(caller, pm.callers)
        pm.end_progress(caller)
        self.assertNotIn(caller, pm.callers)

    def test_end_progress_method_will_remove_the_progress_windows_if_there_are_no_callers_left(self):
        """testing if the end_progress method will remove the progress window
        it there are no callers left
        """
        pm = ProgressWindowManager()
        caller = pm.register('test', 5)
        caller.step()
        self.assertIn(caller, pm.callers)
        pm.end_progress(caller)
        self.assertNotIn(caller, pm.callers)

        # also check if the endProgress is called in the mock object
        self.assertTrue(
            'endProgress' in self.mock_progress_window.call_info
        )

        # and the value is True
        self.assertTrue(self.mock_progress_window.call_info['endProgress'])

