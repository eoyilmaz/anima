# -*- coding: utf-8 -*-
from anima.ui.dialogs.asset_migration_tool_dialog import AssetStorage


def test_asset_storage_initialization():
    """Test asset storage initialization."""
    storage = AssetStorage()
    assert isinstance(storage, AssetStorage)


def test_asset_storage_add_entity_asset(
    create_db, create_project, prepare_asset_storage
):
    """Test AssetStorage.add_entity() with an Asset."""
    from stalker import Asset

    project = create_project
    char1 = (
        Asset.query.filter(Asset.project == project)
        .filter(Asset.name == "Char1")
        .first()
    )

    assert char1 is not None

    storage = AssetStorage()
    storage.add_entity(char1)

    assert char1 in storage.storage


def test_asset_storage_add_entity_task(
    create_db, create_project, prepare_asset_storage
):
    """Test AssetStorage.add_entity() with a Task."""
    from stalker import Asset, Task

    project = create_project
    char1 = (
        Asset.query.filter(Asset.project == project)
        .filter(Asset.name == "Char1")
        .first()
    )
    model = Task.query.filter(Task.parent == char1).filter(Task.name == "Model").first()

    assert model is not None

    storage = AssetStorage()
    storage.add_entity(model)

    assert char1 in storage.storage
    assert model in storage.storage[char1]


def test_asset_storage_add_entity_version(
    create_db, create_project, prepare_asset_storage
):
    """Test AssetStorage.add_entity() with a Version."""
    from stalker import Asset, Task, Version

    project = create_project
    char1 = (
        Asset.query.filter(Asset.project == project)
        .filter(Asset.name == "Char1")
        .first()
    )
    model = Task.query.filter(Task.parent == char1).filter(Task.name == "Model").first()
    assert model is not None
    v1 = model.versions[0]
    assert v1 is not None
    assert isinstance(v1, Version)

    storage = AssetStorage()
    storage.add_entity(v1)

    assert char1 in storage.storage
    assert model in storage.storage[char1]
    assert v1.take_name in storage.storage[char1][model]
    assert v1 == storage.storage[char1][model][v1.take_name]


def test_asset_storage_add_entities_assets(
    create_db, create_project, prepare_asset_storage
):
    """Test AssetStorage.add_entity() with a assets."""
    from stalker import Asset, Task, Version

    project = create_project
    char1 = (
        Asset.query.filter(Asset.project == project)
        .filter(Asset.name == "Char1")
        .first()
    )
    char2 = (
        Asset.query.filter(Asset.project == project)
        .filter(Asset.name == "Char2")
        .first()
    )
    assert char1 is not None
    assert char2 is not None

    storage = AssetStorage()
    storage.add_entities([char1, char2])

    assert char1 in storage.storage
    assert char2 in storage.storage


def test_asset_storage_remove_entity_asset(
    create_db, create_project, prepare_asset_storage
):
    """Test AssetStorage.remove_entity() with a Asset."""
    from stalker import Asset, Task, Version

    project = create_project
    char1 = (
        Asset.query.filter(Asset.project == project)
        .filter(Asset.name == "Char1")
        .first()
    )
    model = Task.query.filter(Task.parent == char1).filter(Task.name == "Model").first()
    assert model is not None
    v1 = model.versions[0]
    assert v1 is not None
    assert isinstance(v1, Version)

    storage = AssetStorage()
    storage.add_entity(v1)

    # Remove the asset
    storage.remove_entity(char1)
    # expect an empty dictionary
    assert char1 not in storage.storage


def test_asset_storage_remove_entity_task(
    create_db, create_project, prepare_asset_storage
):
    """Test AssetStorage.remove_entity() with a Task."""
    from stalker import Asset, Task, Version

    project = create_project
    char1 = (
        Asset.query.filter(Asset.project == project)
        .filter(Asset.name == "Char1")
        .first()
    )
    model = Task.query.filter(Task.parent == char1).filter(Task.name == "Model").first()
    assert model is not None
    v1 = model.versions[0]
    assert v1 is not None
    assert isinstance(v1, Version)

    storage = AssetStorage()
    storage.add_entity(v1)

    # Remove the task
    storage.remove_entity(model)
    # The char1 should still be there
    assert char1 in storage.storage
    # but not the model and version
    assert model not in storage.storage[char1]


def test_asset_storage_remove_entity_version(
    create_db, create_project, prepare_asset_storage
):
    """Test AssetStorage.remove_entity() with a Version."""
    from stalker import Asset, Task, Version

    project = create_project
    char1 = (
        Asset.query.filter(Asset.project == project)
        .filter(Asset.name == "Char1")
        .first()
    )
    model = Task.query.filter(Task.parent == char1).filter(Task.name == "Model").first()
    assert model is not None
    v1 = model.versions[0]
    assert v1 is not None
    assert isinstance(v1, Version)

    storage = AssetStorage()
    storage.add_entity(v1)

    # Remove the task
    storage.remove_entity(v1)
    # The char1 should still be there
    assert char1 in storage.storage
    # The model should be there too
    assert model in storage.storage[char1]
    # the take should not be there
    assert v1.take_name not in storage.storage[char1][model]


def test_asset_storage_is_in_storage_asset(
    create_db, create_project, prepare_asset_storage
):
    """Test AssetStorage.is_in_storage() with an Asset."""
    from stalker import Asset, Task, Version

    project = create_project
    char1 = (
        Asset.query.filter(Asset.project == project)
        .filter(Asset.name == "Char1")
        .first()
    )
    model = Task.query.filter(Task.parent == char1).filter(Task.name == "Model").first()
    assert model is not None
    v1 = model.versions[0]
    v2 = model.versions[1]
    v3 = model.versions[2]
    assert v1 is not None
    assert v2 is not None
    assert v3 is not None

    storage = AssetStorage()
    storage.add_entity(v1)

    assert storage.is_in_storage(char1) is True
    assert storage.is_in_storage(model) is True
    assert storage.is_in_storage(v1) is True
    assert storage.is_in_storage(v2) is False
    assert storage.is_in_storage(v3) is False
