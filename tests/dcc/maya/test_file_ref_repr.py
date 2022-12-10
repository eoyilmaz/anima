# -*- coding: utf-8 -*-
import pytest

from stalker.db.session import DBSession

from tests.dcc.maya.utils import create_version


@pytest.fixture(scope="function")
def create_ref_test_data(create_test_data, create_pymel):
    """additional setup"""
    data = create_test_data
    pm = create_pymel
    # now do your addition
    # create ass take for asset2
    data["repr_version1"] = create_version(data["asset2"], "Main@ASS", data["version3"])
    data["repr_version2"] = create_version(data["asset2"], "Main@ASS", data["version3"])
    data["repr_version3"] = create_version(data["asset2"], "Main@ASS", data["version3"])

    data["repr_version1"].is_published = True
    data["repr_version3"].is_published = True

    data["repr_version4"] = create_version(
        data["asset2"], "Main@BBox", data["version3"]
    )
    data["repr_version5"] = create_version(
        data["asset2"], "Main@BBox", data["version3"]
    )
    data["repr_version6"] = create_version(
        data["asset2"], "Main@BBox", data["version3"]
    )

    data["repr_version4"].is_published = True
    data["repr_version6"].is_published = True

    data["repr_version7"] = create_version(data["asset2"], "Main@GPU", data["version3"])
    data["repr_version8"] = create_version(data["asset2"], "Main@GPU", data["version3"])
    data["repr_version9"] = create_version(data["asset2"], "Main@GPU", data["version3"])

    data["repr_version9"].is_published = True

    data["repr_version10"] = create_version(
        data["asset2"], "Take1@ASS", data["version3"]
    )
    data["repr_version11"] = create_version(
        data["asset2"], "Take1@ASS", data["version3"]
    )
    data["repr_version12"] = create_version(
        data["asset2"], "Take1@ASS", data["version3"]
    )

    data["repr_version11"].is_published = True

    data["repr_version13"] = create_version(
        data["asset2"], "Take1@BBox", data["version3"]
    )
    data["repr_version14"] = create_version(
        data["asset2"], "Take1@BBox", data["version3"]
    )
    data["repr_version15"] = create_version(
        data["asset2"], "Take1@BBox", data["version3"]
    )

    data["repr_version14"].is_published = True

    data["repr_version16"] = create_version(
        data["asset2"], "Take1@GPU", data["version3"]
    )
    data["repr_version17"] = create_version(
        data["asset2"], "Take1@GPU", data["version3"]
    )
    data["repr_version18"] = create_version(
        data["asset2"], "Take1@GPU", data["version3"]
    )

    data["repr_version16"].is_published = True
    data["repr_version17"].is_published = True
    data["repr_version18"].is_published = True

    # a reference with only ASS representation
    data["repr_version19"] = create_version(data["asset2"], "Take2")
    data["repr_version20"] = create_version(data["asset2"], "Take2")
    data["repr_version21"] = create_version(data["asset2"], "Take2")

    data["repr_version21"].is_published = True

    data["repr_version22"] = create_version(
        data["asset2"], "Take2@ASS", data["version21"]
    )
    data["repr_version23"] = create_version(
        data["asset2"], "Take2@ASS", data["version21"]
    )
    data["repr_version24"] = create_version(
        data["asset2"], "Take2@ASS", data["version21"]
    )

    data["repr_version24"].is_published = True

    data["version1"].is_published = True
    data["version3"].is_published = True

    DBSession.commit()

    import pymel.core as pm
    pm.newFile(force=True)
    yield data


def test_FileReference_class_has_to_repr_method(create_ref_test_data):
    """testing if FileReference has a to_repr() method"""
    from pymel.core.system import FileReference

    assert hasattr(FileReference, "to_repr")


def test_FileReference_class_has_list_all_repr_method(create_ref_test_data):
    """testing if FileReference has a list_all_repr() method"""
    from pymel.core.system import FileReference

    assert hasattr(FileReference, "list_all_repr")


def test_FileReference_class_has_list_find_repr_method(create_ref_test_data):
    """testing if FileReference has a find_repr() method"""
    from pymel.core.system import FileReference

    assert hasattr(FileReference, "find_repr")


def test_to_repr_is_working_properly(create_ref_test_data, create_maya_env):
    """testing if FileReference.to_repr() is working properly"""
    # reference version1 to the scene
    data = create_ref_test_data
    maya_env = create_maya_env
    maya_env.save_as(data["version4"])
    ref = maya_env.reference(data["version1"])
    assert ref.path == data["version1"].absolute_full_path
    # now invoke to_repr on the FileReference node
    ref.to_repr("ASS")
    # and expect its path to be replaced with data["repr_version3"]
    assert ref.path == data["repr_version3"].absolute_full_path


def test_to_base_is_working_properly(create_ref_test_data, create_maya_env):
    """testing if FileReference.to_base() is working properly"""
    data = create_ref_test_data
    maya_env = create_maya_env
    # reference version1 to the scene
    maya_env.save_as(data["version4"])
    ref = maya_env.reference(data["repr_version1"])
    assert ref.path == data["repr_version1"].absolute_full_path
    # now invoke to_base on the FileReference node
    ref.to_base()
    # and expect its path to be replaced with data["repr_version3"]
    assert ref.path == data["version3"].absolute_full_path


def test_list_all_repr_is_working_properly(create_ref_test_data, create_maya_env):
    """testing if list_all_repr is working properly"""
    data = create_ref_test_data
    maya_env = create_maya_env
    maya_env.save_as(data["version4"])
    ref = maya_env.reference(data["repr_version1"])
    assert ref.path == data["repr_version1"].absolute_full_path
    result = ref.list_all_repr()
    assert sorted(["Base", "ASS", "BBox", "GPU"]) == sorted(result)


def test_find_repr_is_working_properly(create_ref_test_data, create_maya_env):
    """testing if find_repr is working properly"""
    data = create_ref_test_data
    maya_env = create_maya_env
    maya_env.save_as(data["version4"])
    ref = maya_env.reference(data["repr_version1"])
    assert ref.path == data["repr_version1"].absolute_full_path
    result = ref.find_repr("GPU")
    assert result.absolute_full_path == data["repr_version9"].absolute_full_path


def test_is_base_is_working_properly(create_ref_test_data, create_maya_env):
    """testing if is_base is working properly"""
    data = create_ref_test_data
    maya_env = create_maya_env
    maya_env.save_as(data["version4"])
    ref = maya_env.reference(data["repr_version1"])
    assert ref.path == data["repr_version1"].absolute_full_path
    assert not ref.is_base()

    ref = maya_env.reference(data["version1"])
    assert ref.path == data["version1"].absolute_full_path
    assert ref.is_base()


def test_get_base_is_working_properly(create_ref_test_data, create_maya_env):
    """testing if get_base is working properly"""
    data = create_ref_test_data
    maya_env = create_maya_env
    maya_env.save_as(data["version4"])
    ref = maya_env.reference(data["repr_version1"])
    assert ref.path == data["repr_version1"].absolute_full_path
    assert not ref.is_base()
    v = ref.get_base()
    assert v.absolute_full_path == data["version3"].absolute_full_path


def test_is_repr_method_is_working_properly(create_ref_test_data, create_maya_env):
    """testing if is_repr is working properly"""
    data = create_ref_test_data
    maya_env = create_maya_env
    maya_env.save_as(data["version4"])
    ref = maya_env.reference(data["repr_version1"])
    assert ref.path == data["repr_version1"].absolute_full_path
    assert not ref.is_repr("Base")
    assert ref.is_repr("ASS")


def test_repr_property_is_working_properly(create_ref_test_data, create_maya_env):
    """testing if ``repr`` property is working properly"""
    data = create_ref_test_data
    maya_env = create_maya_env
    maya_env.save_as(data["version4"])
    ref = maya_env.reference(data["repr_version1"])
    assert ref.path == data["repr_version1"].absolute_full_path
    assert ref.repr == "ASS"
