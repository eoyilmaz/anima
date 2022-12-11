# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="function")
def migration_test_data(create_test_data, create_pymel, create_maya_env):
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env

    # *********************************
    # Asset2
    # *********************************

    # Asset2 - Take1
    pm.newFile(force=True)
    root_node = pm.nt.Transform(name='Asset2_Main')
    box = pm.polyCube(name="Box1")[0]
    pm.parent(box, root_node)
    pm.runtime.DeleteHistory()
    maya_env.save_as(data["version1"])
    maya_env.save_as(data["version2"])
    maya_env.save_as(data["version3"])

    # Asset2 - Take1
    pm.newFile(force=True)
    root_node = pm.nt.Transform(name='Asset2_Take1')
    box = pm.polyCube(name="Box1")[0]
    pm.parent(box, root_node)
    pm.runtime.DeleteHistory()
    maya_env.save_as(data["version4"])
    maya_env.save_as(data["version5"])
    maya_env.save_as(data["version6"])

    yield data


def test_asset_migration_tool_initialization(migration_test_data):
    """Test AssetMigrationTool initialization."""
    from anima.dcc.mayaEnv.general import AssetMigrationTool
    amt = AssetMigrationTool()
    assert isinstance(amt, AssetMigrationTool)
