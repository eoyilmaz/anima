# -*- coding: utf-8 -*-

import pytest

from stalker import Project, Task, Asset, Version
from stalker.db.session import DBSession

from anima.dcc.mayaEnv import auxiliary


@pytest.fixture(scope="function")
def migration_test_data(create_test_data, create_pymel, create_maya_env):
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env

    # *********************************
    # Target Project
    # create a test project
    data["project2"] = Project(
        name="Test Project 2",
        code="TP2",
        repositories=[data["repo1"]],
        status_list=data["project_status_list"],
        structure=data["structure"],
        image_format=data["image_format"],
    )
    DBSession.add(data["project2"])
    DBSession.commit()

    data["assets_task2"] = Task(name="Assets", project=data["project2"])
    data["assets_task3"] = Task(name="Assets", project=data["project2"])
    DBSession.add_all([data["assets_task2"], data["assets_task3"]])
    DBSession.commit()

    data["random_asset1"] = Asset(
        name="Random Asset1",
        code="RandomAsset1",
        type=data["exterior_type"],
        parent=data["assets_task3"]
    )
    DBSession.add(data["random_asset1"])

    data["random_asset1_model"] = Task(
        name="Model",
        type=data["model_type"],
        parent=data["random_asset1"]
    )
    DBSession.add(data["random_asset1_model"])
    DBSession.commit()

    data["random_asset1_model_main_version1"] = Version(
        task=data["random_asset1_model"]
    )
    DBSession.add(data["random_asset1_model_main_version1"])
    DBSession.commit()

    # *********************************
    # Asset2
    # *********************************

    # Asset2 - Model - Main
    pm.newFile(force=True)
    root_node = pm.nt.Transform(name="Asset2_Main")
    box = pm.polyCube(name="Box1")[0]
    pm.parent(box, root_node)
    pm.runtime.DeleteHistory()
    maya_env.save_as(data["asset2_model_main_v001"])
    maya_env.save_as(data["asset2_model_main_v002"])
    maya_env.save_as(data["asset2_model_main_v003"])
    DBSession.commit()

    # Asset2 - Take1
    pm.newFile(force=True)
    root_node = pm.nt.Transform(name="Asset2_Take1")
    box = pm.polyCube(name="Box4")[0]
    pm.parent(box, root_node)
    pm.runtime.DeleteHistory()
    maya_env.save_as(data["asset2_model_take1_v001"])
    maya_env.save_as(data["asset2_model_take1_v002"])
    maya_env.save_as(data["asset2_model_take1_v003"])
    DBSession.commit()

    # --------------------------
    # Ext2
    # Model
    pm.newFile(force=True)
    root_node = pm.nt.Transform(name="Ext2_Geo")
    ground_geo = pm.polyCube(name="GroundGeo")[0]
    # fix uvs
    pm.polyEditUV(
        "{}.map[0:1000]".format(ground_geo.getShape()), pu=0.5, pv=0.5, su=0.5, sv=0.5
    )
    pm.parent(ground_geo, root_node)
    pm.runtime.DeleteHistory()
    maya_env.save_as(data["ext2_model_main_v001"])
    maya_env.save_as(data["ext2_model_main_v002"])
    data["ext2_model_main_v003"].is_published = True
    maya_env.save_as(data["ext2_model_main_v003"])
    maya_env.save_as(data["random_asset1_model_main_version1"])
    data["random_asset1_model_main_version1"].parent = None
    DBSession.commit()

    # --------------------------
    # LookDev
    pm.newFile(force=True)
    maya_env.save_as(data["ext2_look_dev_main_v001"])
    maya_env.reference(data["ext2_model_main_v003"])
    # assign a shader
    surface_shader = pm.shadingNode("surfaceShader", asShader=1)
    shading_group = pm.nt.ShadingEngine(name="surfaceShaderSG")
    surface_shader.outColor.connect(shading_group.surfaceShader)
    ground_geo = pm.ls("GroundGeo", r=1)[0]
    pm.sets("initialShadingGroup", remove=ground_geo.getShape())
    pm.sets(shading_group, fe=ground_geo.getShape())

    # save versions
    maya_env.save_as(data["ext2_look_dev_main_v001"])
    maya_env.save_as(data["ext2_look_dev_main_v002"])
    # publish it
    data["ext2_look_dev_main_v003"].is_published = True
    maya_env.save_as(data["ext2_look_dev_main_v003"])

    # --------------------------
    # Layout
    pm.newFile(force=True)
    maya_env.save_as(data["ext2_layout_main_v001"])
    # Create a root_node
    root_node = pm.nt.Transform(name="Ext2_Layout")
    # Reference the LookDev
    ref_node = maya_env.reference(data["ext2_look_dev_main_v003"])
    # parent the root of the look dev node to the root node
    look_dev_root_node = auxiliary.get_root_nodes(ref_node)[0]
    pm.parent(look_dev_root_node, root_node)
    maya_env.save_as(data["ext2_layout_main_v001"])
    maya_env.save_as(data["ext2_layout_main_v002"])
    data["ext2_layout_main_v003"].is_published = True
    maya_env.save_as(data["ext2_layout_main_v003"])

    yield data


def test_asset_migration_tool_initialization(migration_test_data):
    """Test AssetMigrationTool initialization."""
    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    assert isinstance(amt, AssetMigrationTool)


def test_migrating_simple_asset_1(migration_test_data):
    """Test AssetMigrationTool with simple asset. Stalker Data."""
    # Asset
    #   Model
    #     Main
    # Check Stalker data
    data = migration_test_data
    migration_recipe = {
        data["asset2"].id: {
            "new_parent_id": data["assets_task2"].id,
            "tasks": {
                data["asset2_model"].id: {
                    "Main": {"new_take_name": "Main", "versions": [data["asset2_model_main_v003"]]}
                }
            },
        }
    }

    assert data["assets_task2"].children == []

    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    amt.migrate()

    # we now should have a new asset under the Assets Task2
    assert data["assets_task2"].children != []
    new_asset = data["assets_task2"].children[0]
    assert isinstance(new_asset, Asset)
    assert new_asset.name == data["asset2"].name
    assert new_asset.code == data["asset2"].code
    assert new_asset.type == data["asset2"].type
    assert new_asset.children != []
    model_task = new_asset.children[0]
    assert isinstance(model_task, Task)
    assert model_task.name == "Model"
    assert model_task.versions != []
    assert len(model_task.versions) == 1
    version = model_task.versions[0]
    assert version.take_name == "Main"


def test_migrating_simple_asset_2(migration_test_data, create_pymel, create_maya_env):
    """Test AssetMigrationTool carries file content for simple asset. File Content,"""
    # Asset
    #   Model
    #     Main
    # Check file content
    data = migration_test_data
    pm = create_pymel
    maya_env = create_maya_env
    migration_recipe = {
        data["asset2"].id: {
            "new_parent_id": data["assets_task2"].id,
            "tasks": {
                data["asset2_model"].id: {
                    "Main": {
                        "new_take_name": "Main",
                        "versions": [data["asset2_model_main_v003"]],
                    }
                }
            },
        }
    }

    assert data["assets_task2"].children == []

    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    amt.migrate()

    # we now should have a new asset under the Assets Task2
    new_asset = data["assets_task2"].children[0]
    model_task = new_asset.children[0]
    version = model_task.versions[0]
    assert version.extension == ".ma"

    # open the maya scene
    # and check content
    maya_env.open(version, force=True)

    root_node = pm.ls("Asset2_Main")[0]
    assert root_node is not None
    box = pm.ls("Box1")[0]
    assert box is not None
    assert box.getParent() == root_node


def test_migrating_simple_asset_3(migration_test_data, create_pymel, create_maya_env):
    """Test AssetMigrationTool carries file content for simple asset. Stalker Data."""
    # Asset
    #   Model
    #     Main
    #     Take1
    # Check Stalker data for two takes
    data = migration_test_data
    migration_recipe = {
        data["asset2"].id: {
            "new_parent_id": data["assets_task2"].id,
            "tasks": {
                data["asset2_model"].id: {
                    "Main": {"new_take_name": "Main", "versions": [data["asset2_model_main_v003"]]},
                    "Take1": {"new_take_name": "Take1", "versions": [data["asset2_model_take1_v003"]]},
                }
            },
        }
    }

    assert data["assets_task2"].children == []

    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    amt.migrate()

    # we now should have a new asset under the Assets Task2
    assert data["assets_task2"].children != []
    new_asset = data["assets_task2"].children[0]
    assert isinstance(new_asset, Asset)
    assert new_asset.name == data["asset2"].name
    assert new_asset.code == data["asset2"].code
    assert new_asset.type == data["asset2"].type
    assert new_asset.children != []
    model_task = new_asset.children[0]
    assert isinstance(model_task, Task)
    assert model_task.name == "Model"
    assert model_task.versions != []
    assert len(model_task.versions) == 2
    assert (
        Version.query.filter(Version.task == model_task)
        .filter(Version.take_name == "Main")
        .count()
        == 1
    )
    assert (
        Version.query.filter(Version.task == model_task)
        .filter(Version.take_name == "Take1")
        .count()
        == 1
    )


def test_migrating_simple_asset_4(migration_test_data, create_pymel, create_maya_env):
    """Test AssetMigrationTool carries file content for simple asset. File Content."""
    # Asset
    #   Model
    #     Main
    #     Take1
    # Check file contents
    data = migration_test_data
    pm = create_pymel
    maya_env = create_maya_env
    migration_recipe = {
        data["asset2"].id: {
            "new_parent_id": data["assets_task2"].id,
            "tasks": {
                data["asset2_model"].id: {
                    "Main": {"new_take_name": "Main", "versions": [data["asset2_model_main_v003"]]},
                    "Take1": {"new_take_name": "Take1", "versions": [data["asset2_model_take1_v003"]]},
                }
            },
        }
    }

    assert data["assets_task2"].children == []

    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    amt.migrate()

    # we now should have a new asset under the Assets Task2
    # Main
    new_asset = data["assets_task2"].children[0]
    model_task = new_asset.children[0]
    version = (
        Version.query.filter(Version.task == model_task)
        .filter(Version.take_name == "Main")
        .first()
    )
    assert version.extension == ".ma"

    # open the maya scene
    # and check content
    maya_env.open(version, force=True)

    root_node = pm.ls("Asset2_Main")[0]
    assert root_node is not None
    box = pm.ls("Box1")[0]
    assert box is not None
    assert box.getParent() == root_node

    # Take1
    version = (
        Version.query.filter(Version.task == model_task)
        .filter(Version.take_name == "Take1")
        .first()
    )
    assert version.extension == ".ma"

    # open the maya scene
    # and check content
    maya_env.open(version, force=True)

    root_node = pm.ls("Asset2_Take1")[0]
    assert root_node is not None
    box = pm.ls("Box4")[0]
    assert box is not None
    assert box.getParent() == root_node


def test_migrating_simple_env_asset_1(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool with a simple environment asset. Stalker Data."""
    # EnvAsset
    #   Model (don't move)
    #   LookDev
    #   Layout
    # Check Stalker data
    data = migration_test_data
    pm = create_pymel
    maya_env = create_maya_env
    migration_recipe = {
        data["ext2"].id: {
            "new_parent_id": data["assets_task2"].id,
            "tasks": {
                data[
                    "ext2_layout"
                ].id: {  # tricky part, this needs to be moved after look dev
                    "Main": {"versions": [data["ext2_layout_main_v003"]]},
                },
                data["ext2_look_dev"].id: {
                    "Main": {"versions": [data["ext2_look_dev_main_v003"]]},
                },
            },
        }
    }

    assert data["assets_task2"].children == []

    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    amt.migrate()

    # we now should have a new asset under the Assets Task2
    assert data["assets_task2"].children != []
    new_asset = data["assets_task2"].children[0]
    assert isinstance(new_asset, Asset)
    assert new_asset.name == data["ext2"].name
    assert new_asset.code == data["ext2"].code
    assert new_asset.type == data["ext2"].type
    assert len(new_asset.children) == 2

    # Model (There should be no model task as it is not moved)
    model_task = (
        Task.query.filter(Task.parent == new_asset).filter(Task.name == "Model").first()
    )
    assert model_task is None

    # LookDev Task
    look_dev_task = (
        Task.query.filter(Task.parent == new_asset)
        .filter(Task.name == "LookDev")
        .first()
    )
    assert look_dev_task.name == "LookDev"
    assert len(look_dev_task.versions) == 1
    look_dev_version = look_dev_task.versions[0]
    assert look_dev_version.take_name == "Main"
    assert len(look_dev_version.inputs) == 1
    assert data["ext2_model_main_v003"] in look_dev_version.inputs  # baam!

    # Layout Task
    layout_task = (
        Task.query.filter(Task.parent == new_asset)
        .filter(Task.name == "Layout")
        .first()
    )
    assert layout_task.name == "Layout"
    assert len(layout_task.versions) == 1
    layout_version = layout_task.versions[0]
    assert layout_version.take_name == "Main"
    assert len(layout_version.inputs) == 1
    assert look_dev_version in layout_version.inputs  # baam 2!


def test_migrating_simple_env_asset_2(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool with a simple environment asset."""
    #   Model (don't move)
    #   LookDev
    #   Layout
    # Check Stalker data
    data = migration_test_data
    pm = create_pymel
    maya_env = create_maya_env
    migration_recipe = {
        data["ext2"].id: {
            "new_parent_id": data["assets_task2"].id,
            "tasks": {
                data[
                    "ext2_layout"
                ].id: {  # tricky part, this needs to be moved after look dev
                    "Main": {"versions": [data["ext2_layout_main_v003"]]},
                },
                data["ext2_look_dev"].id: {
                    "Main": {"versions": [data["ext2_look_dev_main_v003"]]},
                },
            },
        }
    }

    assert data["assets_task2"].children == []

    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    amt.migrate()

    # we now should have a new asset under the Assets Task2
    assert data["assets_task2"].children != []
    new_asset = data["assets_task2"].children[0]
    assert isinstance(new_asset, Asset)
    assert new_asset.name == data["ext2"].name
    assert new_asset.code == data["ext2"].code
    assert new_asset.type == data["ext2"].type
    assert len(new_asset.children) == 2

    # Model (There should be no model task as it is not moved)
    model_task = (
        Task.query.filter(Task.parent == new_asset).filter(Task.name == "Model").first()
    )
    assert model_task is None

    # LookDev Task
    look_dev_task = (
        Task.query.filter(Task.parent == new_asset)
        .filter(Task.name == "LookDev")
        .first()
    )
    look_dev_version = look_dev_task.versions[0]
    maya_env.open(look_dev_version, force=True)
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == data["ext2_model_main_v003"]  # baam!

    # Layout Task
    layout_task = (
        Task.query.filter(Task.parent == new_asset)
        .filter(Task.name == "Layout")
        .first()
    )
    layout_version = layout_task.versions[0]
    maya_env.open(layout_version, force=True)
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == look_dev_version  # baam 2!


def test_migrating_complex_env_asset_1(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool with a complex environment asset."""
    # Ext1 (Asset - Exterior)
    # +- Building1 (Asset - Building)
    # |  +- Layout (Task - Layout)
    # |  |  +- version66
    # |  +- LookDev (Task - Look Development)
    # |  |  +- version69
    # |  +- Props (Task)
    # |     +- YAPI (Task)
    # |        +- Model (Task - Model)
    # |        |  +- version75
    # |        +- LookDev (Task - Look Development)
    # |           +- version78
    # +- Building2 (Asset - Building)
    # |  +- Layout (Task - Layout)
    # |  |  +- version84
    # |  +- LookDev (Task - Look Development)
    # |  |  +- version87
    # |  +- Props (Task)
    # |     +- YAPI (Task)
    # |        +- Model (Task - Model)
    # |        |  +- version93
    # |        +- LookDev (Task - Look Development)
    # |           +- version96
    # +- Layout (Task - Layout)
    # |  +- version102
    # +- LookDev (Task - Look Development)
    # |  +- version105
    # +- Props (Task)
    # |  +- Prop1 (Asset)
    # |     +- Model (Task - Model)
    # |     |  +- **Main** (Take)
    # |     |  |  +- version111
    # |     |  +- **Kisa** (Take)
    # |     |     +- version123
    # |     +- LookDev (Task - Look Development)
    # |        +- **Main** (Take)
    # |        |  +- version114
    # |        +- **Kisa** (Take)
    # |           +- version120
    # +- Vegetation (Task - Vegetation)
    #    +- version117
    # Check Stalker data
    data = migration_test_data
    pm = create_pymel
    maya_env = create_maya_env
    migration_recipe = {
        data["ext2"].id: {
            "new_parent_id": data["assets_task2"].id,
            "tasks": {
                data["ext2_layout"].id: {
                    # tricky part, this needs to be moved after look dev
                    "Main": {"versions": [data["ext2_layout_main_v003"]]},
                },
                data["ext2_look_dev"].id: {
                    "Main": {"versions": [data["ext2_look_dev_main_v003"]]},
                },
                data["Props"].id: {}
            },
        }
    }

    assert data["assets_task2"].children == []

    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    amt.migrate()

    raise NotImplementedError("Test is not implemented yet")


def test_migration_complex_env_asset_2(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool with a complex environment asset."""
    # EnvAsset
    #   Layout
    #   Props
    #     Bina1
    #       Model
    #       LookDev
    # Check File content
    raise NotImplementedError("Test is not implemented yet")


def test_migrating_with_alternative_versions_data_1(
    migration_test_data, create_pymel, create_maya_env
):
    """Test a version with referenced data, references are moved previously."""
    # EnvAsset
    #   Model (don't move)
    #   LookDev
    # Check Stalker data
    data = migration_test_data
    pm = create_pymel
    maya_env = create_maya_env
    migration_recipe = {
        data["ext2"].id: {
            "new_parent_id": data["assets_task2"].id,
            "tasks": {
                data["ext2_look_dev"].id: {
                    "Main": {"versions": [data["ext2_look_dev_main_v003"]]},
                },
            },
        }
    }

    assert data["assets_task2"].children == []

    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    # inject alternative
    amt.version_lut[data["ext2_model_main_v003"]] = data["random_asset1_model_main_version1"]
    amt.migrate()

    # we now should have a new asset under the Assets Task2
    assert data["assets_task2"].children != []
    new_asset = data["assets_task2"].children[0]
    assert isinstance(new_asset, Asset)
    assert new_asset.name == data["ext2"].name
    assert new_asset.code == data["ext2"].code
    assert new_asset.type == data["ext2"].type
    assert len(new_asset.children) == 1  # only look dev is moved

    # Model (There should be no model task as it is not moved)
    model_task = (
        Task.query.filter(Task.parent == new_asset).filter(Task.name == "Model").first()
    )
    assert model_task is None
    # Layout (There should be no layout task as it is not moved)
    layout_task = (
        Task.query.filter(Task.parent == new_asset).filter(Task.name == "Layout").first()
    )
    assert layout_task is None

    # LookDev Task
    look_dev_task = (
        Task.query.filter(Task.parent == new_asset)
        .filter(Task.name == "LookDev")
        .first()
    )
    assert look_dev_task.name == "LookDev"
    assert len(look_dev_task.versions) == 1
    look_dev_version = look_dev_task.versions[0]
    assert look_dev_version.take_name == "Main"
    assert len(look_dev_version.inputs) == 1
    assert data["random_asset1_model_main_version1"] in look_dev_version.inputs  # baam!


def test_migration_recipe_to_same_take_name(
    migration_test_data, create_pymel, create_maya_env
):
    """Test recipe has two different takes that moves versions to the same take name."""
    # Asset
    #   Model
    #     Main  -> Main
    #     Take1 -> Main
    # Check Stalker data
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_asset_method_with_None(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_asset(None)."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_asset_method_with_non_asset(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_asset() with asset argument something other than an
    Asset instance."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_asset_metho_with_a_proper_asset(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_asset() with a proper Asset instance."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_set_target_parent_asset_is_None(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.set_target_parent() with asset is None."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_set_target_parent_asset_is_not_a_asset_instance(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.set_target_parent() with asset is not an Asset
    instance."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_set_target_parent_asset_is_a_proper_asset_instance(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.set_target_parent() with the asset argument being a
    proper Asset instance."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_set_target_parent_new_parent_is_None(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.set_target_parent() with the new_parent argument is
    None."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_set_target_parent_new_parent_is_not_a_task_or_project(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.set_target_parent() with the new_parent argument is not
    a Task or Project instance."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_set_target_parent_new_parent_is_a_task(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.set_target_parent() with the new_parent argument value
    being a Task instance."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_set_target_parent_new_parent_is_a_project(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.set_target_parent() with the new_parent argument value
    being a Project instance."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_set_target_parent_new_parent_is_in_the_same_project(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.set_target_parent() is in the same project."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_set_target_parent_new_parent_is_a_child_of_original_asset(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.set_target_parent() is a child task of the given Asset."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_take_task_is_None(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_take() task is None."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_take_task_is_not_task_instance(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_take() task is not a Task instance."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_take_task_is_proper_task_instance(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_take() task is a proper Task instance."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_take_task_is_not_a_child_of_existing_assets(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_take() task is not a child of existing assets."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_take_old_take_name_is_None(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_take() old_take_name is None."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_take_old_take_name_is_not_a_str(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_take() old_take_name is not a string."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_take_old_take_name_does_not_exist(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_take() old_take_name doesn't exist."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_take_new_take_name_is_None(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_take() new_take_name is None."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_take_new_take_name_is_not_a_str(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_take() new_take_name is not a str."""
    raise NotImplementedError("Test is not implemented yet")


def test_asset_migration_tool_add_take_new_take_name_is_a_str(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool.add_take() new_take_name is a str."""
    raise NotImplementedError("Test is not implemented yet")


def test_move_old_versions_1(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool to move a scene with newer versions detected."""
    raise NotImplementedError("Test is not implemented yet")
