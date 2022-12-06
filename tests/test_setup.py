# -*- coding: utf-8 -*-


def test_database_is_correctly_created(create_test_db):
    """testing if the fixture is working properly"""
    from stalker.db.session import DBSession

    assert str(DBSession.connection().engine.dialect.name) == "sqlite"
