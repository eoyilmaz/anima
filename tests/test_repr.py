# -*- coding: utf-8 -*-
import shutil
import tempfile

import unittest
import os

import pytest

from anima.representation import Representation


temp_repo_path = tempfile.mkdtemp()
remove_these_files_buffer = []


def test_list_all_lists_all_representations(repr_test_setup):
    """testing if Representation.list_all() returns a list of strings
    showing the repr names.
    """
    expected_result = ['Base', 'BBox', 'ASS', 'GPU']
    rep = Representation(repr_test_setup["version1"])
    result = rep.list_all()
    assert sorted(expected_result) == sorted(result)


def test_list_all_lists_all_representations_from_non_base_version(repr_test_setup):
    """testing if Representation.list_all() returns a list of strings
    showing the repr names by using non base version.
    """
    expected_result = ['Base', 'Hires', 'Midres', 'Lores']
    rep = Representation(repr_test_setup["version10"])
    result = rep.list_all()
    assert sorted(expected_result) == sorted(result)


def test_find_method_finds_the_given_representation(repr_test_setup):
    """testing if Representation.find() finds the latest version with the
    given representation.
    """
    rep = Representation(repr_test_setup["version1"])
    result = rep.find('BBox')
    assert repr_test_setup["version5"] == result


def test_find_method_finds_the_given_repr_from_different_repr(repr_test_setup):
    """testing if Representation.find() finds the latest version with the
    given representation from a different representation than the base one.
    """
    rep = Representation(repr_test_setup["version4"])
    result = rep.find('ASS')
    assert repr_test_setup["version7"] == result


def test_find_method_returns_none_for_invalid_repr_name(repr_test_setup):
    """testing if Representation.find() returns None for invalid or
    nonexistent repr name
    """
    rep = Representation(repr_test_setup["version4"])
    assert rep.find('NonExists') is None


def test_has_any_repr_method_is_working_properly(repr_test_setup):
    """testing if Representation.has_any_repr() method is working properly
    """
    rep = Representation(repr_test_setup["version1"])
    assert rep.has_any_repr()

    rep.version = repr_test_setup["version17"]
    assert rep.has_any_repr()

    rep.version = repr_test_setup["version19"]
    assert not rep.has_any_repr()


def test_has_repr_method_is_working_properly(repr_test_setup):
    """testing if Representation.has_repr() method is working properly
    """
    rep = Representation(repr_test_setup["version1"])
    assert rep.has_repr('BBox') is True

    rep.version = repr_test_setup["version17"]
    assert rep.has_repr('Lores') is True

    rep.version = repr_test_setup["version19"]
    assert rep.has_repr('BBox') is False


def test_get_base_take_name_is_working_properly(repr_test_setup):
    """testing if the Representation.get_base_take_name() method is working
    properly
    """
    rep = Representation()
    assert 'Main' == rep.get_base_take_name(repr_test_setup["version1"])
    assert 'alt1' == rep.get_base_take_name(repr_test_setup["version10"])
    assert 'alt1' == rep.get_base_take_name(repr_test_setup["version12"])
    assert 'NoRepr' == rep.get_base_take_name(repr_test_setup["version18"])


def test_version_argument_is_skipped(repr_test_setup):
    """testing if it is possible to skip the version argument
    """
    rep = Representation()
    assert rep.version is None


def test_version_argument_is_none(repr_test_setup):
    """testing if the version argument can be None
    """
    rep = Representation(None)
    assert rep.version is None


def test_version_attribute_is_set_to_none(repr_test_setup):
    """testing if setting the version attribute to None is possible
    """
    rep = Representation(repr_test_setup["version1"])
    assert rep.version is not None
    rep.version = None
    assert rep.version is None


def test_version_argument_is_not_a_version_instance(repr_test_setup):
    """testing if a TypeError will be raised when the version argument is
    not a Version instance
    """
    with pytest.raises(TypeError) as cm:
        Representation('not a version')

    assert (
        'Representation.version should be a '
        'stalker.models.version.Version instance, not str' == str(cm.value)
    )


def test_version_attribute_is_not_a_version_instance(repr_test_setup):
    """testing if a TypeError will be raised when the version attribute is
    set to a value other then None and a Version instance
    """
    rep = Representation()
    with pytest.raises(TypeError) as cm:
        rep.version = 'not a version'

    assert (
        'Representation.version should be a '
        'stalker.models.version.Version instance, not str' == str(cm.value)
    )


def test_version_argument_is_working_properly(repr_test_setup):
    """testing if the version argument value is correctly passed to the
    version attribute
    """
    rep = Representation(repr_test_setup["version1"])
    assert rep.version == repr_test_setup["version1"]


def test_version_attribute_is_working_properly(repr_test_setup):
    """testing if the version attribute is working properly
    """
    rep = Representation(repr_test_setup["version1"])
    assert rep.version != repr_test_setup["version2"]
    rep.version = repr_test_setup["version2"]
    assert rep.version == repr_test_setup["version2"]


def test_is_base_method_is_working_properly(repr_test_setup):
    """testing if Representation.is_base() method is working properly
    """
    rep = Representation(repr_test_setup["version1"])
    assert rep.is_base() is True

    rep = Representation(repr_test_setup["version4"])
    assert rep.is_base() is False


def test_is_repr_method_is_working_properly(repr_test_setup):
    """testing if Representation.is_repr() method is working properly
    """
    rep = Representation(repr_test_setup["version1"])
    assert rep.is_repr('Base') is True

    rep = Representation(repr_test_setup["version4"])
    assert rep.is_repr('Base') is False

    rep = Representation(repr_test_setup["version4"])
    assert rep.is_repr('BBox') is True


def test_repr_property_is_working_properly(repr_test_setup):
    """testing if Representation.repr property is working properly
    """
    rep = Representation(repr_test_setup["version1"])
    assert rep.repr == 'Base'

    rep = Representation(repr_test_setup["version4"])
    assert rep.repr == 'BBox'
