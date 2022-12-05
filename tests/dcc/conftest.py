# -*- coding: utf-8 -*-

import pytest

from stalker import db
from stalker.db.session import DBSession


@pytest.fixture(scope="module")
def setup_dbsession():
    """Configure DBSession."""
    DBSession.remove()
    yield
    DBSession.remove()


@pytest.fixture(scope="function")
def create_test_db(setup_dbsession):
    """Create test DB."""
    db.setup({'sqlalchemy.url': 'sqlite:///:memory:'})
    db.init()
    yield
