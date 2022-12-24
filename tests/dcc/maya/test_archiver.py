# -*- coding: utf-8 -*-

import logging
import os
import tempfile

from anima.dcc.mayaEnv.archive import Archiver

logger = logging.getLogger("anima.dcc.mayaEnv.archive")
logger.setLevel(logging.WARNING)


def test_create_default_project_will_create_a_folder(trash_bin):
    """testing if the create_default_project will create a default maya project
    structure and return the path.
    """
    arch = Archiver()
    tempdir = tempfile.gettempdir()

    project_path = arch.create_default_project(tempdir)
    trash_bin.append(project_path)

    assert os.path.exists(project_path)


def test_create_default_project_will_create_a_workspace_mel_file(
    create_test_data, trash_bin
):
    """testing if the create_default_project will create a default maya project
    structure with a proper workspace.mel
    """
    arch = Archiver()
    tempdir = tempfile.gettempdir()

    project_path = arch.create_default_project(tempdir)
    trash_bin.append(project_path)

    workspace_mel_path = os.path.join(project_path, "workspace.mel")

    assert os.path.exists(workspace_mel_path)


def test_create_default_project_workspace_mel_content_is_correct(
    create_test_data, trash_bin
):
    """testing if the content of the workspace.mel file is correct when the
    create_default_project method is used.
    """
    arch = Archiver()
    tempdir = tempfile.gettempdir()

    project_path = arch.create_default_project(tempdir)
    trash_bin.append(project_path)

    workspace_mel_path = os.path.join(project_path, "workspace.mel")

    with open(workspace_mel_path) as f:
        content = f.read()

    expected_result = """// Anima Archiver Default Project Definition

workspace -fr "translatorData" "data";
workspace -fr "offlineEdit" "scenes/edits";
workspace -fr "renderData" "renderData";
workspace -fr "scene" "scenes";
workspace -fr "3dPaintTextures" "sourceimages/3dPaintTextures";
workspace -fr "eps" "data";
workspace -fr "OBJexport" "data";
workspace -fr "mel" "scripts";
workspace -fr "furShadowMap" "renderData/fur/furShadowMap";
workspace -fr "particles" "cache/particles";
workspace -fr "audio" "sound";
workspace -fr "scripts" "scripts";
workspace -fr "sound" "sound";
workspace -fr "DXF_FBX export" "data";
workspace -fr "furFiles" "renderData/fur/furFiles";
workspace -fr "depth" "renderData/depth";
workspace -fr "autoSave" "autosave";
workspace -fr "furAttrMap" "renderData/fur/furAttrMap";
workspace -fr "diskCache" "data";
workspace -fr "fileCache" "cache/nCache";
workspace -fr "ASS Export" "data";
workspace -fr "FBX export" "data";
workspace -fr "sourceImages" "sourceimages";
workspace -fr "FBX" "data";
workspace -fr "DAE_FBX export" "data";
workspace -fr "movie" "movies";
workspace -fr "Alembic" "data";
workspace -fr "DAE_FBX" "data";
workspace -fr "iprImages" "renderData/iprImages";
workspace -fr "mayaAscii" "scenes";
workspace -fr "furImages" "renderData/fur/furImages";
workspace -fr "furEqualMap" "renderData/fur/furEqualMap";
workspace -fr "illustrator" "data";
workspace -fr "DXF_FBX" "data";
workspace -fr "mayaBinary" "scenes";
workspace -fr "move" "data";
workspace -fr "images" "images";
workspace -fr "fluidCache" "cache/nCache/fluid";
workspace -fr "clips" "clips";
workspace -fr "ASS" "data";
workspace -fr "OBJ" "data";
workspace -fr "templates" "assets";
workspace -fr "shaders" "renderData/shaders";
"""
    assert content == expected_result


def test_create_default_project_workspace_mel_already_exists(
    create_test_data, trash_bin
):
    """testing if no error will be raised when the workspace.mel file is
    already there
    """
    data = create_test_data
    arch = Archiver()
    tempdir = tempfile.gettempdir()

    # there should be no error to call it multiple times
    project_path = arch.create_default_project(tempdir)
    trash_bin.append(project_path)

    project_path = arch.create_default_project(tempdir)
    project_path = arch.create_default_project(tempdir)


def test_flatten_is_working_properly_with_no_references(create_test_data, trash_bin):
    """testing if the Archiver.flatten() is working properly for a scene
    with no references.
    """
    data = create_test_data
    arch = Archiver()
    project_path = arch.flatten(data["asset2_model_main_v001"].absolute_full_path)
    trash_bin.append(project_path)

    # the returned path should be a maya project directory
    assert os.path.exists(project_path)

    # there should be a workspace.mel file
    assert os.path.exists(os.path.join(project_path, "workspace.mel"))

    # there should be a maya scene file under path/scenes with the same
    # name of the source file
    assert os.path.exists(
        os.path.join(project_path, "scenes", data["asset2_model_main_v001"].filename)
    )


def test_flatten_is_working_properly_with_only_one_level_of_references(
    create_test_data, trash_bin, create_pymel, create_maya_env
):
    """testing if the Archiver.flatten() is working properly for a scene
    with only one level of references.
    """
    data = create_test_data
    maya_env = create_maya_env
    pm = create_pymel
    # open data["asset2_model_main_v001"]
    maya_env.open(data["asset2_model_main_v001"], force=True)

    # and reference data["asset2_model_take1_v001"] to it
    maya_env.reference(data["asset2_model_take1_v001"])

    # and save it
    pm.saveFile()

    # renew the scene
    pm.newFile(force=1)

    # create an archiver
    arch = Archiver()

    project_path = arch.flatten(data["asset2_model_main_v001"].absolute_full_path)
    trash_bin.append(project_path)

    # now check if we have two files under the path/scenes directory
    archived_version1_path = os.path.join(
        project_path, "scenes", data["asset2_model_main_v001"].filename
    )

    archived_version4_unresolved_path = os.path.join(
        "scenes/refs", data["asset2_model_take1_v001"].filename
    )

    archived_version4_path = os.path.join(
        project_path, archived_version4_unresolved_path
    )

    assert os.path.exists(archived_version1_path)
    assert os.path.exists(archived_version4_path)

    # open the archived version1
    pm.workspace.open(project_path)
    pm.openFile(archived_version1_path)

    # expect it to have one reference
    all_refs = pm.listReferences()
    assert len(all_refs) == 1

    # and the path is matching to archived version4 path
    ref = all_refs[0]
    assert ref.path == archived_version4_path
    assert ref.unresolvedPath() == archived_version4_unresolved_path


def test_flatten_is_working_properly_with_only_one_level_of_multiple_references_to_the_same_file(
    create_test_data, trash_bin, create_pymel, create_maya_env
):
    """testing if the Archiver.flatten() is working properly for a scene
    with only one level of multiple references to the same file.
    """
    data = create_test_data
    maya_env = create_maya_env
    pm = create_pymel
    # open data["asset2_model_main_v001"]
    maya_env.open(data["asset2_model_main_v001"], force=True)

    # and reference data["asset2_model_take1_v001"] more than once to it
    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v001"])

    # and save it
    pm.saveFile()

    # renew the scene
    pm.newFile(force=1)

    # create an archiver
    arch = Archiver()

    project_path = arch.flatten(data["asset2_model_main_v001"].absolute_full_path)
    trash_bin.append(project_path)

    # now check if we have two files under the path/scenes directory
    archived_version1_path = os.path.join(
        project_path, "scenes", data["asset2_model_main_v001"].filename
    )

    archived_version4_unresolved_path = os.path.join(
        "scenes/refs", data["asset2_model_take1_v001"].filename
    )

    archived_version4_path = os.path.join(
        project_path, archived_version4_unresolved_path
    )

    assert os.path.exists(archived_version1_path)
    assert os.path.exists(archived_version4_path)

    # open the archived version1
    pm.workspace.open(project_path)
    pm.openFile(archived_version1_path)

    # expect it to have three references
    all_refs = pm.listReferences()
    assert len(all_refs) == 3

    # and the path is matching to archived version4 path
    ref = all_refs[0]
    assert ref.path == archived_version4_path
    assert ref.unresolvedPath() == archived_version4_unresolved_path

    ref = all_refs[1]
    assert ref.path == archived_version4_path
    assert ref.unresolvedPath() == archived_version4_unresolved_path

    ref = all_refs[2]
    assert ref.path == archived_version4_path
    assert ref.unresolvedPath() == archived_version4_unresolved_path


def test_flatten_is_working_properly_with_multiple_level_of_references(
    create_test_data, trash_bin, create_pymel, create_maya_env
):
    """testing if the Archiver.flatten() is working properly for a scene
    with multiple levels of references.
    """
    data = create_test_data
    maya_env = create_maya_env
    pm = create_pymel
    # open data["asset2_model_take1_v001"]
    maya_env.open(data["asset2_model_take1_v001"], force=True)

    # and reference data["version7"] to it
    maya_env.reference(data["version7"])

    # and save it
    pm.saveFile()

    # open data["asset2_model_main_v001"]
    maya_env.open(data["asset2_model_main_v001"], force=True)

    # and reference data["asset2_model_take1_v001"] to it
    maya_env.reference(data["asset2_model_take1_v001"])

    # and save it
    pm.saveFile()

    # renew the scene
    pm.newFile(force=1)

    # create an archiver
    arch = Archiver()

    project_path = arch.flatten(data["asset2_model_main_v001"].absolute_full_path)
    trash_bin.append(project_path)

    # now check if we have two files under the path/scenes directory
    archived_version1_path = os.path.join(
        project_path, "scenes", data["asset2_model_main_v001"].filename
    )

    archived_version4_path = os.path.join(
        project_path, "scenes/refs", data["asset2_model_take1_v001"].filename
    )

    archived_version4_unresolved_path = os.path.join(
        "scenes/refs", data["asset2_model_take1_v001"].filename
    )

    archived_version7_path = os.path.join(
        project_path, "scenes/refs", data["version7"].filename
    )

    archived_version7_unresolved_path = os.path.join(
        "scenes/refs", data["version7"].filename
    )

    assert os.path.exists(archived_version1_path)
    assert os.path.exists(archived_version4_path)
    assert os.path.exists(archived_version7_path)

    # open the archived version1
    pm.workspace.open(project_path)
    pm.openFile(archived_version1_path)

    # expect it to have one reference
    all_refs = pm.listReferences()
    assert len(all_refs) == 1

    # and the path is matching to archived version4 path
    ref = all_refs[0]
    assert ref.path == archived_version4_path
    assert ref.unresolvedPath() == archived_version4_unresolved_path

    # check the deeper level references
    deeper_ref = pm.listReferences(parentReference=ref)[0]
    assert deeper_ref.path == archived_version7_path
    assert deeper_ref.unresolvedPath() == archived_version7_unresolved_path


def test_flatten_is_working_properly_with_the_external_files_of_the_references(
    create_test_data, trash_bin, create_pymel, create_maya_env
):
    """testing if the Archiver.flatten() is working properly for a scene
    with references that has external files like textures, sound etc.
    """
    data = create_test_data
    maya_env = create_maya_env
    pm = create_pymel
    # open data["version7"]
    maya_env.open(data["version7"], force=True)

    # create an image file at the project root
    image_filename = "test.jpg"
    image_path = os.path.join(data["version7"].absolute_path, "..", "sourceimages")
    image_full_path = os.path.join(image_path, image_filename)

    # create the file
    os.makedirs(image_path, exist_ok=True)
    with open(image_full_path, "w+") as f:
        f.writelines([""])

    audio_filename = "test.wav"
    audio_path = os.path.join(data["version7"].absolute_path, "sound")
    audio_full_path = os.path.join(audio_path, audio_filename)

    # create the file
    os.makedirs(audio_path, exist_ok=True)
    with open(audio_full_path, "w+") as f:
        f.writelines([""])

    # create one image and one audio node
    pm.createNode("file").attr("fileTextureName").set(image_full_path)
    pm.createNode("audio").attr("filename").set(audio_full_path)

    # save it
    # replace external paths
    maya_env.replace_external_paths()
    pm.saveFile()

    # open data["asset2_model_take1_v001"]
    maya_env.open(data["asset2_model_take1_v001"], force=True)

    # and reference data["version7"] to it
    maya_env.reference(data["version7"])

    # and save it
    pm.saveFile()

    # open data["asset2_model_main_v001"]
    maya_env.open(data["asset2_model_main_v001"], force=True)

    # and reference data["asset2_model_take1_v001"] to it
    maya_env.reference(data["asset2_model_take1_v001"])

    # and save it
    pm.saveFile()

    # renew the scene
    pm.newFile(force=1)

    # create an archiver
    arch = Archiver()

    project_path = arch.flatten(data["asset2_model_main_v001"].absolute_full_path)
    trash_bin.append(project_path)

    # now check if we have the files under the path/scenes directory
    archived_version1_path = os.path.join(
        project_path, "scenes", data["asset2_model_main_v001"].filename
    )

    # and references under path/scenes/refs path
    archived_version4_path = os.path.join(
        project_path, "scenes/refs", data["asset2_model_take1_v001"].filename
    )

    archived_version4_unresolved_path = os.path.join(
        "scenes/refs", data["asset2_model_take1_v001"].filename
    )

    archived_version7_path = os.path.join(
        project_path, "scenes/refs", data["version7"].filename
    )

    archived_version7_unresolved_path = os.path.join(
        "scenes/refs", data["version7"].filename
    )

    archived_image_path = os.path.join(project_path, "sourceimages", image_filename)
    archived_audio_path = os.path.join(project_path, "sound", audio_filename)

    assert os.path.exists(archived_version1_path)
    assert os.path.exists(archived_version4_path)
    assert os.path.exists(archived_version7_path)
    assert os.path.exists(archived_image_path)
    assert os.path.exists(archived_audio_path)

    # open the archived version1
    pm.workspace.open(project_path)
    pm.openFile(archived_version1_path)

    # expect it to have one reference
    all_refs = pm.listReferences()
    assert len(all_refs) == 1

    # and the path is matching to archived version4 path
    ref = all_refs[0]
    assert ref.path == archived_version4_path
    assert ref.unresolvedPath() == archived_version4_unresolved_path

    # check the deeper level references
    deeper_ref = pm.listReferences(parentReference=ref)[0]
    assert deeper_ref.path == archived_version7_path
    assert deeper_ref.unresolvedPath() == archived_version7_unresolved_path

    # and deeper level files
    ref_image_path = pm.ls(type="file")[0].attr("fileTextureName").get()
    assert ref_image_path == os.path.join(project_path, "sourceimages", image_filename)
    ref_audio_path = pm.ls(type="audio")[0].attr("filename").get()
    assert ref_audio_path == os.path.join(project_path, "sound", audio_filename)


def test_flatten_is_working_properly_with_exclude_mask(
    create_test_data, trash_bin, create_pymel, create_maya_env
):
    """testing if the Archiver.flatten() is working properly for a scene
    with references that has external files like textures, sound etc. and
    there is also an exclude_mask
    """
    data = create_test_data
    maya_env = create_maya_env
    pm = create_pymel
    # open data["version7"]
    maya_env.open(data["version7"], force=True)

    # create an image file at the project root
    image_filename = "test.jpg"
    image_path = os.path.join(data["version7"].absolute_path, "..", "sourceimages")
    image_full_path = os.path.join(image_path, image_filename)

    # create the file
    os.makedirs(image_path, exist_ok=True)
    with open(image_full_path, "w+") as f:
        f.writelines([""])

    audio_filename = "test.wav"
    audio_path = os.path.join(data["version7"].absolute_path, "sound")
    audio_full_path = os.path.join(audio_path, audio_filename)

    # create the file
    os.makedirs(audio_path, exist_ok=True)
    with open(audio_full_path, "w+") as f:
        f.writelines([""])

    # create one image and one audio node
    pm.createNode("file").attr("fileTextureName").set(image_full_path)
    pm.createNode("audio").attr("filename").set(audio_full_path)

    # save it
    # replace external paths
    maya_env.replace_external_paths()
    pm.saveFile()

    # open data["asset2_model_take1_v001"]
    maya_env.open(data["asset2_model_take1_v001"], force=True)

    # and reference data["version7"] to it
    maya_env.reference(data["version7"])

    # and save it
    pm.saveFile()

    # open data["asset2_model_main_v001"]
    maya_env.open(data["asset2_model_main_v001"], force=True)

    # and reference data["asset2_model_take1_v001"] to it
    maya_env.reference(data["asset2_model_take1_v001"])

    # and save it
    pm.saveFile()

    # renew the scene
    pm.newFile(force=1)

    # create an archiver
    arch = Archiver(exclude_mask=[".png", ".jpg", ".tga"])

    project_path = arch.flatten(data["asset2_model_main_v001"].absolute_full_path)
    trash_bin.append(project_path)

    # now check if we have the files under the path/scenes directory
    archived_version1_path = os.path.join(
        project_path, "scenes", data["asset2_model_main_v001"].filename
    )

    # and references under path/scenes/refs path
    archived_version4_path = os.path.join(
        project_path, "scenes/refs", data["asset2_model_take1_v001"].filename
    )

    archived_version4_unresolved_path = os.path.join(
        "scenes/refs", data["asset2_model_take1_v001"].filename
    )

    archived_version7_path = os.path.join(
        project_path, "scenes/refs", data["version7"].filename
    )

    archived_version7_unresolved_path = os.path.join(
        "scenes/refs", data["version7"].filename
    )

    archived_image_path = os.path.join(project_path, "sourceimages", image_filename)
    archived_audio_path = os.path.join(project_path, "sound", audio_filename)

    assert os.path.exists(archived_version1_path)
    assert os.path.exists(archived_version4_path)
    assert os.path.exists(archived_version7_path)
    # jpg should not be included
    assert not os.path.exists(archived_image_path)
    assert os.path.exists(archived_audio_path)

    # open the archived version1
    pm.workspace.open(project_path)
    pm.openFile(archived_version1_path)

    # expect it to have one reference
    all_refs = pm.listReferences()
    assert len(all_refs) == 1

    # and the path is matching to archived version4 path
    ref = all_refs[0]
    assert ref.path == archived_version4_path
    assert ref.unresolvedPath() == archived_version4_unresolved_path

    # check the deeper level references
    deeper_ref = pm.listReferences(parentReference=ref)[0]
    assert deeper_ref.path == archived_version7_path
    assert deeper_ref.unresolvedPath() == archived_version7_unresolved_path

    # and deeper level files
    ref_image_path = pm.ls(type="file")[0].attr("fileTextureName").get()
    # the path of the jpg should be intact
    assert ref_image_path == "$REPOTPR/TP/Test_Task_1/sourceimages/test.jpg"

    ref_audio_path = pm.ls(type="audio")[0].attr("filename").get()
    assert ref_audio_path == os.path.join(project_path, "sound", audio_filename)


def test_flatten_is_working_properly_with_multiple_reference_to_the_same_file_with_multiple_level_of_references(
    create_test_data, trash_bin, create_pymel, create_maya_env
):
    """testing if the Archiver.flatten() is working properly for a scene
    with multiple levels of references.
    """
    data = create_test_data
    maya_env = create_maya_env
    pm = create_pymel
    # open data["asset2_model_take1_v001"]
    maya_env.open(data["asset2_model_take1_v001"], force=True)

    # and reference data["version7"] to it
    maya_env.reference(data["version7"])

    # and save it
    pm.saveFile()

    # open data["asset2_model_main_v001"]
    maya_env.open(data["asset2_model_main_v001"], force=True)

    # and reference data["asset2_model_take1_v001"] multiple times to it
    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v001"])

    # and save it
    pm.saveFile()

    # renew the scene
    pm.newFile(force=1)

    # create an archiver
    arch = Archiver()

    project_path = arch.flatten(data["asset2_model_main_v001"].absolute_full_path)
    trash_bin.append(project_path)

    # now check if we have two files under the path/scenes directory
    archived_version1_path = os.path.join(
        project_path, "scenes", data["asset2_model_main_v001"].filename
    )

    # version4
    archived_version4_unresolved_path = os.path.join(
        "scenes/refs", data["asset2_model_take1_v001"].filename
    )

    archived_version4_path = os.path.join(
        project_path, archived_version4_unresolved_path
    )

    # version7
    archived_version7_unresolved_path = os.path.join(
        "scenes/refs", data["version7"].filename
    )

    archived_version7_path = os.path.join(
        project_path, archived_version7_unresolved_path
    )

    assert os.path.exists(archived_version1_path)
    assert os.path.exists(archived_version4_path)
    assert os.path.exists(archived_version7_path)

    # open the archived version1
    pm.workspace.open(project_path)
    pm.newFile(force=True)
    pm.openFile(archived_version1_path, force=True)

    # expect it to have three reference to the same file
    all_refs = pm.listReferences()
    assert len(all_refs) == 3

    # and the path is matching to archived version4 path
    # 1st
    ref = all_refs[0]
    assert ref.path == archived_version4_path

    # check the unresolved path
    assert ref.unresolvedPath() == archived_version4_unresolved_path

    # check the deeper level references
    deeper_ref = pm.listReferences(parentReference=ref)[0]
    assert deeper_ref.path == archived_version7_path

    # check the unresolved path
    assert deeper_ref.unresolvedPath() == archived_version7_unresolved_path

    # 2nd
    ref = all_refs[1]
    assert ref.path == archived_version4_path

    # check the unresolved path
    assert ref.unresolvedPath() == archived_version4_unresolved_path

    # check the deeper level references
    deeper_ref = pm.listReferences(parentReference=ref)[0]
    assert deeper_ref.path == archived_version7_path

    # check the unresolved path
    assert deeper_ref.unresolvedPath() == archived_version7_unresolved_path

    # 3rd
    ref = all_refs[2]
    assert ref.path == archived_version4_path

    # check the unresolved path
    assert ref.unresolvedPath() == archived_version4_unresolved_path

    # check the deeper level references
    deeper_ref = pm.listReferences(parentReference=ref)[0]
    assert deeper_ref.path == archived_version7_path

    # check the unresolved path
    assert deeper_ref.unresolvedPath() == archived_version7_unresolved_path


def test_flatten_is_working_properly_for_external_files(
    create_test_data, trash_bin, create_pymel, create_maya_env
):
    """testing if the Archiver.flatten() is working properly for a scene
    with textures, audio etc. external files
    """
    data = create_test_data
    maya_env = create_maya_env
    pm = create_pymel
    # open data["version7"]
    maya_env.open(data["version7"], force=True)

    # create an image file at the project root
    image_filename = "test.jpg"
    image_path = os.path.join(data["version7"].absolute_path, "Textures")
    image_full_path = os.path.join(image_path, image_filename)

    # create the file
    os.makedirs(image_path, exist_ok=True)
    with open(image_full_path, "w+") as f:
        f.writelines([""])

    audio_filename = "test.wav"
    audio_path = os.path.join(data["version7"].absolute_path, "sound")
    audio_full_path = os.path.join(audio_path, audio_filename)

    # create the file
    os.makedirs(audio_path, exist_ok=True)
    with open(audio_full_path, "w+") as f:
        f.writelines([""])

    # create one image and one audio node
    pm.createNode("file").attr("fileTextureName").set(image_full_path)
    pm.createNode("audio").attr("filename").set(audio_full_path)

    # save it
    # replace external paths
    maya_env.replace_external_paths()
    pm.saveFile()

    # renew the scene
    pm.newFile(force=1)

    # create an archiver
    arch = Archiver()

    project_path = arch.flatten(data["version7"].absolute_full_path)
    trash_bin.append(project_path)

    # now check if we have the files under the path/scenes directory
    archived_version7_path = os.path.join(
        project_path, "scenes", data["version7"].filename
    )

    archived_image_path = os.path.join(project_path, "sourceimages", image_filename)

    assert os.path.exists(archived_version7_path)
    assert os.path.exists(archived_image_path)

    # open the archived version1
    pm.workspace.open(project_path)
    pm.openFile(archived_version7_path)

    # and image files
    ref_image_path = pm.ls(type="file")[0].attr("fileTextureName").get()
    assert ref_image_path == os.path.join(project_path, "sourceimages", image_filename)
    ref_audio_path = pm.ls(type="audio")[0].attr("filename").get()
    assert ref_audio_path, os.path.join(project_path, "sound", audio_filename)


def test_flatten_will_restore_the_current_workspace(
    create_test_data, trash_bin, create_pymel, create_maya_env
):
    """testing if the Archiver.flatten() will restore the current workspace
    path after it has finished flattening
    """
    data = create_test_data
    maya_env = create_maya_env
    pm = create_pymel
    # open data["asset2_model_main_v001"]
    maya_env.open(data["asset2_model_main_v001"], force=True)

    current_workspace = pm.workspace.path

    arch = Archiver()
    project_path = arch.flatten(data["asset2_model_main_v001"].absolute_full_path)
    trash_bin.append(project_path)

    # now check if the current workspace is intact
    assert current_workspace == pm.workspace.path


def test_archive_will_create_a_zip_file_from_the_given_directory(
    create_test_data, trash_bin
):
    """testing if the Archiver.archive() will create a zip file and return
    the path of it
    """
    data = create_test_data
    arch = Archiver()
    project_path = arch.flatten(data["asset2_model_main_v001"].absolute_full_path)
    trash_bin.append(project_path)

    parent_path = os.path.dirname(project_path) + "/"

    # create a list of paths
    original_files = []
    for current_dir_path, dir_names, file_names in os.walk(project_path):
        for dir_name in dir_names:
            original_files.append(
                os.path.join(current_dir_path, dir_name)[len(parent_path):].replace(
                    "\\", "/"
                )
                + "/"
            )
        for file_name in file_names:
            original_files.append(
                os.path.join(current_dir_path, file_name)[len(parent_path):].replace(
                    "\\", "/"
                )
            )

    # archive it
    archive_path = arch.archive(project_path)
    trash_bin.append(archive_path)

    assert os.path.exists(archive_path)

    # and it is a valid zip file
    import zipfile

    with zipfile.ZipFile(archive_path) as z:
        all_names = z.namelist()

    assert sorted(original_files) == sorted(all_names)


def test_bind_to_original_will_bind_the_references_to_their_original_counter_part_in_the_repository(
    create_test_data, trash_bin, create_pymel, create_maya_env
):
    """testing if bind_to_original will be able to switch first level
    references with their original counterpart in the repository
    """
    data = create_test_data
    maya_env = create_maya_env
    pm = create_pymel
    # open data["asset2_model_take1_v001"]
    maya_env.open(data["asset2_model_take1_v001"], force=True)

    # and reference data["version7"] to it
    maya_env.reference(data["version7"])

    # and save it
    pm.saveFile()

    # open data["asset2_model_main_v001"]
    maya_env.open(data["asset2_model_main_v001"], force=True)

    # and reference data["asset2_model_take1_v001"] multiple times to it
    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v001"])

    # and save it
    pm.saveFile()

    # renew the scene
    pm.newFile(force=1)

    # create an archiver
    arch = Archiver()

    project_path = arch.flatten(data["asset2_model_main_v001"].absolute_full_path)
    trash_bin.append(project_path)

    # now check if we have two files under the path/scenes directory
    archived_version1_path = os.path.join(
        project_path, "scenes", data["asset2_model_main_v001"].filename
    )

    # version4
    archived_version4_unresolved_path = os.path.join(
        "scenes/refs", data["asset2_model_take1_v001"].filename
    )

    archived_version4_path = os.path.join(
        project_path, archived_version4_unresolved_path
    )

    # version7
    archived_version7_unresolved_path = os.path.join(
        "scenes/refs", data["version7"].filename
    )

    archived_version7_path = os.path.join(
        project_path, archived_version7_unresolved_path
    )

    assert os.path.exists(archived_version1_path)
    assert os.path.exists(archived_version4_path)
    assert os.path.exists(archived_version7_path)

    # open the archived version1
    pm.workspace.open(project_path)
    pm.newFile(force=True)
    pm.openFile(archived_version1_path, force=True)

    # expect it to have three reference to the same file
    all_refs = pm.listReferences()
    assert len(all_refs) == 3

    # check if the first level references are using the flattened files
    assert (
        all_refs[0].unresolvedPath().replace("\\", "/")
        == archived_version4_unresolved_path
    )
    assert all_refs[1].unresolvedPath() == archived_version4_unresolved_path
    assert all_refs[2].unresolvedPath() == archived_version4_unresolved_path

    # close the file
    pm.newFile(force=True)

    # now use bind to original to bind them to the originals
    arch.bind_to_original(archived_version1_path)

    # re-open the file and expect it to be bound to the originals
    pm.openFile(archived_version1_path, force=True)

    # list references
    all_refs = pm.listReferences()

    assert all_refs[0].unresolvedPath() == data["asset2_model_take1_v001"].full_path
    assert all_refs[1].unresolvedPath() == data["asset2_model_take1_v001"].full_path
    assert all_refs[2].unresolvedPath() == data["asset2_model_take1_v001"].full_path
