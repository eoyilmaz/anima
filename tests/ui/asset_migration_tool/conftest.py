# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(scope="function")
def prepare_asset_storage():
    """Create a reset the EntityStorage."""
    from anima.ui.dialogs.asset_migration_tool_dialog import EntityStorage
    EntityStorage.reset_storage()
