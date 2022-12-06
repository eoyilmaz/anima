# -*- coding: utf-8 -*-
"""Tests for the anima.dcc.create_repo_vars() function."""

import os

import pytest
from stalker import db, Repository
from stalker.db.session import DBSession


@pytest.fixture(scope="function")
def create_test_repo(create_test_db):
    # create test repositories
    data = dict()
    data["repo1"] = Repository(
        name="Test Repo 1",
        code="TR1",
        linux_path="/test/repo/1/linux/path",
        windows_path="T:/test/repo/1/windows/path",
        osx_path="/test/repo/1/osx/path",
    )

    data["repo2"] = Repository(
        name="Test Repo 2",
        code="TR2",
        linux_path="/test/repo/2/linux/path",
        windows_path="T:/test/repo/2/windows/path",
        osx_path="/test/repo/2/osx/path",
    )

    data["repo3"] = Repository(
        name="Test Repo 3",
        code="TR3",
        linux_path="/test/repo/3/linux/path",
        windows_path="T:/test/repo/3/windows/path",
        osx_path="/test/repo/3/osx/path",
    )

    data["repo4"] = Repository(
        name="Test Repo 4",
        code="TR4",
        linux_path="/test/repo/4/linux/path",
        windows_path="T:/test/repo/4/windows/path",
        osx_path="/test/repo/4/osx/path",
    )

    data["repo5"] = Repository(
        name="Test Repo 5",
        code="TR5",
        linux_path="/test/repo/5/linux/path",
        windows_path="T:/test/repo/5/windows/path",
        osx_path="/test/repo/5/osx/path",
    )

    data["all_repos"] = [
        data["repo1"],
        data["repo2"],
        data["repo3"],
        data["repo4"],
        data["repo5"],
    ]

    DBSession.add_all(data["all_repos"])
    DBSession.commit()
    yield data


def test_environment_var_values_are_correct(create_test_repo):
    """testing if all environment var values are correct"""
    data = create_test_repo
    from anima import defaults

    for repo in data["all_repos"]:
        assert (
            os.environ[
                defaults.repo_env_template
                % {
                    "id": repo.id,
                    "code": repo.code,
                }
            ]
            == repo.path
        )


def test_to_os_independent_path_is_working_properly(create_test_repo):
    """testing if stalker.Repository.to_os_independent_path() is working
    as we are expecting it to work
    """
    data = create_test_repo
    # repo4
    linux_path = "/test/repo/4/linux/path/PRJ1/Assets/test.ma"
    windows_path = "T:/test/repo/4/windows/path/PRJ1/Assets/test.ma"
    osx_path = "/test/repo/4/osx/path/PRJ1/Assets/test.ma"

    os_independent_path = "$REPO%s/PRJ1/Assets/test.ma" % data["repo4"].code

    assert Repository.to_os_independent_path(linux_path) == os_independent_path
    assert Repository.to_os_independent_path(windows_path) == os_independent_path
    assert Repository.to_os_independent_path(osx_path) == os_independent_path

    # repo5
    linux_path = "/test/repo/5/linux/path/PRJ1/Assets/test.ma"
    windows_path = "T:/test/repo/5/windows/path/PRJ1/Assets/test.ma"
    osx_path = "/test/repo/5/osx/path/PRJ1/Assets/test.ma"

    os_independent_path = "$REPO%s/PRJ1/Assets/test.ma" % data["repo5"].code

    assert Repository.to_os_independent_path(linux_path) == os_independent_path
    assert Repository.to_os_independent_path(windows_path) == os_independent_path
    assert Repository.to_os_independent_path(osx_path) == os_independent_path
