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

    data["external_dcc"] = ExternalDCC(**data["kwargs"])

    yield data

    # clean up the test
    shutil.rmtree(data["temp_path"])


def test_name_argument_cannot_be_skipped(test_data):
    """a TypeError will raise when the name argument is skipped"""
    test_data["kwargs"].pop("name")
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_name_argument_cannot_be_None(test_data):
    """a TypeError will be raised when the name argument is None"""
    test_data["kwargs"]["name"] = None
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_name_attribute_cannot_be_set_to_None(test_data):
    """a TypeError will be raised when the name attribute is set
    to None
    """
    pytest.raises(TypeError, setattr, test_data["external_dcc"], "name", None)


def test_name_argument_should_be_a_string(test_data):
    """a TypeError will be raised when the name argument is not
    a string
    """
    test_data["kwargs"]["name"] = 32
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_name_attribute_should_be_set_to_a_string(test_data):
    """a TypeError will be raised when the name attribute is set
    to a value other than a string
    """
    pytest.raises(TypeError, setattr, test_data["external_dcc"], "name", 23)


def test_name_argument_is_working_properly(test_data):
    """name argument value is correctly passed to the name
    attribute
    """
    test_value = "ZBrush"
    test_data["kwargs"]["name"] = test_value
    external_dcc = ExternalDCC(**test_data["kwargs"])
    assert test_value == external_dcc.name


def test_name_attribute_is_working_properly(test_data):
    """name attribute value is correctly set"""
    test_value = "ZBrush"
    test_data["external_dcc"].name = test_value
    assert test_value == test_data["external_dcc"].name


def test_extension_argument_cannot_be_skipped(test_data):
    """a TypeError will raised when the extension argument is
    skipped
    """
    test_data["kwargs"].pop("extensions")
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_extension_argument_cannot_be_None(test_data):
    """a TypeError will be raised when the extension argument is
    None
    """
    test_data["kwargs"]["extensions"] = None
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_extension_attribute_cannot_be_set_to_None(test_data):
    """a TypeError will be raised when the extension attribute
    is set to None
    """
    pytest.raises(TypeError, setattr, test_data["external_dcc"], "extensions", None)


def test_extension_argument_should_be_a_string(test_data):
    """a TypeError will be raised when the extension argument is
    not a string
    """
    test_data["kwargs"]["extensions"] = 32
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_extension_attribute_should_be_set_to_a_string(test_data):
    """a TypeError will be raised when the extension attribute
    is set to a value other than a string
    """
    pytest.raises(TypeError, setattr, test_data["external_dcc"], "extensions", 23)


def test_extension_argument_with_no_dots_is_working(test_data):
    """extension argument accepts strings without a dot at the
    beginning
    """
    test_data["kwargs"]["extensions"] = ["psd"]
    external_dcc = ExternalDCC(**test_data["kwargs"])
    assert [".psd"] == external_dcc.extensions


def test_extension_attribute_with_no_dots_is_working(test_data):
    """extension attribute accepts strings without a dot at the
    beginning
    """
    test_data["external_dcc"].extensions = ["psd"]
    assert [".psd"] == test_data["external_dcc"].extensions


def test_extension_argument_is_working_properly(test_data):
    """extension argument value is correctly passed to the
    extension attribute
    """
    test_value = [".ztl"]
    test_data["kwargs"]["extensions"] = test_value
    external_dcc = ExternalDCC(**test_data["kwargs"])
    assert test_value == external_dcc.extensions


def test_extension_attribute_is_working_properly(test_data):
    """extension attribute value is correctly set"""
    test_value = [".ztl"]
    test_data["external_dcc"].extensions = test_value
    assert test_value == test_data["external_dcc"].extensions


def test_structure_argument_can_be_skipped(test_data):
    """structure argument can be skipped"""
    test_data["kwargs"].pop("structure")
    ExternalDCC(**test_data["kwargs"])


def test_structure_attribute_value_when_structure_argument_is_skipped(test_data):
    """structure argument attribute will be an empty list
    when the structure argument is skipped
    """
    test_data["kwargs"].pop("structure")
    external_dcc = ExternalDCC(**test_data["kwargs"])
    assert external_dcc.structure == []


def test_structure_argument_can_be_set_to_None(test_data):
    """structure argument can be set to None"""
    test_data["kwargs"]["structure"] = None
    ExternalDCC(**test_data["kwargs"])


def test_structure_attribute_value_when_structure_argument_is_None(test_data):
    """structure argument attribute will be an empty list
    when the structure argument value is None
    """
    test_data["kwargs"]["structure"] = None
    external_dcc = ExternalDCC(**test_data["kwargs"])
    assert external_dcc.structure == []


def test_structure_attribute_can_be_set_to_None(test_data):
    """structure attribute value will be an empty list when
    the structure attribute is set to None
    """
    test_data["external_dcc"].structure = None


def test_structure_argument_is_not_a_list(test_data):
    """a TypeError will be raised when the structure argument
    is not None or a list
    """
    test_data["kwargs"]["structure"] = "this is not a list"
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_structure_attribute_is_not_a_list(test_data):
    """a TypeError will be raised when the structure attribute
    is not a set to None or a list
    """
    pytest.raises(
        TypeError, ExternalDCC, test_data["external_dcc"], "structure", "this is not a list"
    )


def test_structure_argument_is_not_a_list_of_strings(test_data):
    """a TypeError will be raised when not all the the elements
    are strings in structure argument
    """
    test_data["kwargs"]["structure"] = ["not", 1, "list of", "strings"]
    pytest.raises(TypeError, ExternalDCC, **test_data["kwargs"])


def test_structure_attribute_is_not_a_list_of_strings(test_data):
    """a TypeError will be raised when not all the the elements
    are strings in structure attribute value
    """
    test_value = ["not", 1, "list of", "strings"]
    pytest.raises(
        TypeError, setattr, test_data["external_dcc"], "structure", test_value
    )


def test_structure_argument_is_working_properly(test_data):
    """structure argument value is correctly passed to the
    structure attribute
    """
    test_value = ["Outputs", "Inputs", "cache"]
    test_data["kwargs"]["structure"] = test_value
    external_dcc = ExternalDCC(**test_data["kwargs"])
    assert sorted(test_value) == sorted(external_dcc.structure)


def test_structure_attribute_is_working_properly(test_data):
    """structure attribute value can be correctly updated"""
    test_value = ["Outputs", "Inputs", "cache"]
    test_data["external_dcc"].structure = test_value
    assert sorted(test_value) == sorted(test_data["external_dcc"].structure)


def test_conform_version_argument_accepts_Version_instances_only(test_data):
    """a TypeError will be raised when the version argument in
    conform method is not a Version instance
    """
    pytest.raises(
        TypeError, test_data["external_dcc"].conform, version="not a version instance"
    )


def test_conform_method_will_set_the_version_extension(test_data):
    """conform method will set the version extension to the
    DCC extension correctly
    """
    assert test_data["version"].extension != ".ztl"
    external_dcc = ExternalDCC(name="ZBrush", extensions=[".ztl"])
    external_dcc.conform(test_data["version"])
    assert test_data["version"].extension == ".ztl"


def test_conform_method_will_set_the_version_created_with(test_data):
    """conform method will set the version extension to the DCC name"""
    assert test_data["version"].extension != ".ztl"
    external_dcc = ExternalDCC(name="ZBrush", extensions=[".ztl"])
    external_dcc.conform(test_data["version"])
    assert test_data["version"].extension == ".ztl"
    assert test_data["version"].created_with == "ZBrush"


def test_initialize_structure_version_argument_accepts_Version_instances_only(
    test_data,
):
    """a TypeError will be raised when the version argument in
    initialize_structure() is not a Version instance
    """
    pytest.raises(
        TypeError,
        test_data["external_dcc"].initialize_structure,
        version="not a version instance",
    )


def test_initialize_structure_will_create_the_folders_of_the_dcc(test_data):
    """initialize_structure() will create the folders
    at the given Version instance path
    """
    test_data["external_dcc"].initialize_structure(test_data["version"])
    for folder in test_data["external_dcc"].structure:
        assert os.path.exists(os.path.join(test_data["version"].absolute_path, folder))


def test_initialize_structure_will_handle_OSErrors(test_data):
    """initialize_structure() will handle OSErrors when
    creating folders which are already there
    """
    # call it multiple times
    test_data["external_dcc"].initialize_structure(test_data["version"])
    test_data["external_dcc"].initialize_structure(test_data["version"])
    test_data["external_dcc"].initialize_structure(test_data["version"])


def test_save_as_will_conform_and_initialize_structure(test_data):
    """save_as method will conform the given version and
    initialize the structure
    """
    test_data["external_dcc"].save_as(test_data["version"])
    assert test_data["external_dcc"].extensions[0] == test_data["version"].extension
    for folder in test_data["external_dcc"].structure:
        assert os.path.exists(os.path.join(test_data["version"].absolute_path, folder))


def test_get_settings_file_path_returns_the_settings_path_correctly(test_data):
    """get_settings_path returns the settings path correctly"""
    assert (
        os.path.expanduser("~/.atrc/last_version")
        == ExternalDCC.get_settings_file_path()
    )


def test_append_to_recent_files_version_argument_is_not_a_Version_instance(test_data):
    """a TypeError will be raised when the version argument in
    append_to_recent_files() method is not a stalker.models.version.Version
    instance
    """
    pytest.raises(TypeError, test_data["external_dcc"].append_to_recent_files, 3121)


def test_append_to_recent_files_working_properly(test_data):
    """append_to_recent_files() method is working properly"""
    # set the id attribute of the test version to a random number
    test_data["version"].id = 234
    test_data["external_dcc"].append_to_recent_files(test_data["version"])
    # check the settings file
    path = test_data["external_dcc"].get_settings_file_path()
    with open(path, "r") as f:
        vid = f.read()
    assert vid == str(234)


def test_get_last_version_is_working_properly(test_data):
    """get_last_version() returns Version instance properly."""
    from stalker.db.session import DBSession

    DBSession.add(test_data["version"])
    DBSession.commit()
    assert test_data["version"].id is not None
    test_data["external_dcc"].append_to_recent_files(test_data["version"])
    last_version = test_data["external_dcc"].get_last_version()
    assert last_version == test_data["version"]


def test_get_dcc_names_method_will_return_all_dcc_names_properly(
    create_test_db,
):
    """ExternalDCCFactory.get_dcc_names() returns all the DCC names as a list of strs."""
    from anima.dcc.external import external_dccs

    expected_result = list(external_dccs.keys())
    ext_dcc_factory = ExternalDCCFactory()
    result = ext_dcc_factory.get_dcc_names()
    assert expected_result == result


def test_get_dcc_names_method_will_return_complex_dcc_names_properly(
    create_test_db,
):
    """ExternalDCCFactory.get_dcc_names() method will
    return all the DCC names as a list of strings in desired format
    when dcc_name_format is set
    """
    name_format = "{extension} - {name}"
    expected_result = [
        ".ztl - ZBrush",
        ".mud - MudBox",
        #'.psd - Photoshop'
    ]
    ext_dcc_factory = ExternalDCCFactory()
    result = ext_dcc_factory.get_dcc_names(name_format=name_format)
    assert sorted(expected_result) == sorted(result)


def test_get_dcc_method_name_argument_is_not_a_string(create_test_db):
    """a TypeError will be raised when the name argument is not
    a string in ExternalDCCFactory.get_dcc() method
    """
    ext_dcc_factory = ExternalDCCFactory()
    pytest.raises(TypeError, ext_dcc_factory.get_dcc, 234)


def test_get_dcc_method_name_is_not_in_list(create_test_db):
    """a ValueError will be raised when the name argument value
    is not in the anima.dcc.external_dccs list
    """
    ext_dcc_factory = ExternalDCCFactory()
    pytest.raises(ValueError, ext_dcc_factory.get_dcc, "Modo")


def test_get_dcc_method_will_return_desired_dcc(create_test_db):
    """ExternalDCCFactory.get_dcc() will return desired ExternalDCC instance."""
    ext_dcc_factory = ExternalDCCFactory()

    zbrush_tool = ext_dcc_factory.get_dcc("ZBrush")
    assert isinstance(zbrush_tool, ExternalDCC)
    assert zbrush_tool.name == "ZBrush"
    assert zbrush_tool.extensions == [".ztl"]
    assert zbrush_tool.structure == ["Outputs"]

    mudbox = ext_dcc_factory.get_dcc("MudBox")
    assert isinstance(mudbox, ExternalDCC)
    assert mudbox.name == "MudBox"
    assert mudbox.extensions == [".mud"]
    assert mudbox.structure == ["Outputs"]


def test_get_dcc_method_will_return_desired_dcc_even_with_complex_formats(
    create_test_db,
):
    """ExternalDCCFactory.get_dcc() will return desired
    ExternalDCC instance even with names like "MudBox (.mud)"
    """
    ext_dcc_factory = ExternalDCCFactory()

    zbrush = ext_dcc_factory.get_dcc("ZBrush (.ztl)", name_format="{name} ({extension})")
    assert isinstance(zbrush, ExternalDCC)
    assert zbrush.name == "ZBrush"
    assert zbrush.extensions == [".ztl"]
    assert zbrush.structure == ["Outputs"]

    mudbox = ext_dcc_factory.get_dcc("MudBox (.mud)", name_format="{name} ({extension})")
    assert isinstance(mudbox, ExternalDCC)
    assert mudbox.name == "MudBox"
    assert mudbox.extensions == [".mud"]
    assert mudbox.structure == ["Outputs"]


def test_get_dcc_method_will_return_desired_dcc_even_with_custom_formats(
    create_test_db,
):
    """ExternalDCCFactory.get_dcc() will return desired
    ExternalDCC instance even with names like "MudBox (.mud)"
    """
    ext_dcc_factory = ExternalDCCFactory()
    name_format = "({extension}) - {name}"
    zbrush = ext_dcc_factory.get_dcc("(.ztl) ZBrush", name_format=name_format)
    assert isinstance(zbrush, ExternalDCC)
    assert zbrush.name == "ZBrush"
    assert zbrush.extensions == [".ztl"]
    assert zbrush.structure == ["Outputs"]

    mudbox = ext_dcc_factory.get_dcc("(.mud) MudBox", name_format=name_format)
    assert isinstance(mudbox, ExternalDCC)
    assert mudbox.name == "MudBox"
    assert mudbox.extensions == [".mud"]
    assert mudbox.structure == ["Outputs"]
