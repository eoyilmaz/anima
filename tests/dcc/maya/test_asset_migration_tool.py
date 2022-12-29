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
        parent=data["assets_task3"],
    )
    DBSession.add(data["random_asset1"])

    data["random_asset1_model"] = Task(
        name="Model", type=data["model_type"], parent=data["random_asset1"]
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


def test_get_intermediate_tasks(migration_test_data):
    """Test get_intermediate_tasks() function."""
    data = migration_test_data
    from anima.ui.dialogs import asset_migration_tool_dialog
    result = asset_migration_tool_dialog.get_intermediate_tasks(
        data["environments"], data["building1_yapi_look_dev"]
    )
    expected = [
        data["exteriors"],
        data["ext1"],
        data["building1"],
        data["building1_props"],
        data["building1_yapi"],
        data["building1_yapi_look_dev"]
    ]
    assert result == expected


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
        },
        data["asset2_model"].id: {
            "new_parent_id": data["asset2"].id,
            "takes": {
                "Main": {
                    "new_take_name": "Main",
                    "versions": [data["asset2_model_main_v003"]],
                }
            },
        },
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
        },
        data["asset2_model"].id: {
            "new_parent_id": data["asset2"].id,
            "takes": {
                "Main": {
                    "new_take_name": "Main",
                    "versions": [data["asset2_model_main_v003"]],
                }
            },
        },
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
        },
        data["asset2_model"].id: {
            "new_parent_id": data["asset2"].id,
            "takes": {
                "Main": {
                    "new_take_name": "Main",
                    "versions": [data["asset2_model_main_v003"]],
                },
                "Take1": {
                    "new_take_name": "Take1",
                    "versions": [data["asset2_model_take1_v003"]],
                },
            },
        },
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
        },
        data["asset2_model"].id: {
            "new_parent_id": data["asset2"].id,
            "takes": {
                "Main": {
                    "new_take_name": "Main",
                    "versions": [data["asset2_model_main_v003"]],
                },
                "Take1": {
                    "new_take_name": "Take1",
                    "versions": [data["asset2_model_take1_v003"]],
                },
            },
        },
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
        },
        data["ext2_layout"].id: {  # tricky part, this needs to be moved after look dev
            "new_parent_id": data["ext2"].id,
            "takes": {
                "Main": {"versions": [data["ext2_layout_main_v003"]]},
            },
        },
        data["ext2_look_dev"].id: {
            "new_parent_id": data["ext2"].id,
            "takes": {
                "Main": {"versions": [data["ext2_look_dev_main_v003"]]},
            },
        },
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
        },
        data["ext2_layout"].id: {  # tricky part, this needs to be moved after look dev
            "new_parent_id": data["ext2"].id,
            "takes": {
                "Main": {"versions": [data["ext2_layout_main_v003"]]},
            },
        },
        data["ext2_look_dev"].id: {
            "new_parent_id": data["ext2"].id,
            "takes": {
                "Main": {"versions": [data["ext2_look_dev_main_v003"]]},
            },
        },
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
    # +- Ext1 (Asset - Exterior)
    #    +- Building1 (Asset - Building)
    #    |  +- Layout (Task - Layout)
    #    |  |  +- building1_layout_main_v003
    #    |  +- LookDev (Task - Look Development)
    #    |  |  +- building1_look_dev_main_v003
    #    |  +- Props (Task)
    #    |     +- building1_yapi (Asset)
    #    |        +- Model (Task - Model)
    #    |        |  +- building1_yapi_model_main_v003
    #    |        +- LookDev (Task - Look Development)
    #    |           +- building1_yapi_look_dev_main_v003
    #    +- Building2 (Asset - Building)
    #    |  +- Layout (Task - Layout)
    #    |  |  +- building2_layout_main_v003
    #    |  +- LookDev (Task - Look Development)
    #    |  |  +- building2_look_dev_main_v003
    #    |  +- Props (Task)
    #    |     +- building2_yapi (Asset)
    #    |        +- Model (Task - Model)
    #    |        |  +- building2_yapi_model_main_v003
    #    |        +- LookDev (Task - Look Development)
    #    |           +- building2_yapi_look_dev_main_v003
    #    +- Layout (Task - Layout)
    #    |  +- ext1_layout_main_v003
    #    +- LookDev (Task - Look Development)
    #    |  +- ext1_look_dev_main_v003
    #    +- Props (Task)
    #    |  +- Prop1 (Asset)
    #    |     +- Model (Task - Model)
    #    |     |  +- **Main** (Take)
    #    |     |  |  +- prop1_model_main_v003
    #    |     |  +- **Kisa** (Take)
    #    |     |     +- prop1_model_kisa_v003
    #    |     +- LookDev (Task - Look Development)
    #    |        +- **Main** (Take)
    #    |        |  +- prop1_look_dev_main_v003
    #    |        +- **Kisa** (Take)
    #    |           +- prop1_look_dev_kisa_v003
    #    +- Vegetation (Task - Vegetation)
    #       +- ext1_vegetation_main_v003
    # Check Stalker data
    data = migration_test_data
    pm = create_pymel
    maya_env = create_maya_env
    migration_recipe = {
        data["ext1"].id: {
            "new_parent_id": data["assets_task2"].id,
        },
        data["ext1_layout"].id: {
            "takes": {
                # tricky part, this needs to be moved after look dev
                "Main": {"versions": [data["ext1_layout_main_v003"]]},
            },
        },
        data["ext1_look_dev"].id: {
            "takes": {
                "Main": {"versions": [data["ext1_look_dev_main_v003"]]},
            },
        },
        data["building1"].id: {},
        data["building1_layout"].id: {
            "takes": {
                "Main": {"versions": [data["building1_layout_main_v003"]]},
            },
        },
        data["building1_look_dev"].id: {
            "takes": {
                "Main": {"versions": [data["building1_look_dev_main_v003"]]},
            },
        },
        data["building1_props"].id: {},
        data["building1_yapi"].id: {},
        data["building1_yapi_model"].id: {
            "takes": {"Main": {"versions": [data["building1_yapi_model_main_v003"]]}}
        },
        data["building1_yapi_look_dev"].id: {
            "takes": {"Main": {"versions": [data["building1_yapi_look_dev_main_v003"]]}}
        },
        data["building2"].id: {},
        data["building2_layout"].id: {
            "takes": {
                "Main": {"versions": [data["building2_layout_main_v003"]]},
            },
        },
        data["building2_look_dev"].id: {
            "takes": {
                "Main": {"versions": [data["building2_look_dev_main_v003"]]},
            },
        },
        data["building2_props"].id: {},
        data["building2_yapi"].id: {},
        data["building2_yapi_model"].id: {
            "takes": {"Main": {"versions": [data["building2_yapi_model_main_v003"]]}}
        },
        data["building2_yapi_look_dev"].id: {
            "takes": {"Main": {"versions": [data["building2_yapi_look_dev_main_v003"]]}}
        },
        data["ext1_props"].id: {},
        data["prop1"].id: {},
        data["prop1_model"].id: {
            "takes": {
                "Main": {"versions": [data["prop1_model_main_v003"]]},
                "Kisa": {"versions": [data["prop1_model_kisa_v003"]]},
            }
        },
        data["prop1_look_dev"].id: {
            "takes": {
                "Main": {"versions": [data["prop1_look_dev_main_v003"]]},
                "Kisa": {"versions": [data["prop1_look_dev_kisa_v003"]]},
            }
        },
        data["ext1_vegetation"].id: {
            "takes": {"Main": {"versions": [data["ext1_vegetation_main_v003"]]}}
        },
    }

    assert data["assets_task2"].children == []
    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    amt.migrate()

    assert data["assets_task2"].children != []
    assert len(data["assets_task2"].children) == 1
    ext1 = data["assets_task2"].children[0]
    assert isinstance(ext1, Asset)
    assert ext1.name == data["ext1"].name
    assert ext1.code == data["ext1"].code
    assert ext1.type == data["exterior_type"]
    assert len(ext1.children) == 6

    # Building1
    building1 = (
        Asset.query.filter(Asset.parent == ext1)
        .filter(Asset.name == data["building1"].name)
        .first()
    )
    assert building1 is not None
    assert isinstance(building1, Asset)
    assert building1.name == data["building1"].name
    assert building1.code == data["building1"].code
    assert building1.type == data["building_type"]
    assert len(building1.children) == 3

    # Building1 Layout
    building1_layout = (
        Task.query.filter(Task.parent == building1)
        .filter(Task.name == data["building1_layout"].name)
        .first()
    )
    assert building1_layout is not None
    assert isinstance(building1_layout, Task)
    assert building1_layout.name == data["building1_layout"].name
    assert building1_layout.type == data["layout_type"]
    assert len(building1_layout.versions) == 1
    v1 = building1_layout.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1

    # Building1 LookDev
    building1_look_dev = (
        Task.query.filter(Task.parent == building1)
        .filter(Task.name == data["building1_look_dev"].name)
        .first()
    )
    assert building1_look_dev is not None
    assert isinstance(building1_look_dev, Task)
    assert building1_look_dev.name == data["building1_look_dev"].name
    assert building1_look_dev.type == data["look_development_type"]
    assert len(building1_look_dev.versions) == 1
    v1 = building1_look_dev.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1

    # Building1 Props
    building1_props = (
        Task.query.filter(Task.parent == building1)
        .filter(Task.name == data["building1_props"].name)
        .first()
    )
    assert building1_props is not None
    assert isinstance(building1_props, Task)
    assert building1_props.name == data["building1_props"].name
    assert building1_props.type is None
    assert len(building1_props.children) == 1
    assert len(building1_props.versions) == 0

    # Building1 Yapi
    building1_yapi = building1_props.children[0]
    assert isinstance(building1_yapi, Asset)
    assert building1_yapi.name == data["building1_yapi"].name
    assert building1_yapi.name == data["building1_yapi"].code
    assert building1_yapi.type == data["building_type"]
    assert len(building1_yapi.versions) == 0
    assert len(building1.children) == 3

    # Building1 Yapi Model
    building1_yapi_model = (
        Task.query.filter(Task.parent == building1_yapi)
        .filter(Task.name == data["building1_yapi_model"].name)
        .first()
    )
    assert building1_yapi_model is not None
    assert isinstance(building1_yapi_model, Task)
    assert building1_yapi_model.name == data["building1_yapi_model"].name
    assert building1_yapi_model.type == data["model_type"]
    assert len(building1_yapi_model.children) == 0
    assert len(building1_yapi_model.versions) == 1
    v1 = building1_yapi_model.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1

    # Building1 Yapi LookDev
    building1_yapi_look_dev = (
        Task.query.filter(Task.parent == building1_yapi)
        .filter(Task.name == data["building1_yapi_look_dev"].name)
        .first()
    )
    assert building1_yapi_look_dev is not None
    assert isinstance(building1_yapi_look_dev, Task)
    assert building1_yapi_look_dev.name == data["building1_yapi_look_dev"].name
    assert building1_yapi_look_dev.type == data["look_development_type"]
    assert len(building1_yapi_look_dev.children) == 0
    assert len(building1_yapi_look_dev.versions) == 1
    v1 = building1_yapi_look_dev.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1

    # Building2
    building2 = (
        Asset.query.filter(Asset.parent == ext1)
        .filter(Asset.name == data["building2"].name)
        .first()
    )
    assert building2 is not None
    assert isinstance(building2, Asset)
    assert building2.name == data["building2"].name
    assert building2.code == data["building2"].code
    assert building2.type == data["building_type"]
    assert len(building2.children) == 3

    # Building2 Layout
    building2_layout = (
        Task.query.filter(Task.parent == building2)
        .filter(Task.name == data["building2_layout"].name)
        .first()
    )
    assert building2_layout is not None
    assert isinstance(building2_layout, Task)
    assert building2_layout.name == data["building2_layout"].name
    assert building2_layout.type == data["layout_type"]
    assert len(building2_layout.versions) == 1
    v1 = building2_layout.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1

    # Building2 LookDev
    building2_look_dev = (
        Task.query.filter(Task.parent == building2)
        .filter(Task.name == data["building2_look_dev"].name)
        .first()
    )
    assert building2_look_dev is not None
    assert isinstance(building2_look_dev, Task)
    assert building2_look_dev.name == data["building2_look_dev"].name
    assert building2_look_dev.type == data["look_development_type"]
    assert len(building2_look_dev.versions) == 1
    v1 = building2_look_dev.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1

    # Building2 Props
    building2_props = (
        Task.query.filter(Task.parent == building2)
        .filter(Task.name == data["building2_props"].name)
        .first()
    )
    assert building2_props is not None
    assert isinstance(building2_props, Task)
    assert building2_props.name == data["building2_props"].name
    assert building2_props.type is None
    assert len(building2_props.versions) == 0
    assert len(building2_props.children) == 1

    # Building2 Yapi
    building2_yapi = building2_props.children[0]
    assert isinstance(building2_yapi, Asset)
    assert building2_yapi.name == data["building2_yapi"].name
    assert building2_yapi.name == data["building2_yapi"].code
    assert building2_yapi.type == data["building_type"]
    assert len(building2_yapi.versions) == 0
    assert len(building2.children) == 3

    # Building2 Yapi Model
    building2_yapi_model = (
        Task.query.filter(Task.parent == building2_yapi)
        .filter(Task.name == data["building2_yapi_model"].name)
        .first()
    )
    assert building2_yapi_model is not None
    assert isinstance(building2_yapi_model, Task)
    assert building2_yapi_model.name == data["building2_yapi_model"].name
    assert building2_yapi_model.type == data["model_type"]
    assert len(building2_yapi_model.children) == 0
    assert len(building2_yapi_model.versions) == 1
    v1 = building2_yapi_model.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1

    # Building2 Yapi LookDev
    building2_yapi_look_dev = (
        Task.query.filter(Task.parent == building2_yapi)
        .filter(Task.name == data["building2_yapi_look_dev"].name)
        .first()
    )
    assert building2_yapi_look_dev is not None
    assert isinstance(building2_yapi_look_dev, Task)
    assert building2_yapi_look_dev.name == data["building2_yapi_look_dev"].name
    assert building2_yapi_look_dev.type == data["look_development_type"]
    assert len(building2_yapi_look_dev.children) == 0
    assert len(building2_yapi_look_dev.versions) == 1
    v1 = building2_yapi_look_dev.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1

    # Ext1 Layout
    ext1_layout = (
        Task.query.filter(Task.parent == ext1)
        .filter(Task.name == data["ext1_layout"].name)
        .first()
    )
    assert ext1_layout is not None
    assert isinstance(ext1_layout, Task)
    assert ext1_layout.name == data["ext1_layout"].name
    assert ext1_layout.type == data["layout_type"]
    assert len(ext1_layout.children) == 0
    assert len(ext1_layout.versions) == 1
    v1 = ext1_layout.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1

    # Ext1 Look_dev
    ext1_look_dev = (
        Task.query.filter(Task.parent == ext1)
        .filter(Task.name == data["ext1_look_dev"].name)
        .first()
    )
    assert ext1_look_dev is not None
    assert isinstance(ext1_look_dev, Task)
    assert ext1_look_dev.name == data["ext1_look_dev"].name
    assert ext1_look_dev.type == data["look_development_type"]
    assert len(ext1_look_dev.children) == 0
    assert len(ext1_look_dev.versions) == 1
    v1 = ext1_look_dev.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1

    # Ext1 Props
    ext1_props = (
        Task.query.filter(Task.parent == ext1)
        .filter(Task.name == data["ext1_props"].name)
        .first()
    )
    assert ext1_props is not None
    assert isinstance(ext1_props, Task)
    assert ext1_props.name == data["ext1_props"].name
    assert len(ext1_props.children) == 1
    assert len(ext1_props.versions) == 0

    # Ext1 Props Prop1
    prop1 = ext1_props.children[0]
    assert prop1 is not None
    assert isinstance(prop1, Asset)
    assert prop1.name == data["prop1"].name
    assert prop1.code == data["prop1"].code
    assert prop1.type == data["prop_type"]
    assert len(prop1.children) == 2
    assert len(prop1.versions) == 0

    # Ext1 Props Prop1 Model
    prop1_model = (
        Task.query.filter(Task.parent == prop1)
        .filter(Task.name == data["prop1_model"].name)
        .first()
    )
    assert prop1_model is not None
    assert isinstance(prop1_model, Task)
    assert prop1_model.name == data["prop1_model"].name
    assert prop1_model.type == data["model_type"]
    assert len(prop1_model.children) == 0
    assert len(prop1_model.versions) == 2
    v1 = prop1_model.versions[0]
    v2 = prop1_model.versions[1]
    assert v1.take_name in ["Main", "Kisa"]
    assert v2.take_name in ["Main", "Kisa"]

    # Ext1 Props Prop1 Look_dev
    prop1_look_dev = (
        Task.query.filter(Task.parent == prop1)
        .filter(Task.name == data["prop1_look_dev"].name)
        .first()
    )
    assert prop1_look_dev is not None
    assert isinstance(prop1_look_dev, Task)
    assert prop1_look_dev.name == data["prop1_look_dev"].name
    assert prop1_look_dev.type == data["look_development_type"]
    assert len(prop1_look_dev.children) == 0
    assert len(prop1_look_dev.versions) == 2
    v1 = prop1_look_dev.versions[0]
    v2 = prop1_look_dev.versions[1]
    assert v1.take_name in ["Main", "Kisa"]
    assert v2.take_name in ["Main", "Kisa"]

    # Ext1 Vegetation
    ext1_vegetation = (
        Task.query.filter(Task.parent == ext1)
        .filter(Task.name == data["ext1_vegetation"].name)
        .first()
    )
    assert ext1_vegetation is not None
    assert isinstance(ext1_vegetation, Task)
    assert ext1_vegetation.name == data["ext1_vegetation"].name
    assert ext1_vegetation.type == data["vegetation_type"]
    assert len(ext1_vegetation.children) == 0
    assert len(ext1_vegetation.versions) == 1
    v1 = ext1_vegetation.versions[0]
    assert v1.take_name == "Main"
    assert v1.version_number == 1


def test_migrating_complex_env_asset_2(
    migration_test_data, create_pymel, create_maya_env
):
    """Test AssetMigrationTool with a complex environment asset. File content."""
    # +- Ext1 (Asset - Exterior)
    #    +- Building1 (Asset - Building)
    #    |  +- Layout (Task - Layout)
    #    |  |  +- building1_layout_main_v003
    #    |  +- LookDev (Task - Look Development)
    #    |  |  +- building1_look_dev_main_v003
    #    |  +- Props (Task)
    #    |     +- building1_yapi (Asset)
    #    |        +- Model (Task - Model)
    #    |        |  +- building1_yapi_model_main_v003
    #    |        +- LookDev (Task - Look Development)
    #    |           +- building1_yapi_look_dev_main_v003
    #    +- Building2 (Asset - Building)
    #    |  +- Layout (Task - Layout)
    #    |  |  +- building2_layout_main_v003
    #    |  +- LookDev (Task - Look Development)
    #    |  |  +- building2_look_dev_main_v003
    #    |  +- Props (Task)
    #    |     +- building2_yapi (Asset)
    #    |        +- Model (Task - Model)
    #    |        |  +- building2_yapi_model_main_v003
    #    |        +- LookDev (Task - Look Development)
    #    |           +- building2_yapi_look_dev_main_v003
    #    +- Layout (Task - Layout)
    #    |  +- ext1_layout_main_v003
    #    +- LookDev (Task - Look Development)
    #    |  +- ext1_look_dev_main_v003
    #    +- Props (Task)
    #    |  +- Prop1 (Asset)
    #    |     +- Model (Task - Model)
    #    |     |  +- **Main** (Take)
    #    |     |  |  +- prop1_model_main_v003
    #    |     |  +- **Kisa** (Take)
    #    |     |     +- prop1_model_kisa_v003
    #    |     +- LookDev (Task - Look Development)
    #    |        +- **Main** (Take)
    #    |        |  +- prop1_look_dev_main_v003
    #    |        +- **Kisa** (Take)
    #    |           +- prop1_look_dev_kisa_v003
    #    +- Vegetation (Task - Vegetation)
    #       +- ext1_vegetation_main_v003
    # Check Stalker data
    data = migration_test_data
    pm = create_pymel
    maya_env = create_maya_env
    migration_recipe = {
        data["ext1"].id: {
            "new_parent_id": data["assets_task2"].id,
        },
        data["ext1_layout"].id: {
            "takes": {
                # tricky part, this needs to be moved after look dev
                "Main": {"versions": [data["ext1_layout_main_v003"]]},
            },
        },
        data["ext1_look_dev"].id: {
            "takes": {
                "Main": {"versions": [data["ext1_look_dev_main_v003"]]},
            },
        },
        data["building1"].id: {},
        data["building1_layout"].id: {
            "takes": {
                "Main": {"versions": [data["building1_layout_main_v003"]]},
            },
        },
        data["building1_look_dev"].id: {
            "takes": {
                "Main": {"versions": [data["building1_look_dev_main_v003"]]},
            },
        },
        data["building1_props"].id: {},
        data["building1_yapi"].id: {},
        data["building1_yapi_model"].id: {
            "takes": {"Main": {"versions": [data["building1_yapi_model_main_v003"]]}}
        },
        data["building1_yapi_look_dev"].id: {
            "takes": {"Main": {"versions": [data["building1_yapi_look_dev_main_v003"]]}}
        },
        data["building2"].id: {},
        data["building2_layout"].id: {
            "takes": {
                "Main": {"versions": [data["building2_layout_main_v003"]]},
            },
        },
        data["building2_look_dev"].id: {
            "takes": {
                "Main": {"versions": [data["building2_look_dev_main_v003"]]},
            },
        },
        data["building2_props"].id: {},
        data["building2_yapi"].id: {},
        data["building2_yapi_model"].id: {
            "takes": {"Main": {"versions": [data["building2_yapi_model_main_v003"]]}}
        },
        data["building2_yapi_look_dev"].id: {
            "takes": {"Main": {"versions": [data["building2_yapi_look_dev_main_v003"]]}}
        },
        data["ext1_props"].id: {},
        data["prop1"].id: {},
        data["prop1_model"].id: {
            "takes": {
                "Main": {"versions": [data["prop1_model_main_v003"]]},
                "Kisa": {"versions": [data["prop1_model_kisa_v003"]]},
            }
        },
        data["prop1_look_dev"].id: {
            "takes": {
                "Main": {"versions": [data["prop1_look_dev_main_v003"]]},
                "Kisa": {"versions": [data["prop1_look_dev_kisa_v003"]]},
            }
        },
        data["ext1_vegetation"].id: {
            "takes": {"Main": {"versions": [data["ext1_vegetation_main_v003"]]}}
        },
    }

    assert data["assets_task2"].children == []
    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    amt.migrate()

    ext1 = data["assets_task2"].children[0]

    # Building1
    building1 = (
        Asset.query.filter(Asset.parent == ext1)
        .filter(Asset.name == data["building1"].name)
        .first()
    )

    # Building1 Layout
    building1_layout = (
        Task.query.filter(Task.parent == building1)
        .filter(Task.name == data["building1_layout"].name)
        .first()
    )
    building1_layout_main_v001 = building1_layout.versions[0]

    # Building1 LookDev
    building1_look_dev = (
        Task.query.filter(Task.parent == building1)
        .filter(Task.name == data["building1_look_dev"].name)
        .first()
    )
    building1_look_dev_main_v001 = building1_look_dev.versions[0]

    # Building1 Props
    building1_props = (
        Task.query.filter(Task.parent == building1)
        .filter(Task.name == data["building1_props"].name)
        .first()
    )

    # Building1 Yapi
    building1_yapi = building1_props.children[0]

    # Building1 Yapi Model
    building1_yapi_model = (
        Task.query.filter(Task.parent == building1_yapi)
        .filter(Task.name == data["building1_yapi_model"].name)
        .first()
    )
    building1_yapi_model_main_v001 = building1_yapi_model.versions[0]

    # Building1 Yapi LookDev
    building1_yapi_look_dev = (
        Task.query.filter(Task.parent == building1_yapi)
        .filter(Task.name == data["building1_yapi_look_dev"].name)
        .first()
    )
    building1_yapi_look_dev_main_v001 = building1_yapi_look_dev.versions[0]

    # Building2
    building2 = (
        Asset.query.filter(Asset.parent == ext1)
        .filter(Asset.name == data["building2"].name)
        .first()
    )

    # Building2 Layout
    building2_layout = (
        Task.query.filter(Task.parent == building2)
        .filter(Task.name == data["building2_layout"].name)
        .first()
    )
    building2_layout_main_v001 = building2_layout.versions[0]

    # Building2 LookDev
    building2_look_dev = (
        Task.query.filter(Task.parent == building2)
        .filter(Task.name == data["building2_look_dev"].name)
        .first()
    )
    building2_look_dev_main_v001 = building2_look_dev.versions[0]

    # Building2 Props
    building2_props = (
        Task.query.filter(Task.parent == building2)
        .filter(Task.name == data["building2_props"].name)
        .first()
    )

    # Building2 Yapi
    building2_yapi = building2_props.children[0]

    # Building2 Yapi Model
    building2_yapi_model = (
        Task.query.filter(Task.parent == building2_yapi)
        .filter(Task.name == data["building2_yapi_model"].name)
        .first()
    )
    building2_yapi_model_main_v001 = building2_yapi_model.versions[0]

    # Building2 Yapi LookDev
    building2_yapi_look_dev = (
        Task.query.filter(Task.parent == building2_yapi)
        .filter(Task.name == data["building2_yapi_look_dev"].name)
        .first()
    )
    building2_yapi_look_dev_main_v001 = building2_yapi_look_dev.versions[0]

    # Ext1 Layout
    ext1_layout = (
        Task.query.filter(Task.parent == ext1)
        .filter(Task.name == data["ext1_layout"].name)
        .first()
    )
    ext1_layout_main_v001 = ext1_layout.versions[0]

    # Ext1 Look_dev
    ext1_look_dev = (
        Task.query.filter(Task.parent == ext1)
        .filter(Task.name == data["ext1_look_dev"].name)
        .first()
    )
    ext1_look_dev_main_v001 = ext1_look_dev.versions[0]

    # Ext1 Props
    ext1_props = (
        Task.query.filter(Task.parent == ext1)
        .filter(Task.name == data["ext1_props"].name)
        .first()
    )

    # Ext1 Props Prop1
    prop1 = ext1_props.children[0]

    # Ext1 Props Prop1 Model
    prop1_model = (
        Task.query.filter(Task.parent == prop1)
        .filter(Task.name == data["prop1_model"].name)
        .first()
    )
    prop1_model_main_v001 = prop1_model.versions[0]
    prop1_model_kisa_v001 = prop1_model.versions[1]
    if prop1_model_main_v001.take_name != "Main":
        prop1_model_main_v001 = prop1_model.versions[1]
        prop1_model_kisa_v001 = prop1_model.versions[0]

    # Ext1 Props Prop1 Look_dev
    prop1_look_dev = (
        Task.query.filter(Task.parent == prop1)
        .filter(Task.name == data["prop1_look_dev"].name)
        .first()
    )
    prop1_look_dev_main_v001 = prop1_look_dev.versions[0]
    prop1_look_dev_kisa_v001 = prop1_look_dev.versions[1]
    if prop1_look_dev_main_v001.take_name != "Main":
        prop1_look_dev_main_v001 = prop1_look_dev.versions[1]
        prop1_look_dev_kisa_v001 = prop1_look_dev.versions[0]

    # Ext1 Vegetation
    ext1_vegetation = (
        Task.query.filter(Task.parent == ext1)
        .filter(Task.name == data["ext1_vegetation"].name)
        .first()
    )
    ext1_vegetation_main_v001 = ext1_vegetation.versions[0]

    # Version Content Check
    # Building1 Layout Main v001
    maya_env.open(
        building1_layout_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == building1_yapi_look_dev_main_v001

    # Building1 LookDev Main v001
    maya_env.open(
        building1_look_dev_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == building1_layout_main_v001

    # Building1 Yapi Model Main v001
    maya_env.open(
        building1_yapi_model_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 0

    # Building1 Yapi LookDev Main v001
    maya_env.open(
        building1_yapi_look_dev_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == building1_yapi_model_main_v001

    # Building2 Layout
    maya_env.open(
        building2_layout_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == building2_yapi_look_dev_main_v001

    # Building2 LookDev
    maya_env.open(
        building2_look_dev_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == building2_layout_main_v001

    # Building2 Yapi Model
    maya_env.open(
        building2_yapi_model_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 0

    # Building2 Yapi LookDev
    maya_env.open(
        building2_yapi_look_dev_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == building2_yapi_model_main_v001

    # Ext1 Layout
    maya_env.open(
        ext1_layout_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 3
    assert refs[0].version in [
        building1_layout_main_v001,
        building2_layout_main_v001,
        ext1_vegetation_main_v001,
    ]
    assert refs[1].version in [
        building1_layout_main_v001,
        building2_layout_main_v001,
        ext1_vegetation_main_v001,
    ]
    assert refs[2].version in [
        building1_layout_main_v001,
        building2_layout_main_v001,
        ext1_vegetation_main_v001,
    ]

    # Ext1 Look_dev
    maya_env.open(
        ext1_look_dev_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == ext1_layout_main_v001

    # Ext1 Props Prop1 Model
    # Main
    maya_env.open(
        prop1_model_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 0

    # Kisa
    maya_env.open(
        prop1_model_kisa_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 0

    # Ext1 Props Prop1 LookDev
    # Main
    maya_env.open(
        prop1_look_dev_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == prop1_model_main_v001

    # Kisa
    maya_env.open(
        prop1_look_dev_kisa_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 1
    assert refs[0].version == prop1_model_kisa_v001

    # Vegetation
    maya_env.open(
        ext1_vegetation_main_v001,
        force=True,
        skip_update_check=True,
        prompt=False,
        clean_malware=False,
    )
    refs = pm.listReferences()
    assert len(refs) == 0


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
        },
        data["ext2_look_dev"].id: {
            "new_parent_id": data["ext2"].id,
            "takes": {
                "Main": {"versions": [data["ext2_look_dev_main_v003"]]},
            },
        },
    }

    assert data["assets_task2"].children == []

    from anima.dcc.mayaEnv.asset_migration_tool import AssetMigrationTool

    amt = AssetMigrationTool()
    amt.migration_recipe = migration_recipe
    # inject alternative
    amt.version_lut[data["ext2_model_main_v003"]] = data[
        "random_asset1_model_main_version1"
    ]
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
        Task.query.filter(Task.parent == new_asset)
        .filter(Task.name == "Layout")
        .first()
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


def test_move_old_versions_1(migration_test_data, create_pymel, create_maya_env):
    """Test AssetMigrationTool to move a scene with newer versions detected."""
    raise NotImplementedError("Test is not implemented yet")
