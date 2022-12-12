# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
import pytest

from stalker import (
    db,
    User,
    Repository,
    Status,
    FilenameTemplate,
    Structure,
    StatusList,
    ImageFormat,
    Project,
    Type,
    Task,
    Asset,
    Sequence,
    Shot,
)
from stalker.db.session import DBSession


import logging

from tests.dcc.maya.utils import create_version

logger = logging.getLogger("anima.dcc.mayaEnv")
logger.setLevel(logging.WARNING)


@pytest.fixture(scope="module")
def create_pymel():
    """Quit maya after the test"""
    os.environ["ANIMA_TEST_SETUP"] = ""
    import pymel.core as pm

    yield pm
    # quit maya
    # pm.runtime.Quit()


@pytest.fixture(scope="function")
def create_maya_env():
    """Create a proper maya env."""
    # create the environment instance
    from anima.dcc.mayaEnv import Maya

    maya_env = Maya()
    maya_env.use_progress_window = False
    yield maya_env


@pytest.fixture(scope="function")
def create_maya_test_db():
    """create test database for maya"""
    # -----------------------------------------------------------------
    # start of the setUp
    # create the environment variable and point it to a temp directory
    import anima

    anima.stalker_server_internal_address = "internal"
    anima.stalker_server_external_address = "external"

    logger.debug("initializing db")
    db.setup({"sqlalchemy.url": "sqlite:///:memory:"})
    db.init()
    logger.debug("initializing db complete")

    logger.debug("creating temp repository path")
    temp_repo_path = tempfile.mkdtemp()

    yield temp_repo_path

    # cleanup the test
    # set the db.session to None
    DBSession.remove()

    # delete the temp folder
    shutil.rmtree(temp_repo_path, ignore_errors=True)


@pytest.fixture(scope="function")
def trash_bin():
    """Create a trash bin to throw files in to be deleted after test."""
    # create a buffer for extra created files, which are to be removed
    remove_these_files_buffer = []

    yield remove_these_files_buffer

    for f in remove_these_files_buffer:
        if os.path.isfile(f):
            os.remove(f)
        elif os.path.isdir(f):
            shutil.rmtree(f, True)


@pytest.fixture(scope="function")
def create_test_data(create_maya_test_db, create_pymel, create_maya_env):
    """create test data."""
    logger.debug("creating user1")
    data = dict()
    data["temp_repo_path"] = create_maya_test_db
    pm = create_pymel
    maya_env = create_maya_env
    from anima.dcc.mayaEnv import auxiliary

    data["user1"] = User(
        name="User 1", login="user1", email="user1@users.com", password="12345"
    )

    logger.debug("creating repo1")
    data["repo1"] = Repository(
        name="Test Project Repository",
        code="TPR",
        linux_path=data["temp_repo_path"],
        windows_path=data["temp_repo_path"],
        osx_path=data["temp_repo_path"],
    )
    logger.debug("committing repo1")
    DBSession.add(data["repo1"])
    DBSession.commit()
    logger.debug("commit repo1 done!")

    logger.debug("creating statuses")
    data["status_new"] = Status.query.filter_by(code="NEW").first()
    data["status_wip"] = Status.query.filter_by(code="WIP").first()
    data["status_comp"] = Status.query.filter_by(code="CMPL").first()
    logger.debug("creating statuses done")

    logger.debug("creating filename template")
    data["task_template"] = FilenameTemplate(
        name="Task Template",
        target_entity_type="Task",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}"
        "{{parent_task.nice_name}}/"
        "{%- endfor -%}",
        filename="{{version.nice_name}}" '_v{{"%03d"|format(version.version_number)}}',
    )
    logger.debug("creating filename template done")

    logger.debug("creating asset template")
    data["asset_template"] = FilenameTemplate(
        name="Asset Template",
        target_entity_type="Asset",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}"
        "{{parent_task.nice_name}}/"
        "{%- endfor -%}",
        filename="{{version.nice_name}}" '_v{{"%03d"|format(version.version_number)}}',
    )
    logger.debug("creating asset template done")

    logger.debug("creating shot template")
    data["shot_template"] = FilenameTemplate(
        name="Shot Template",
        target_entity_type="Shot",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}"
        "{{parent_task.nice_name}}/"
        "{%- endfor -%}",
        filename="{{version.nice_name}}" '_v{{"%03d"|format(version.version_number)}}',
    )
    logger.debug("creating shot template done")

    data["sequence_template"] = FilenameTemplate(
        name="Sequence Template",
        target_entity_type="Sequence",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}"
        "{{parent_task.nice_name}}/"
        "{%- endfor -%}",
        filename="{{version.nice_name}}" '_v{{"%03d"|format(version.version_number)}}',
    )

    data["structure"] = Structure(
        name="Project Struture",
        templates=[
            data["task_template"],
            data["asset_template"],
            data["shot_template"],
            data["sequence_template"],
        ],
    )

    data["project_status_list"] = StatusList.query.filter_by(
        target_entity_type="Project"
    ).first()

    data["image_format"] = ImageFormat(
        name="HD 1080", width=1920, height=1080, pixel_aspect=1.0
    )

    # create a test project
    data["project"] = Project(
        name="Test Project",
        code="TP",
        repositories=[data["repo1"]],
        status_list=data["project_status_list"],
        structure=data["structure"],
        image_format=data["image_format"],
    )
    DBSession.add(data["project"])
    DBSession.commit()

    data["task_status_list"] = StatusList.query.filter_by(
        target_entity_type="Task"
    ).first()
    data["asset_status_list"] = StatusList.query.filter_by(
        target_entity_type="Asset"
    ).first()
    data["shot_status_list"] = StatusList.query.filter_by(
        target_entity_type="Shot"
    ).first()
    data["sequence_status_list"] = StatusList.query.filter_by(
        target_entity_type="Sequence"
    ).first()

    data["character_type"] = Type(
        name="Character", code="CHAR", target_entity_type="Asset"
    )

    # Types
    data["character_design_type"] = Type(
        name="Character Design", code="chardesign", target_entity_type="Task"
    )

    data["anim_type"] = Type(name="Animation", code="anim", target_entity_type="Task")

    data["model_type"] = Type(name="Model", code="model", target_entity_type="Task")

    data["look_development_type"] = Type(
        name="Look Development", code="lookdev", target_entity_type="Task"
    )

    data["rig_type"] = Type(name="Rig", code="rig", target_entity_type="Task")

    data["exterior_type"] = Type(
        name="Exterior", code="rig", target_entity_type="Asset"
    )

    data["building_type"] = Type(
        name="Building", code="building", target_entity_type="Asset"
    )

    data["layout_type"] = Type(name="Layout", code="layout", target_entity_type="Task")

    data["prop_type"] = Type(name="Prop", code="prop", target_entity_type="Asset")

    data["vegetation_type"] = Type(
        name="Vegetation", code="vegetation", target_entity_type="Task"
    )

    # create a test series of root task
    data["task1"] = Task(name="Test Task 1", project=data["project"])
    data["task2"] = Task(name="Test Task 2", project=data["project"])
    data["task3"] = Task(name="Test Task 3", project=data["project"])

    # then a couple of child tasks
    data["task4"] = Task(name="Test Task 4", parent=data["task1"])
    data["task5"] = Task(
        name="Test Task 5",
        parent=data["task1"],
    )
    data["task6"] = Task(
        name="Test Task 6",
        parent=data["task1"],
    )

    # create a root asset
    data["asset1"] = Asset(
        name="Asset 1",
        code="asset1",
        type=data["character_type"],
        project=data["project"],
    )
    data["asset1_model"] = Task(
        name="Model", type=data["model_type"], parent=data["asset1"]
    )
    data["asset1_lookdev"] = Task(
        name="LookDev", type=data["look_development_type"], parent=data["asset1"]
    )

    # create a child asset
    data["asset2"] = Asset(
        name="Asset 2", code="asset2", type=data["character_type"], parent=data["task4"]
    )
    data["asset2_model"] = Task(
        name="Model", type=data["model_type"], parent=data["asset2"]
    )
    data["asset2_lookdev"] = Task(
        name="LookDev", type=data["look_development_type"], parent=data["asset2"]
    )

    # create a root Sequence
    data["sequence1"] = Sequence(name="Sequence1", code="SEQ1", project=data["project"])

    # create a child Sequence
    data["sequence2"] = Sequence(name="Sequence2", code="SEQ2", parent=data["task2"])

    # create a root Shot
    data["shot1"] = Shot(code="SH001", project=data["project"])

    # create a child Shot (child of a Sequence)
    data["shot2"] = Shot(code="SH002", parent=data["sequence1"])

    # create a child Shot (child of a child Sequence)
    data["shot3"] = Shot(code="SH003", parent=data["sequence2"])

    data["shot3_anim"] = Task(name="Anim", type=data["anim_type"], parent=data["shot3"])

    # ******************************************************************
    #
    # Lets create some real data
    #
    # ******************************************************************

    # Tasks
    data["assets"] = Task(name="Assets", project=data["project"])

    data["characters"] = Task(name="Characters", parent=data["assets"])

    data["char1"] = Asset(
        name="Char1",
        code="Char1",
        type=data["character_type"],
        parent=data["characters"],
    )

    data["character_design"] = Task(
        name="Character Design",
        type=data["character_design_type"],
        parent=data["char1"],
    )

    data["char1_model"] = Task(
        name="Model",
        parent=data["char1"],
        type=data["model_type"],
        depends=[data["character_design"]],
    )

    data["char1_look_dev"] = Task(
        name="Look Dev",  # this is named Look Dev instead of LookDev on
        parent=data["char1"],  # purpose
        type=data["look_development_type"],
        depends=[data["char1_model"]],
    )

    data["char1_rig"] = Task(
        name="Rig",  # this is named Look Dev instead of LookDev on
        parent=data["char1"],  # purpose
        type=data["rig_type"],
        depends=[data["char1_model"]],
    )

    data["environments"] = Task(name="Environments", parent=data["assets"])

    data["exteriors"] = Task(name="Exteriors", parent=data["environments"])

    data["ext1"] = Asset(
        name="Ext1", code="Ext1", type=data["exterior_type"], parent=data["exteriors"]
    )

    # Building 1
    data["building1"] = Asset(
        name="Building1",
        code="Building1",
        type=data["building_type"],
        parent=data["ext1"],
    )

    data["building1_layout"] = Task(
        name="Layout", type=data["layout_type"], parent=data["building1"]
    )

    data["building1_layout_proxy"] = Task(
        name="Proxy", type=data["layout_type"], parent=data["building1_layout"]
    )

    data["building1_layout_hires"] = Task(
        name="Hires",
        type=data["layout_type"],
        parent=data["building1_layout"],
        depends=[data["building1_layout_proxy"]],
    )

    data["building1_look_dev"] = Task(
        name="LookDev", type=data["look_development_type"], parent=data["building1"]
    )

    data["building1_props"] = Task(name="Props", parent=data["building1"])

    data["building1_yapi"] = Task(name="YAPI", parent=data["building1_props"])

    data["building1_yapi_model"] = Task(
        name="Model", type=data["model_type"], parent=data["building1_yapi"]
    )

    data["building1_yapi_model_proxy"] = Task(
        name="Proxy", type=data["model_type"], parent=data["building1_yapi_model"]
    )

    data["building1_yapi_model_hires"] = Task(
        name="Hires", type=data["model_type"], parent=data["building1_yapi_model"]
    )

    data["building1_yapi_look_dev"] = Task(
        name="LookDev",
        type=data["look_development_type"],
        parent=data["building1_yapi"],
        depends=[data["building1_yapi_model_hires"]],
    )

    data["building1_layout_proxy"].depends.append(data["building1_yapi_model_proxy"])

    data["building1_layout_hires"].depends.append(data["building1_yapi_model_hires"])

    # Building 2
    data["building2"] = Asset(
        name="Building2",
        code="Building2",
        type=data["building_type"],
        parent=data["ext1"],
    )

    data["building2_layout"] = Task(
        name="Layout", type=data["layout_type"], parent=data["building2"]
    )

    data["building2_layout_proxy"] = Task(
        name="Proxy", type=data["layout_type"], parent=data["building2_layout"]
    )

    data["building2_layout_hires"] = Task(
        name="Hires",
        type=data["layout_type"],
        parent=data["building2_layout"],
        depends=[data["building2_layout_proxy"]],
    )

    data["building2_look_dev"] = Task(
        name="LookDev", type=data["look_development_type"], parent=data["building2"]
    )

    data["building2_props"] = Task(name="Props", parent=data["building2"])

    data["building2_yapi"] = Task(name="YAPI", parent=data["building2_props"])

    data["building2_yapi_model"] = Task(
        name="Model", type=data["model_type"], parent=data["building2_yapi"]
    )

    data["building2_yapi_model_proxy"] = Task(
        name="Proxy", type=data["model_type"], parent=data["building2_yapi_model"]
    )

    data["building2_yapi_model_hires"] = Task(
        name="Hires", type=data["model_type"], parent=data["building2_yapi_model"]
    )

    data["building2_yapi_look_dev"] = Task(
        name="LookDev",
        type=data["look_development_type"],
        parent=data["building2_yapi"],
        depends=[data["building2_yapi_model_hires"]],
    )

    data["building2_layout_proxy"].depends.append(data["building2_yapi_model_proxy"])

    data["building2_layout_hires"].depends.append(data["building2_yapi_model_hires"])

    # continue to ext1 layout
    data["ext1_layout"] = Task(
        name="Layout", type=data["layout_type"], parent=data["ext1"]
    )

    data["ext1_layout_proxy"] = Task(
        name="Proxy", type=data["layout_type"], parent=data["ext1_layout"]
    )

    data["ext1_layout_hires"] = Task(
        name="Hires",
        type=data["layout_type"],
        parent=data["ext1_layout"],
        depends=[data["ext1_layout_proxy"]],
    )

    data["ext1_look_dev"] = Task(
        name="LookDev",
        type=data["look_development_type"],
        parent=data["ext1"],
        depends=[data["ext1_layout"]],
    )

    data["ext1_props"] = Task(name="Props", parent=data["ext1"])

    data["prop1"] = Asset(
        name="Prop1", code="Prop1", type=data["prop_type"], parent=data["ext1_props"]
    )

    data["prop1_model"] = Task(
        name="Model", type=data["model_type"], parent=data["prop1"]
    )

    data["prop1_model_proxy"] = Task(
        name="Proxy", type=data["model_type"], parent=data["prop1_model"]
    )

    data["prop1_model_hires"] = Task(
        name="Hires",
        type=data["model_type"],
        parent=data["prop1_model"],
        depends=[data["prop1_model_proxy"]],
    )

    data["prop1_look_dev"] = Task(
        name="LookDev", type=data["look_development_type"], parent=data["prop1"]
    )

    # and finally vegetation
    data["ext1_vegetation"] = Task(
        name="Vegetation", parent=data["ext1"], type=data["vegetation_type"]
    )

    # commit everything
    DBSession.add_all(
        [
            data["repo1"],
            data["status_new"],
            data["status_wip"],
            data["status_comp"],
            data["project_status_list"],
            data["project"],
            data["task_status_list"],
            data["asset_status_list"],
            data["shot_status_list"],
            data["sequence_status_list"],
            data["task1"],
            data["task2"],
            data["task3"],
            data["task4"],
            data["task5"],
            data["task6"],
            data["asset1"],
            data["asset2"],
            data["shot1"],
            data["shot2"],
            data["shot3"],
            data["sequence1"],
            data["sequence2"],
            data["task_template"],
            data["asset_template"],
            data["shot_template"],
            data["sequence_template"],
            data["character_design_type"],
            data["model_type"],
            data["look_development_type"],
            data["rig_type"],
            data["exterior_type"],
            data["building_type"],
            data["layout_type"],
            data["prop_type"],
            data["vegetation_type"],
            data["assets"],
            data["characters"],
            data["char1"],
            data["character_design"],
            data["char1_model"],
            data["char1_look_dev"],
            data["char1_rig"],
            data["environments"],
            data["exteriors"],
            data["ext1"],
            data["building1"],
            data["building1_layout"],
            data["building1_layout_proxy"],
            data["building1_layout_hires"],
            data["building1_look_dev"],
            data["building1_props"],
            data["building1_yapi"],
            data["building1_yapi_model"],
            data["building1_yapi_model_proxy"],
            data["building1_yapi_model_hires"],
            data["building1_yapi_look_dev"],
            data["building2"],
            data["building2_layout"],
            data["building2_layout_proxy"],
            data["building2_layout_hires"],
            data["building2_look_dev"],
            data["building2_props"],
            data["building2_yapi"],
            data["building2_yapi_model"],
            data["building2_yapi_model_proxy"],
            data["building2_yapi_model_hires"],
            data["building2_yapi_look_dev"],
            data["ext1_layout"],
            data["ext1_layout_proxy"],
            data["ext1_layout_hires"],
            data["ext1_look_dev"],
            data["ext1_props"],
            data["prop1"],
            data["prop1_model"],
            data["prop1_model_proxy"],
            data["prop1_model_hires"],
            data["prop1_look_dev"],
            data["ext1_vegetation"],
        ]
    )
    DBSession.commit()

    # asset2 model
    data["version1"] = create_version(data["asset2_model"], "Main")
    data["version2"] = create_version(data["asset2_model"], "Main")
    data["version3"] = create_version(data["asset2_model"], "Main")

    data["version4"] = create_version(data["asset2_model"], "Take1")
    data["version5"] = create_version(data["asset2_model"], "Take1")
    data["version6"] = create_version(data["asset2_model"], "Take1")

    # asset2 lookdev
    data["asset2_lookdev_main_version1"] = create_version(
        data["asset2_lookdev"], "Main"
    )
    data["asset2_lookdev_main_version2"] = create_version(
        data["asset2_lookdev"], "Main"
    )
    data["asset2_lookdev_main_version3"] = create_version(
        data["asset2_lookdev"], "Main"
    )

    data["asset2_lookdev_take1_version1"] = create_version(
        data["asset2_lookdev"], "Take1"
    )
    data["asset2_lookdev_take1_version2"] = create_version(
        data["asset2_lookdev"], "Take1"
    )
    data["asset2_lookdev_take1_version3"] = create_version(
        data["asset2_lookdev"], "Take1"
    )

    # task5
    data["version7"] = create_version(data["task5"], "Main")
    data["version8"] = create_version(data["task5"], "Main")
    data["version9"] = create_version(data["task5"], "Main")

    data["version10"] = create_version(data["task5"], "Take1")
    data["version11"] = create_version(data["task5"], "Take1")
    data["version12"] = create_version(data["task5"], "Take1")

    # task6
    data["version13"] = create_version(data["task6"], "Main")
    data["version14"] = create_version(data["task6"], "Main")
    data["version15"] = create_version(data["task6"], "Main")

    data["version16"] = create_version(data["task6"], "Take1")
    data["version17"] = create_version(data["task6"], "Take1")
    data["version18"] = create_version(data["task6"], "Take1")

    # shot3
    data["version19"] = create_version(data["shot3_anim"], "Main")
    data["version20"] = create_version(data["shot3_anim"], "Main")
    data["version21"] = create_version(data["shot3_anim"], "Main")

    data["version22"] = create_version(data["shot3_anim"], "Take1")
    data["version23"] = create_version(data["shot3_anim"], "Take1")
    data["version24"] = create_version(data["shot3_anim"], "Take1")

    # task3
    data["version25"] = create_version(data["task3"], "Main")
    data["version26"] = create_version(data["task3"], "Main")
    data["version27"] = create_version(data["task3"], "Main")

    data["version28"] = create_version(data["task3"], "Take1")
    data["version29"] = create_version(data["task3"], "Take1")
    data["version30"] = create_version(data["task3"], "Take1")

    # asset1
    data["version31"] = create_version(data["asset1"], "Main")
    data["version32"] = create_version(data["asset1"], "Main")
    data["version33"] = create_version(data["asset1"], "Main")

    data["version34"] = create_version(data["asset1"], "Take1")
    data["version35"] = create_version(data["asset1"], "Take1")
    data["version36"] = create_version(data["asset1"], "Take1")

    # shot2
    data["version37"] = create_version(data["shot2"], "Main")
    data["version38"] = create_version(data["shot2"], "Main")
    data["version39"] = create_version(data["shot2"], "Main")

    data["version40"] = create_version(data["shot2"], "Take1")
    data["version41"] = create_version(data["shot2"], "Take1")
    data["version42"] = create_version(data["shot2"], "Take1")

    # shot1
    data["version43"] = create_version(data["shot1"], "Main")
    data["version44"] = create_version(data["shot1"], "Main")
    data["version45"] = create_version(data["shot1"], "Main")

    data["version46"] = create_version(data["shot1"], "Take1")
    data["version47"] = create_version(data["shot1"], "Take1")
    data["version48"] = create_version(data["shot1"], "Take1")

    # Reflected Data
    # Char1 - Character Design
    data["version49"] = create_version(data["character_design"], "Main")
    data["version50"] = create_version(data["character_design"], "Main")
    data["version51"] = create_version(data["character_design"], "Main")

    # Char1 - Model
    data["version52"] = create_version(data["char1_model"], "Main")
    data["version53"] = create_version(data["char1_model"], "Main")
    data["version54"] = create_version(data["char1_model"], "Main")

    # Char1 - Look Dev
    data["version55"] = create_version(data["char1_look_dev"], "Main")
    data["version56"] = create_version(data["char1_look_dev"], "Main")
    data["version57"] = create_version(data["char1_look_dev"], "Main")

    # Char1 - Rig
    data["version58"] = create_version(data["char1_rig"], "Main")
    data["version59"] = create_version(data["char1_rig"], "Main")
    data["version60"] = create_version(data["char1_rig"], "Main")

    # Building1
    # Building1 - Layout - Proxy
    data["version61"] = create_version(data["building1_layout_proxy"], "Main")
    data["version62"] = create_version(data["building1_layout_proxy"], "Main")
    data["version63"] = create_version(data["building1_layout_proxy"], "Main")

    # Building1 - Layout - Hires
    data["version64"] = create_version(data["building1_layout_hires"], "Main")
    data["version65"] = create_version(data["building1_layout_hires"], "Main")
    data["version66"] = create_version(data["building1_layout_hires"], "Main")

    # Building1 - LookDev
    data["version67"] = create_version(data["building1_look_dev"], "Main")
    data["version68"] = create_version(data["building1_look_dev"], "Main")
    data["version69"] = create_version(data["building1_look_dev"], "Main")

    # Building1 | Props | Yapi | Model | Proxy
    data["version70"] = create_version(data["building1_yapi_model_proxy"], "Main")
    data["version71"] = create_version(data["building1_yapi_model_proxy"], "Main")
    data["version72"] = create_version(data["building1_yapi_model_proxy"], "Main")

    # Building1 | Props | Yapi | Model | Hires
    data["version73"] = create_version(data["building1_yapi_model_hires"], "Main")
    data["version74"] = create_version(data["building1_yapi_model_hires"], "Main")
    data["version75"] = create_version(data["building1_yapi_model_hires"], "Main")

    # Building1 | Props | Yapi | LookDev
    data["version76"] = create_version(data["building1_yapi_look_dev"], "Main")
    data["version77"] = create_version(data["building1_yapi_look_dev"], "Main")
    data["version78"] = create_version(data["building1_yapi_look_dev"], "Main")

    # Building2 | Layout | Proxy
    data["version79"] = create_version(data["building2_layout_proxy"], "Main")
    data["version80"] = create_version(data["building2_layout_proxy"], "Main")
    data["version81"] = create_version(data["building2_layout_proxy"], "Main")

    # Building2 | Layout | Hires
    data["version82"] = create_version(data["building2_layout_hires"], "Main")
    data["version83"] = create_version(data["building2_layout_hires"], "Main")
    data["version84"] = create_version(data["building2_layout_hires"], "Main")

    # Building2 | LookDev
    data["version85"] = create_version(data["building2_look_dev"], "Main")
    data["version86"] = create_version(data["building2_look_dev"], "Main")
    data["version87"] = create_version(data["building2_look_dev"], "Main")

    # Building2 | Props | Yapi | Model | Proxy
    data["version88"] = create_version(data["building2_yapi_model_proxy"], "Main")
    data["version89"] = create_version(data["building2_yapi_model_proxy"], "Main")
    data["version90"] = create_version(data["building2_yapi_model_proxy"], "Main")

    # Building2 | Props | Yapi | Model | Hires
    data["version91"] = create_version(data["building2_yapi_model_hires"], "Main")
    data["version92"] = create_version(data["building2_yapi_model_hires"], "Main")
    data["version93"] = create_version(data["building2_yapi_model_hires"], "Main")

    # Building2 | Props | Yapi | LookDev
    data["version94"] = create_version(data["building2_yapi_look_dev"], "Main")
    data["version95"] = create_version(data["building2_yapi_look_dev"], "Main")
    data["version96"] = create_version(data["building2_yapi_look_dev"], "Main")

    # Ext1 | Layout | Proxy
    data["version97"] = create_version(data["ext1_layout_proxy"], "Main")
    data["version98"] = create_version(data["ext1_layout_proxy"], "Main")
    data["version99"] = create_version(data["ext1_layout_proxy"], "Main")

    # Ext1 | Layout | Hires
    data["version100"] = create_version(data["ext1_layout_hires"], "Main")
    data["version101"] = create_version(data["ext1_layout_hires"], "Main")
    data["version102"] = create_version(data["ext1_layout_hires"], "Main")

    # Ext1 | LookDev
    data["version103"] = create_version(data["ext1_look_dev"], "Main")
    data["version104"] = create_version(data["ext1_look_dev"], "Main")
    data["version105"] = create_version(data["ext1_look_dev"], "Main")

    # Ext1 | Props | Prop1 | Model | Proxy
    data["version106"] = create_version(data["prop1_model_proxy"], "Main")
    data["version107"] = create_version(data["prop1_model_proxy"], "Main")
    data["version108"] = create_version(data["prop1_model_proxy"], "Main")

    # Ext1 | Props | Prop1 | Model | Hires
    data["version109"] = create_version(data["prop1_model_hires"], "Main")
    data["version110"] = create_version(data["prop1_model_hires"], "Main")
    data["version111"] = create_version(data["prop1_model_hires"], "Main")

    # Ext1 | Props | Prop1 | LookDev
    data["version112"] = create_version(data["prop1_look_dev"], "Main")
    data["version113"] = create_version(data["prop1_look_dev"], "Main")
    data["version114"] = create_version(data["prop1_look_dev"], "Main")

    # Ext1 | Vegetation
    data["version115"] = create_version(data["ext1_vegetation"], "Main")
    data["version116"] = create_version(data["ext1_vegetation"], "Main")
    data["version117"] = create_version(data["ext1_vegetation"], "Main")

    # Ext1 | Prop | LookDev (Kisa)
    data["version118"] = create_version(data["prop1_look_dev"], "Kisa")
    data["version119"] = create_version(data["prop1_look_dev"], "Kisa")
    data["version120"] = create_version(data["prop1_look_dev"], "Kisa")

    # Ext1 | Prop | Model (Kisa)
    data["version121"] = create_version(data["prop1_model_hires"], "Kisa")
    data["version122"] = create_version(data["prop1_model_hires"], "Kisa")
    data["version123"] = create_version(data["prop1_model_hires"], "Kisa")

    DBSession.commit()

    # load mtoa plugin
    try:
        pm.loadPlugin("mtoa")
    except RuntimeError:
        # no mtoa plugin
        # pass the test
        pass

    # now fill some content
    # Vegetation
    pm.newFile(force=True)

    # add the nodes
    base_transform = pm.nt.Transform(name="kksEnv___vegetation_ALL")
    strokes = pm.nt.Transform(name="kks___vegetation_pfxStrokes")
    strokes.v.set(0)
    polygons = pm.nt.Transform(name="kks___vegetation_pfxPolygons")
    paintable_geos = pm.nt.Transform(name="kks___vegetation_paintableGeos")

    # hide paintable geos
    paintable_geos.setAttr("v", False)

    pm.parent(strokes, base_transform)
    pm.parent(polygons, base_transform)
    pm.parent(paintable_geos, base_transform)

    # create some flowers
    pm.parent(pm.nt.Transform(name="KksEnv_PFXbrush___acacia___strokes"), strokes)

    pm.parent(pm.nt.Transform(name="Kks_PFXbrush___clover___strokes"), strokes)

    # create some transform nodes
    acacia_polygons = pm.nt.Transform(name="KksEnv_PFXbrush___acacia___polygons")
    pm.parent(acacia_polygons, polygons)

    # and polygons
    acacia_mesh_group = pm.nt.Transform(name="kksEnv_PFXbrush___acacia1MeshGroup")
    acacia_main = pm.polyCube(name="kksEnv_PFXbrush___acacia1Main")[0]
    acacia_leaf = pm.polyCube(name="kksEnv_PFXbrush___acacia1Leaf")[0]
    pm.runtime.DeleteHistory()

    pm.parent(acacia_mesh_group, acacia_polygons)
    pm.parent(acacia_main, acacia_mesh_group)
    pm.parent(acacia_leaf, acacia_mesh_group)

    clover_polygons = pm.nt.Transform(name="KksEnv_PFXbrush___clover___polygons")
    pm.parent(clover_polygons, polygons)

    # and polygons
    clover_mesh_group = pm.nt.Transform(name="kksEnv_PFXbrush___clover1MeshGroup")
    clover_main = pm.polyCube(name="kksEnv_PFXbrush___clover1Main")[0]
    clover_leaf = pm.polyCube(name="kksEnv_PFXbrush___clover1Leaf")[0]
    pm.runtime.DeleteHistory()

    pm.parent(clover_mesh_group, clover_polygons)
    pm.parent(clover_main, clover_mesh_group)
    pm.parent(clover_leaf, clover_mesh_group)

    # save its
    maya_env.save_as(version=data["version115"])
    maya_env.save_as(version=data["version116"])
    maya_env.save_as(version=data["version117"])

    # ***************************************
    # Prop1
    # ***************************************
    # Prop1 | Model | Hires | Main take
    pm.newFile(force=True)
    root_node = pm.nt.Transform(name="prop1")
    kulp = pm.polyCube(name="kulp")
    pm.parent(kulp[0], root_node)
    pm.runtime.DeleteHistory()
    maya_env.save_as(data["version109"])
    maya_env.save_as(data["version110"])
    maya_env.save_as(data["version111"])
    data["version111"].is_published = True

    # save it also under "Kisa" take
    maya_env.save_as(data["version121"])
    maya_env.save_as(data["version122"])
    maya_env.save_as(data["version123"])
    data["version123"].is_published = True

    # Prop1 | Look Dev | Main
    pm.newFile(force=True)
    maya_env.save_as(data["version112"])
    maya_env.reference(data["version111"])
    # assign a material to the object
    mat = pm.createSurfaceShader("aiStandard", name="kulp_aiStandard")
    pm.sets(mat[1], fe=pm.ls(type="mesh"))

    # save it
    maya_env.save_as(data["version112"])
    maya_env.save_as(data["version113"])
    maya_env.save_as(data["version114"])
    data["version114"].is_published = True

    # create "Kisa" take
    # Prop1 | Look Dev | Kisa
    pm.newFile(force=True)
    maya_env.save_as(data["version118"])
    maya_env.reference(data["version123"])
    # assign a material to the object
    mat = pm.createSurfaceShader("aiStandard", name="kulp_aiStandard")
    pm.sets(mat[1], fe=pm.ls(type="mesh"))

    maya_env.save_as(data["version118"])
    maya_env.save_as(data["version119"])
    maya_env.save_as(data["version120"])
    data["version120"].is_published = True

    # ****************************************
    # create Building1
    # ****************************************
    # hires model
    pm.newFile(force=True)

    building1_yapi = pm.nt.Transform(name="building1_yapi")
    some_cube = pm.polyCube(name="duvarlar")
    pm.runtime.DeleteHistory(some_cube[1])
    pm.parent(some_cube[0], building1_yapi)

    # save it
    maya_env.save_as(data["version73"])
    maya_env.save_as(data["version74"])
    maya_env.save_as(data["version75"])
    data["version75"].is_published = True

    # save it also for Building2 | Props | Yapi | Model
    building1_yapi.rename("building2_yapi")
    maya_env.save_as(data["version91"])
    maya_env.save_as(data["version92"])
    maya_env.save_as(data["version93"])
    data["version93"].is_published = True

    # Building1 | Props | Yapi | Look Dev
    pm.newFile(force=True)
    maya_env.save_as(data["version76"])
    maya_env.reference(data["version75"])

    # create an arnold material
    mat = pm.createSurfaceShader("aiStandard", name="bina_aiStandard")
    pm.sets(mat[1], fe=pm.ls(type="mesh"))

    # save it
    maya_env.save_as(data["version76"])
    maya_env.save_as(data["version77"])
    maya_env.save_as(data["version78"])
    data["version78"].is_published = True

    # save it for Building2 | Props | Yapi | Look Dev
    pm.listReferences()[0].replaceWith(data["version93"].absolute_full_path)
    maya_env.save_as(data["version94"])
    maya_env.save_as(data["version95"])
    maya_env.save_as(data["version96"])
    data["version96"].is_published = True

    # building1 layout
    pm.newFile(force=1)
    base_group = pm.nt.Transform(name="building1_layout")

    maya_env.save_as(data["version64"])
    ref_node = maya_env.reference(data["version78"])
    ref_root_node = auxiliary.get_root_nodes(ref_node)
    pm.parent(ref_root_node, base_group)

    maya_env.save_as(data["version64"])
    maya_env.save_as(data["version65"])
    maya_env.save_as(data["version66"])
    data["version66"].is_published = True

    # building2 layout
    pm.newFile(force=1)
    base_group = pm.nt.Transform(name="building2_layout")

    # reference building2 | yapi | look dev
    maya_env.save_as(data["version82"])
    ref_node = maya_env.reference(data["version96"])
    ref_root_node = auxiliary.get_root_nodes(ref_node)
    pm.parent(ref_root_node, base_group)

    maya_env.save_as(data["version82"])
    maya_env.save_as(data["version83"])
    maya_env.save_as(data["version84"])
    data["version84"].is_published = True

    # building1 | look dev
    pm.newFile(force=True)
    # reference building1 | Layout | Hires
    maya_env.save_as(data["version67"])
    maya_env.reference(data["version66"])
    # just save it
    maya_env.save_as(data["version67"])
    maya_env.save_as(data["version68"])
    maya_env.save_as(data["version69"])
    data["version69"].is_published = True

    # building2 | look dev
    pm.newFile(force=True)
    # reference building1 | Layout | Hires
    maya_env.save_as(data["version85"])
    maya_env.reference(data["version84"])
    # just save it
    maya_env.save_as(data["version85"])
    maya_env.save_as(data["version86"])
    maya_env.save_as(data["version87"])
    data["version87"].is_published = True

    # prepare the main layout of the exterior
    pm.newFile(force=True)
    maya_env.save_as(data["version100"])
    # reference Building1 | Layout | Hires
    maya_env.reference(data["version66"])
    # reference Building2 | Layout | Hires
    maya_env.reference(data["version84"])

    # create the layout root node
    root_node = pm.nt.Transform(name="ext1_layout")
    # parent the other buildings under this node
    building1_layout = pm.ls("building1_layout", r=1)[0]
    building2_layout = pm.ls("building2_layout", r=1)[0]

    pm.parent(building1_layout, root_node)
    pm.parent(building2_layout, root_node)

    # move them around
    building1_layout.setAttr("t", (10, 0, 0))
    building2_layout.setAttr("t", (0, 0, 10))

    # reference the vegetation
    ref_node = maya_env.reference(data["version117"])
    ref_root_node = auxiliary.get_root_nodes(ref_node)
    pm.parent(ref_root_node, root_node)

    # save it
    maya_env.save_as(data["version100"])
    maya_env.save_as(data["version101"])
    maya_env.save_as(data["version102"])
    data["version102"].is_published = True

    # *********************************
    # The Look Dev of the environment
    # *********************************
    pm.newFile(force=True)
    maya_env.save_as(data["version103"])
    maya_env.reference(data["version102"])
    maya_env.save_as(data["version103"])
    maya_env.save_as(data["version104"])
    maya_env.save_as(data["version105"])
    data["version105"].is_published = True
    pm.newFile(force=True)

    # +- task1
    # |  |
    # |  +- task4
    # |  |  |
    # |  |  +- asset2
    # |  |     +- Model
    # |  |     |  +- Main
    # |  |     |  |  +- version1
    # |  |     |  |  +- version2 (P)
    # |  |     |  |  +- version3 (P)
    # |  |     |  +- Take1
    # |  |     |     +- version4 (P)
    # |  |     |     +- version5
    # |  |     |     +- version6 (P)
    # |  |     +- LookDev
    # |  |        +- Main
    # |  |        |  +- asset2_lookdev_main_version1
    # |  |        |  +- asset2_lookdev_main_version2 (P)
    # |  |        |  +- asset2_lookdev_main_version3 (P)
    # |  |        +- Take1
    # |  |           +- asset2_lookdev_take1_version1 (P)
    # |  |           +- asset2_lookdev_take1_version2
    # |  |           +- asset2_lookdev_take1_version3 (P)
    # |  |
    # |  +- task5
    # |  |  +- Main
    # |  |  |  +- version7
    # |  |  |  +- version8
    # |  |  |  +- version9
    # |  |  +- Take1
    # |  |     +- version10
    # |  |     +- version11
    # |  |     +- version12 (P)
    # |  |
    # |  +- task6
    # |     +- Main
    # |     |  +- version13
    # |     |  +- version14
    # |     |  +- version15
    # |     +- Take1
    # |        +- version16 (P)
    # |        +- version17
    # |        +- version18 (P)
    # |
    # +- task2
    # |  |
    # |  +- sequence2
    # |     |
    # |     +- shot3
    # |        +- Anim
    # |           +- Main
    # |           |  +- version19
    # |           |  +- version20
    # |           |  +- version21
    # |           +- Take1
    # |              +- version22
    # |              +- version23
    # |              +- version24
    # |
    # +- task3
    # |  +- Main
    # |  |  +- version25
    # |  |  +- version26
    # |  |  +- version27
    # |  +- Take1
    # |     +- version28
    # |     +- version29
    # |     +- version30
    # |
    # +- asset1
    # |  +- Model
    # |     +- Main
    # |     |  +- version31
    # |     |  +- version32
    # |     |  +- version33
    # |     +- Take1
    # |        +- version34
    # |        +- version35
    # |        +- version36
    # |
    # +- sequence1
    # |  +- shot2
    # |     +- Main
    # |     |  +- version37
    # |     |  +- version38
    # |     |  +- version39
    # |     +- Take1
    # |        +- version40
    # |        +- version41
    # |        +- version42
    # |
    # +- shot1
    # |  +- Main
    # |  |  +- version43
    # |  |  +- version44
    # |  |  +- version45
    # |  +- Take1
    # |     +- version46
    # |     +- version47
    # |     +- version48
    # |
    # +- Assets (Task)
    #    +- Characters (Task)
    #    |  +- Char1 (Asset - Character)
    #    |     +- Character Design (Task - Character Design)
    #    |     |  +- version49
    #    |     |  +- version50
    #    |     |  +- version51
    #    |     |
    #    |     +- Model (Task - Model)
    #    |     |  +- version52
    #    |     |  +- version53
    #    |     |  +- version54
    #    |     |
    #    |     +- Look Dev (Task - Look Development)
    #    |     |  +- version55
    #    |     |  +- version56
    #    |     |  +- version57
    #    |     |
    #    |     +- Rig (Task - Rig)
    #    |        +- version58
    #    |        +- version59
    #    |        +- version60
    #    |
    #    +- Environments (Task)
    #       +- Exteriors (Task)
    #          +- Ext1 (Asset - Exterior)
    #             +- Building1 (Asset - Building)
    #             |  +- Layout (Task - Layout)
    #             |  |  +- Proxy (Task - Layout)
    #             |  |  |  +- version61
    #             |  |  |  +- version62
    #             |  |  |  +- version63
    #             |  |  |
    #             |  |  +- Hires (Task - Layout)
    #             |  |     +- version64
    #             |  |     +- version65
    #             |  |     +- version66
    #             |  |
    #             |  +- LookDev (Task - Look Development)
    #             |  |  +- version67
    #             |  |  +- version68
    #             |  |  +- version69
    #             |  |
    #             |  +- Props (Task)
    #             |     +- YAPI (Task)
    #             |        +- Model (Task - Model)
    #             |        |  +- Proxy (Task - Model)
    #             |        |  |  +- version70
    #             |        |  |  +- version71
    #             |        |  |  +- version72
    #             |        |  |
    #             |        |  +- Hires (Task - Model)
    #             |        |     +- version73
    #             |        |     +- version74
    #             |        |     +- version75
    #             |        |
    #             |        +- LookDev (Task - Look Development)
    #             |           +- version76
    #             |           +- version77
    #             |           +- version78
    #             |
    #             +- Building2 (Asset - Building)
    #             |  +- Layout (Task - Layout)
    #             |  |  +- Proxy (Task - Layout)
    #             |  |  |  +- version79
    #             |  |  |  +- version80
    #             |  |  |  +- version81
    #             |  |  |
    #             |  |  +- Hires (Task - Layout)
    #             |  |     +- version82
    #             |  |     +- version83
    #             |  |     +- version84
    #             |  |
    #             |  +- LookDev (Task - Look Development)
    #             |  |  +- version85
    #             |  |  +- version86
    #             |  |  +- version87
    #             |  |
    #             |  +- Props (Task)
    #             |     +- YAPI (Task)
    #             |        +- Model (Task - Model)
    #             |        |  +- Proxy (Task - Model)
    #             |        |  |  +- version88
    #             |        |  |  +- version89
    #             |        |  |  +- version90
    #             |        |  |
    #             |        |  +- Hires (Task - Model)
    #             |        |     +- version91
    #             |        |     +- version92
    #             |        |     +- version93
    #             |        |
    #             |        +- LookDev (Task - Look Development)
    #             |           +- version94
    #             |           +- version95
    #             |           +- version96
    #             |
    #             +- Layout (Task - Layout)
    #             |  +- Proxy (Task - Layout)
    #             |  |  +- version97
    #             |  |  +- version98
    #             |  |  +- version99
    #             |  |
    #             |  +- Hires (Task - Layout)
    #             |     +- version100
    #             |     +- version101
    #             |     +- version102
    #             |
    #             +- LookDev (Task - Look Development)
    #             |  +- version103
    #             |  +- version104
    #             |  +- version105
    #             |
    #             +- Props (Task)
    #             |  +- Prop1 (Asset)
    #             |     +- Model (Task - Model)
    #             |     |  +- Proxy (Task - Model)
    #             |     |  |  +- version106
    #             |     |  |  +- version107
    #             |     |  |  +- version108
    #             |     |  |
    #             |     |  +- Hires (Task - Model)
    #             |     |     +- **Main** (Take)
    #             |     |     |  +- version109
    #             |     |     |  +- version110
    #             |     |     |  +- version111
    #             |     |     +- **Kisa** (Take)
    #             |     |        +- version121
    #             |     |        +- version122
    #             |     |        +- version123
    #             |     |
    #             |     +- LookDev (Task - Look Development)
    #             |        +- **Main** (Take)
    #             |        |  +- version112
    #             |        |  +- version113
    #             |        |  +- version114
    #             |        +- **Kisa** (Take)
    #             |           +- version118
    #             |           +- version119
    #             |           +- version120
    #             |
    #             +- Vegetation (Task - Vegetation)
    #                +- version115
    #                +- version116
    #                +- version117

    # just renew the scene
    pm.newFile(force=True)
    yield data
