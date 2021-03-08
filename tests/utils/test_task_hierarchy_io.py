# -*- coding: utf-8 -*-
import os

__here__ = os.path.dirname(__file__)


def test_creating_test_data(create_db, create_project):
    """testing if the test project is created correctly
    """
    # now we should have some projects
    project = create_project
    from stalker import Project
    assert isinstance(project, Project)

    from stalker import Task
    all_tasks = Task.query.all()
    assert len(all_tasks) == 79


def test_stalker_entity_encoder_is_working_properly(create_db, create_project):
    """testing if JSON Encoder will export data to JSON properly
    """
    from stalker import Task
    project = create_project
    assets_task = Task.query\
        .filter(Task.project==project).filter(Task.name=='Assets').first()
    assert isinstance(assets_task, Task)

    import json
    from anima.utils import task_hierarchy_io
    data = json.dumps(assets_task, cls=task_hierarchy_io.StalkerEntityEncoder,
                      check_circular=False, indent=4)

    global __here__

    with open(os.path.join(__here__, "data", "test_template2.json")) as f:
        expected_data = f.read()

    assert data == expected_data


def test_stalker_entity_decoder_will_create_new_data(create_db, create_empty_project):
    """testing if JSON decoder will create new data
    """
    from stalker import Task
    project = create_empty_project

    import json
    from anima.utils import task_hierarchy_io

    global __here__
    file_path = os.path.join(__here__, "data", "test_template3.json")

    with open(file_path) as f:
        data = json.load(f)

    decoder = \
        task_hierarchy_io.StalkerEntityDecoder(
            project=project
        )
    loaded_entity = decoder.loads(data)

    from stalker.db.session import DBSession
    DBSession.add(loaded_entity)
    DBSession.commit()

    # now there should be only one Assets task
    from stalker import Task
    assets_task = Task.query.filter(Task.name=='Assets').first()

    assert isinstance(assets_task, Task)
    assert assets_task.name == 'Assets'


def test_stalker_entity_decoder_will_not_create_existing_tasks(create_db, create_empty_project):
    """testing if JSON decoder will not recreate existing data
    """
    from stalker import Task
    project = create_empty_project

    import json
    from anima.utils import task_hierarchy_io

    global __here__
    file_path = os.path.join(__here__, "data", "test_template3.json")

    with open(file_path) as f:
        data = json.load(f)

    decoder = \
        task_hierarchy_io.StalkerEntityDecoder(
            project=project
        )
    loaded_entity = decoder.loads(data)

    from stalker.db.session import DBSession
    DBSession.add(loaded_entity)
    DBSession.commit()

    # now there should be only one Assets task
    from stalker import Task
    assets_tasks = Task.query.filter(Task.name=='Assets').all()

    assert len(assets_tasks) == 1


def test_stalker_entity_decoder_will_not_create_existing_child_tasks(create_db, create_empty_project):
    """testing if JSON decoder will not recreate existing child tasks
    """
    from stalker import Task
    project = create_empty_project

    import json
    from anima.utils import task_hierarchy_io

    global __here__
    file_path = os.path.join(__here__, "data", "test_template4.json")

    with open(file_path) as f:
        data = json.load(f)

    # create backup of the data
    import copy
    data_backup = copy.deepcopy(data)

    decoder = \
        task_hierarchy_io.StalkerEntityDecoder(
            project=project
        )
    loaded_entity = decoder.loads(data)

    from stalker.db.session import DBSession
    DBSession.add(loaded_entity)
    DBSession.commit()

    # check if they are loaded normally
    from stalker import Asset, Task
    ananas_asset = Asset.query\
        .filter(Asset.project==project)\
        .filter(Asset.name=='Ananas')\
        .first()
    assert ananas_asset is not None
    assert isinstance(ananas_asset, Asset)

    ananas_look_dev = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='lookDev')\
        .first()
    assert ananas_look_dev is not None
    assert isinstance(ananas_look_dev, Task)

    ananas_model = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='model')\
        .first()
    assert ananas_model is not None
    assert isinstance(ananas_model, Task)

    # now load it again
    data = copy.deepcopy(data_backup)

    loaded_entity = decoder.loads(data)
    DBSession.add(loaded_entity)
    DBSession.commit()

    # now there should be only one Assets task
    from stalker import Task
    assets_tasks = Task.query.filter(Task.name=='Assets').all()
    assert len(assets_tasks) == 1

    # check if there is only one Ananas asset
    ananas_assets = Asset.query\
        .filter(Asset.project==project)\
        .filter(Asset.name=='Ananas')\
        .all()
    assert len(ananas_assets) == 1

    # check if there is only one LookDev task under the Ananas asset
    ananas_asset = ananas_assets[0]
    ananas_look_devs = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='lookDev')\
        .all()
    assert len(ananas_look_devs) == 1

    ananas_models = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='model')\
        .all()
    assert len(ananas_models) == 1


def test_stalker_entity_decoder_will_append_new_data(create_db, create_empty_project):
    """testing if JSON decoder will append new data on top of the existing one
    even when the JSON contains data about the already existing tasks
    """
    from stalker import Task
    project = create_empty_project

    import json
    from anima.utils import task_hierarchy_io

    global __here__
    file_path = os.path.join(__here__, "data", "test_template5.json")

    with open(file_path) as f:
        data = json.load(f)

    # create backup of the data
    import copy
    data_backup = copy.deepcopy(data)

    decoder = \
        task_hierarchy_io.StalkerEntityDecoder(
            project=project
        )
    loaded_entity = decoder.loads(data)

    from stalker.db.session import DBSession
    DBSession.add(loaded_entity)
    DBSession.commit()

    # check if they are loaded normally
    from stalker import Asset, Task
    ananas_asset = Asset.query\
        .filter(Asset.project==project)\
        .filter(Asset.name=='Ananas')\
        .first()
    assert ananas_asset is not None
    assert isinstance(ananas_asset, Asset)

    ananas_look_dev = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='lookDev')\
        .first()
    assert ananas_look_dev is not None
    assert isinstance(ananas_look_dev, Task)

    ananas_model = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='model')\
        .first()
    assert ananas_model is not None
    assert isinstance(ananas_model, Task)

    # now load it again
    data = copy.deepcopy(data_backup)
    loaded_entity = decoder.loads(data)
    DBSession.add(loaded_entity)
    DBSession.commit()

    # now there should be only one Assets task
    from stalker import Task
    assets_tasks = Task.query.filter(Task.name=='Assets').all()
    assert len(assets_tasks) == 1

    # check if there is only one Ananas asset
    ananas_assets = Asset.query\
        .filter(Asset.project==project)\
        .filter(Asset.name=='Ananas')\
        .all()
    assert len(ananas_assets) == 1

    # check if there is only one LookDev task under the Ananas asset
    ananas_asset = ananas_assets[0]
    ananas_look_devs = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='lookDev')\
        .all()
    assert len(ananas_look_devs) == 1

    ananas_models = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='model')\
        .all()
    assert len(ananas_models) == 1

    # check if there is a Peach asset
    peach_asset = Asset.query\
        .filter(Asset.project==project)\
        .filter(Asset.name=='Peach')\
        .first()
    assert peach_asset is not None
    assert isinstance(peach_asset, Asset)

    # check peach child tasks
    peach_model = Task.query\
        .filter(Task.parent==peach_asset)\
        .filter(Task.name=='model')\
        .first()

    assert peach_model is not None
    assert isinstance(peach_model, Task)

    peach_look_dev = Task.query\
        .filter(Task.parent==peach_asset)\
        .filter(Task.name=='lookDev')\
        .first()

    assert peach_look_dev is not None
    assert isinstance(peach_look_dev, Task)


def test_stalker_entity_decoder_will_create_versions(create_db, create_empty_project):
    """testing if JSON decoder will create new versions along with tasks
    """
    from stalker import Task
    project = create_empty_project

    import json
    from anima.utils import task_hierarchy_io

    global __here__
    file_path = os.path.join(__here__, "data", "test_template5.json")

    with open(file_path) as f:
        data = json.load(f)

    decoder = \
        task_hierarchy_io.StalkerEntityDecoder(
            project=project
        )
    loaded_entity = decoder.loads(data)

    from stalker.db.session import DBSession
    DBSession.add(loaded_entity)
    DBSession.commit()

    from stalker import Asset, Task
    ananas_asset = Asset.query\
        .filter(Asset.project==project)\
        .filter(Asset.name=='Ananas')\
        .first()

    ananas_look_dev = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='lookDev')\
        .first()

    # check versions are created normally
    assert len(ananas_look_dev.versions) == 1


def test_stalker_entity_decoder_will_not_recreate_versions(create_db, create_empty_project):
    """testing if JSON decoder will not recreate already created versions
    """
    from stalker import Task
    project = create_empty_project

    import json
    from anima.utils import task_hierarchy_io

    global __here__
    file_path = os.path.join(__here__, "data", "test_template5.json")

    with open(file_path) as f:
        data = json.load(f)

    import copy
    data_backup = copy.deepcopy(data)

    decoder = \
        task_hierarchy_io.StalkerEntityDecoder(
            project=project
        )
    loaded_entity = decoder.loads(data)

    from stalker.db.session import DBSession
    DBSession.add(loaded_entity)
    DBSession.commit()

    from stalker import Asset, Task
    ananas_assets = Asset.query\
        .filter(Asset.project==project)\
        .filter(Asset.name=='Ananas')\
        .all()
    assert len(ananas_assets) == 1
    ananas_asset = ananas_assets[0]

    ananas_look_devs = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='lookDev')\
        .all()
    assert len(ananas_look_devs) == 1
    ananas_look_dev = ananas_look_devs[0]

    assert len(ananas_look_dev.versions) == 1

    # load a couple times more
    # 1
    data = copy.deepcopy(data_backup)
    loaded_entity = decoder.loads(data)
    DBSession.add(loaded_entity)
    DBSession.commit()

    # 2)
    data = copy.deepcopy(data_backup)
    loaded_entity = decoder.loads(data)
    DBSession.add(loaded_entity)
    DBSession.commit()

    # 3
    data = copy.deepcopy(data_backup)
    loaded_entity = decoder.loads(data)
    DBSession.add(loaded_entity)
    DBSession.commit()

    # 4
    data = copy.deepcopy(data_backup)
    loaded_entity = decoder.loads(data)
    DBSession.add(loaded_entity)
    DBSession.commit()

    from stalker import Asset, Task
    ananas_assets = Asset.query\
        .filter(Asset.project==project)\
        .filter(Asset.name=='Ananas')\
        .all()
    assert len(ananas_assets) == 1
    ananas_asset = ananas_assets[0]

    ananas_look_devs = Task.query\
        .filter(Task.parent==ananas_asset)\
        .filter(Task.name=='lookDev')\
        .all()
    assert len(ananas_look_devs) == 1
    ananas_look_dev = ananas_look_devs[0]

    assert len(ananas_look_dev.versions) == 1
    assert ananas_look_dev.versions[0].version_number == 1


def test_stalker_entity_decoder_will_not_recreate_versions_2(create_db, create_empty_project):
    """testing if JSON decoder will not recreate already created versions when the versions data is not oredered to the
    version number
    """
    from stalker import Task
    project = create_empty_project

    import json
    from anima.utils import task_hierarchy_io

    global __here__
    file_path = os.path.join(__here__, "data", "test_template6.json")

    with open(file_path) as f:
        data = json.load(f)

    import copy
    data_backup = copy.deepcopy(data)

    decoder = \
        task_hierarchy_io.StalkerEntityDecoder(
            project=project
        )
    loaded_entity = decoder.loads(data)

    from stalker.db.session import DBSession
    DBSession.add(loaded_entity)
    DBSession.commit()

    from stalker import Asset, Task
    kutu_assets = Asset.query\
        .filter(Asset.project==project)\
        .filter(Asset.name=='Kutu')\
        .all()
    assert len(kutu_assets) == 1
    kutu_asset = kutu_assets[0]

    kutu_look_devs = Task.query\
        .filter(Task.parent==kutu_asset)\
        .filter(Task.name=='lookDev')\
        .all()
    assert len(kutu_look_devs) == 1
    kutu_look_dev = kutu_look_devs[0]

    assert len(kutu_look_dev.versions) == 9

    current_version = kutu_look_dev.versions[0]
    assert current_version.version_number == \
           int(current_version.filename.split("_v")[-1].split(".")[0])
    current_version = kutu_look_dev.versions[1]
    assert current_version.version_number == \
           int(current_version.filename.split("_v")[-1].split(".")[0])
    current_version = kutu_look_dev.versions[2]
    assert current_version.version_number == \
           int(current_version.filename.split("_v")[-1].split(".")[0])
    current_version = kutu_look_dev.versions[3]
    assert current_version.version_number == \
           int(current_version.filename.split("_v")[-1].split(".")[0])
    current_version = kutu_look_dev.versions[4]
    assert current_version.version_number == \
           int(current_version.filename.split("_v")[-1].split(".")[0])
    current_version = kutu_look_dev.versions[5]
    assert current_version.version_number == \
           int(current_version.filename.split("_v")[-1].split(".")[0])
    current_version = kutu_look_dev.versions[6]
    assert current_version.version_number == \
           int(current_version.filename.split("_v")[-1].split(".")[0])
    current_version = kutu_look_dev.versions[7]
    assert current_version.version_number == \
           int(current_version.filename.split("_v")[-1].split(".")[0])
    current_version = kutu_look_dev.versions[8]
    assert current_version.version_number == \
           int(current_version.filename.split("_v")[-1].split(".")[0])

    # load a couple times more
    # 1
    data = copy.deepcopy(data_backup)
    loaded_entity = decoder.loads(data)
    DBSession.add(loaded_entity)
    DBSession.commit()

    # 2)
    data = copy.deepcopy(data_backup)
    loaded_entity = decoder.loads(data)
    DBSession.add(loaded_entity)
    DBSession.commit()

    # 3
    data = copy.deepcopy(data_backup)
    loaded_entity = decoder.loads(data)
    DBSession.add(loaded_entity)
    DBSession.commit()

    # 4
    data = copy.deepcopy(data_backup)
    loaded_entity = decoder.loads(data)
    DBSession.add(loaded_entity)
    DBSession.commit()

    from stalker import Asset, Task
    kutu_assets = Asset.query\
        .filter(Asset.project==project)\
        .filter(Asset.name=='Kutu')\
        .all()
    assert len(kutu_assets) == 1
    kutu_asset = kutu_assets[0]

    kutu_look_devs = Task.query\
        .filter(Task.parent==kutu_asset)\
        .filter(Task.name=='lookDev')\
        .all()
    assert len(kutu_look_devs) == 1
    kutu_look_dev = kutu_look_devs[0]

    assert len(kutu_look_dev.versions) == 9
    assert kutu_look_dev.versions[-1].version_number == 8
