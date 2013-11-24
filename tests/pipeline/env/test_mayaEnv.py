# -*- coding: utf-8 -*-
# anima-tools
# Copyright (C) 2013 Erkan Ozgur Yilmaz
#
# This file is part of anima-tools.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import unittest2
import tempfile

import pymel.core as pm

from stalker import (db, Project, Repository, StatusList, Status, Asset, Shot,\
                     Task, Sequence)
from anima.pipeline.env import mayaEnv



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

        self.temp_repo_path = tempfile.gettempdir()

        self.repo1 = Repository(
            name='Test Project Repository',
            linux_path=self.temp_repo_path,
            windows_path=self.temp_repo_path,
            osx_path=self.temp_repo_path
        )

        self.status_new = Status(name='New', code='NEW')
        self.status_wip = Status(name='Work In Progress', code='WIP')
        self.status_comp = Status(name='Completed', code='CMPL')

        self.project_status_list = StatusList(
            name='Project Statuses',
            target_entity_type='Project',
            statuses=[self.status_new, self.status_wip, self.status_comp]
        )

        # create a test project
        self.project = Project(
            name='Test Project',
            code='TP',
            repository=self.repo1,
            status_list=self.project_status_list
        )

        self.task_status_list = StatusList(
            name='Task Statuses',
            target_entity_type='Task',
            statuses=[self.status_new, self.status_wip, self.status_comp]
        )
        self.asset_status_list = StatusList(
            name='Asset Statuses',
            target_entity_type='Asset',
            statuses=[self.status_new, self.status_wip, self.status_comp]
        )
        self.shot_status_list = StatusList(
            name='Shot Statuses',
            target_entity_type='Shot',
            statuses=[self.status_new, self.status_wip, self.status_comp]
        )
        self.sequence_status_list = StatusList(
            name='Sequence Statuses',
            target_entity_type='Sequence',
            statuses=[self.status_new, self.status_wip, self.status_comp]
        )

        # create a test series of root task
        self.task1 = Task(
            name='Test Task 1',
            project=self.project,
            status_list=self.task_status_list
        )
        self.task2 = Task(
            name='Test Task 2',
            project=self.project,
            status_list=self.task_status_list
        )
        self.task3 = Task(
            name='Test Task 3',
            project=self.project,
            status_list=self.task_status_list
        )

        # then a couple of child tasks
        self.task4 = Task(
            name='Test Task 4',
            parent=self.task1,
            status_list=self.task_status_list
        )
        self.task5 = Task(
            name='Test Task 5',
            parent=self.task1,
            status_list=self.task_status_list
        )
        self.task6 = Task(
            name='Test Task 6',
            parent=self.task1,
            status_list=self.task_status_list
        )

        # create a root asset
        self.asset1 = Asset(
            name='Asset 1',
            code='asset1',
            project=self.project,
            status_list=self.asset_status_list
        )

        # create a child asset
        self.asset2 = Asset(
            name='Asset 2',
            code='asset2',
            parent=self.task4,
            status_list=self.asset_status_list
        )

        # create a root Sequence
        self.sequence1 = Sequence(
            name='Sequence1',
            code='SEQ1',
            project=self.project,
            status_list=self.sequence_status_list
        )

        # create a child Sequence
        self.sequence2 = Sequence(
            name='Sequence2',
            code='SEQ2',
            parent=self.task2,
            status_list=self.sequence_status_list
        )

        # create a root Shot
        self.shot1 = Shot(
            name='Shot 1',
            project=self.project,
            status_list=self.shot_status_list
        )

        # create a child Shot (child of a Sequence)
        self.shot2 = Shot(
            name='Shot 2',
            parent=self.sequence1,
            status_list=self.shot_status_list
        )

        # create a child Shot (child of a child Sequence)
        self.shot3 = Shot(
            name='Shot 3',
            parent=self.sequence2,
            status_list=self.shot_status_list
        )
        
        # commit everything
        db.DBSession.add_all([
            self.repo1, self.status_new, self.status_wip, self.status_comp,
            self.project_status_list, self.project, self.task_status_list,
            self.asset_status_list, self.shot_status_list,
            self.sequence_status_list, self.task1, self.task2, self.task3,
            self.task4, self.task5, self.task6, self.asset1, self.asset2,
            self.shot1, self.shot2, self.shot3, self.sequence1, self.sequence2
        ])

        # create the environment instance
        self.maya_env = mayaEnv.Maya()

        # just renew the scene
        pm.newFile(force=True)

    def tearDown(self):
        """cleanup the test
        """
        # set the db.session to None
        db.DBSession.remove()

        # delete the temp folder
        shutil.rmtree(self.temp_repo_path)

        # quit maya
        pm.runtime.Quit()
    
    def test_save_as_creates_a_maya_file_at_version_full_path(self):
        """testing if the save_as creates a maya file at the Version.full_path
        """
        
        # check the version file doesn't exists
        self.assertFalse(os.path.exists(self.version1.full_path))
        
        # save the version
        self.mEnv.save_as(self.version1)
        
        # check the file exists
        self.assertTrue(os.path.exists(self.version1.full_path))
    
    def test_save_as_sets_the_version_extension_to_ma(self):
        """testing if the save_as method sets the version extension to ma
        """
        
        self.version1.extension = ""
        self.mEnv.save_as(self.version1)
        self.assertEqual(self.version1.extension, ".ma")
    
    def test_save_as_sets_the_render_version_string(self):
        """testing if the save_as method sets the version string in the render
        settings
        """
        
        self.mEnv.save_as(self.version1)
        
        # now check if the render settings version is the same with the
        # version.version_number
        
        render_version = pm.getAttr("defaultRenderGlobals.renderVersion")
        self.assertEqual(render_version, "v%03d" % self.version1.version_number)
    
    def test_save_as_sets_the_render_format_to_exr_for_mentalray(self):
        """testing if the save_as method sets the render format to exr
        """
        
        # load mayatomr plugin
        pm.loadPlugin("Mayatomr")
        
        # set the current renderer to mentalray
        dRG = pm.PyNode("defaultRenderGlobals")
        
        dRG.setAttr('currentRenderer', 'mentalRay')
        
        # dirty little maya tricks
        pm.mel.miCreateDefaultNodes()
        
        mrG = pm.PyNode("mentalrayGlobals")
        
        self.mEnv.save_as(self.version1)
        
        # now check if the render format is correctly set to exr with zip
        # compression
        self.assertEqual(dRG.getAttr("imageFormat"), 51)
        self.assertEqual(dRG.getAttr("imfkey"), "exr")
        self.assertEqual(mrG.getAttr("imageCompression"), 4)
    
    def test_save_as_sets_the_render_file_name_for_Assets(self):
        """testing if the save_as sets the render file name correctly
        """
        
        self.mEnv.save_as(self.version1)
        
        # check if the path equals to
        expected_path = self.version1.output_path +\
                        "/<Layer>/"+ self.version1.project.code + "_" +\
                        self.version1.base_name +"_" +\
                        self.version1.take_name +\
                        "_<Layer>_<RenderPass>_<Version>"

        image_path = os.path.join(
            pm.workspace.path,
            pm.workspace.fileRules['image']
        ).replace("\\", "/")

        expected_path = utils.relpath(
            image_path,
            expected_path,
        )

        dRG = pm.PyNode("defaultRenderGlobals")

        self.assertEqual(
            expected_path,
            dRG.getAttr("imageFilePrefix")
        )
    
    def test_save_as_sets_the_render_file_name_for_Shots(self):
        """testing if the save_as sets the render file name correctly
        """
        
        test_seq = Sequence(self.project, "Test Sequence 1")
        test_seq.save()
        
        test_shot = Shot(test_seq, 1)
        test_shot.save()
        
        self.kwargs["type"] = self.shot_vtypes[0]
        self.kwargs["version_of"] = test_shot
        
        self.version1 = Version(**self.kwargs)
        
        self.mEnv.save_as(self.version1)
        
        # check if the path equals to
        expected_path = self.version1.output_path + \
                        "/<Layer>/"+ self.version1.project.code + "_" + \
                        self.version1.version_of.sequence.code + "_" + \
                        self.version1.base_name +"_" + \
                        self.version1.take_name + \
                            "_<Layer>_<RenderPass>_<Version>"
        
        image_path = os.path.join(
            pm.workspace.path,
            pm.workspace.fileRules['image']
        ).replace("\\", "/")
        
        expected_path = utils.relpath(
            image_path,
            expected_path,
        )
        
        dRG = pm.PyNode("defaultRenderGlobals")
        
        self.assertEqual(
            expected_path,
            dRG.getAttr("imageFilePrefix")
        )
    
    def test_save_as_replaces_file_image_paths(self):
        """testing if save_as method replaces image paths with REPO relative
        path
        """
        
        self.mEnv.save_as(self.version1)
        
        # create file node
        file_node = pm.createNode("file")
        
        # set it to a path in the workspace
        texture_path = os.path.join(
            pm.workspace.path, ".maya_files/textures/test.jpg"
        )
        file_node.fileTextureName.set(texture_path)
        
        # save a newer version
        version2 = Version(**self.kwargs)
        version2.save()
        
        self.mEnv.save_as(version2)
        
        # now check if the file nodes fileTextureName is converted to a
        # relative path to the current workspace
        
        expected_path = texture_path.replace(os.environ["REPO"], "$REPO")
        
        self.assertEqual(
            file_node.getAttr("fileTextureName"),
            expected_path
        )

    def test_save_as_sets_the_resolution(self):
        """testing if save_as sets the render resolution for the current scene
        """

        project = self.version1.project

        width = 1920
        height = 1080
        pixel_aspect = 1.0

        project.width = width
        project.height = height
        project.pixel_aspect = pixel_aspect
        project.save()

        # save the scene
        self.mEnv.save_as(self.version1)

        # check the resolutions
        dRes = pm.PyNode("defaultResolution")
        self.assertEqual(dRes.width.get(), width)
        self.assertEqual(dRes.height.get(), height)
        self.assertEqual(dRes.pixelAspect.get(), pixel_aspect)

    def test_save_as_sets_the_resolution_only_for_first_version(self):
        """testing if save_as sets the render resolution for the current scene
        but only for the first version of the asset
        """
        
        project = self.version1.project
        
        width = 1920
        height = 1080
        pixel_aspect = 1.0
        
        project.width = width
        project.height = height
        project.pixel_aspect = pixel_aspect
        project.save()
        
        # save the scene
        self.mEnv.save_as(self.version1)
        
        # check the resolutions
        dRes = pm.PyNode("defaultResolution")
        self.assertEqual(dRes.width.get(), width)
        self.assertEqual(dRes.height.get(), height)
        self.assertEqual(dRes.pixelAspect.get(), pixel_aspect)
        
        # now change the resolution of the maya file
        new_width = 1280
        new_height = 720
        new_pixel_aspect = 1.0
        dRes.width.set(new_width)
        dRes.height.set(new_height)
        dRes.pixelAspect.set(new_pixel_aspect)
        
        # save the version again
        new_version = Version(**self.kwargs)
        new_version.save()
        
        self.mEnv.save_as(new_version)
        
        # test if the resolution is not changed
        self.assertEqual(dRes.width.get(), new_width)
        self.assertEqual(dRes.height.get(), new_height)
        self.assertEqual(dRes.pixelAspect.get(), new_pixel_aspect)

    def test_save_as_fills_the_referenced_versions_list(self):
        """testing if the save_as method updates the Version.references list
        with the current references list from the Maya
        """
        
        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list
        
        versionBase = Version(**self.kwargs)
        versionBase.save()
        
        # change the take name
        self.kwargs["take_name"] = "Take1"
        version1 = Version(**self.kwargs)
        version1.save()
        
        self.kwargs["take_name"] = "Take2"
        version2 = Version(**self.kwargs)
        version2.save()
        
        self.kwargs["take_name"] = "Take3"
        version3 = Version(**self.kwargs)
        version3.save()
        
        # now create scenes with these files
        self.mEnv.save_as(version1)
        self.mEnv.save_as(version2)
        self.mEnv.save_as(version3) # this is the dummy version
        
        # create a new scene
        pm.newFile(force=True)
        
        # check if the versionBase.references is an empty list
        self.assertTrue(versionBase.references==[])
        
        # reference the given versions
        self.mEnv.reference(version1)
        self.mEnv.reference(version2)
        
        # save it as versionBase
        self.mEnv.save_as(versionBase)
        
        # now check if versionBase.references is updated
        self.assertTrue(len(versionBase.references)==2)
        
        self.assertTrue(version1 in versionBase.references)
        self.assertTrue(version2 in versionBase.references)
    
    def test_save_as_references_to_a_version_in_same_workspace_are_replaced_with_abs_path_with_env_variable(self):
        """testing if the save_as method updates the references paths with an
        absolute path starting with conf.repository_env_key for references to
        a version in the same project thus the referenced path is relative
        """
        
        # create project
        proj1 = Project("Proj1")
        proj1.save()
        proj1.create()
        
        # create assets
        asset1 = Asset(proj1, "Asset 1")
        asset1.save()
        
        # create a version of asset vtype 
        vers1 = Version(asset1, asset1.code, self.asset_vtypes[0], self.user1)
        vers1.save()
        
        # save it
        self.mEnv.save_as(vers1)
        
        # new scene
        pm.newFile(force=True)
        
        # create another version with different type
        vers2 = Version(asset1, asset1.code, self.asset_vtypes[1], self.user1)
        vers2.save()
        
        # reference the other version
        self.mEnv.reference(vers1)
        
        # save it
        self.mEnv.save_as(vers2)
        
        # now check if the referenced vers1 starts with $REPO
        refs = pm.listReferences()
        
        # there should be only one ref
        self.assertTrue(len(refs)==1)
        
        # and the path should start with conf.repository_env_key
        self.assertTrue(
            refs[0].unresolvedPath().startswith("$" + conf.repository_env_key)
        )
    
    def test_save_as_of_a_scene_with_two_references_to_the_same_version(self):
        """testing if the case where the current maya scene has two references
        to the same file is gracefully handled by assigning the version only
        once
        """
        
        # create project
        proj1 = Project("Proj1")
        proj1.save()
        proj1.create()
        
        # create assets
        asset1 = Asset(proj1, "Asset 1")
        asset1.save()
        
        # create a version of asset vtype 
        vers1 = Version(asset1, asset1.code, self.asset_vtypes[0], self.user1)
        vers1.save()
        
        # save it
        self.mEnv.save_as(vers1)
        
        # new scene
        pm.newFile(force=True)
        
        # create another version with different type
        vers2 = Version(asset1, asset1.code, self.asset_vtypes[1], self.user1)
        vers2.save()
        
        # reference the other version twice
        self.mEnv.reference(vers1)
        self.mEnv.reference(vers1)
        
        # save it and expect no InvalidRequestError
        self.mEnv.save_as(vers2)
        
        self.mEnv.reference(vers1)
        vers3 = Version(asset1, asset1.code, self.asset_vtypes[1], self.user1)
        vers3.save()
        
        self.mEnv.save_as(vers3)
    
    def test_save_as_will_not_save_the_file_if_there_are_file_textures_with_local_path(self):
        """testing if save_as will raise a RuntimeError if there are file
        textures with local path
        """
        # create a texture file with local path
        new_texture_file = pm.nt.File()
        # generate a local path
        local_file_full_path = os.path.join(
            tempfile.gettempdir(),
            "temp.png"
        )
        new_texture_file.fileTextureName.set(local_file_full_path)
        
        # now try to save it as a new version and expect a RuntimeError
        self.assertRaises(
            RuntimeError,
            self.mEnv.save_as,
            self.version1
        )
    
    def test_open_updates_the_referenced_versions_list(self):
        """testing if the open method updates the Version.references list with
        the current references list from the Maya
        """

        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        versionBase = Version(**self.kwargs)
        versionBase.save()

        # change the take naem
        self.kwargs["take_name"] = "Take1"
        version1 = Version(**self.kwargs)
        version1.save()

        self.kwargs["take_name"] = "Take2"
        version2 = Version(**self.kwargs)
        version2.save()

        self.kwargs["take_name"] = "Take3"
        version3 = Version(**self.kwargs)
        version3.save()

        # now create scenes with these files
        self.mEnv.save_as(version1)
        self.mEnv.save_as(version2)
        self.mEnv.save_as(version3) # this is the dummy version

        # create a new scene
        pm.newFile(force=True)

        # check if the versionBase.references is an empty list
        self.assertTrue(versionBase.references==[])

        # reference the given versions
        self.mEnv.reference(version1)
        self.mEnv.reference(version2)

        # save it as versionBase
        self.mEnv.save_as(versionBase)

        # now check if versionBase.references is updated
        # this part is already tested in save_as
        self.assertTrue(len(versionBase.references)==2)
        self.assertTrue(version1 in versionBase.references)
        self.assertTrue(version2 in versionBase.references)
        
        # now remove references
        ref_data = self.mEnv.get_referenced_versions()
        for data in ref_data:
            ref_node = data[1]
            ref_node.remove()

        # do a save (not save_as)
        pm.saveFile()
        
        # clean scene
        pm.newFile(force=True)
        
        # open the same asset
        self.mEnv.open_(versionBase, force=True)
        
        # and check the references is updated
        self.assertEqual(len(versionBase.references), 0)
        self.assertEqual(versionBase.references, [])

    def test_open_loads_the_references(self):
        """testing if the open method loads the references
        """

        # create a couple of versions and reference them to each other
        # and reference them to the the scene and check if maya updates the
        # Version.references list

        versionBase = Version(**self.kwargs)
        versionBase.save()

        # change the take naem
        self.kwargs["take_name"] = "Take1"
        version1 = Version(**self.kwargs)
        version1.save()

        self.kwargs["take_name"] = "Take2"
        version2 = Version(**self.kwargs)
        version2.save()

        self.kwargs["take_name"] = "Take3"
        version3 = Version(**self.kwargs)
        version3.save()

        # now create scenes with these files
        self.mEnv.save_as(version1)
        self.mEnv.save_as(version2)
        self.mEnv.save_as(version3) # this is the dummy version

        # create a new scene
        pm.newFile(force=True)

        # check if the versionBase.references is an empty list
        self.assertTrue(versionBase.references==[])

        # reference the given versions
        self.mEnv.reference(version1)
        self.mEnv.reference(version2)
        
        # save it as versionBase
        self.mEnv.save_as(versionBase)

        # clean scene
        pm.newFile(force=True)
        
        # re-open the file
        self.mEnv.open_(versionBase, force=True)
        self.mEnv.post_open(versionBase)
        
        # check if the references are loaded
        ref_data = self.mEnv.get_referenced_versions()
        for data in ref_data:
            ref_node = data[1]
            self.assertTrue(ref_node.isLoaded())
    
    def test_save_as_in_another_project_updates_paths_correctly(self):
        """testing if the external paths are updated correctly if the document
        is created in one maya project but it is saved under another one.
        """
        
        # create a new scene
        # save it under one Asset Version with name Asset1
        
        asset1 = Asset(self.project, "Asset 1")
        asset1.save()
        
        self.kwargs["version_of"] = asset1
        self.kwargs["base_name"] = asset1.code
        version1 = Version(**self.kwargs)
        version1.save()
        
        self.kwargs["take_name"] = "References1"
        version_ref1 = Version(**self.kwargs)
        version_ref1.save()
        
        self.kwargs["take_name"] = "References2"
        version_ref2 = Version(**self.kwargs)
        version_ref2.save()
        
        # save a maya file with this references
        self.mEnv.save_as(version_ref1)
        self.mEnv.save_as(version_ref2)
        
        # save the original version
        self.mEnv.save_as(version1)
        
        # create a couple of file textures
        file_texture1 = pm.createNode("file")
        file_texture2 = pm.createNode("file")
        
        path1 = os.path.dirname(version1.path) +  "/.maya_files/TEXTURES/a.jpg"
        path2 = os.path.dirname(version1.path) +  "/.maya_files/TEXTURES/b.jpg"
        
        # set them to some relative paths
        file_texture1.fileTextureName.set(path1)
        file_texture2.fileTextureName.set(path2)
        
        # create a couple of references in the same project
        self.mEnv.reference(version_ref1)
        self.mEnv.reference(version_ref2)
        
        # save again
        self.mEnv.save_as(version1)

        # then save it under another Asset with name Asset2
        # because with this new system all the Assets folders are a maya
        # project, the references should be updated correctly
        asset2 = Asset(self.project, "Asset 2")
        asset2.save()
        
        # create a new Version for Asset 2
        self.kwargs["version_of"] = asset2
        self.kwargs["base_name"] = asset2.code
        version2 = Version(**self.kwargs)
        
        # now save it under that asset
        self.mEnv.save_as(version2)
        
        # check if the paths are updated
        self.assertEqual(
            file_texture1.fileTextureName.get(),
            "$REPO/TEST_PROJECT/Assets/Asset_1/.maya_files/TEXTURES/a.jpg"
        )

        self.assertEqual(
            file_texture2.fileTextureName.get(),
            "$REPO/TEST_PROJECT/Assets/Asset_1/.maya_files/TEXTURES/b.jpg"
        )
    
    def test_save_as_sets_the_fps(self):
        """testing if the save_as method sets the fps value correctly
        """
        
        # create two projects with different fps values
        # first create a new scene and save it under the first project
        # and then save it under the other project
        # and check if the fps follows the project values
        
        project1 = Project("FPS_TEST_PROJECT_1")
        project1.fps = 24
        project1.create()
        
        project2 = Project("FPS_TEST_PROJECT_2")
        project2.fps = 30
        project2.save()
        
        # create assets
        asset1 = Asset(project1, "Test Asset 1")
        asset1.save()
        
        asset2 = Asset(project2, "Test Asset 2")
        asset2.save()
        
        # create versions
        version1 = Version(
            version_of=asset1,
            base_name=asset1.code,
            type=self.asset_vtypes[0],
            created_by=self.user1
        )
        
        version2 = Version(
            version_of=asset2,
            base_name=asset2.code,
            type=self.asset_vtypes[0],
            created_by=self.user1
        )
        
        # save the current scene for asset1
        self.mEnv.save_as(version1)
        
        # check the fps value
        self.assertEqual(
            self.mEnv.get_fps(),
            24
        )
        
        # now save it for asset2
        self.mEnv.save_as(version2)
        
        # check the fps value
        self.assertEqual(
            self.mEnv.get_fps(),
            30
        )
    
    def test_reference_creates_references_with_paths_starting_with_repository_env_key(self):
        """testing if reference method creates references with unresolved paths
        starting with conf.repository_env_key
        """

        proj1 = Project("Test Project 1")
        proj1.create()
        proj1.save()

        asset1 = Asset(proj1, "Test Asset 1")
        asset1.save()

        vers1 = Version(asset1, asset1.code, self.asset_vtypes[0], self.user1)
        vers1.save()

        vers2 = Version(asset1, asset1.code, self.asset_vtypes[0], self.user1)
        vers2.save()

        self.mEnv.save_as(vers1)

        pm.newFile(force=True)

        self.mEnv.save_as(vers2)

        # refence vers1 to vers2
        self.mEnv.reference(vers1)

        # now check if the referenced files unresolved path is already starting
        # with conf.repository_env_key

        refs = pm.listReferences()

        # there should be only one reference
        self.assertEqual(len(refs), 1)

        # the unresolved path should start with $REPO
        self.assertTrue(
            refs[0].unresolvedPath().startswith("$" + conf.repository_env_key)
        )

        self.assertTrue(refs[0].isLoaded())

    def test_reference_creates_references_to_Versions_in_other_workspaces_loaded(self):
        """testing if reference method creates references to Versions with
        different VersionType and the reference state will be loaded
        """
        
        proj1 = Project("Test Project 1")
        proj1.create()
        proj1.save()
    
        asset1 = Asset(proj1, "Test Asset 1")
        asset1.save()
    
        vers1 = Version(asset1, asset1.code, self.asset_vtypes[0], self.user1)
        vers1.save()
    
        vers2 = Version(asset1, asset1.code, self.asset_vtypes[1], self.user1)
        vers2.save()
    
        self.mEnv.save_as(vers1)
    
        pm.newFile(force=True)
    
        self.mEnv.save_as(vers2)
    
        # refence vers1 to vers2
        self.mEnv.reference(vers1)
    
        # now check if the referenced files unresolved path is already starting
        # with conf.repository_env_key
        
        refs = pm.listReferences()
    
        # there should be only one reference
        self.assertEqual(len(refs), 1)
    
        # the unresolved path should start with $REPO
        self.assertTrue(
            refs[0].unresolvedPath().startswith("$" + conf.repository_env_key)
        )
        
        self.assertTrue(refs[0].isLoaded())
    
    def test_save_as_replaces_imagePlane_filename_with_env_variable(self):
        """testing if save_as replaces the imagePlane filename with repository
        environment variable
        """
        
        # create a camera
        # create an image plane
        # set it to something
        # save the scene
        # check if the path is replaced with repository environment variable
        
        self.fail("test is not implemented yet")
    
    def test_save_as_creates_the_workspace_mel_file_in_the_given_path(self):
        """testing if save_as creates the workspace.mel file in the Asset or
        Shot root
        """
        # check if the workspace.mel file does not exist yet
        workspace_mel_full_path = os.path.join(
            os.path.dirname(self.version1.path),
            'workspace.mel'
        )
        self.assertFalse(os.path.exists(workspace_mel_full_path))
        self.mEnv.save_as(self.version1)
        self.assertTrue(os.path.exists(workspace_mel_full_path))
    
    def test_save_as_creates_the_workspace_fileRule_folders(self):
        """testing if save_as creates the fileRule folders
        """
        # first prove that the folders doesn't exist
        for key in pm.workspace.fileRules.keys():
            file_rule_partial_path = pm.workspace.fileRules[key]
            file_rule_full_path = os.path.join(
                os.path.dirname(self.version1.path),
                file_rule_partial_path
            )
            self.assertFalse(os.path.exists(file_rule_full_path))
        
        self.mEnv.save_as(self.version1)
        
        # save_as and now expect the folders to be created
        for key in pm.workspace.fileRules.keys():
            file_rule_partial_path = pm.workspace.fileRules[key]
            file_rule_full_path = os.path.join(
                os.path.dirname(self.version1.path),
                file_rule_partial_path
            )
            self.assertTrue(os.path.exists(file_rule_full_path))
