# -*- coding: utf-8 -*-
import tempfile

import pytest

from stalker import Link, Type, Version
from stalker.db.session import DBSession

from anima.representation import (
    BASE_REPR_NAME,
    REPR_TYPE_NAME,
    Representation,
    get_repr_type,
)


temp_repo_path = tempfile.mkdtemp()
remove_these_files_buffer = []


def test_base_repr_name_is_base():
    """BASE_REPR_NAME is "Base"."""
    assert BASE_REPR_NAME == "Base"


def test_get_repr_type_is_working_as_expected(repr_test_setup):
    """get_repr_type() function is returning the repr type."""
    repr_type = get_repr_type()
    assert isinstance(repr_type, Type)
    assert repr_type.name == REPR_TYPE_NAME
    assert repr_type.target_entity_type == "Link"


#
# Version Extensions
#


def test_get_representation_names_method_exists():
    """Version.get_representation_names() method exists."""
    assert hasattr(Version, "get_representation_names") is True


def test_get_representation_names_returns_all_representation_names_as_a_list(
    repr_test_setup,
):
    """Version.get_representation_names() returns a list of repr names."""
    data = repr_test_setup
    expected_result = [BASE_REPR_NAME, "Bounding Box", "Arnold Scene Source", "GPU"]
    result = data["version2"].get_representation_names()
    assert isinstance(result, list)
    assert len(result) == len(expected_result)
    assert sorted(result) == sorted(expected_result)


def test_get_representation_method_exists():
    """Version.get_representation() method exists."""
    assert hasattr(Version, "get_representation") is True


def test_get_representation_repr_name_is_skipped(repr_test_setup):
    """Version.get_representation() repr_name is skipped."""
    data = repr_test_setup
    v = data["version2"]
    with pytest.raises(TypeError) as cm:
        v.get_representation()

    assert str(cm.value) == (
        "get_representation() missing 1 required positional argument: " "'repr_name'"
    )


def test_get_representation_repr_name_is_not_a_str(repr_test_setup):
    """Version.get_representation() repr_name is not a str."""
    data = repr_test_setup
    v = data["version2"]
    with pytest.raises(TypeError) as cm:
        v.get_representation(12345)

    assert str(cm.value) == ("repr_name should be a str, not int: '12345'")


def test_get_representation_finds_the_given_representation(repr_test_setup):
    """Version.get_representation() finds the latest Link with the given representation."""
    data = repr_test_setup
    repr_name = "Bounding Box"
    v = data["version3"]
    repr = v.get_representation(repr_name)
    assert isinstance(repr, Link)
    assert repr in data["version3"].outputs
    assert repr.name == repr_name


def test_get_representation_cannot_find_the_latest_representation(repr_test_setup):
    """Version.get_representation() can only return repr from the current Version."""
    data = repr_test_setup
    rep = data["version1"].get_representation("Bounding Box")
    assert rep is None


def test_get_representation_method_returns_none_for_invalid_repr_name(repr_test_setup):
    """Version.get_representation() returns None for invalid or nonexistent repr name."""
    data = repr_test_setup
    v = data["version4"]
    assert v.get_representation("Does not exists") is None


def test_has_representations_method_exists():
    """Version.has_representations() method exists."""
    assert hasattr(Version, "has_representations") is True


def test_has_representations_method_is_working_as_expected(repr_test_setup):
    """Version.has_representations() method is working as expected."""
    data = repr_test_setup
    v = data["version1"]
    assert v.has_representations() is False

    v = data["version2"]
    assert v.has_representations() is True

    v = data["version3"]
    assert v.has_representations() is True


def test_has_representation_method_exists():
    """Version.has_representation() method exists."""
    assert hasattr(Version, "has_representation") is True


def test_has_representation_repr_name_is_skipped(repr_test_setup):
    """Version.has_representation() repr_name is skipped."""
    data = repr_test_setup
    v = data["version2"]
    with pytest.raises(TypeError) as cm:
        v.has_representation()

    assert str(cm.value) == (
        "has_representation() missing 1 required positional argument: " "'repr_name'"
    )


def test_has_representation_repr_name_is_not_a_str(repr_test_setup):
    """Version.has_representation() repr_name is not a str raises TypeError."""
    data = repr_test_setup
    v = data["version2"]
    with pytest.raises(TypeError) as cm:
        v.has_representation(12345)

    assert str(cm.value) == ("repr_name should be a str, not int: '12345'")


def test_has_representation_method_is_working_as_expected(repr_test_setup):
    """Version.has_representation() method is working as expected."""
    data = repr_test_setup
    v = data["version2"]
    assert v.has_representation("Bounding Box") is True

    v = data["version4"]
    assert v.has_representation("LOD100") is True

    v = data["version5"]
    assert v.has_representation("Bounding Box") is False


def test_get_base_representation_exists():
    """Version.get_base_representation() method exists."""
    assert hasattr(Version, "get_base_representation") is True


def test_get_base_representation_returns_the_base_representation(repr_test_setup):
    """Version.get_base_representation() returns the base representation."""
    data = repr_test_setup
    v = data["version1"]
    repr = v.get_base_representation()
    assert isinstance(repr, Link)
    assert repr in v.outputs
    assert repr.name == BASE_REPR_NAME


def test_create_representation_exists():
    """Version.create_representation() exists."""
    assert hasattr(Version, "create_representation")


def test_create_representation_repr_name_is_not_a_str(repr_test_setup):
    """Version.create_representation() repr_name is not a str raises TypeError."""
    data = repr_test_setup
    v = data["version1"]
    with pytest.raises(TypeError) as cm:
        _ = v.create_representation(1234)

    assert str(cm.value) == ("repr_name should be a str, not int: '1234'")


def test_create_representation_repr_name_exists_already(repr_test_setup):
    """Version.create_representation() repr_name exists already."""
    data = repr_test_setup
    v = data["version2"]
    with pytest.raises(ValueError) as cm:
        _ = v.create_representation("Bounding Box")

    assert str(cm.value) == (
        "'Bounding Box' representation already exists in this Version"
    )


def test_create_representation_is_working_as_expected(repr_test_setup):
    """Version.create_representation() is working as expected."""
    data = repr_test_setup
    v = data["version1"]
    test_value = "Bounding Box"
    l = v.create_representation(test_value)
    assert isinstance(l, Link)
    assert l.name == test_value
    assert l.type is not None
    assert l.type.name == REPR_TYPE_NAME
    assert l in v.outputs


#
# Link Representation
#


def test_is_representation_method_exists():
    """Link.is_representation() method does exist."""
    assert hasattr(Link, "is_representation")


def test_is_representation_method_is_working_as_expected_for_repr(repr_test_setup):
    """Link.is_representation() is working as expected."""
    data = repr_test_setup
    v = data["version1"]
    repr = v.outputs[0]
    assert isinstance(repr, Link)
    assert repr.is_representation() is True


def test_is_representation_method_is_working_as_expected_for_non_repr(repr_test_setup):
    """Link.is_representation() is working as expected."""
    # test not representation
    l = Link()
    DBSession.save(l)
    assert l.is_representation() is False


def test_is_base_representation_method_exists():
    """Link.is_base_representation() does exist."""
    assert hasattr(Link, "is_base_representation")


def test_is_base_representation_method_is_working_as_expected(repr_test_setup):
    """Link.is_base_representation() is working as expected."""
    data = repr_test_setup
    v = data["version2"]
    repr = None
    for link in v.outputs:
        if link.name == BASE_REPR_NAME:
            repr = link
            break
    assert repr is not None
    assert isinstance(repr, Link)
    assert repr.name == BASE_REPR_NAME
    assert repr.is_base_representation() is True

    not_base_repr = None
    for link in v.outputs:
        if link.name != BASE_REPR_NAME:
            not_base_repr = link
            break
    assert not_base_repr is not None
    assert isinstance(not_base_repr, Link)
    assert not_base_repr.is_base_representation() is False


def test_representation_of_attribute_exists():
    """representation_of attribute exists."""
    assert hasattr(Link, "representation_of")


def test_representation_of_attr_returns_related_version_if_is_repr(repr_test_setup):
    """Link.representation_of attr returns the related Version if this is a repr."""
    data = repr_test_setup
    v = data["version1"]
    l = v.outputs[0]
    assert l.representation_of == v
    v = data["version2"]

    assert all(l.representation_of == v for l in v.outputs)


def test_representation_of_attr_returns_none_if_it_is_not_a_repr(repr_test_setup):
    """Link.representation_of attr returns None if Link is not a repr."""
    data = repr_test_setup
    v = data["version1"]
    l = Link()
    DBSession.save(l)
    v.outputs.append(l)
    DBSession.commit()
    assert l.representation_of is None
