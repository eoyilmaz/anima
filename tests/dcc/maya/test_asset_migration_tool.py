# -*- coding: utf-8 -*-

import pytest


def test_asset_migration_tool_initialization(create_db, create_project):
    """Test AssetMigrationTool initialization."""
    from stalker import Asset, Task, Project
    project1 = create_project
    project2 = Project.query.filter(Project.code=="TP2").first()
    assert project2 is not None
    env1 = Asset.query.filter(Asset.code=="Env1").first()
    assert env1 is not None
    assert env1.project == project1
    # migrate the env1 to the second project

    from anima.dcc.mayaEnv.general import AssetMigrationTool
    amt = AssetMigrationTool()
    assert isinstance(amt, AssetMigrationTool)
