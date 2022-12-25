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
logger.setLevel(logging.DEBUG)


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

    data["char1_char_design"] = Task(
        name="Character Design",
        type=data["character_design_type"],
        parent=data["char1"],
    )

    data["char1_model"] = Task(
        name="Model",
        parent=data["char1"],
        type=data["model_type"],
        depends=[data["char1_char_design"]],
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
    data["ext2"] = Asset(
        name="Ext2", code="Ext2", type=data["exterior_type"], parent=data["exteriors"]
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

    data["building1_look_dev"] = Task(
        name="LookDev", type=data["look_development_type"], parent=data["building1"]
    )

    data["building1_props"] = Task(name="Props", parent=data["building1"])

    data["building1_yapi"] = Asset(
        name="YAPI",
        code="YAPI",
        type=data["building_type"],
        parent=data["building1_props"],
    )

    data["building1_yapi_model"] = Task(
        name="Model", type=data["model_type"], parent=data["building1_yapi"]
    )

    data["building1_yapi_look_dev"] = Task(
        name="LookDev",
        type=data["look_development_type"],
        parent=data["building1_yapi"],
        depends=[data["building1_yapi_model"]],
    )

    data["building1_layout"].depends.append(data["building1_yapi_model"])

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

    data["building2_look_dev"] = Task(
        name="LookDev", type=data["look_development_type"], parent=data["building2"]
    )

    data["building2_props"] = Task(name="Props", parent=data["building2"])

    data["building2_yapi"] = Asset(
        name="YAPI",
        code="YAPI",
        type=data["building_type"],
        parent=data["building2_props"],
    )

    data["building2_yapi_model"] = Task(
        name="Model", type=data["model_type"], parent=data["building2_yapi"]
    )

    data["building2_yapi_look_dev"] = Task(
        name="LookDev",
        type=data["look_development_type"],
        parent=data["building2_yapi"],
        depends=[data["building2_yapi_model"]],
    )

    data["building2_layout"].depends.append(data["building2_yapi_model"])

    # continue to ext1 layout
    data["ext1_layout"] = Task(
        name="Layout", type=data["layout_type"], parent=data["ext1"]
    )
    data["ext1_look_dev"] = Task(
        name="LookDev",
        type=data["look_development_type"],
        parent=data["ext1"],
        depends=[data["ext1_layout"]],
    )
    data["ext2_model"] = Task(
        name="Model",
        type=data["model_type"],
        parent=data["ext2"],
    )
    data["ext2_look_dev"] = Task(
        name="LookDev",
        type=data["look_development_type"],
        parent=data["ext2"],
        depends=[data["ext2_model"]],
    )
    data["ext2_layout"] = Task(
        name="Layout",
        type=data["layout_type"],
        parent=data["ext2"],
        depends=[data["ext2_look_dev"]],
    )

    data["ext1_props"] = Task(name="Props", parent=data["ext1"])

    data["prop1"] = Asset(
        name="Prop1", code="Prop1", type=data["prop_type"], parent=data["ext1_props"]
    )

    data["prop1_model"] = Task(
        name="Model", type=data["model_type"], parent=data["prop1"]
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
            data["char1_char_design"],
            data["char1_model"],
            data["char1_look_dev"],
            data["char1_rig"],
            data["environments"],
            data["exteriors"],
            data["ext1"],
            data["ext2"],
            data["building1"],
            data["building1_layout"],
            data["building1_look_dev"],
            data["building1_props"],
            data["building1_yapi"],
            data["building1_yapi_model"],
            data["building1_yapi_look_dev"],
            data["building2"],
            data["building2_layout"],
            data["building2_look_dev"],
            data["building2_props"],
            data["building2_yapi"],
            data["building2_yapi_model"],
            data["building2_yapi_look_dev"],
            data["ext1_layout"],
            data["ext1_look_dev"],
            data["ext1_props"],
            data["ext2_model"],
            data["ext2_look_dev"],
            data["ext2_layout"],
            data["prop1"],
            data["prop1_model"],
            data["prop1_look_dev"],
            data["ext1_vegetation"],
        ]
    )
    DBSession.commit()

    # asset2 model
    data["asset2_model_main_v001"] = create_version(data["asset2_model"], "Main")
    data["asset2_model_main_v002"] = create_version(data["asset2_model"], "Main")
    data["asset2_model_main_v003"] = create_version(data["asset2_model"], "Main")

    data["asset2_model_take1_v001"] = create_version(data["asset2_model"], "Take1")
    data["asset2_model_take1_v002"] = create_version(data["asset2_model"], "Take1")
    data["asset2_model_take1_v003"] = create_version(data["asset2_model"], "Take1")

    # asset2 lookdev
    data["asset2_lookdev_main_v001"] = create_version(data["asset2_lookdev"], "Main")
    data["asset2_lookdev_main_v002"] = create_version(data["asset2_lookdev"], "Main")
    data["asset2_lookdev_main_v003"] = create_version(data["asset2_lookdev"], "Main")

    data["asset2_lookdev_take1_v001"] = create_version(data["asset2_lookdev"], "Take1")
    data["asset2_lookdev_take1_v002"] = create_version(data["asset2_lookdev"], "Take1")
    data["asset2_lookdev_take1_v003"] = create_version(data["asset2_lookdev"], "Take1")

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
    data["shot3_anim_main_v001"] = create_version(data["shot3_anim"], "Main")
    data["shot3_anim_main_v002"] = create_version(data["shot3_anim"], "Main")
    data["shot3_anim_main_v003"] = create_version(data["shot3_anim"], "Main")

    data["shot3_anim_take1_v001"] = create_version(data["shot3_anim"], "Take1")
    data["shot3_anim_take1_v002"] = create_version(data["shot3_anim"], "Take1")
    data["shot3_anim_take1_v003"] = create_version(data["shot3_anim"], "Take1")

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
    data["char1_char_design_main_v001"] = create_version(
        data["char1_char_design"], "Main"
    )
    data["char1_char_design_main_v002"] = create_version(
        data["char1_char_design"], "Main"
    )
    data["char1_char_design_main_v003"] = create_version(
        data["char1_char_design"], "Main"
    )

    # Char1 - Model
    data["char1_model_main_v001"] = create_version(data["char1_model"], "Main")
    data["char1_model_main_v002"] = create_version(data["char1_model"], "Main")
    data["char1_model_main_v003"] = create_version(data["char1_model"], "Main")

    # Char1 - Look Dev
    data["char1_look_dev_main_v001"] = create_version(data["char1_look_dev"], "Main")
    data["char1_look_dev_main_v002"] = create_version(data["char1_look_dev"], "Main")
    data["char1_look_dev_main_v003"] = create_version(data["char1_look_dev"], "Main")

    # Char1 - Rig
    data["char1_rig_main_v001"] = create_version(data["char1_rig"], "Main")
    data["char1_rig_main_v002"] = create_version(data["char1_rig"], "Main")
    data["char1_rig_main_v003"] = create_version(data["char1_rig"], "Main")

    # Building1
    # Building1 - Layout
    data["building1_layout_main_v001"] = create_version(
        data["building1_layout"], "Main"
    )
    data["building1_layout_main_v002"] = create_version(
        data["building1_layout"], "Main"
    )
    data["building1_layout_main_v003"] = create_version(
        data["building1_layout"], "Main"
    )

    # Building1 - LookDev
    data["building1_look_dev_main_v001"] = create_version(
        data["building1_look_dev"], "Main"
    )
    data["building1_look_dev_main_v002"] = create_version(
        data["building1_look_dev"], "Main"
    )
    data["building1_look_dev_main_v003"] = create_version(
        data["building1_look_dev"], "Main"
    )

    # Building1 | Props | Yapi | Model
    data["building1_yapi_model_main_v001"] = create_version(
        data["building1_yapi_model"], "Main"
    )
    data["building1_yapi_model_main_v002"] = create_version(
        data["building1_yapi_model"], "Main"
    )
    data["building1_yapi_model_main_v003"] = create_version(
        data["building1_yapi_model"], "Main"
    )

    # Building1 | Props | Yapi | LookDev
    data["building1_yapi_look_dev_main_v001"] = create_version(
        data["building1_yapi_look_dev"], "Main"
    )
    data["building1_yapi_look_dev_main_v002"] = create_version(
        data["building1_yapi_look_dev"], "Main"
    )
    data["building1_yapi_look_dev_main_v003"] = create_version(
        data["building1_yapi_look_dev"], "Main"
    )

    # Building2 | Layout
    data["building2_layout_main_v001"] = create_version(
        data["building2_layout"], "Main"
    )
    data["building2_layout_main_v002"] = create_version(
        data["building2_layout"], "Main"
    )
    data["building2_layout_main_v003"] = create_version(
        data["building2_layout"], "Main"
    )

    # Building2 | LookDev
    data["building2_look_dev_main_v001"] = create_version(
        data["building2_look_dev"], "Main"
    )
    data["building2_look_dev_main_v002"] = create_version(
        data["building2_look_dev"], "Main"
    )
    data["building2_look_dev_main_v003"] = create_version(
        data["building2_look_dev"], "Main"
    )

    # Building2 | Props | Yapi | Model
    data["building2_yapi_model_main_v001"] = create_version(
        data["building2_yapi_model"], "Main"
    )
    data["building2_yapi_model_main_v002"] = create_version(
        data["building2_yapi_model"], "Main"
    )
    data["building2_yapi_model_main_v003"] = create_version(
        data["building2_yapi_model"], "Main"
    )

    # Building2 | Props | Yapi | LookDev
    data["building2_yapi_look_dev_main_v001"] = create_version(
        data["building2_yapi_look_dev"], "Main"
    )
    data["building2_yapi_look_dev_main_v002"] = create_version(
        data["building2_yapi_look_dev"], "Main"
    )
    data["building2_yapi_look_dev_main_v003"] = create_version(
        data["building2_yapi_look_dev"], "Main"
    )

    # Ext1 | Layout
    data["ext1_layout_main_v001"] = create_version(data["ext1_layout"], "Main")
    data["ext1_layout_main_v002"] = create_version(data["ext1_layout"], "Main")
    data["ext1_layout_main_v003"] = create_version(data["ext1_layout"], "Main")

    # Ext1 | LookDev
    data["ext1_look_dev_main_v001"] = create_version(data["ext1_look_dev"], "Main")
    data["ext1_look_dev_main_v002"] = create_version(data["ext1_look_dev"], "Main")
    data["ext1_look_dev_main_v003"] = create_version(data["ext1_look_dev"], "Main")

    # Ext1 | Props | Prop1 | Model
    data["prop1_model_main_v001"] = create_version(data["prop1_model"], "Main")
    data["prop1_model_main_v002"] = create_version(data["prop1_model"], "Main")
    data["prop1_model_main_v003"] = create_version(data["prop1_model"], "Main")

    # Ext1 | Props | Prop1 | LookDev
    data["prop1_look_dev_main_v001"] = create_version(data["prop1_look_dev"], "Main")
    data["prop1_look_dev_main_v002"] = create_version(data["prop1_look_dev"], "Main")
    data["prop1_look_dev_main_v003"] = create_version(data["prop1_look_dev"], "Main")

    # Ext1 | Vegetation
    data["ext1_vegetation_main_v001"] = create_version(data["ext1_vegetation"], "Main")
    data["ext1_vegetation_main_v002"] = create_version(data["ext1_vegetation"], "Main")
    data["ext1_vegetation_main_v003"] = create_version(data["ext1_vegetation"], "Main")

    # Ext1 | Prop | LookDev (Kisa)
    data["prop1_look_dev_kisa_v001"] = create_version(data["prop1_look_dev"], "Kisa")
    data["prop1_look_dev_kisa_v002"] = create_version(data["prop1_look_dev"], "Kisa")
    data["prop1_look_dev_kisa_v003"] = create_version(data["prop1_look_dev"], "Kisa")

    # Ext1 | Prop | Model (Kisa)
    data["prop1_model_kisa_v001"] = create_version(data["prop1_model"], "Kisa")
    data["prop1_model_kisa_v002"] = create_version(data["prop1_model"], "Kisa")
    data["prop1_model_kisa_v003"] = create_version(data["prop1_model"], "Kisa")

    # Ext2 | Model
    data["ext2_model_main_v001"] = create_version(data["ext2_model"], "Main")
    data["ext2_model_main_v002"] = create_version(data["ext2_model"], "Main")
    data["ext2_model_main_v003"] = create_version(data["ext2_model"], "Main")

    # Ext2 | LookDev
    data["ext2_look_dev_main_v001"] = create_version(data["ext2_look_dev"], "Main")
    data["ext2_look_dev_main_v002"] = create_version(data["ext2_look_dev"], "Main")
    data["ext2_look_dev_main_v003"] = create_version(data["ext2_look_dev"], "Main")

    # Ext2 | Layout
    data["ext2_layout_main_v001"] = create_version(data["ext2_layout"], "Main")
    data["ext2_layout_main_v002"] = create_version(data["ext2_layout"], "Main")
    data["ext2_layout_main_v003"] = create_version(data["ext2_layout"], "Main")

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
    maya_env.save_as(version=data["ext1_vegetation_main_v001"])
    maya_env.save_as(version=data["ext1_vegetation_main_v002"])
    maya_env.save_as(version=data["ext1_vegetation_main_v003"])

    # ***************************************
    # Prop1
    # ***************************************
    # Prop1 | Model | Main take
    pm.newFile(force=True)
    root_node = pm.nt.Transform(name="prop1")
    kulp = pm.polyCube(name="kulp")
    pm.parent(kulp[0], root_node)
    pm.runtime.DeleteHistory()
    maya_env.save_as(data["prop1_model_main_v001"])
    maya_env.save_as(data["prop1_model_main_v002"])
    maya_env.save_as(data["prop1_model_main_v003"])
    data["prop1_model_main_v003"].is_published = True

    # save it also under "Kisa" take
    maya_env.save_as(data["prop1_model_kisa_v001"])
    maya_env.save_as(data["prop1_model_kisa_v002"])
    maya_env.save_as(data["prop1_model_kisa_v003"])
    data["prop1_model_kisa_v003"].is_published = True

    # Prop1 | Look Dev | Main
    pm.newFile(force=True)
    maya_env.save_as(data["prop1_look_dev_main_v001"])
    maya_env.reference(data["prop1_model_main_v003"])
    # assign a material to the object
    mat = pm.createSurfaceShader("aiStandard", name="kulp_aiStandard")
    pm.sets(mat[1], fe=pm.ls(type="mesh"))

    # save it
    maya_env.save_as(data["prop1_look_dev_main_v001"])
    maya_env.save_as(data["prop1_look_dev_main_v002"])
    maya_env.save_as(data["prop1_look_dev_main_v003"])
    data["prop1_look_dev_main_v003"].is_published = True

    # create "Kisa" take
    # Prop1 | Look Dev | Kisa
    pm.newFile(force=True)
    maya_env.save_as(data["prop1_look_dev_kisa_v001"])
    maya_env.reference(data["prop1_model_kisa_v003"])
    # assign a material to the object
    mat = pm.createSurfaceShader("aiStandard", name="kulp_aiStandard")
    pm.sets(mat[1], fe=pm.ls(type="mesh"))

    maya_env.save_as(data["prop1_look_dev_kisa_v001"])
    maya_env.save_as(data["prop1_look_dev_kisa_v002"])
    maya_env.save_as(data["prop1_look_dev_kisa_v003"])
    data["prop1_look_dev_kisa_v003"].is_published = True

    # ****************************************
    # create Building1
    # ****************************************
    # model
    pm.newFile(force=True)

    building1_yapi = pm.nt.Transform(name="building1_yapi")
    some_cube = pm.polyCube(name="duvarlar")
    pm.runtime.DeleteHistory(some_cube[1])
    pm.parent(some_cube[0], building1_yapi)

    # save it
    maya_env.save_as(data["building1_yapi_model_main_v001"])
    maya_env.save_as(data["building1_yapi_model_main_v002"])
    maya_env.save_as(data["building1_yapi_model_main_v003"])
    data["building1_yapi_model_main_v003"].is_published = True

    # save it also for Building2 | Props | Yapi | Model
    building1_yapi.rename("building2_yapi")
    maya_env.save_as(data["building2_yapi_model_main_v001"])
    maya_env.save_as(data["building2_yapi_model_main_v002"])
    maya_env.save_as(data["building2_yapi_model_main_v003"])
    data["building2_yapi_model_main_v003"].is_published = True

    # Building1 | Props | Yapi | Look Dev
    pm.newFile(force=True)
    maya_env.save_as(data["building1_yapi_look_dev_main_v001"])
    maya_env.reference(data["building1_yapi_model_main_v003"])

    # create an arnold material
    mat = pm.createSurfaceShader("aiStandard", name="bina_aiStandard")
    pm.sets(mat[1], fe=pm.ls(type="mesh"))

    # save it
    maya_env.save_as(data["building1_yapi_look_dev_main_v001"])
    maya_env.save_as(data["building1_yapi_look_dev_main_v002"])
    maya_env.save_as(data["building1_yapi_look_dev_main_v003"])
    data["building1_yapi_look_dev_main_v003"].is_published = True

    # save it for Building2 | Props | Yapi | Look Dev
    pm.listReferences()[0].replaceWith(
        data["building2_yapi_model_main_v003"].absolute_full_path
    )
    maya_env.save_as(data["building2_yapi_look_dev_main_v001"])
    maya_env.save_as(data["building2_yapi_look_dev_main_v002"])
    maya_env.save_as(data["building2_yapi_look_dev_main_v003"])
    data["building2_yapi_look_dev_main_v003"].is_published = True

    # building1 layout
    pm.newFile(force=1)
    base_group = pm.nt.Transform(name="building1_layout")

    maya_env.save_as(data["building1_layout_main_v001"])
    ref_node = maya_env.reference(data["building1_yapi_look_dev_main_v003"])
    ref_root_node = auxiliary.get_root_nodes(ref_node)
    pm.parent(ref_root_node, base_group)

    maya_env.save_as(data["building1_layout_main_v001"])
    maya_env.save_as(data["building1_layout_main_v002"])
    maya_env.save_as(data["building1_layout_main_v003"])
    data["building1_layout_main_v003"].is_published = True

    # building2 layout
    pm.newFile(force=1)
    base_group = pm.nt.Transform(name="building2_layout")

    # reference building2 | yapi | look dev
    maya_env.save_as(data["building2_layout_main_v001"])
    ref_node = maya_env.reference(data["building2_yapi_look_dev_main_v003"])
    ref_root_node = auxiliary.get_root_nodes(ref_node)
    pm.parent(ref_root_node, base_group)

    maya_env.save_as(data["building2_layout_main_v001"])
    maya_env.save_as(data["building2_layout_main_v002"])
    maya_env.save_as(data["building2_layout_main_v003"])
    data["building2_layout_main_v003"].is_published = True

    # building1 | look dev
    pm.newFile(force=True)
    # reference building1 | Layout
    maya_env.save_as(data["building1_look_dev_main_v001"])
    maya_env.reference(data["building1_layout_main_v003"])
    # just save it
    maya_env.save_as(data["building1_look_dev_main_v001"])
    maya_env.save_as(data["building1_look_dev_main_v002"])
    maya_env.save_as(data["building1_look_dev_main_v003"])
    data["building1_look_dev_main_v003"].is_published = True

    # building2 | look dev
    pm.newFile(force=True)
    # reference building1 | Layout
    maya_env.save_as(data["building2_look_dev_main_v001"])
    maya_env.reference(data["building2_layout_main_v003"])
    # just save it
    maya_env.save_as(data["building2_look_dev_main_v001"])
    maya_env.save_as(data["building2_look_dev_main_v002"])
    maya_env.save_as(data["building2_look_dev_main_v003"])
    data["building2_look_dev_main_v003"].is_published = True

    # prepare the main layout of the exterior
    pm.newFile(force=True)
    maya_env.save_as(data["ext1_layout_main_v001"])
    # reference Building1 | Layout
    maya_env.reference(data["building1_layout_main_v003"])
    # reference Building2 | Layout
    maya_env.reference(data["building2_layout_main_v003"])

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
    ref_node = maya_env.reference(data["ext1_vegetation_main_v003"])
    ref_root_node = auxiliary.get_root_nodes(ref_node)
    pm.parent(ref_root_node, root_node)

    # save it
    maya_env.save_as(data["ext1_layout_main_v001"])
    maya_env.save_as(data["ext1_layout_main_v002"])
    maya_env.save_as(data["ext1_layout_main_v003"])
    data["ext1_layout_main_v003"].is_published = True

    # *********************************
    # The Look Dev of the environment
    # *********************************
    pm.newFile(force=True)
    maya_env.save_as(data["ext1_look_dev_main_v001"])
    maya_env.reference(data["ext1_layout_main_v003"])
    maya_env.save_as(data["ext1_look_dev_main_v001"])
    maya_env.save_as(data["ext1_look_dev_main_v002"])
    maya_env.save_as(data["ext1_look_dev_main_v003"])
    data["ext1_look_dev_main_v003"].is_published = True
    pm.newFile(force=True)

    # +- task1
    # |  |
    # |  +- task4
    # |  |  |
    # |  |  +- asset2
    # |  |     +- Model
    # |  |     |  +- Main
    # |  |     |  |  +- asset2_model_main_v001
    # |  |     |  |  +- asset2_model_main_v002 (P)
    # |  |     |  |  +- asset2_model_main_v003 (P)
    # |  |     |  +- Take1
    # |  |     |     +- asset2_model_take1_v001 (P)
    # |  |     |     +- asset2_model_take1_v002
    # |  |     |     +- asset2_model_take1_v003 (P)
    # |  |     +- LookDev
    # |  |        +- Main
    # |  |        |  +- asset2_lookdev_main_v001
    # |  |        |  +- asset2_lookdev_main_v002 (P)
    # |  |        |  +- asset2_lookdev_main_v003 (P)
    # |  |        +- Take1
    # |  |           +- asset2_lookdev_take1_v001 (P)
    # |  |           +- asset2_lookdev_take1_v002
    # |  |           +- asset2_lookdev_take1_v003 (P)
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
    # |           |  +- shot3_anim_main_v001
    # |           |  +- shot3_anim_main_v002
    # |           |  +- shot3_anim_main_v003
    # |           +- Take1
    # |              +- shot3_anim_take1_v001
    # |              +- shot3_anim_take1_v001
    # |              +- shot3_anim_take1_v001
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
    #    |     |  +- char1_char_design_main_v001
    #    |     |  +- char1_char_design_main_v002
    #    |     |  +- char1_char_design_main_v003
    #    |     |
    #    |     +- Model (Task - Model)
    #    |     |  +- char1_model_main_v001
    #    |     |  +- char1_model_main_v002
    #    |     |  +- char1_model_main_v003
    #    |     |
    #    |     +- Look Dev (Task - Look Development)
    #    |     |  +- char1_look_dev_main_v001
    #    |     |  +- char1_look_dev_main_v002
    #    |     |  +- char1_look_dev_main_v003
    #    |     |
    #    |     +- Rig (Task - Rig)
    #    |        +- char1_rig_main_v001
    #    |        +- char1_rig_main_v002
    #    |        +- char1_rig_main_v003
    #    |
    #    +- Environments (Task)
    #       +- Exteriors (Task)
    #          +- Ext1 (Asset - Exterior)
    #          |  +- Building1 (Asset - Building)
    #          |  |  +- Layout (Task - Layout)
    #          |  |  |  +- building1_layout_main_v001
    #          |  |  |  +- building1_layout_main_v002
    #          |  |  |  +- building1_layout_main_v003
    #          |  |  |
    #          |  |  +- LookDev (Task - Look Development)
    #          |  |  |  +- building1_look_dev_main_v001
    #          |  |  |  +- building1_look_dev_main_v002
    #          |  |  |  +- building1_look_dev_main_v003
    #          |  |  |
    #          |  |  +- Props (Task)
    #          |  |     +- building1_yapi (Asset)
    #          |  |        +- Model (Task - Model)
    #          |  |        |  +- building1_yapi_model_main_v001
    #          |  |        |  +- building1_yapi_model_main_v002
    #          |  |        |  +- building1_yapi_model_main_v003
    #          |  |        |
    #          |  |        +- LookDev (Task - Look Development)
    #          |  |           +- building1_yapi_look_dev_main_v001
    #          |  |           +- building1_yapi_look_dev_main_v002
    #          |  |           +- building1_yapi_look_dev_main_v003
    #          |  |
    #          |  +- Building2 (Asset - Building)
    #          |  |  +- Layout (Task - Layout)
    #          |  |  |  +- building2_layout_main_v001
    #          |  |  |  +- building2_layout_main_v002
    #          |  |  |  +- building2_layout_main_v003
    #          |  |  |
    #          |  |  +- LookDev (Task - Look Development)
    #          |  |  |  +- building2_look_dev_main_v001
    #          |  |  |  +- building2_look_dev_main_v002
    #          |  |  |  +- building2_look_dev_main_v003
    #          |  |  |
    #          |  |  +- Props (Task)
    #          |  |     +- building2_yapi (Asset)
    #          |  |        +- Model (Task - Model)
    #          |  |        |  +- building2_yapi_model_main_v001
    #          |  |        |  +- building2_yapi_model_main_v002
    #          |  |        |  +- building2_yapi_model_main_v003
    #          |  |        |
    #          |  |        +- LookDev (Task - Look Development)
    #          |  |           +- building2_yapi_look_dev_main_v001
    #          |  |           +- building2_yapi_look_dev_main_v002
    #          |  |           +- building2_yapi_look_dev_main_v003
    #          |  |
    #          |  +- Layout (Task - Layout)
    #          |  |  +- ext1_layout_main_v001
    #          |  |  +- ext1_layout_main_v002
    #          |  |  +- ext1_layout_main_v003
    #          |  |
    #          |  +- LookDev (Task - Look Development)
    #          |  |  +- ext1_look_dev_main_v001
    #          |  |  +- ext1_look_dev_main_v002
    #          |  |  +- ext1_look_dev_main_v003
    #          |  |
    #          |  +- Props (Task)
    #          |  |  +- Prop1 (Asset)
    #          |  |     +- Model (Task - Model)
    #          |  |     |  +- **Main** (Take)
    #          |  |     |  |  +- prop1_model_main_v001
    #          |  |     |  |  +- prop1_model_main_v002
    #          |  |     |  |  +- prop1_model_main_v003
    #          |  |     |  +- **Kisa** (Take)
    #          |  |     |     +- prop1_model_kisa_v001
    #          |  |     |     +- prop1_model_kisa_v002
    #          |  |     |     +- prop1_model_kisa_v003
    #          |  |     |
    #          |  |     +- LookDev (Task - Look Development)
    #          |  |        +- **Main** (Take)
    #          |  |        |  +- prop1_look_dev_main_v001
    #          |  |        |  +- prop1_look_dev_main_v002
    #          |  |        |  +- prop1_look_dev_main_v003
    #          |  |        +- **Kisa** (Take)
    #          |  |           +- prop1_look_dev_kisa_v001
    #          |  |           +- prop1_look_dev_kisa_v002
    #          |  |           +- prop1_look_dev_kisa_v003
    #          |  |
    #          |  +- Vegetation (Task - Vegetation)
    #          |     +- ext1_vegetation_main_v001
    #          |     +- ext1_vegetation_main_v002
    #          |     +- ext1_vegetation_main_v003
    #          +- Ext2 (Asset - Exterior)
    #             +- Model (Task - Model)
    #             |  +- ext2_model_main_v001
    #             |  +- ext2_model_main_v002
    #             |  +- ext2_model_main_v003
    #             +- LookDev (Task - Look Development)
    #             |  +- ext2_look_dev_main_v001
    #             |  +- ext2_look_dev_main_v002
    #             |  +- ext2_look_dev_main_v003
    #             +- Layout (Task - Layout)
    #                +- ext2_layout_main_v001
    #                +- ext2_layout_main_v002
    #                +- ext2_layout_main_v003

    # just renew the scene
    pm.newFile(force=True)
    yield data
