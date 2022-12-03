# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(scope="function")
def prepare_asset_storage():
    """Create a reset the AssetStorage."""
    from anima.ui.dialogs.asset_migration_tool_dialog import AssetStorage
    AssetStorage.reset_storage()