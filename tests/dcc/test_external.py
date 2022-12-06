# -*- coding: utf-8 -*-
"""Tests for ExternalDCC class."""

import shutil
import tempfile
import os

import pytest
from stalker import (
    Version,
    Task,
    Project,
    Structure,
    StatusList,
    Repository,
    Status,
    FilenameTemplate,
)

from anima.dcc.external import ExternalDCC, ExternalDCCFactory


@pytest.fixture(scope="function")
def test_data(create_test_db):
    """Set up the test data."""
    data = dict()
    data["temp_path"] = tempfile.mkdtemp()
    data["repo"] = Repository(
        name="Test Repository",
        code="TR",
        linux_path=data["temp_path"],
        windows_path=data["temp_path"],
        osx_path=data["temp_path"],
    )
    data["status_new"] = Status.query.filter_by(code="NEW").first()
    data["status_wip"] = Status.query.filter_by(code="WIP").first()
    data["status_cmpl"] = Status.query.filter_by(code="CMPL").first()

    data["project_status_list"] = StatusList.query.filter_by(
        target_entity_type="Project"
    ).first()
    data["task_filename_template"] = FilenameTemplate(
        name="Task Filename Template",
        target_entity_type="Task",
        path="{{project.code}}/{%- for parent_task in parent_tasks -%}"
        "{{parent_task.nice_name}}/{%- endfor -%}",
        filename="{{version.nice_name}}"
        '_v{{"%03d"|format(version.version_number)}}{{extension}}',
    )
    data["project_structure"] = Structure(
        name="Project Structure", templates=[data["task_filename_template"]]
    )
    data["project"] = Project(
        name="Test Project",
        code="TP",
        status_list=data["project_status_list"],
        repository=data["repo"],
        structure=data["project_structure"],
    )

    data["task"] = Task(name="Test Task", project=data["project"])
    from stalker.db.session import DBSession

    DBSession.add(data["task"])
    DBSession.commit()

    data["version"] = Version(task=data["task"])

    data["kwargs"] = {
        "name": "Photoshop",
        "extensions": ["psd"],
        "structure": ["Outputs"],
    }

    data["external_env"] = ExternalDCC(**data["kwargs"])

    yield data

    # clean up the test
    shutil.rmtree(data["temp_path"])


def test_name_argument_cannot_be_skipped(test_data):
    """testing if a TypeError will raise when the name argument is skipped"""
    test_data["kwargs"].pop("name")
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_name_argument_cannot_be_None(test_data):
    """testing if a TypeError will be raised when the name argument is None"""
    test_data["kwargs"]["name"] = None
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_name_attribute_cannot_be_set_to_None(test_data):
    """testing if a TypeError will be raised when the name attribute is set
    to None
    """
    pytest.raises(TypeError, setattr, test_data["external_env"], "name", None)


def test_name_argument_should_be_a_string(test_data):
    """testing if a TypeError will be raised when the name argument is not
    a string
    """
    test_data["kwargs"]["name"] = 32
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_name_attribute_should_be_set_to_a_string(test_data):
    """testing if a TypeError will be raised when the name attribute is set
    to a value other than a string
    """
    pytest.raises(TypeError, setattr, test_data["external_env"], "name", 23)


def test_name_argument_is_working_properly(test_data):
    """testing if the name argument value is correctly passed to the name
    attribute
    """
    test_value = "ZBrush"
    test_data["kwargs"]["name"] = test_value
    external_env = ExternalDCC(**test_data["kwargs"])
    assert test_value == external_env.name


def test_name_attribute_is_working_properly(test_data):
    """testing if the name attribute value is correctly set"""
    test_value = "ZBrush"
    test_data["external_env"].name = test_value
    assert test_value == test_data["external_env"].name


def test_extension_argument_cannot_be_skipped(test_data):
    """testing if a TypeError will raised when the extension argument is
    skipped
    """
    test_data["kwargs"].pop("extensions")
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_extension_argument_cannot_be_None(test_data):
    """testing if a TypeError will be raised when the extension argument is
    None
    """
    test_data["kwargs"]["extensions"] = None
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_extension_attribute_cannot_be_set_to_None(test_data):
    """testing if a TypeError will be raised when the extension attribute
    is set to None
    """
    pytest.raises(TypeError, setattr, test_data["external_env"], "extensions", None)


def test_extension_argument_should_be_a_string(test_data):
    """testing if a TypeError will be raised when the extension argument is
    not a string
    """
    test_data["kwargs"]["extensions"] = 32
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_extension_attribute_should_be_set_to_a_string(test_data):
    """testing if a TypeError will be raised when the extension attribute
    is set to a value other than a string
    """
    pytest.raises(TypeError, setattr, test_data["external_env"], "extensions", 23)


def test_extension_argument_with_no_dots_is_working(test_data):
    """testing if extension argument accepts strings without a dot at the
    beginning
    """
    test_data["kwargs"]["extensions"] = ["psd"]
    external_env = ExternalDCC(**test_data["kwargs"])
    assert [".psd"] == external_env.extensions


def test_extension_attribute_with_no_dots_is_working(test_data):
    """testing if extension attribute accepts strings without a dot at the
    beginning
    """
    test_data["external_env"].extensions = ["psd"]
    assert [".psd"] == test_data["external_env"].extensions


def test_extension_argument_is_working_properly(test_data):
    """testing if the extension argument value is correctly passed to the
    extension attribute
    """
    test_value = [".ztl"]
    test_data["kwargs"]["extensions"] = test_value
    external_env = ExternalDCC(**test_data["kwargs"])
    assert test_value == external_env.extensions


def test_extension_attribute_is_working_properly(test_data):
    """testing if the extension attribute value is correctly set"""
    test_value = [".ztl"]
    test_data["external_env"].extensions = test_value
    assert test_value == test_data["external_env"].extensions


def test_structure_argument_can_be_skipped(test_data):
    """testing if the structure argument can be skipped"""
    test_data["kwargs"].pop("structure")
    ExternalDCC(**test_data["kwargs"])


def test_structure_attribute_value_when_structure_argument_is_skipped(test_data):
    """testing if the structure argument attribute will be an empty list
    when the structure argument is skipped
    """
    test_data["kwargs"].pop("structure")
    external_env = ExternalDCC(**test_data["kwargs"])
    assert external_env.structure == []


def test_structure_argument_can_be_set_to_None(test_data):
    """testing if the structure argument can be set to None"""
    test_data["kwargs"]["structure"] = None
    ExternalDCC(**test_data["kwargs"])


def test_structure_attribute_value_when_structure_argument_is_None(test_data):
    """testing if the structure argument attribute will be an empty list
    when the structure argument value is None
    """
    test_data["kwargs"]["structure"] = None
    external_env = ExternalDCC(**test_data["kwargs"])
    assert external_env.structure == []


def test_structure_attribute_can_be_set_to_None(test_data):
    """testing if the structure attribute value will be an empty list when
    the structure attribute is set to None
    """
    test_data["external_env"].structure = None


def test_structure_argument_is_not_a_list(test_data):
    """testing if a TypeError will be raised when the structure argument
    is not None or a list
    """
    test_data["kwargs"]["structure"] = "this is not a list"
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_structure_attribute_is_not_a_list(test_data):
    """testing if a TypeError will be raised when the structure attribute
    is not a set to None or a list
    """
    pytest.raises(
        TypeError, ExternalDCC, test_data["external_env"], "structure", "this is not a list"
    )


def test_structure_argument_is_not_a_list_of_strings(test_data):
    """testing if a TypeError will be raised when not all the the elements
    are strings in structure argument
    """
    test_data["kwargs"]["structure"] = ["not", 1, "list of", "strings"]
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_structure_attribute_is_not_a_list_of_strings(test_data):
    """testing if a TypeError will be raised when not all the the elements
    are strings in structure attribute value
    """
    test_value = ["not", 1, "list of", "strings"]
    pytest.raises(
        TypeError, setattr, test_data["external_env"], "structure", test_value
    )


def test_structure_argument_is_working_properly(test_data):
    """testing if the structure argument value is correctly passed to the
    structure attribute
    """
    test_value = ["Outputs", "Inputs", "cache"]
    test_data["kwargs"]["structure"] = test_value
    external_env = ExternalDCC(**test_data["kwargs"])
    assert sorted(test_value) == sorted(external_env.structure)


def test_structure_attribute_is_working_properly(test_data):
    """testing if the structure attribute value can be correctly updated"""
    test_value = ["Outputs", "Inputs", "cache"]
    test_data["external_env"].structure = test_value
    assert sorted(test_value) == sorted(test_data["external_env"].structure)


def test_conform_version_argument_accepts_Version_instances_only(test_data):
    """testing if a TypeError will be raised when the version argument in
    conform method is not a Version instance
    """
    pytest.raises(
        TypeError, test_data["external_env"].conform, version="not a version instance"
    )


def test_conform_method_will_set_the_version_extension(test_data):
    """testing if the conform method will set the version extension to the
    DCC extension correctly
    """
    assert test_data["version"].extension != ".ztl"
    external_env = ExternalDCC(name="ZBrush", extensions=[".ztl"])

    external_env.conform(test_data["version"])
    assert test_data["version"].extension == ".ztl"


def test_conform_method_will_set_the_version_created_with(test_data):
    """testing if the conform method will set the version extension to the DCC name"""
    assert test_data["version"].extension != ".ztl"
    external_env = ExternalDCC(name="ZBrush", extensions=[".ztl"])
    external_env.conform(test_data["version"])
    assert test_data["version"].extension == ".ztl"
    assert test_data["version"].created_with == "ZBrush"


def test_initialize_structure_version_argument_accepts_Version_instances_only(
    test_data,
):
    """testing if a TypeError will be raised when the version argument in
    initialize_structure method is not a Version instance
    """
    pytest.raises(
        TypeError,
        test_data["external_env"].initialize_structure,
        version="not a version instance",
    )


def test_initialize_structure_will_create_the_folders_of_the_environment(test_data):
    """testing if the initialize_structure method will create the folders
    at the given Version instance path
    """
    test_data["external_env"].initialize_structure(test_data["version"])
    for folder in test_data["external_env"].structure:
        assert os.path.exists(os.path.join(test_data["version"].absolute_path, folder))


def test_initialize_structure_will_handle_OSErrors(test_data):
    """testing if the initialize_structure method will handle OSErrors when
    creating folders which are already there
    """
    # call it multiple times
    test_data["external_env"].initialize_structure(test_data["version"])
    test_data["external_env"].initialize_structure(test_data["version"])
    test_data["external_env"].initialize_structure(test_data["version"])


def test_save_as_will_conform_and_initialize_structure(test_data):
    """testing if the save_as method will conform the given version and
    initialize the structure
    """
    test_data["external_env"].save_as(test_data["version"])
    assert test_data["external_env"].extensions[0] == test_data["version"].extension
    for folder in test_data["external_env"].structure:
        assert os.path.exists(os.path.join(test_data["version"].absolute_path, folder))


def test_get_settings_file_path_returns_the_settings_path_correctly(test_data):
    """testing if the get_settings_path returns the settings path correctly"""
    assert (
        os.path.expanduser("~/.atrc/last_version")
        == ExternalDCC.get_settings_file_path()
    )


def test_append_to_recent_files_version_argument_is_not_a_Version_instance(test_data):
    """testing if a TypeError will be raised when the version argument in
    append_to_recent_files() method is not a stalker.models.version.Version
    instance
    """
    pytest.raises(TypeError, test_data["external_env"].append_to_recent_files, 3121)


def test_append_to_recent_files_working_properly(test_data):
    """testing if the append_to_recent_files() method is working properly"""
    # set the id attribute of the test version to a random number
    test_data["version"].id = 234
    test_data["external_env"].append_to_recent_files(test_data["version"])
    # check the settings file
    path = test_data["external_env"].get_settings_file_path()
    with open(path, "r") as f:
        vid = f.read()
    assert vid == str(234)


def test_get_last_version_is_working_properly(test_data):
    """testing if hte get_last_version() method will return Version
    instance properly
    """
    from stalker.db.session import DBSession

    DBSession.add(test_data["version"])
    DBSession.commit()
    assert test_data["version"].id is not None
    test_data["external_env"].append_to_recent_files(test_data["version"])
    last_version = test_data["external_env"].get_last_version()
    assert last_version == test_data["version"]


def test_get_env_names_method_will_return_all_environment_names_properly(
    create_test_db,
):
    """testing if ExternalDCCFactory.get_env_names() method will
    return all the DCC names as a list of strings
    """
    from anima.dcc.external import external_dccs

    expected_result = list(external_dccs.keys())
    ext_env_factory = ExternalDCCFactory()
    result = ext_env_factory.get_env_names()
    assert expected_result == result


def test_get_env_names_method_will_return_complex_environment_names_properly(
    create_test_db,
):
    """testing if ExternalDCCFactory.get_env_names() method will
    return all the DCC names as a list of strings in desired format
    when environment_name_format is set
    """
    name_format = "%e - %n"
    expected_result = [
        ".ztl - ZBrush",
        ".mud - MudBox",
        #'.psd - Photoshop'
    ]
    ext_env_factory = ExternalDCCFactory()
    result = ext_env_factory.get_env_names(name_format=name_format)
    assert sorted(expected_result) == sorted(result)


def test_get_env_method_name_argument_is_not_a_string(create_test_db):
    """testing if a TypeError will be raised when the name argument is not
    a string in ExternalEnvironmentFactory.get_env() method
    """
    ext_env_factory = ExternalDCCFactory()
    pytest.raises(TypeError, ext_env_factory.get_env, 234)


def test_get_env_method_name_is_not_in_list(create_test_db):
    """testing if a ValueError will be raised when the name argument value
    is not in the anima.dcc.external_environments list
    """
    ext_env_factory = ExternalDCCFactory()
    pytest.raises(ValueError, ext_env_factory.get_env, "Modo")


def test_get_env_method_will_return_desired_environment(create_test_db):
    """testing if ExternalDCCFactory.get_env() will return desired
    ExternalEnvironment instance
    """
    ext_env_factory = ExternalDCCFactory()

    zbrush_tool = ext_env_factory.get_env("ZBrush")
    assert isinstance(zbrush_tool, ExternalDCC)
    assert zbrush_tool.name == "ZBrush"
    assert zbrush_tool.extensions == [".ztl"]
    assert zbrush_tool.structure == ["Outputs"]

    mudbox = ext_env_factory.get_env("MudBox")
    assert isinstance(mudbox, ExternalDCC)
    assert mudbox.name == "MudBox"
    assert mudbox.extensions == [".mud"]
    assert mudbox.structure == ["Outputs"]


def test_get_env_method_will_return_desired_environment_even_with_complex_formats(
    create_test_db,
):
    """testing if ExternalDCCFactory.get_env() will return desired
    ExternalEnvironment instance even with names like "MudBox (.mud)"
    """
    ext_env_factory = ExternalDCCFactory()

    zbrush = ext_env_factory.get_env("ZBrush (.ztl)", name_format="%n (%e)")
    assert isinstance(zbrush, ExternalDCC)
    assert zbrush.name == "ZBrush"
    assert zbrush.extensions == [".ztl"]
    assert zbrush.structure == ["Outputs"]

    mudbox = ext_env_factory.get_env("MudBox (.mud)", name_format="%n (%e)")
    assert isinstance(mudbox, ExternalDCC)
    assert mudbox.name == "MudBox"
    assert mudbox.extensions == [".mud"]
    assert mudbox.structure == ["Outputs"]


def test_get_env_method_will_return_desired_environment_even_with_custom_formats(
    create_test_db,
):
    """testing if ExternalDCCFactory.get_env() will return desired
    ExternalEnvironment instance even with names like "MudBox (.mud)"
    """
    ext_env_factory = ExternalDCCFactory()
    name_format = "(%e) - %n"
    zbrush = ext_env_factory.get_env("(.ztl) - ZBrush", name_format=name_format)
    assert isinstance(zbrush, ExternalDCC)
    assert zbrush.name == "ZBrush"
    assert zbrush.extensions == [".ztl"]
    assert zbrush.structure == ["Outputs"]

    mudbox = ext_env_factory.get_env("(.mud) - MudBox", name_format=name_format)
    assert isinstance(mudbox, ExternalDCC)
    assert mudbox.name == "MudBox"
    assert mudbox.extensions == [".mud"]
    assert mudbox.structure == ["Outputs"]
