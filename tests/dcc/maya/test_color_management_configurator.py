# -*- coding: utf-8 -*-
"""Test MayaColorManagementConfigurator."""
import json
import os
import shutil
import tempfile

import pytest
from stalker import Repository, Asset, Task, Version
from stalker.db.session import DBSession


@pytest.fixture(scope="function")
def temp_project(create_project):
    """Fixture for color management tests."""
    project = create_project
    # update repository path to be a temp path
    tempdir = tempfile.mkdtemp()
    repo = project.repository
    repo.windows_path = tempdir
    repo.linux_path = tempdir
    repo.osx_path = tempdir
    yield project
    # clean up the path
    shutil.rmtree(tempdir)


@pytest.fixture(scope="function")
def color_managed_project(temp_project, create_pymel):
    """Create color management files."""
    pm = create_pymel
    project = temp_project
    repo = project.repository
    assert isinstance(repo, Repository)
    ref_folder_path = os.path.join(repo.path, project.code, "References")
    cm_config_file_name = "COLOR_MANAGEMENT_CONFIG"
    cm_config_file_full_path = os.path.join(ref_folder_path, cm_config_file_name)
    os.makedirs(ref_folder_path, exist_ok=True)
    config_data = {
        pm.about(v=1): "scene-linear Rec.709-sRGB"
    }
    with open(cm_config_file_full_path, "w") as f:
        json.dump(config_data, f)

    yield project


def test_default_color_management_is_set_to_aces_cg(
    create_test_db, create_pymel, create_maya_env
):
    """Test if default color management is set to ACEScg."""
    pm = create_pymel
    cmp = pm.colorManagementPrefs
    assert cmp(q=1, cmEnabled=1) is True
    assert (
        cmp(q=1, configFilePath=1)
        == "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio"
    )
    assert cmp(q=1, configFileVersion=1) == "2.0"
    assert cmp(q=1, displayName=1) == "sRGB"
    assert cmp(q=1, outputUseViewTransform=1) is True
    assert cmp(q=1, outputTransformName=1) == "ACES 1.0 SDR-video (sRGB)"
    assert cmp(q=1, renderingSpaceName=1) == "ACEScg"
    if int(pm.about(v=1)) >= 2022:
        assert cmp(q=1, viewTransformName=1) == "ACES 1.0 SDR-video (sRGB)"


def test_color_management_is_set_to_aces_cg(
    create_test_db, create_pymel, create_maya_env
):
    """Test if color management can be set to ACEScg."""
    pm = create_pymel
    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator

    MayaColorManagementConfigurator.configure(config_name="ACEScg")
    cmp = pm.colorManagementPrefs
    assert cmp(q=1, cmEnabled=1) is True
    assert (
        cmp(q=1, configFilePath=1)
        == "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio"
    )
    assert cmp(q=1, configFileVersion=1) == "2.0"
    assert cmp(q=1, displayName=1) == "sRGB"
    assert cmp(q=1, outputUseViewTransform=1) is True
    assert cmp(q=1, outputTransformName=1) == "ACES 1.0 SDR-video (sRGB)"
    assert cmp(q=1, renderingSpaceName=1) == "ACEScg"
    if int(pm.about(v=1)) >= 2022:
        assert cmp(q=1, viewTransformName=1) == "ACES 1.0 SDR-video (sRGB)"


def test_color_management_is_set_to_linear_srgb(
    create_test_db, create_pymel, create_maya_env
):
    """Test if color management can be set to linear-sRGB."""
    pm = create_pymel
    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator

    MayaColorManagementConfigurator.configure(config_name="scene-linear Rec.709-sRGB")
    cmp = pm.colorManagementPrefs
    assert cmp(q=1, cmEnabled=1) is True
    assert (
        cmp(q=1, configFilePath=1)
        == "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio"
    )
    assert cmp(q=1, configFileVersion=1) == "2.0"
    assert cmp(q=1, displayName=1) == "sRGB"
    assert cmp(q=1, outputUseViewTransform=1) is True
    assert cmp(q=1, outputTransformName=1) == "Un-tone-mapped (sRGB)"
    assert cmp(q=1, renderingSpaceName=1) == "scene-linear Rec.709-sRGB"
    if int(pm.about(v=1)) >= 2022:
        assert cmp(q=1, viewTransformName=1) == "Un-tone-mapped (sRGB)"


def test_configure_uses_default_config_if_config_name_is_none(
    create_test_db, create_pymel, create_maya_env
):
    """Test if default config is going to be used when the config_name is None."""
    pm = create_pymel
    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator

    MayaColorManagementConfigurator.configure(config_name="scene-linear Rec.709-sRGB")
    cmp = pm.colorManagementPrefs
    assert cmp(q=1, cmEnabled=1) is True
    assert (
        cmp(q=1, configFilePath=1)
        == "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio"
    )
    assert cmp(q=1, configFileVersion=1) == "2.0"
    assert cmp(q=1, displayName=1) == "sRGB"
    assert cmp(q=1, outputUseViewTransform=1) is True
    assert cmp(q=1, outputTransformName=1) == "Un-tone-mapped (sRGB)"
    assert cmp(q=1, renderingSpaceName=1) == "scene-linear Rec.709-sRGB"
    if int(pm.about(v=1)) >= 2022:
        assert cmp(q=1, viewTransformName=1) == "Un-tone-mapped (sRGB)"

    # now configure with config_name = None
    MayaColorManagementConfigurator.configure(config_name=None)
    assert cmp(q=1, cmEnabled=1) is True
    assert (
        cmp(q=1, configFilePath=1)
        == "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio"
    )
    assert cmp(q=1, configFileVersion=1) == "2.0"
    assert cmp(q=1, displayName=1) == "sRGB"
    assert cmp(q=1, outputUseViewTransform=1) is True
    assert cmp(q=1, outputTransformName=1) == "ACES 1.0 SDR-video (sRGB)"
    assert cmp(q=1, renderingSpaceName=1) == "ACEScg"
    if int(pm.about(v=1)) >= 2022:
        assert cmp(q=1, viewTransformName=1) == "ACES 1.0 SDR-video (sRGB)"


def test_configure_raise_value_error_if_config_name_is_not_valid(
    create_test_db, create_pymel, create_maya_env
):
    """Test if a ValueError will be raised if config_name is not valid."""
    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator

    with pytest.raises(ValueError) as cm:
        MayaColorManagementConfigurator.configure(
            config_name="not a valid config name"
        )

    assert str(cm.value) == (
        '"not a valid config name" is not a valid value for ``config_name`` '
        "argument in MayaColorManagementConfigurator.configure(), it should be one of "
        '["ACEScg", "scene-linear Rec.709-sRGB"]'
    )


def test_configure_will_use_the_project_default_config(
    create_test_db,
    create_pymel,
    create_maya_env,
    create_test_data,
    color_managed_project,
):
    """Test if the project default will be used if a project can be found in current
    Maya session."""
    pm = create_pymel
    maya_env = create_maya_env
    data = create_test_data
    project = color_managed_project
    pm.newFile(force=True)

    # by default Maya should use ACEScg
    cmp = pm.colorManagementPrefs
    assert cmp(q=1, cmEnabled=1) is True
    assert (
        cmp(q=1, configFilePath=1)
        == "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio"
    )
    assert cmp(q=1, configFileVersion=1) == "2.0"
    assert cmp(q=1, displayName=1) == "sRGB"
    assert cmp(q=1, outputUseViewTransform=1) is True
    assert cmp(q=1, outputTransformName=1) == "ACES 1.0 SDR-video (sRGB)"
    assert cmp(q=1, renderingSpaceName=1) == "ACEScg"
    if int(pm.about(v=1)) >= 2022:
        assert cmp(q=1, viewTransformName=1) == "ACES 1.0 SDR-video (sRGB)"

    # create a new version for the char1_model task
    char1 = (
        Asset.query.filter(Asset.name == "Char1")
        .filter(Asset.project == project)
        .first()
    )
    model = Task.query.filter(Task.parent == char1).filter(Task.name == "Model").first()
    v = Version(task=model)
    DBSession.add(v)
    DBSession.commit()

    from anima.dcc.mayaEnv import Maya

    assert isinstance(maya_env, Maya)
    maya_env.save_as(v)

    # after saving this and calling configure without an argument
    # color management should be set to the project default
    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator

    MayaColorManagementConfigurator.configure()
    assert cmp(q=1, cmEnabled=1) is True
    assert (
        cmp(q=1, configFilePath=1)
        == "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio"
    )
    assert cmp(q=1, configFileVersion=1) == "2.0"
    assert cmp(q=1, displayName=1) == "sRGB"
    assert cmp(q=1, outputUseViewTransform=1) is True
    assert cmp(q=1, outputTransformName=1) == "Un-tone-mapped (sRGB)"
    assert cmp(q=1, renderingSpaceName=1) == "scene-linear Rec.709-sRGB"
    if int(pm.about(v=1)) >= 2022:
        assert cmp(q=1, viewTransformName=1) == "Un-tone-mapped (sRGB)"


def test_configure_project_should_create_project_config_file(
    create_test_db, create_pymel, create_maya_env, create_test_data, temp_project
):
    """test calling configure_project with a project and a config_name should create
    config file."""
    project = temp_project
    # check if there is no such COLOR_MANAGEMENT_CONFIG file in the project
    repo = project.repository
    assert isinstance(repo, Repository)
    config_file_path = os.path.join(
        repo.path, project.code, "References", "COLOR_MANAGEMENT_CONFIG"
    )
    assert not os.path.exists(config_file_path)

    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator

    MayaColorManagementConfigurator.configure_project(
        project, "scene-linear Rec.709-sRGB"
    )
    assert os.path.exists(config_file_path)


def test_configure_project_should_configure_a_project_persistently(
    create_test_db, create_pymel, create_maya_env, create_test_data, temp_project
):
    """test calling configure_project with a project and a config_name should
    persistently configure the project."""
    pm = create_pymel
    project = temp_project
    # check if there is no such COLOR_MANAGEMENT_CONFIG file in the project
    repo = project.repository
    assert isinstance(repo, Repository)
    config_file_path = os.path.join(
        repo.path, project.code, "References", "COLOR_MANAGEMENT_CONFIG"
    )
    assert not os.path.exists(config_file_path)

    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator

    MayaColorManagementConfigurator.configure_project(
        project, "scene-linear Rec.709-sRGB"
    )
    with open(config_file_path, "r") as f:
        data = json.load(f)
        cm_name = data[pm.about(v=1)].strip()

    assert cm_name == "scene-linear Rec.709-sRGB"


def test_configure_project_project_is_none(
        create_test_db, create_pymel, create_maya_env, create_test_data, temp_project
):
    """test configure project with project argument is None."""
    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator

    with pytest.raises(TypeError) as cm:
        MayaColorManagementConfigurator.configure_project(
            None, "scene-linear Rec.709-sRGB"
        )

    assert str(cm.value) == (
        "In MayaColorManagementConfigurator.configure_project() "
        "the project argument should be a stalker Project instance, "
        "not NoneType"
    )


def test_configure_project_project_is_not_a_project_instance(
        create_test_db, create_pymel, create_maya_env, create_test_data, temp_project
):
    """test configure project with project argument is not a project instance."""
    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator

    with pytest.raises(TypeError) as cm:
        MayaColorManagementConfigurator.configure_project(
            "not a project", "scene-linear Rec.709-sRGB"
        )

    assert str(cm.value) == (
        "In MayaColorManagementConfigurator.configure_project() "
        "the project argument should be a stalker Project instance, "
        "not str"
    )


def test_configure_project_config_name_is_not_valid(
    create_test_db, create_pymel, create_maya_env, create_test_data, temp_project
):
    """test configure project with config_name argument is not valid."""
    project = temp_project
    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator

    with pytest.raises(ValueError) as cm:
        MayaColorManagementConfigurator.configure_project(
            project, "linear-sRGB"
        )

    assert str(cm.value) == (
        "In MayaColorManagementConfigurator.configure_project() the config_name "
        "argument should be one of "
        '["ACEScg", "scene-linear Rec.709-sRGB"]'
    )
