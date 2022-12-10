# -*- coding: utf-8 -*-
"""Tests for maya DCC with publishers."""
import pytest
from stalker import Type, Version
from stalker.db.session import DBSession

from anima import publish


@pytest.fixture(scope="function")
def setup_publishers():
    """setup once"""
    backup_publishers = publish.publishers
    publish.clear_publishers()

    yield

    # also restore publishers
    publish.publishers = backup_publishers


def test_save_as_calls_publishers_for_published_versions(
    setup_publishers, create_test_data, create_pymel, create_maya_env
):
    """testing if Maya.save_as() runs the registered publishers for
    published versions before really saving the file.
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # register two new publishers
    publishers_called = []

    @publish.publisher("LookDev")
    def publisher1():
        publishers_called.append("publisher1")

    @publish.publisher("Model")
    def publisher2():
        publishers_called.append("publisher2")

    # now save a new version to a task which is a LookDev task
    pm.newFile(force=True)

    data["task6"].type = Type(name="LookDev", code="LookDev", target_entity_type="Task")

    v = Version(task=data["task6"])
    v.is_published = True
    DBSession.add(v)

    # check called publishers
    assert publishers_called == []
    maya_env.save_as(v)
    assert publishers_called == ["publisher1"]


def test_save_as_does_not_call_publishers_for_published_versions(
    setup_publishers, create_test_data, create_pymel, create_maya_env
):
    """testing if Maya.save_as() runs the registered publishers for
    published versions before really saving the file.
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # register two new publishers
    publishers_called = []

    @publish.publisher("LookDev")
    def publisher1():
        publishers_called.append("publisher1")

    @publish.publisher("Model")
    def publisher2():
        publishers_called.append("publisher2")

    # now save a new version to a task which is a LookDev task
    pm.newFile(force=True)

    v = Version(task=data["task6"])
    DBSession.add(v)

    # check called publishers
    assert publishers_called == []
    maya_env.save_as(v)
    assert publishers_called == []
