# -*- coding: utf-8 -*-
import json
import os
import shutil
import tempfile

import pytest

# set log level to DEBUG
import logging
from anima import logger
from anima.publish import clear_publishers

logger.setLevel(logging.DEBUG)

# store current folder path
__here__ = os.path.dirname(__file__)


@pytest.fixture(scope="function")
def test_data():
    """Read the test data."""
    # reads the test data as text
    here = os.path.dirname(__file__)
    test_data_file_path = os.path.join(here, "utils/data", "test_template.json")
    with open(test_data_file_path) as f:
        test_data = json.load(f)

    yield test_data


@pytest.fixture(scope="function")
def create_db():
    """creates a test database"""
    from stalker import db

    print("setting up test database")
    db.setup({"sqlalchemy.url": "sqlite://"})
    print("initializing test database")
    db.init()


@pytest.fixture(scope="function")
def create_empty_project():
    """creates empty project test data"""
    from stalker.db.session import DBSession
    from stalker import (
        FilenameTemplate,
        Repository,
        Project,
        Structure,
    )

    repo = Repository(
        name="Test Repository",
        code="TR",
        windows_path="T:/",
        linux_path="/mnt/T/",
        osx_path="/Volumes/T/",
    )

    task_filename_template = FilenameTemplate(
        name="Task Filename Template",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}"
        "/{%- endfor -%}",
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type="Task",
    )
    asset_filename_template = FilenameTemplate(
        name="Asset Filename Template",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}"
        "/{%- endfor -%}",
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type="Asset",
    )
    shot_filename_template = FilenameTemplate(
        name="Shot Filename Template",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}"
        "/{%- endfor -%}",
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type="Shot",
    )
    sequence_filename_template = FilenameTemplate(
        name="Sequence Filename Template",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}"
        "/{%- endfor -%}",
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type="Sequence",
    )

    structure = Structure(
        name="Default Project Structure",
        templates=[
            task_filename_template,
            asset_filename_template,
            shot_filename_template,
            sequence_filename_template,
        ],
    )

    DBSession.add_all(
        [
            structure,
            task_filename_template,
            asset_filename_template,
            shot_filename_template,
            sequence_filename_template,
        ]
    )
    DBSession.commit()

    project = Project(
        name="Test Project",
        code="TP",
        repository=repo,
        structure=structure,
    )
    DBSession.add(project)
    DBSession.commit()

    yield project


@pytest.fixture(scope="function")
def create_project():
    """creates test data"""
    from stalker.db.session import DBSession
    from stalker import (
        Task,
        Asset,
        Type,
        Sequence,
        Shot,
        Version,
        FilenameTemplate,
        Repository,
        Project,
        Structure,
    )

    repo = Repository(
        name="Test Repository",
        code="TR",
        windows_path="T:/",
        linux_path="/mnt/T/",
        osx_path="/Volumes/T/",
    )

    task_filename_template = FilenameTemplate(
        name="Task Filename Template",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}"
        "/{%- endfor -%}",
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type="Task",
    )
    asset_filename_template = FilenameTemplate(
        name="Asset Filename Template",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}"
        "/{%- endfor -%}",
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type="Asset",
    )
    shot_filename_template = FilenameTemplate(
        name="Shot Filename Template",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}"
        "/{%- endfor -%}",
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type="Shot",
    )
    sequence_filename_template = FilenameTemplate(
        name="Sequence Filename Template",
        path="$REPO{{project.repository.code}}/{{project.code}}/"
        "{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}"
        "/{%- endfor -%}",
        filename='{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}',
        target_entity_type="Sequence",
    )

    structure = Structure(
        name="Default Project Structure",
        templates=[
            task_filename_template,
            asset_filename_template,
            shot_filename_template,
            sequence_filename_template,
        ],
    )

    DBSession.add_all(
        [
            structure,
            task_filename_template,
            asset_filename_template,
            shot_filename_template,
            sequence_filename_template,
        ]
    )
    DBSession.commit()

    project = Project(
        name="Test Project",
        code="TP",
        repository=repo,
        structure=structure,
    )
    DBSession.add(project)
    DBSession.commit()

    project2 = Project(
        name="Test Project 2", code="TP2", repository=repo, structure=structure
    )
    DBSession.add(project2)
    DBSession.commit()

    assets_task = Task(name="Assets", project=project)
    characters_task = Task(name="Characters", parent=assets_task)
    props_task = Task(name="Props", parent=assets_task)
    environments_task = Task(name="Environments", parent=assets_task)

    sequences_task = Task(name="Sequences", project=project)

    # Asset Types
    char_type = Type(name="Character", code="Char", target_entity_type="Asset")
    prop_type = Type(name="Prop", code="Prop", target_entity_type="Asset")
    exterior_type = Type(name="Exterior", code="Exterior", target_entity_type="Asset")
    interior_type = Type(name="Interior", code="Interior", target_entity_type="Asset")

    # Task Types
    model_type = Type(name="Model", code="Model", target_entity_type="Task")
    look_dev_type = Type(
        name="Look Development", code="LookDev", target_entity_type="Task"
    )
    rig_type = Type(name="Rig", code="Rig", target_entity_type="Task")
    layout_type = Type(name="Layout", code="Layout", target_entity_type="Task")

    anim_type = Type(name="Animation", code="Animation", target_entity_type="Task")
    camera_type = Type(name="Camera", code="Camera", target_entity_type="Task")
    plate_type = Type(name="Plate", code="Plate", target_entity_type="Task")
    fx_type = Type(name="FX", code="FX", target_entity_type="Task")
    lighting_type = Type(name="Lighting", code="Lighting", target_entity_type="Task")
    comp_type = Type(name="Comp", code="Comp", target_entity_type="Task")
    DBSession.add_all(
        [
            char_type,
            prop_type,
            exterior_type,
            interior_type,
            model_type,
            look_dev_type,
            rig_type,
            layout_type,
            anim_type,
            camera_type,
            plate_type,
            fx_type,
            lighting_type,
            comp_type,
        ]
    )
    DBSession.commit()

    # char1
    char1 = Asset(name="Char1", code="Char1", parent=characters_task, type=char_type)
    model = Task(name="Model", type=model_type, parent=char1)
    look_dev_task = Task(name="LookDev", type=look_dev_type, parent=char1)
    rig = Task(name="Rig", type=rig_type, parent=char1)
    DBSession.add_all([char1, model, look_dev_task, rig])
    DBSession.commit()

    model_v1 = Version(task=model, take_name="Main", version_number=1)
    model_v2 = Version(task=model, take_name="Main", version_number=2)
    model_v3 = Version(task=model, take_name="Main", version_number=3)
    look_dev_v1 = Version(task=look_dev_task, take_name="Main", version_number=1)
    look_dev_v1.inputs.append(model_v1)
    look_dev_v2 = Version(task=look_dev_task, take_name="Main", version_number=2)
    look_dev_v2.inputs.append(model_v2)
    look_dev_v3 = Version(task=look_dev_task, take_name="Main", version_number=3)
    look_dev_v3.inputs.append(model_v3)
    rig_v1 = Version(task=rig, take_name="Main", version_number=1)
    rig_v1.inputs.append(model_v1)
    rig_v2 = Version(task=rig, take_name="Main", version_number=2)
    rig_v2.inputs.append(model_v2)
    rig_v3 = Version(task=rig, take_name="Main", version_number=3)
    rig_v3.inputs.append(model_v3)
    DBSession.add_all([model_v1, model_v2, model_v3, look_dev_v1, look_dev_v2, look_dev_v3])
    DBSession.commit()

    # char2
    char2 = Asset(name="Char2", code="Char2", parent=characters_task, type=char_type)
    model = Task(name="Model", type=model_type, parent=char2)
    look_dev_task = Task(name="LookDev", type=look_dev_type, parent=char2)
    rig = Task(name="Rig", type=rig_type, parent=char2)
    DBSession.add_all([char2, model, look_dev_task, rig])
    DBSession.commit()

    # prop1
    prop1 = Asset(name="Prop2", code="Prop2", parent=props_task, type=prop_type)
    model = Task(name="Model", type=model_type, parent=prop1)
    look_dev_task = Task(name="LookDev", type=look_dev_type, parent=prop1)
    DBSession.add_all([prop1, model, look_dev_task])
    DBSession.commit()

    # prop2
    prop2 = Asset(name="Prop2", code="Prop2", parent=props_task, type=prop_type)
    model = Task(name="Model", type=model_type, parent=prop2)
    look_dev_task = Task(name="LookDev", type=look_dev_type, parent=prop2)
    DBSession.add_all([prop2, model, look_dev_task])
    DBSession.commit()

    # environments
    # env1
    env1 = Asset(name="Env1", code="Env1", type=exterior_type, parent=environments_task)
    layout_task = Task(name="Layout", type=layout_type, parent=env1)
    props_task = Task(name="Props", parent=env1)
    yapi1_asset = Asset(name="Yapi1", code="Yapi1", type=prop_type, parent=props_task)
    model_task = Task(name="Model", type=model_type, parent=yapi1_asset)
    look_dev_task = Task(name="LookDev", type=look_dev_type, parent=yapi1_asset)

    DBSession.add_all(
        [env1, layout_task, props_task, yapi1_asset, model_task, look_dev_task]
    )
    DBSession.commit()

    # env2
    env2 = Asset(name="Env2", code="Env2", type=exterior_type, parent=environments_task)
    layout_task = Task(name="Layout", type=layout_type, parent=env2)
    props_task = Task(name="Props", parent=env2)
    yapi1_asset = Asset(name="Yapi2", code="Yapi2", type=prop_type, parent=props_task)
    model_task = Task(name="Model", type=model_type, parent=yapi1_asset)
    look_dev_task = Task(name="LookDev", type=look_dev_type, parent=yapi1_asset)

    DBSession.add_all(
        [env2, layout_task, props_task, yapi1_asset, model_task, look_dev_task]
    )
    DBSession.commit()

    # Add Assets Task to the second project
    assets_task2 = Task(name="Assets", project=project2)
    environments_task2 = Task(name="Environments", parent=assets_task2)
    DBSession.add_all([assets_task2, environments_task2])
    DBSession.commit()

    # sequences and shots
    seq1 = Sequence(name="Seq1", code="Seq1", parent=sequences_task)
    edit_task = Task(name="Edit", parent=seq1)
    shots_task = Task(name="Shots", parent=seq1)

    DBSession.add_all([seq1, edit_task, shots_task])
    DBSession.commit()

    # shot1
    shot1 = Shot(
        name="Seq001_001_0010",
        code="Seq001_001_0010",
        sequences=[seq1],
        parent=shots_task,
    )

    anim_task = Task(name="Anim", type=anim_type, parent=shot1)
    camera_task = Task(name="Camera", type=camera_type, parent=shot1)
    plate_task = Task(name="Plate", type=plate_type, parent=shot1)
    fx_task = Task(name="FX", type=fx_type, parent=shot1)
    lighting_task = Task(name="Lighting", type=lighting_type, parent=shot1)
    comp_task = Task(name="Comp", type=comp_type, parent=shot1)

    DBSession.add_all(
        [shot1, anim_task, camera_task, plate_task, fx_task, lighting_task, comp_task]
    )
    DBSession.commit()

    # shot2
    shot2 = Shot(
        name="Seq001_001_0020",
        code="Seq001_001_0020",
        sequences=[seq1],
        parent=shots_task,
    )

    anim_task = Task(name="Anim", type=anim_type, parent=shot2)
    camera_task = Task(name="Camera", type=camera_type, parent=shot2)
    plate_task = Task(name="Plate", type=plate_type, parent=shot2)
    fx_task = Task(name="FX", type=fx_type, parent=shot2)
    lighting_task = Task(name="Lighting", type=lighting_type, parent=shot2)
    comp_task = Task(name="Comp", type=comp_type, parent=shot2)

    DBSession.add_all(
        [shot2, anim_task, camera_task, plate_task, fx_task, lighting_task, comp_task]
    )
    DBSession.commit()

    # shot3
    shot3 = Shot(
        name="Seq001_001_0030",
        code="Seq001_001_0030",
        sequences=[seq1],
        parent=shots_task,
    )

    anim_task = Task(name="Anim", type=anim_type, parent=shot3)
    camera_task = Task(name="Camera", type=camera_type, parent=shot3)
    plate_task = Task(name="Plate", type=plate_type, parent=shot3)
    fx_task = Task(name="FX", type=fx_type, parent=shot3)
    lighting_task = Task(name="Lighting", type=lighting_type, parent=shot3)
    comp_task = Task(name="Comp", type=comp_type, parent=shot3)

    DBSession.add_all(
        [shot3, anim_task, camera_task, plate_task, fx_task, lighting_task, comp_task]
    )
    DBSession.commit()

    # Seq2
    # sequences and shots
    seq2 = Sequence(name="Seq2", code="Seq2", parent=sequences_task)
    edit_task = Task(name="Edit", parent=seq2)
    shots_task = Task(name="Shots", parent=seq2)

    DBSession.add_all([seq2, edit_task, shots_task])
    DBSession.commit()

    # shot1
    shot1 = Shot(
        name="Seq002_001_0010",
        code="Seq002_001_0010",
        sequences=[seq2],
        parent=shots_task,
    )

    anim_task = Task(name="Anim", type=anim_type, parent=shot1)
    camera_task = Task(name="Camera", type=camera_type, parent=shot1)
    plate_task = Task(name="Plate", type=plate_type, parent=shot1)
    fx_task = Task(name="FX", type=fx_type, parent=shot1)
    lighting_task = Task(name="Lighting", type=lighting_type, parent=shot1)
    comp_task = Task(name="Comp", type=comp_type, parent=shot1)

    DBSession.add_all(
        [shot1, anim_task, camera_task, plate_task, fx_task, lighting_task, comp_task]
    )
    DBSession.commit()

    # shot2
    shot2 = Shot(
        name="Seq002_001_0020",
        code="Seq002_001_0020",
        sequences=[seq2],
        parent=shots_task,
    )

    anim_task = Task(name="Anim", type=anim_type, parent=shot2)
    camera_task = Task(name="Camera", type=camera_type, parent=shot2)
    plate_task = Task(name="Plate", type=plate_type, parent=shot2)
    fx_task = Task(name="FX", type=fx_type, parent=shot2)
    lighting_task = Task(name="Lighting", type=lighting_type, parent=shot2)
    comp_task = Task(name="Comp", type=comp_type, parent=shot2)

    DBSession.add_all(
        [shot2, anim_task, camera_task, plate_task, fx_task, lighting_task, comp_task]
    )
    DBSession.commit()

    # shot3
    shot3 = Shot(
        name="Seq002_001_0030",
        code="Seq002_001_0030",
        sequences=[seq2],
        parent=shots_task,
    )

    anim_task = Task(name="Anim", type=anim_type, parent=shot3)
    camera_task = Task(name="Camera", type=camera_type, parent=shot3)
    plate_task = Task(name="Plate", type=plate_type, parent=shot3)
    fx_task = Task(name="FX", type=fx_type, parent=shot3)
    lighting_task = Task(name="Lighting", type=lighting_type, parent=shot3)
    comp_task = Task(name="Comp", type=comp_type, parent=shot3)

    DBSession.add_all(
        [shot3, anim_task, camera_task, plate_task, fx_task, lighting_task, comp_task]
    )
    DBSession.commit()

    yield project


@pytest.fixture(scope="function")
def ldap_server():
    """creates a mock ldap server for tests"""
    global __here__

    # set some default ldap settings
    from anima import defaults

    defaults.enable_ldap_authentication = True
    defaults.ldap_server_address = "localhost"
    defaults.ldap_base_dn = "DC=animagpu,DC=local"

    # create mapping from LDAP groups to Stalker Groups
    defaults.ldap_user_group_map = {
        "Administrators": "admins",
        "Users": "Normal Users",
        "GPU Users": "Normal Users",
        "GPU Users Admin": "Power Users",
    }

    from ldap3 import Server, Connection, MOCK_SYNC

    test_ldap_server_info_path = os.path.join(__here__, "utils/data", "LDAP_server_info.json")
    test_ldap_server_schema_path = os.path.join(
        __here__, "utils/data", "LDAP_server_schema.json"
    )
    test_ldap_server_entries_path = os.path.join(
        __here__, "utils/data", "LDAP_server_entries.json"
    )

    # Mock Server with example data
    class MockServer(Server):
        def __init__(self, *args, **kwargs):
            logger.debug("Initializing the Mock Server!")
            super(MockServer, self).__init__(*args, **kwargs)

            # load the data
            logger.debug("Loading mock server data")
            self.from_definition(
                "fake_server", test_ldap_server_info_path, test_ldap_server_schema_path
            )

    # Mock the Connection class to always use MOCK_SYNC as strategy
    # and fill it with fake data
    class MockConnection(Connection):
        def __init__(self, *args, **kwargs):
            logger.debug("Initializing the Mock Connection!")
            kwargs["client_strategy"] = MOCK_SYNC
            super(MockConnection, self).__init__(*args, **kwargs)

            # load the mock data
            logger.debug("Loading mock connection data")
            logger.debug(
                "test_ldap_server_entries_path: %s" % test_ldap_server_entries_path
            )
            self.strategy.entries_from_json(test_ldap_server_entries_path)

            # load a fake user for Simple binding
            logger.debug("Loading a fake user for Simple binding")
            self.strategy.add_entry(
                defaults.ldap_base_dn,
                {
                    "cn": "admin",
                    "codePage": 0,
                    "displayName": "admin",
                    "distinguishedName": "CN=admin,OU=GPU Users Admin,DC=animagpu,DC=local",
                    "givenName": "admin",
                    "instanceType": 4,
                    "memberOf": ["CN=GPU Users Admin,CN=Users,DC=animagpu,DC=local"],
                    "name": "admin",
                    "objectCategory": "CN=Person,CN=Schema,CN=Configuration,DC=animagpu,DC=local",
                    # "objectCategory": "CN=Person,CN=Schema,CN=Configuration,%s" % defaults.ldap_base_dn,
                    "objectClass": ["top", "person", "organizationalPerson", "user"],
                    "objectGUID": "{9d96ef4a-14e7-4a77-b5b1-97b2fa239f9f}",
                    "objectSid": "S-1-5-21-2227021422-3894238547-674366654-1131",
                    "primaryGroupID": 513,
                    "revision": 0,
                    "sAMAccountName": "admin",
                    "sAMAccountType": 805306368,
                    "sn": "admin",
                    "uSNChanged": 423892,
                    "uSNCreated": 314308,
                    "userAccountControl": 66048,
                    "userPassword": "password",
                    "userPrincipalName": "admin@animagpu.local",
                },
            )

        def bind(self, *args, **kwargs):
            """mock the bind return value"""
            super(MockConnection, self).bind(*args, **kwargs)
            # always return True if the user is "pipeline"
            allowed_users = [
                "pipeline",
                "CN=Pipeline,CN=Users,DC=animagpu,DC=local",
                "CN=admin,OU=GPU Users Admin,DC=animagpu,DC=local",
            ]
            if self.user in allowed_users and self.password == "password":
                return True
            return False

    logger.debug("Replacing original ldap3.Server class")
    import ldap3

    orig_server_class = ldap3.Server
    ldap3.Server = MockServer
    logger.debug("ldap3.Server: %s" % ldap3.Server)

    logger.debug("Replacing original ldap3.Connection class")
    orig_connection_class = ldap3.Connection
    ldap3.Connection = MockConnection
    logger.debug("ldap3.Connection: %s" % ldap3.Connection)

    yield MockServer, MockConnection

    # restore the class
    logger.debug("Restoring original ldap3.Server class")
    ldap3.Server = orig_server_class
    logger.debug("ldap3.Server: %s" % ldap3.Server)
    logger.debug("Restoring original ldap3.Connection class")
    ldap3.Connection = orig_connection_class
    logger.debug("ldap3.Connection: %s" % ldap3.Connection)


@pytest.fixture(scope="function")
def prepare_publishers():
    """clean up test
    """
    # Yield nothing
    yield
    # clean up publishers dictionary
    clear_publishers()


@pytest.fixture(scope="function")
def prepare_recent_file_cache_path():
    """Setup a themporary recent file cache file."""
    from anima import defaults
    defaults.local_cache_folder = tempfile.gettempdir()
    yield
    from anima.recent import RecentFileManager
    os.remove(RecentFileManager.cache_file_full_path())


def create_version(task, take_name):
    """A helper method for creating a new version.

    :param task: the task
    :param take_name: the take_name name
    :return: the version
    """
    from stalker import Version
    from stalker.db.session import DBSession
    v = Version(task=task, take_name=take_name)
    DBSession.add(v)
    DBSession.commit()
    return v


@pytest.fixture(scope="module")
def repr_test_setup():
    """Repreentation test setup."""
    # -----------------------------------------------------------------
    # start of the setUp
    # create the environment variable and point it to a temp directory
    from stalker import db
    database_url = "sqlite:///:memory:"
    db.setup({'sqlalchemy.url': database_url})
    db.init()

    fixture_data = dict()
    fixture_data["temp_repo_path"] = tempfile.mkdtemp()

    from stalker import User
    fixture_data["user1"] = User(
        name='User 1',
        login='user1',
        email='user1@users.com',
        password='12345'
    )

    from stalker import Repository
    fixture_data["repo1"] = Repository(
        name='Test Project Repository',
        code="TP",
        linux_path=fixture_data["temp_repo_path"],
        windows_path=fixture_data["temp_repo_path"],
        osx_path=fixture_data["temp_repo_path"]
    )

    from stalker import Status
    fixture_data["status_new"] = Status.query.filter_by(code='NEW').first()
    fixture_data["status_wip"] = Status.query.filter_by(code='WIP').first()
    fixture_data["status_comp"] = Status.query.filter_by(code='CMPL').first()

    from stalker import FilenameTemplate
    fixture_data["task_template"] = FilenameTemplate(
        name='Task Template',
        target_entity_type='Task',
        path='{{project.code}}/'
             '{%- for parent_task in parent_tasks -%}'
             '{{parent_task.nice_name}}/'
             '{%- endfor -%}',
        filename='{{version.nice_name}}'
                 '_v{{"%03d"|format(version.version_number)}}',
    )

    from stalker import Structure
    fixture_data["structure"] = Structure(
        name='Project Struture',
        templates=[fixture_data["task_template"]]
    )

    from stalker import StatusList
    fixture_data["project_status_list"] = StatusList.query.filter_by(target_entity_type='Project').first()

    from stalker import ImageFormat
    fixture_data["image_format"] = ImageFormat(
        name='HD 1080',
        width=1920,
        height=1080,
        pixel_aspect=1.0
    )

    # create a test project
    from stalker import Project
    fixture_data["project"] = Project(
        name='Test Project',
        code='TP',
        repository=fixture_data["repo1"],
        status_list=fixture_data["project_status_list"],
        structure=fixture_data["structure"],
        image_format=fixture_data["image_format"]
    )

    fixture_data["task_status_list"] = StatusList.query.filter_by(target_entity_type='Task').first()

    from stalker import Type
    fixture_data["character_type"] = Type(
        name='Character',
        code='CHAR',
        target_entity_type='Asset'
    )

    from stalker import Task
    # create a test series of root task
    fixture_data["task1"] = Task(
        name='Test Task 1',
        project=fixture_data["project"]
    )
    fixture_data["task2"] = Task(
        name='Test Task 2',
        project=fixture_data["project"]
    )

    # commit everything
    from stalker.db.session import DBSession
    DBSession.add_all([
        fixture_data["repo1"], fixture_data["status_new"],
        fixture_data["status_wip"], fixture_data["status_comp"],
        fixture_data["project_status_list"], fixture_data["project"],
        fixture_data["task_status_list"],
        fixture_data["task1"], fixture_data["task2"],
        fixture_data["task_template"]
    ])
    DBSession.commit()

    fixture_data["version1"] = create_version(fixture_data["task1"], 'Main')
    fixture_data["version2"] = create_version(fixture_data["task1"], 'Main')
    fixture_data["version3"] = create_version(fixture_data["task1"], 'Main')

    # create other reprs
    # BBOX
    fixture_data["version4"] = create_version(fixture_data["task1"], 'Main@BBox')
    fixture_data["version5"] = create_version(fixture_data["task1"], 'Main@BBox')
    fixture_data["version5"].is_published = True
    DBSession.commit()

    # ASS
    fixture_data["version6"] = create_version(fixture_data["task1"], 'Main@ASS')
    fixture_data["version7"] = create_version(fixture_data["task1"], 'Main@ASS')
    fixture_data["version7"].is_published = True
    DBSession.commit()

    # GPU
    fixture_data["version8"] = create_version(fixture_data["task1"], 'Main@GPU')
    fixture_data["version9"] = create_version(fixture_data["task1"], 'Main@GPU')

    # Non default take name
    fixture_data["version10"] = create_version(fixture_data["task1"], 'alt1')
    fixture_data["version11"] = create_version(fixture_data["task1"], 'alt1')

    # Hires
    fixture_data["version12"] = create_version(fixture_data["task1"], 'alt1@Hires')
    fixture_data["version13"] = create_version(fixture_data["task1"], 'alt1@Hires')

    # Midres
    fixture_data["version14"] = create_version(fixture_data["task1"], 'alt1@Midres')
    fixture_data["version15"] = create_version(fixture_data["task1"], 'alt1@Midres')

    # Lores
    fixture_data["version16"] = create_version(fixture_data["task1"], 'alt1@Lores')
    fixture_data["version17"] = create_version(fixture_data["task1"], 'alt1@Lores')
    fixture_data["version17"].is_published = True

    # No Repr
    fixture_data["version18"] = create_version(fixture_data["task1"], 'NoRepr')
    fixture_data["version19"] = create_version(fixture_data["task1"], 'NoRepr')
    DBSession.commit()

    # create a buffer for extra created files, which are to be removed
    fixture_data["remove_these_files_buffer"] = []

    yield fixture_data

    # Clean up
    # set the db.session to None
    from stalker.db.session import DBSession
    DBSession.remove()

    # delete the temp folder
    shutil.rmtree(fixture_data["temp_repo_path"], ignore_errors=True)

    for f in fixture_data["remove_these_files_buffer"]:
        if os.path.isfile(f):
            os.remove(f)
        elif os.path.isdir(f):
            shutil.rmtree(f, True)
