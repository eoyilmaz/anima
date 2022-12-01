# -*- coding: utf-8 -*-
from anima.ui.dialogs.asset_migration_tool_dialog import AssetStorage


def test_asset_storage_initialization():
    """Test asset storage initialization."""
    storage = AssetStorage()
    assert isinstance(storage, AssetStorage)
