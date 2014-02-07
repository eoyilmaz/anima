# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import shutil
import unittest2
import tempfile

import pymel

from stalker import (db, Project, Repository, StatusList, Status, Asset, Shot,
                     Task, Sequence, Version, User, Type, Structure,
                     FilenameTemplate, ImageFormat)

from anima.pipeline import utils
from anima.pipeline.env import mayaEnv
from anima.pipeline.utils import walk_version_hierarchy


class MayaEnvTestCase(unittest2.TestCase):
    """tests the maya env
    """

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
                 '{%- for parent_task in version.task.parents -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.asset_template = FilenameTemplate(
            name='Asset Template',
            target_entity_type='Asset',
            path='{{project.code}}/'
                 '{%- for parent_task in version.task.parents -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.structure = Structure(
            name='Project Struture',
            templates=[self.task_template, self.asset_template]
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
            self.task_template
        ])

        # create the environment instance
        self.maya_env = mayaEnv.Maya()

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
        shutil.rmtree(self.temp_repo_path, ignore_errors=True)

        for f in self.remove_these_files_buffer:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f, True)

    @classmethod
    def tearDownClass(cls):
        # quit maya
        pymel.core.runtime.Quit()

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
        self.maya_env.open_(versionBase, force=True)

        # and check the references is updated
        self.assertEqual(0, len(versionBase.inputs))
        self.assertEqual(versionBase.inputs, [])

    def test_open_does_not_load_unloaded_references(self):
        """testing if the open method dosn't load unloaded references
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
        self.maya_env.open_(version_base, force=True)
        self.maya_env.post_open(version_base)

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
        version1 = Version(task=self.task6)
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
        version1 = Version(task=self.task6)
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


class MayaEnvDeepReferenceUpdateTestCase(unittest2.TestCase):
    """tests the maya env with deep reference updates
    """

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
                 '{%- for parent_task in version.task.parents -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.asset_template = FilenameTemplate(
            name='Asset Template',
            target_entity_type='Asset',
            path='{{project.code}}/'
                 '{%- for parent_task in version.task.parents -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.shot_template = FilenameTemplate(
            name='Shot Template',
            target_entity_type='Shot',
            path='{{project.code}}/'
                 '{%- for parent_task in version.task.parents -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.sequence_template = FilenameTemplate(
            name='Sequence Template',
            target_entity_type='Sequence',
            path='{{project.code}}/'
                 '{%- for parent_task in version.task.parents -%}'
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
        self.maya_env = mayaEnv.Maya()

        # now create versions
        def create_version(task, take_name):
            """Creates a new version
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

        # asset2
        self.version1 = create_version(self.asset2, 'Main')
        self.version2 = create_version(self.asset2, 'Main')
        self.version3 = create_version(self.asset2, 'Main')

        self.version4 = create_version(self.asset2, 'Take1')
        self.version5 = create_version(self.asset2, 'Take1')
        self.version6 = create_version(self.asset2, 'Take1')

        # task5
        self.version7 = create_version(self.task5, 'Main')
        self.version8 = create_version(self.task5, 'Main')
        self.version9 = create_version(self.task5, 'Main')

        self.version10 = create_version(self.task5, 'Take1')
        self.version11 = create_version(self.task5, 'Take1')
        self.version12 = create_version(self.task5, 'Take1')

        # task6
        self.version13 = create_version(self.task6, 'Main')
        self.version14 = create_version(self.task6, 'Main')
        self.version15 = create_version(self.task6, 'Main')

        self.version16 = create_version(self.task6, 'Take1')
        self.version17 = create_version(self.task6, 'Take1')
        self.version18 = create_version(self.task6, 'Take1')

        # shot3
        self.version19 = create_version(self.shot3, 'Main')
        self.version20 = create_version(self.shot3, 'Main')
        self.version21 = create_version(self.shot3, 'Main')

        self.version22 = create_version(self.shot3, 'Take1')
        self.version23 = create_version(self.shot3, 'Take1')
        self.version24 = create_version(self.shot3, 'Take1')

        # task3
        self.version25 = create_version(self.task3, 'Main')
        self.version26 = create_version(self.task3, 'Main')
        self.version27 = create_version(self.task3, 'Main')

        self.version28 = create_version(self.task3, 'Take1')
        self.version29 = create_version(self.task3, 'Take1')
        self.version30 = create_version(self.task3, 'Take1')

        # asset1
        self.version31 = create_version(self.asset1, 'Main')
        self.version32 = create_version(self.asset1, 'Main')
        self.version33 = create_version(self.asset1, 'Main')

        self.version34 = create_version(self.asset1, 'Take1')
        self.version35 = create_version(self.asset1, 'Take1')
        self.version36 = create_version(self.asset1, 'Take1')

        # shot2
        self.version37 = create_version(self.shot2, 'Main')
        self.version38 = create_version(self.shot2, 'Main')
        self.version39 = create_version(self.shot2, 'Main')

        self.version40 = create_version(self.shot2, 'Take1')
        self.version41 = create_version(self.shot2, 'Take1')
        self.version42 = create_version(self.shot2, 'Take1')

        # shot1
        self.version43 = create_version(self.shot1, 'Main')
        self.version44 = create_version(self.shot1, 'Main')
        self.version45 = create_version(self.shot1, 'Main')

        self.version46 = create_version(self.shot1, 'Take1')
        self.version47 = create_version(self.shot1, 'Take1')
        self.version48 = create_version(self.shot1, 'Take1')

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
        # |  |        +- version4
        # |  |        +- version5 (P)
        # |  |        +- version6
        # |  |
        # |  +- task5
        # |  |  +- Main
        # |  |  |  +- version7
        # |  |  |  +- version8
        # |  |  |  +- version9
        # |  |  +- Take1
        # |  |     +- version10
        # |  |     +- version11
        # |  |     +- version12
        # |  |
        # |  +- task6
        # |     +- Main
        # |     |  +- version13
        # |     |  +- version14
        # |     |  +- version15
        # |     +- Take1
        # |        +- version16
        # |        +- version17
        # |        +- version18
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
        shutil.rmtree(self.temp_repo_path, ignore_errors=True)

        for f in self.remove_these_files_buffer:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f, True)

    @classmethod
    def tearDownClass(cls):
        # quit maya
        pymel.core.runtime.Quit()

    def test_deep_reference_update_is_working_properly(self):
        """testing if deep_reference_update is working properly in an
        environment with highly complex relations of versions, where there are
        new published versions in the middle of the hierarchy where versions
        referencing them also has new versions but not using those published
        versions.
        """
        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        self.version5.inputs.append(self.version2)
        self.version5.is_published = True

        # leave version6 as not published
        self.version12.inputs.append(self.version5)
        db.DBSession.commit()

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

        self.maya_env.deep_reference_update(self.version12)

        # and expect maya to update to
        visited_versions = []
        for v in walk_version_hierarchy(self.version12):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version12, self.version5.latest_published_version,
             self.version3]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

