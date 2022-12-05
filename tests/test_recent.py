# -*- coding: utf-8 -*-
import tempfile
import os

import unittest

import pytest
from anima.recent import RecentFileManager


@pytest.mark.parametrize(
    "env_name, path",
    [
        ("Photoshop", "some path"),
        ("Maya", "some other path"),
        ("Maya", "some new other path"),
        ("Photoshop", "some path 2"),
    ],
)
def test_add_method_is_working_properly(prepare_recent_file_cache_path, env_name, path):
    """testing if the add method will add a new file entry to the recent
    files list
    """
    rfm = RecentFileManager()
    rfm.add(env_name, path)
    assert rfm.recent_files[env_name][0] == path


def test_add_method_with_a_new_environment_name(prepare_recent_file_cache_path):
    """testing if the add method is able to add files to a new DCC"""
    rfm = RecentFileManager()
    rfm.add("New Env", "some path")
    assert rfm.recent_files["New Env"][0] == "some path"


def test_add_method_also_calls_save(prepare_recent_file_cache_path):
    """testing if the add method also calls save method"""
    rfm1 = RecentFileManager()
    rfm1.add("New Env", "some path")
    rfm2 = RecentFileManager()
    assert rfm2["New Env"] == ["some path"]


def test_add_method_pops_previous_versions_and_inserts_them_to_0(
    prepare_recent_file_cache_path,
):
    """testing if an entry will be popped from the recent_files list if it
    is added to the list again
    """
    rfm1 = RecentFileManager()
    rfm1.add("Env1", "path1")
    rfm1.add("Env1", "path2")
    rfm1.add("Env1", "path3")

    assert rfm1["Env1"] == ["path3", "path2", "path1"]

    rfm1.add("Env1", "path1")
    assert rfm1["Env1"] == ["path1", "path3", "path2"]


def test_recent_files_attribute_is_working_properly(prepare_recent_file_cache_path):
    """testing if the recent_files attribute is working properly"""
    rfm1 = RecentFileManager()
    rfm1.add("New Env", "some path")
    assert rfm1.recent_files == {"New Env": ["some path"]}


def test_restore_limits_maximum_files_stored(prepare_recent_file_cache_path):
    """testing if restore limits the maximum files stored"""
    from anima import defaults

    rm = RecentFileManager()
    for i in range(defaults.max_recent_files + 100):
        rm.add("Env1", "some path %s" % i)

    rm2 = RecentFileManager()
    assert len(rm2["Env1"]) == defaults.max_recent_files


def test_restore_is_working_properly(prepare_recent_file_cache_path):
    """testing if the restore method is working properly"""
    rfm1 = RecentFileManager()
    rfm1.add("New Env", "some path")
    rfm1.save()

    rfm2 = RecentFileManager()
    # clear the recent files
    rfm2.recent_files = []
    rfm2.restore()

    assert rfm2.recent_files["New Env"][0] == "some path"


def test_RecentFileManager_is_indexable(prepare_recent_file_cache_path):
    """testing if the RecentFileManager instance is indexable with the
    DCC name
    """
    rfm1 = RecentFileManager()
    rfm1.add("Env1", "Path1")
    rfm1.add("Env1", "Path2")
    rfm1.add("Env1", "Path3")

    rfm1.add("Env2", "Path4")
    rfm1.add("Env2", "Path5")
    rfm1.add("Env2", "Path6")

    assert rfm1["Env1"] == ["Path3", "Path2", "Path1"]
    assert rfm1["Env2"] == ["Path6", "Path5", "Path4"]


def test_remove_method_removes_files_from_given_env(prepare_recent_file_cache_path):
    """testing if the given path will be removed from the given DCC"""
    rfm1 = RecentFileManager()
    rfm1.add("Env1", "Path1")
    rfm1.add("Env1", "Path2")
    rfm1.add("Env1", "Path3")

    rfm1.add("Env2", "Path4")
    rfm1.add("Env2", "Path5")
    rfm1.add("Env2", "Path6")

    assert rfm1["Env1"] == ["Path3", "Path2", "Path1"]
    assert rfm1["Env2"] == ["Path6", "Path5", "Path4"]

    rfm1.remove("Env1", "Path1")
    assert rfm1["Env1"] == ["Path3", "Path2"]

    rfm1.remove("Env1", "Path3")
    assert rfm1["Env1"] == ["Path2"]

    rfm1.remove("Env2", "Path5")
    assert rfm1["Env2"] == ["Path6", "Path4"]
