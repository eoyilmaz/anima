# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


import pytest


@pytest.fixture('session')
def test_data():
    """reads test data
    """
    # reads the test data as text
    import os
    here = os.path.dirname(__file__)
    test_data_file_path = os.path.join(here, 'data', 'test_template.json')

    import json
    with open(test_data_file_path) as f:
        test_data = json.load(f)

    yield test_data


@pytest.fixture('session')
def create_db():
    """creates a test database
    """
    import os
    os.environ.pop('STALKER_PATH')
    from stalker import db
    db.setup({'sqlalchemy.url': 'sqlite://'})
    db.init()


@pytest.fixture('session')
def create_project():
    """creates test data
    """
    from stalker import Repository, Project

    repo = Repository(
        name='Test Repository',
        windows_path='T:/',
        linux_path='/mnt/T/',
        osx_path='/Volumes/T/'
    )

    project = Project(
        name='Test Project',
        code='TP',
        repository=repo
    )

    yield project


def test_database_is_correctly_created(create_db):
    """testing if the fixture is working properly
    """
    from stalker.db.session import DBSession
    assert str(DBSession.connection().engine.dialect.name) == 'sqlite'
