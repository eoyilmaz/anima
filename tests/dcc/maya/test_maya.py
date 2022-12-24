# -*- coding: utf-8 -*-

import pytest

import os
import tempfile

from anima import utils

import pymel.core as pm

from stalker import Project, Repository, Asset, Task, Version
from stalker.db.session import DBSession

from tests.dcc.maya.utils import create_version


def test_save_as_creates_a_maya_file_at_version_absolute_full_path(
    create_test_data, create_maya_env
):
    """testing if the save_as creates a maya file at the Version.full_path"""
    data = create_test_data
    maya_env = create_maya_env
    version1 = Version(task=data["task6"])
    version1.extension = ".ma"
    version1.update_paths()

    # check the version file doesn't exist
    assert not os.path.exists(version1.absolute_full_path)

    # save the version
    maya_env.save_as(version1)

    # check the file exists
    assert os.path.exists(version1.absolute_full_path)


def test_save_as_sets_the_version_extension_to_ma(create_test_data, create_maya_env):
    """testing if the save_as method sets the version extension to ma"""
    data = create_test_data
    maya_env = create_maya_env
    version1 = Version(task=data["task6"])
    version1.extension = ".ma"
    version1.update_paths()

    version1.extension = ""
    maya_env.save_as(version1)
    assert version1.extension == ".ma"


def test_save_as_sets_the_render_version_string(create_test_data, create_maya_env):
    """testing if the save_as method sets the version string in the render
    settings
    """
    data = create_test_data
    maya_env = create_maya_env
    version1 = Version(task=data["task1"])
    version1.extension = ".ma"
    version1.update_paths()
    DBSession.add(version1)
    DBSession.commit()

    maya_env.save_as(version1)

    # now check if the render settings version is the same with the
    # version.version_number

    render_version = pm.getAttr("defaultRenderGlobals.renderVersion")
    assert render_version == "v{:03d}".format(version1.version_number)


# def test_save_as_sets_the_render_format_to_exr_for_arnold(
#     create_test_data, create_maya_env
# ):
#     """testing if the save_as method sets the render format to exr when the
#     renderer is arnold
#     """
#     pytest.skip("Creates segfault!")
#     data = create_test_data
#     maya_env = create_maya_env
#     # load mtoa plugin
#     try:
#         pm.loadPlugin("mtoa")
#     except RuntimeError:
#         # no mtoa plugin
#         # pass the test
#         return
#
#     # set the current renderer to arnold
#     dRG = pm.PyNode("defaultRenderGlobals")
#     dRG.setAttr("currentRenderer", "arnold")
#
#     # dirty little maya tricks: do a render to create arnold globals
#     from mtoa.cmds.arnoldRender import arnoldRender
#
#     arnoldRender(10, 10, False, False, "perspShape", " -layer defaultRenderLayer")
#
#     dAD = pm.PyNode("defaultArnoldDriver")
#
#     version1 = Version(task=data["task1"])
#     version1.extension = ".ma"
#     version1.update_paths()
#     DBSession.add(version1)
#     DBSession.commit()
#     maya_env.save_as(version1)
#
#     # now check if the render format is correctly set to exr with zip
#     # compression
#     assert dRG.getAttr("imageFormat") == 51
#     assert dAD.exrCompression.get() == 2  # zips
#     assert dAD.halfPrecision.get() == 1  # half
#     assert dAD.tiled.get() == 0  # not tiled
#     assert dAD.autocrop.get() == 1  # auto crop


def test_save_as_sets_the_render_file_name_for_assets(
    create_test_data, create_maya_env
):
    """testing if the save_as sets the render file name correctly"""
    data = create_test_data
    maya_env = create_maya_env
    version1 = Version(task=data["task6"])
    version1.extension = ".ma"
    version1.update_paths()

    maya_env.save_as(version1)

    # check if the path equals to
    expected_path = (
        "renders/{take_name}/v{version_number:03d}/<RenderLayer>/"
        "{version_nice_name}_v{version_number:03d}_<RenderLayer>_<RenderPass>".format(
            version_path=version1.absolute_path,
            project_code=version1.task.project.code,
            take_name=version1.take_name,
            version_nice_name=version1.nice_name,
            version_number=version1.version_number,
        )
    )

    dRG = pm.PyNode("defaultRenderGlobals")
    assert expected_path == dRG.getAttr("imageFilePrefix")


def test_save_as_sets_the_render_file_name_for_shots(create_test_data, create_maya_env):
    """testing if the save_as sets the render file name correctly"""
    data = create_test_data
    maya_env = create_maya_env

    version1 = Version(task=data["task6"])
    version1.extension = ".ma"
    version1.update_paths()

    maya_env.save_as(version1)

    # check if the path equals to
    expected_path = (
        "renders/{take_name}/v{version_number:03d}/<RenderLayer>/"
        "{version_nice_name}_v{version_number:03d}_<RenderLayer>_<RenderPass>".format(
            version_path=version1.absolute_path,
            take_name=version1.take_name,
            project_code=version1.task.project.code,
            version_nice_name=version1.nice_name,
            version_number=version1.version_number,
        )
    )

    dRG = pm.PyNode("defaultRenderGlobals")
    assert expected_path == dRG.getAttr("imageFilePrefix")


# def test_save_as_replaces_file_image_paths(create_test_data):
#     """testing if save_as method replaces image paths with REPO relative
#     path
#     """
#     maya_env.save_as(data["asset2_model_main_v001"])
#
#     # create file node
#     file_node = pm.createNode("file")
#
#     # set it to a path in the workspace
#     texture_path = os.path.join(
#         pm.workspace.path, ".maya_files/textures/test.jpg"
#     )
#     file_node.fileTextureName.set(texture_path)
#
#     # save a newer version
#     version2 = Version(**data["kwargs"])
#     version2.save()
#
#     maya_env.save_as(version2)
#
#     # now check if the file nodes fileTextureName is converted to a
#     # relative path to the current workspace
#
#     expected_path = texture_path.replace(os.environ["REPO"], "$REPO")
#
#     assert file_node.getAttr("fileTextureName") == expected_path


def test_save_as_sets_the_resolution(create_test_data, create_maya_env):
    """testing if save_as sets the render resolution for the current scene"""
    data = create_test_data
    maya_env = create_maya_env

    version1 = Version(task=data["task1"])
    version1.extension = ".ma"
    version1.update_paths()
    DBSession.add(version1)
    DBSession.commit()

    width = data["project"].image_format.width
    height = data["project"].image_format.height
    pixel_aspect = data["project"].image_format.pixel_aspect

    # save the scene
    maya_env.save_as(version1)

    # check the resolutions
    dRes = pm.PyNode("defaultResolution")
    assert dRes.width.get() == width
    assert dRes.height.get() == height
    assert dRes.pixelAspect.get() == pixel_aspect


def test_save_as_sets_the_resolution_for_every_version(
    create_test_data, create_maya_env
):
    """testing if save_as sets the render resolution for the current scene
    but only for the first version of the asset
    """
    data = create_test_data
    maya_env = create_maya_env

    version1 = Version(task=data["task1"])
    version1.extension = ".ma"
    version1.update_paths()
    DBSession.add(version1)
    DBSession.commit()

    width = data["project"].image_format.width
    height = data["project"].image_format.height
    pixel_aspect = data["project"].image_format.pixel_aspect

    # save the scene
    maya_env.save_as(version1)

    # check the resolutions
    dRes = pm.PyNode("defaultResolution")
    assert dRes.width.get() == width
    assert dRes.height.get() == height
    assert dRes.pixelAspect.get() == pixel_aspect

    new_width = 1280
    new_height = 720
    new_pixel_aspect = 1.0
    dRes.width.set(new_width)
    dRes.height.set(new_height)
    dRes.pixelAspect.set(new_pixel_aspect)

    # save the version again
    new_version = Version(task=data["task1"])
    new_version.extension = ".ma"
    new_version.update_paths()
    DBSession.add(new_version)
    DBSession.commit()

    maya_env.save_as(new_version)

    # test if the resolution is changed back to project resolution
    assert dRes.width.get() == width
    assert dRes.height.get() == height
    assert dRes.pixelAspect.get() == pixel_aspect


def test_save_as_fills_the_referenced_versions_list(create_test_data, create_maya_env):
    """testing if the save_as method updates the Version.inputs list with
    the current references list from the Maya
    """
    # create a couple of versions and reference them to each other
    # and reference them to the scene and check if maya updates the
    # Version.references list
    data = create_test_data
    maya_env = create_maya_env

    version_base = Version(task=data["task6"])
    DBSession.add(version_base)
    DBSession.commit()

    # change the take name
    version1 = Version(task=data["task6"], take_name="Take1")
    DBSession.add(version1)
    DBSession.commit()

    version2 = Version(task=data["task6"], take_name="Take2")
    DBSession.add(version2)
    DBSession.commit()

    version3 = Version(task=data["task6"], take_name="Take3")
    DBSession.add(version3)
    DBSession.commit()

    # now create scenes with these files
    maya_env.save_as(version1)
    maya_env.save_as(version2)
    maya_env.save_as(version3)  # this is the dummy version

    # create a new scene
    pm.newFile(force=True)
    maya_env.save_as(version_base)

    # check if the version_base.inputs is an empty list
    assert version_base.inputs == []

    # reference the given versions
    maya_env.reference(version1)
    maya_env.reference(version2)

    # save it as version_base
    maya_env.save_as(version_base)

    # now check if version_base.references is updated
    assert len(version_base.inputs) == 2

    assert sorted(version_base.inputs, key=lambda x: x.name) == sorted(
        [version1, version2], key=lambda x: x.name
    )


def test_save_as_of_a_scene_with_two_references_to_the_same_version(
    create_test_data, create_maya_env
):
    """testing if the case where the current maya scene has two references
    to the same file is gracefully handled by assigning the version only
    once
    """
    data = create_test_data
    maya_env = create_maya_env

    # create a version for an asset
    vers1 = Version(task=data["asset1"])

    # save it
    maya_env.save_as(vers1)

    # new scene
    pm.newFile(force=True)

    # create another version with different type
    vers2 = Version(task=data["asset1"])
    maya_env.save_as(vers2)

    # reference the other version twice
    maya_env.reference(vers1)
    maya_env.reference(vers1)

    # save it and expect no InvalidRequestError
    maya_env.save_as(vers2)

    # reference again
    maya_env.reference(vers1)

    # save as another version
    vers3 = Version(task=data["asset1"])
    maya_env.save_as(vers3)


def test_save_as_move_external_files_to_project_folder(
    create_test_data, create_maya_env, trash_bin
):
    """testing if save_as will move all the external files to project
    folder under the "external_files" folder
    """
    data = create_test_data
    maya_env = create_maya_env

    # create a texture file with local path
    new_texture_file = pm.nt.File()
    # generate a local path
    local_file_full_path = os.path.join(tempfile.gettempdir(), "temp.png")
    # touch the file
    with open(local_file_full_path, "w"):
        pass

    trash_bin.append(local_file_full_path)
    new_texture_file.fileTextureName.set(local_file_full_path)

    # now save it as a new version
    version1 = Version(task=data["task1"])
    DBSession.add(version1)
    DBSession.commit()

    maya_env.save_as(version1)

    # and expect the fileTexture has been moved to workspace/external_files
    # folder
    expected_path = Repository.to_os_independent_path(
        os.path.join(version1.absolute_path, "external_files/Textures/temp.png")
    )

    assert expected_path == new_texture_file.fileTextureName.get()


def test_open_updates_the_referenced_versions_list(create_test_data, create_maya_env):
    """testing if the open method updates the Version.inputs list with the
    current references list from the Maya
    """
    # create a couple of versions and reference them to each other
    # and reference them to the scene and check if maya updates the
    # Version.references list
    data = create_test_data
    maya_env = create_maya_env

    version_base = Version(task=data["task1"])
    DBSession.add(version_base)
    DBSession.commit()

    # change the take name
    version1 = Version(task=data["task1"], take_name="Take1")
    DBSession.add(version1)
    DBSession.commit()

    version2 = Version(task=data["task1"], take_name="Take2")
    DBSession.add(version2)
    DBSession.commit()

    version3 = Version(task=data["task1"], take_name="Take3")
    DBSession.add(version2)
    DBSession.commit()

    # now create scenes with these files
    maya_env.save_as(version1)
    maya_env.save_as(version2)
    maya_env.save_as(version3)  # this is the dummy version

    # create a new scene
    pm.newFile(force=True)
    maya_env.save_as(version_base)

    # check if the version_base.references is an empty list
    assert [] == version_base.inputs

    # reference the given versions
    maya_env.reference(version1)
    maya_env.reference(version2)

    # save it as version_base
    maya_env.save_as(version_base)

    # now check if version_base.inputs is updated
    # this part is already tested in save_as
    assert 2 == len(version_base.inputs)
    assert sorted(version_base.inputs, key=lambda x: x.name) == sorted(
        [version1, version2], key=lambda x: x.name
    )

    # now remove references
    for ref_node in pm.listReferences():
        ref_node.remove()

    # do a save (not save_as)
    pm.saveFile()

    # clean scene
    pm.newFile(force=True)

    # open the same version
    maya_env.open(version_base, force=True)

    # and check the references is updated
    assert 0 == len(version_base.inputs)
    assert version_base.inputs == []


def test_open_does_not_load_unloaded_references(create_test_data, create_maya_env):
    """testing if the open method doesn't load unloaded references"""
    # create a couple of versions and reference them to each other
    # and reference them to the scene and check if maya updates the
    # Version.references list
    data = create_test_data
    maya_env = create_maya_env

    version_base = Version(task=data["task1"])
    DBSession.add(version_base)
    DBSession.commit()

    # change the take name
    version1 = Version(task=data["task1"], take_name="Take1")
    DBSession.add(version1)
    DBSession.commit()

    version2 = Version(task=data["task1"], take_name="Take2")
    DBSession.add(version2)
    DBSession.commit()

    version3 = Version(task=data["task1"], take_name="Take3")
    DBSession.add(version3)
    DBSession.commit()

    # now create scenes with these files
    maya_env.save_as(version1)
    maya_env.save_as(version2)
    maya_env.save_as(version3)  # this is the dummy version

    # create a new scene
    pm.newFile(force=True)
    maya_env.save_as(version_base)

    # reference the given versions
    maya_env.reference(version1)
    maya_env.reference(version2)

    # unload a couple of them
    refs = pm.listReferences()
    refs[0].unload()
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # save it as versionBase
    maya_env.save_as(version_base)
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # clean scene
    pm.newFile(force=True)

    # re-open the file
    maya_env.open(version_base, force=True)

    # check if the references are loaded
    refs = pm.listReferences()
    assert refs[1].isLoaded()
    assert not refs[0].isLoaded()


def test_open_with_reference_depth_parameter_is_skipped(
    create_test_data, create_maya_env
):
    """testing if the open method doesn't load unloaded references when
    the reference_depth parameter is skipped
    """
    # create a couple of versions and reference them to each other
    # and reference them to the scene and check if maya updates the
    # Version.references list
    data = create_test_data
    maya_env = create_maya_env

    version_base = Version(task=data["task1"])
    DBSession.add(version_base)
    DBSession.commit()

    # change the take name
    version1 = Version(task=data["task1"], take_name="Take1")
    DBSession.add(version1)
    DBSession.commit()

    version2 = Version(task=data["task1"], take_name="Take2")
    DBSession.add(version2)
    DBSession.commit()

    version3 = Version(task=data["task1"], take_name="Take3")
    DBSession.add(version3)
    DBSession.commit()

    # now create scenes with these files
    maya_env.save_as(version1)
    maya_env.save_as(version2)
    maya_env.save_as(version3)  # this is the dummy version

    # create a new scene
    pm.newFile(force=True)
    maya_env.save_as(version_base)

    # reference the given versions
    maya_env.reference(version1)
    maya_env.reference(version2)

    # unload a couple of them
    refs = pm.listReferences()
    refs[0].unload()
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # save it as versionBase
    maya_env.save_as(version_base)
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # clean scene
    pm.newFile(force=True)

    # re-open the file
    maya_env.open(version_base, force=True)

    # check if the references are loaded
    refs = pm.listReferences()
    assert refs[1].isLoaded()
    assert not refs[0].isLoaded()


def test_open_with_reference_depth_parameter_is_0(create_test_data, create_maya_env):
    """testing if the open method doesn't load unloaded references when
    the reference_depth parameter is 0
    """
    # create a couple of versions and reference them to each other
    # and reference them to the scene and check if maya updates the
    # Version.references list
    data = create_test_data
    maya_env = create_maya_env

    version_base = Version(task=data["task1"])
    DBSession.add(version_base)
    DBSession.commit()

    # change the take name
    version1 = Version(task=data["task1"], take_name="Take1")
    DBSession.add(version1)
    DBSession.commit()

    version2 = Version(task=data["task1"], take_name="Take2")
    DBSession.add(version2)
    DBSession.commit()

    version3 = Version(task=data["task1"], take_name="Take3")
    DBSession.add(version3)
    DBSession.commit()

    # now create scenes with these files
    maya_env.save_as(version1)
    maya_env.save_as(version2)
    maya_env.save_as(version3)  # this is the dummy version

    # create a new scene
    pm.newFile(force=True)
    maya_env.save_as(version_base)

    # reference the given versions
    maya_env.reference(version1)
    maya_env.reference(version2)

    # unload a couple of them
    refs = pm.listReferences()
    refs[0].unload()
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # save it as versionBase
    maya_env.save_as(version_base)
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # clean scene
    pm.newFile(force=True)

    # re-open the file
    maya_env.open(version_base, force=True, reference_depth=0)

    # check if the references are loaded
    refs = pm.listReferences()
    assert refs[1].isLoaded()
    assert not refs[0].isLoaded()


def test_open_with_reference_depth_parameter_is_1(create_test_data, create_maya_env):
    """testing if the open method will load all unloaded references when
    the reference_depth parameter is 1
    """
    # create a couple of versions and reference them to each other
    # and reference them to the scene and check if maya updates the
    # Version.references list
    data = create_test_data
    maya_env = create_maya_env

    version_base = Version(task=data["task1"])
    DBSession.add(version_base)
    DBSession.commit()

    # change the take name
    version1 = Version(task=data["task1"], take_name="Take1")
    DBSession.add(version1)
    DBSession.commit()

    version2 = Version(task=data["task1"], take_name="Take2")
    DBSession.add(version2)
    DBSession.commit()

    version3 = Version(task=data["task1"], take_name="Take3")
    DBSession.add(version3)
    DBSession.commit()

    # now create scenes with these files
    maya_env.save_as(version1)
    maya_env.save_as(version2)
    maya_env.save_as(version3)  # this is the dummy version

    # create a new scene
    pm.newFile(force=True)
    maya_env.save_as(version_base)

    # reference the given versions
    maya_env.reference(version1)
    maya_env.reference(version2)

    # unload a couple of them
    refs = pm.listReferences()
    refs[0].unload()
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # save it as versionBase
    maya_env.save_as(version_base)
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # clean scene
    pm.newFile(force=True)

    # re-open the file
    maya_env.open(version_base, force=True, reference_depth=1)

    # check if the references are loaded
    refs = pm.listReferences()
    assert refs[0].isLoaded()
    assert refs[1].isLoaded()


def test_open_with_reference_depth_parameter_is_2(create_test_data, create_maya_env):
    """testing if the open method will load top only references when the
    reference_depth parameter is 2
    """
    # create a couple of versions and reference them to each other
    # and reference them to the scene and check if maya updates the
    # Version.references list
    data = create_test_data
    maya_env = create_maya_env

    version_base = Version(task=data["task1"])
    DBSession.add(version_base)
    DBSession.commit()

    # change the take name
    version1 = Version(task=data["task1"], take_name="Take1")
    DBSession.add(version1)
    DBSession.commit()

    version2 = Version(task=data["task1"], take_name="Take2")
    DBSession.add(version2)
    DBSession.commit()

    version3 = Version(task=data["task1"], take_name="Take3")
    DBSession.add(version3)
    DBSession.commit()

    version4 = Version(task=data["task1"], take_name="Take3")
    DBSession.add(version3)
    DBSession.commit()

    # now create scenes with these files
    maya_env.save_as(version1)
    maya_env.save_as(version2)
    maya_env.save_as(version3)  # this is the dummy version
    maya_env.save_as(version4)

    # reference version4 to version2
    maya_env.open(version2, force=True)
    maya_env.reference(version4)
    pm.saveFile()

    # create a new scene
    pm.newFile(force=True)
    maya_env.save_as(version_base)

    # reference the given versions
    maya_env.reference(version1)
    maya_env.reference(version2)

    # unload a couple of them
    refs = pm.listReferences()
    refs[0].unload()
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # save it as versionBase
    maya_env.save_as(version_base)
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # clean scene
    pm.newFile(force=True)

    # re-open the file
    maya_env.open(version_base, force=True, reference_depth=2)

    # check if the references are loaded
    refs = pm.listReferences(recursive=True)
    assert refs[0].isLoaded()
    assert refs[1].isLoaded()
    assert not refs[2].isLoaded()


def test_open_with_reference_depth_parameter_is_3(create_test_data, create_maya_env):
    """testing if the open method will load none of the references when the
    reference_depth parameter is 3
    """
    # create a couple of versions and reference them to each other
    # and reference them to the scene and check if maya updates the
    # Version.references list
    data = create_test_data
    maya_env = create_maya_env

    version_base = Version(task=data["task1"])
    DBSession.add(version_base)
    DBSession.commit()

    # change the take name
    version1 = Version(task=data["task1"], take_name="Take1")
    DBSession.add(version1)
    DBSession.commit()

    version2 = Version(task=data["task1"], take_name="Take2")
    DBSession.add(version2)
    DBSession.commit()

    version3 = Version(task=data["task1"], take_name="Take3")
    DBSession.add(version3)
    DBSession.commit()

    version4 = Version(task=data["task1"], take_name="Take3")
    DBSession.add(version3)
    DBSession.commit()

    # now create scenes with these files
    maya_env.save_as(version1)
    maya_env.save_as(version2)
    maya_env.save_as(version3)  # this is the dummy version
    maya_env.save_as(version4)

    # reference version4 to version2
    maya_env.open(version2, force=True)
    maya_env.reference(version4)
    pm.saveFile()

    # create a new scene
    pm.newFile(force=True)
    maya_env.save_as(version_base)

    # reference the given versions
    maya_env.reference(version1)
    maya_env.reference(version2)

    # unload a couple of them
    refs = pm.listReferences()
    refs[0].unload()
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # save it as versionBase
    maya_env.save_as(version_base)
    assert not refs[0].isLoaded()
    assert refs[1].isLoaded()

    # clean scene
    pm.newFile(force=True)

    # re-open the file
    maya_env.open(version_base, force=True, reference_depth=3)

    # check if the references are loaded
    refs = pm.listReferences(recursive=True)
    assert not refs[0].isLoaded()
    assert not refs[1].isLoaded()


def test_open_replaces_first_level_reference_paths_with_os_independent_path(
    create_test_data, create_maya_env
):
    """testing if Maya.open() will replace first level reference paths with
    os independent path
    """
    data = create_test_data
    maya_env = create_maya_env

    # create a new reference
    version_base = Version(task=data["task1"])
    DBSession.add(version_base)
    DBSession.commit()

    # change the take name
    version1 = Version(task=data["task1"], take_name="Take1")
    DBSession.add(version1)
    DBSession.commit()

    version2 = Version(task=data["task1"], take_name="Take2")
    DBSession.add(version2)
    DBSession.commit()

    version3 = Version(task=data["task1"], take_name="Take3")
    DBSession.add(version3)
    DBSession.commit()

    # now create scenes with these files
    maya_env.save_as(version1)
    maya_env.save_as(version2)
    maya_env.save_as(version3)  # this is the dummy version

    # create a new scene
    pm.newFile(force=True)

    # save it as a new version
    maya_env.save_as(version_base)

    # reference the given versions
    ref1 = maya_env.reference(version1)
    ref2 = maya_env.reference(version2)

    # convert the path to abs on purpose
    ref1.replaceWith(ref1.path)
    ref2.replaceWith(ref2.path)

    assert "$" not in ref1.unresolvedPath()
    assert "$" not in ref2.unresolvedPath()
    assert ref1.path == ref1.unresolvedPath()
    assert ref2.path == ref2.unresolvedPath()

    # save the file
    pm.saveFile()

    # check if paths are still using absolute paths
    assert ref1.path == ref1.unresolvedPath()
    assert ref2.path == ref2.unresolvedPath()
    assert os.path.isabs(ref1.unresolvedPath())
    assert os.path.isabs(ref2.unresolvedPath())

    # open it with Maya
    pm.newFile(f=True)

    maya_env.open(version_base, force=True)
    references = pm.listReferences()
    ref1 = references[0]
    ref2 = references[1]

    # and expect the path to be os independent again
    assert ref1.path != ref1.unresolvedPath()
    assert ref2.path != ref2.unresolvedPath()
    assert not os.path.isabs(ref1.unresolvedPath())
    assert not os.path.isabs(ref2.unresolvedPath())
    assert "$" in ref1.unresolvedPath()
    assert "$" in ref2.unresolvedPath()


def test_open_will_open_the_requested_representations_of_the_first_level_references(
    create_test_data, create_maya_env
):
    """testing if Maya.open() will open with the requested representations
    of the first level references
    """
    # create three different versions
    # create both a Base and a BBox representation for each of them
    data = create_test_data
    maya_env = create_maya_env

    # Base repr
    a_base_v1 = create_version(data["asset1"], "Main")

    a_base_v2 = create_version(data["asset1"], "Main")
    a_base_v2.is_published = True

    a_base_v3 = create_version(data["asset1"], "Main")
    a_base_v3.is_published = True

    # BBox repr
    a_bbox_v1 = create_version(data["asset1"], "Main@BBox", a_base_v3)

    a_bbox_v2 = create_version(data["asset1"], "Main@BBox", a_base_v3)
    a_bbox_v2.is_published = True

    a_bbox_v3 = create_version(data["asset1"], "Main@BBox", a_base_v3)
    a_bbox_v3.is_published = True

    # a new series of versions
    # Base repr
    b_base_v1 = create_version(data["asset1"], "Main")

    b_base_v2 = create_version(data["asset1"], "Main")
    b_base_v2.is_published = True

    b_base_v3 = create_version(data["asset1"], "Main")
    b_base_v3.is_published = True

    # BBox repr
    b_bbox_v1 = create_version(data["asset1"], "Main@BBox", b_base_v3)

    b_bbox_v2 = create_version(data["asset1"], "Main@BBox", b_base_v3)
    b_bbox_v2.is_published = True

    b_bbox_v3 = create_version(data["asset1"], "Main@BBox", b_base_v3)
    b_bbox_v3.is_published = True

    # and another one
    # a new series of versions
    # Base repr
    c_base_v1 = create_version(data["asset1"], "Main")

    c_base_v2 = create_version(data["asset1"], "Main")
    c_base_v2.is_published = True

    c_base_v3 = create_version(data["asset1"], "Main")
    c_base_v3.is_published = True

    # BBox repr
    c_bbox_v1 = create_version(data["asset1"], "Main@BBox", c_base_v3)

    c_bbox_v2 = create_version(data["asset1"], "Main@BBox", c_base_v3)
    c_bbox_v2.is_published = True

    c_bbox_v3 = create_version(data["asset1"], "Main@BBox", c_base_v3)
    c_bbox_v3.is_published = True

    # save it as a new version
    base_version = create_version(data["task1"], "Main")

    # reference the Base versions of each of them to this new scene
    maya_env.reference(a_base_v3)
    maya_env.reference(b_base_v3)
    maya_env.reference(c_base_v3)

    # expect all the references to be Base representations
    all_refs = pm.listReferences()
    assert all_refs[0].is_repr("Base")
    assert all_refs[1].is_repr("Base")
    assert all_refs[2].is_repr("Base")

    # save it again
    maya_env.save_as(base_version)

    # new scene
    pm.newFile(force=1)

    # open the same version with requesting the BBox representation
    maya_env.open(base_version, representation="BBox")

    # expect all the references to be BBox representations
    all_refs = pm.listReferences()
    assert all_refs[0].is_repr("BBox")
    assert all_refs[1].is_repr("BBox")
    assert all_refs[2].is_repr("BBox")


def test_save_as_in_another_project_updates_paths_correctly(
    create_test_data, create_maya_env
):
    """testing if the external paths are updated correctly if the document
    is created in one maya project, but it is saved under another one.
    """
    # create a new scene
    # save it under one Asset Version with name Asset1
    data = create_test_data
    maya_env = create_maya_env

    asset1 = Asset(
        name="Asset1", code="Ass1", type=data["character_type"], project=data["project"]
    )
    DBSession.add(asset1)
    DBSession.commit()

    version1 = Version(task=asset1)
    DBSession.add(version1)
    DBSession.commit()

    version_ref1 = Version(task=asset1, take_name="References1")
    DBSession.add(version_ref1)
    DBSession.commit()

    version_ref2 = Version(task=asset1, take_name="References2")
    DBSession.add(version_ref2)
    DBSession.commit()

    # save a maya file with this references
    pm.newFile(f=True)
    maya_env.save_as(version_ref1)
    maya_env.save_as(version_ref2)

    # save the original version
    maya_env.save_as(version1)

    # create a couple of file textures
    file_texture1 = pm.createNode("file")
    file_texture2 = pm.createNode("file")

    path1 = Repository.to_os_independent_path(
        os.path.join(version1.absolute_path, ".maya_files/TEXTURES/a.jpg")
    )
    path2 = Repository.to_os_independent_path(
        os.path.join(version1.absolute_path, ".maya_files/TEXTURES/b.jpg")
    )

    # set them to some relative paths
    file_texture1.fileTextureName.set(path1)
    file_texture2.fileTextureName.set(path2)

    # create a couple of references in the same project
    maya_env.reference(version_ref1)
    maya_env.reference(version_ref2)

    # save again
    maya_env.save_as(version1)

    # then save it under another Asset with name Asset2
    # because with this new system all the Assets folders are a maya
    # project, the references should be updated correctly
    asset2 = Asset(
        name="Asset2", code="Ass2", type=data["character_type"], project=data["project"]
    )
    DBSession.add(asset2)
    DBSession.commit()

    # create a new Version for Asset 2
    version2 = Version(task=asset2)

    # now save it under that asset
    maya_env.save_as(version2)

    # check the file paths they should stay intact
    # because they are already under the repository so no need to change
    # the path
    assert file_texture1.fileTextureName.get() == path1
    assert file_texture2.fileTextureName.get() == path2


def test_save_as_sets_the_fps(create_test_data, create_maya_env):
    """testing if the save_as method sets the fps value correctly"""
    # create two projects with different fps values
    # first create a new scene and save it under the first project
    # and then save it under the other project
    # and check if the fps follows the project values
    data = create_test_data
    maya_env = create_maya_env

    project1 = Project(
        name="FPS Test Project 1",
        code="FTP1",
        status_list=data["project_status_list"],
        structure=data["structure"],
        repositories=[data["repo1"]],
        fps=24,
        image_format=data["image_format"],
    )
    DBSession.add(project1)

    project2 = Project(
        name="FPS Test Project 2",
        code="FTP2",
        status_list=data["project_status_list"],
        structure=data["structure"],
        repositories=[data["repo1"]],
        fps=30,
        image_format=data["image_format"],
    )
    DBSession.add(project2)

    # create assets
    asset1 = Asset(
        name="Test Asset 1", code="TA1", project=project1, type=data["character_type"]
    )
    DBSession.add(asset1)

    asset2 = Asset(
        name="Test Asset 2", code="TA2", project=project2, type=data["character_type"]
    )
    DBSession.add(asset2)
    DBSession.commit()

    # create versions
    version1 = Version(task=asset1, created_by=data["user1"])
    DBSession.add(version1)
    DBSession.commit()

    version2 = Version(task=asset2, created_by=data["user1"])
    DBSession.add(version2)
    DBSession.commit()

    # save the current scene for asset1
    maya_env.save_as(version1)

    # check the fps value
    assert maya_env.get_fps() == 24

    # now save it for asset2
    maya_env.save_as(version2)

    # check the fps value
    assert maya_env.get_fps() == 30


def test_reference_creates_references_with_absolute_paths_containing_env_var(
    create_test_data, create_maya_env
):
    """testing if reference method creates references with unresolved paths
    are absolute paths containing repo env var
    """
    data = create_test_data
    maya_env = create_maya_env

    vers1 = Version(task=data["asset1"], created_by=data["user1"])
    DBSession.add(vers1)
    DBSession.commit()

    vers2 = Version(task=data["asset1"], created_by=data["user1"])
    DBSession.add(vers2)
    DBSession.commit()

    maya_env.save_as(vers1)

    pm.newFile(force=True)
    maya_env.save_as(vers2)

    # reference vers1 to vers2
    ref = maya_env.reference(vers1)

    # now check if the referenced files unresolved path is equal to
    # ver2.absolute_full_path
    refs = pm.listReferences()

    # there should be only one reference
    assert len(refs) == 1

    # the unresolved path should be an absolute path
    assert (
        Repository.to_os_independent_path(vers1.absolute_full_path)
        == ref.unresolvedPath()
    )

    assert ref.isLoaded()


def test_reference_creates_references_of_representations_with_correct_namespace(
    create_test_data, create_maya_env
):
    """testing if references of representations will be referenced with
    correct namespace
    """
    data = create_test_data
    maya_env = create_maya_env

    pm.newFile(force=True)
    a_base_v3 = create_version(data["asset1"], "Main")
    a_bbox_v1 = create_version(data["asset1"], "Main@BBox", a_base_v3)
    some_other_version = create_version(data["asset2"], "Main")
    pm.newFile(force=True)
    maya_env.save_as(some_other_version)

    ref = maya_env.reference(a_bbox_v1)
    assert ref.namespace == os.path.basename(a_base_v3.nice_name)


def test_save_as_replaces_image_plane_filename_with_env_variable(
    create_test_data, create_maya_env
):
    """testing if save_as replaces the imagePlane filename with repository
    environment variable
    """
    data = create_test_data
    maya_env = create_maya_env

    absolute_path = os.path.join(data["asset1"].absolute_path, "Plate/plateA.1.jpg")

    # create an image plane
    image_plane = pm.createNode("imagePlane")

    # and set the path to something absolute
    image_plane.setAttr("imageName", absolute_path)

    vers1 = Version(task=data["asset1"], created_by=data["user1"])
    DBSession.add(vers1)
    DBSession.commit()

    # save the scene
    maya_env.save_as(vers1)

    # check if the path is replaced with repository environment variable
    assert Repository.to_os_independent_path(absolute_path) == image_plane.getAttr(
        "imageName"
    )


def test_save_as_will_even_replace_paths_if_they_are_referenced(
    create_test_data, create_maya_env
):
    """testing if save_as will even replace external paths of referenced
    nodes
    """
    data = create_test_data
    maya_env = create_maya_env

    absolute_path = os.path.normpath(
        os.path.join(data["asset1"].absolute_path, "Plate/plateA.1.jpg")
    )

    normal_path = os.path.normpath(
        os.path.join(data["asset1"].path, "Plate/plateA.1.jpg")
    )

    # create an image plane
    image_plane = pm.createNode("imagePlane")

    # and set the path to something absolute
    image_plane.setAttr("imageName", absolute_path)

    vers1 = Version(task=data["asset1"], created_by=data["user1"])
    DBSession.add(vers1)
    DBSession.commit()

    # save the scene
    maya_env.save_as(vers1)

    # re-set to absolute path
    image_plane.setAttr("imageName", absolute_path)

    # save again
    pm.saveFile()

    assert image_plane.getAttr("imageName") == absolute_path

    vers2 = Version(task=data["asset1"], created_by=data["user1"])
    DBSession.add(vers2)
    DBSession.commit()

    # save the scene as a different version
    pm.newFile(f=1)
    maya_env.save_as(vers2)
    maya_env.reference(vers1)
    maya_env.save_as(vers2)

    image_plane = pm.ls(type="imagePlane")[0]

    # check if the path is not replaced
    assert os.path.normpath(normal_path) == os.path.normpath(
        image_plane.getAttr("imageName")
    )


def test_save_as_creates_the_workspace_mel_file_in_the_given_path(
    create_test_data, create_maya_env
):
    """testing if save_as creates the workspace.mel file in the Asset or
    Shot root
    """
    data = create_test_data
    maya_env = create_maya_env

    task6 = Task(name="Test Task 6 - New", parent=data["task1"])
    DBSession.add(task6)
    DBSession.commit()

    version1 = Version(task=task6)
    version1.extension = ".ma"
    version1.update_paths()

    # check if the workspace.mel file does not exist yet
    workspace_mel_full_path = os.path.join(version1.absolute_path, "workspace.mel")
    assert not os.path.exists(workspace_mel_full_path)
    maya_env.save_as(version1)
    assert os.path.exists(workspace_mel_full_path)


def test_save_as_creates_the_workspace_file_rule_folders(
    create_test_data, create_maya_env
):
    """testing if save_as creates the fileRule folders"""
    data = create_test_data
    maya_env = create_maya_env

    task6 = Task(name="Test Task 6 - New", parent=data["task1"])
    DBSession.add(task6)
    DBSession.commit()

    version1 = Version(task=task6)
    version1.extension = ".ma"
    version1.update_paths()

    # first prove that the folders doesn't exist
    for key in pm.workspace.fileRules.keys():
        file_rule_partial_path = pm.workspace.fileRules.get(key)
        if not file_rule_partial_path:
            continue
        file_rule_full_path = os.path.join(
            version1.absolute_path, file_rule_partial_path
        )
        assert not os.path.exists(file_rule_full_path)

    maya_env.save_as(version1)

    # save_as and now expect the folders to be created
    for key in pm.workspace.fileRules.keys():
        file_rule_partial_path = pm.workspace.fileRules.get(key)
        if not file_rule_partial_path:
            continue
        file_rule_full_path = os.path.join(
            version1.absolute_path, file_rule_partial_path
        )
        assert os.path.exists(file_rule_full_path)


def test_is_in_repo_working_properly(create_test_data, create_maya_env):
    """testing if Maya.is_in_repo() is working properly"""
    data = create_test_data
    maya_env = create_maya_env
    repo_path = data["repo1"].path

    assert maya_env.is_in_repo(repo_path)
    assert maya_env.is_in_repo(os.path.join(repo_path, "a.txt"))
    assert not maya_env.is_in_repo(
        os.path.normpath(os.path.join(repo_path, "../a.txt"))
    )


def test_move_to_local_is_working_properly(
    create_test_data, create_maya_env, trash_bin
):
    """testing if Maya.move_to_local is working properly"""
    data = create_test_data
    maya_env = create_maya_env

    # create a couple of files in some other directories than repo
    another_tmp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(another_tmp_dir, "test.png")

    with open(temp_file_path, "w"):
        pass

    # add the file to be cleaned up list
    trash_bin.append(temp_file_path)
    trash_bin.append(another_tmp_dir)

    # now create a version and move the file to the local path of this
    # version
    version = Version(task=data["task1"])
    version.extension = ".ma"
    version.update_paths()
    DBSession.add(version)
    DBSession.commit()

    new_path = maya_env.move_to_local(version, temp_file_path, "Textures")
    trash_bin.append(new_path)

    # check if the file is there
    assert os.path.exists(new_path)


def test_update_first_level_versions_does_not_update_namespaces(
    create_test_data, create_maya_env
):
    """testing if update_first_level_versions method does not updates
    namespaces
    """
    data = create_test_data
    maya_env = create_maya_env

    vers1 = Version(task=data["asset1"], created_by=data["user1"])
    DBSession.add(vers1)
    DBSession.commit()

    vers2 = Version(task=data["asset1"], created_by=data["user1"], take_name="A")
    vers2.is_published = True
    DBSession.add(vers2)
    DBSession.commit()

    vers3 = Version(task=data["asset1"], created_by=data["user1"], take_name="A")
    vers3.is_published = True
    DBSession.add(vers3)
    DBSession.commit()

    pm.newFile(force=True)
    maya_env.save_as(vers2)

    pm.newFile(force=True)
    maya_env.save_as(vers3)

    maya_env.save_as(vers1)

    # reference vers2 to vers1
    maya_env.reference(vers2)

    # now check if the referenced files unresolved path is equal to
    # ver2.absolute_full_path
    refs = pm.listReferences()

    # there should be only one reference
    assert len(refs) == 1

    # the unresolved path should be an absolute path
    assert vers2.absolute_full_path == refs[0].path

    assert refs[0].isLoaded()

    # update version to the latest published version
    reference_resolution = {
        "root": [vers2],
        "create": [vers1],
        "update": [vers2],
        "leave": [],
    }
    maya_env.update_first_level_versions(reference_resolution)

    # now check if the reference is updated and the namespace is set
    # correctly
    refs = pm.listReferences()
    assert vers3.absolute_full_path == refs[0].path
    assert refs[0].namespace == vers2.nice_name
