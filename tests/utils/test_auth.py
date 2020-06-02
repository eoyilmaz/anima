# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Anima Istanbul
#
# This module is part of anima-tools and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


def test_authenticate_with_stalker(create_db):
    """tests authentication with stalker
    """
    from anima.utils import stalker_authenticate
    result = stalker_authenticate(login='admin', password='admin')
    assert result is True

    result = stalker_authenticate(login='non existing user', password='random_password')
    assert result is False


def test_authenticate_with_stalker_called_only_when_enable_ldap_authentication_is_false(ldap_server, create_db):
    """tests authentication with stalker only called when enable_ldap_authentication is false
    """
    from anima.utils import stalker_authenticate
    result = stalker_authenticate(login='admin', password='admin')
    assert result is True

    result = stalker_authenticate(login='non existing user', password='random_password')
    assert result is False


def test_authenticate_with_ldap(ldap_server, create_db):
    """tests authentication with ldap
    """
    from anima.utils import ldap_authenticate

    login = "CN=admin,OU=GPU Users Admin,DC=animagpu,DC=local"
    password = 'password'

    result = ldap_authenticate(login=login, password=password)
    assert result is True

    login = "CN=Pipeline,CN=Users,DC=animagpu,DC=local"
    password = 'password'

    result = ldap_authenticate(login=login, password=password)
    assert result is True


def test_get_user_name_from_ldap(ldap_server, create_db):
    """testing if getting user name from ldap is working properly
    """
    from anima import defaults
    login = 'pipeline'
    password = 'password'

    from ldap3 import Server, Connection  # These are mocked to use MOCK_SYNC
    server = Server(defaults.ldap_server_address)
    conn = Connection(server, login, password)
    conn.bind()

    from anima.utils import get_user_name_from_ldap
    result = get_user_name_from_ldap(conn, defaults.ldap_base_dn, login)
    assert result == 'Pipeline'


def test_get_user_groups_from_ldap(ldap_server, create_db):
    """testing if getting user groups from ldap is working properly
    """
    login = 'pipeline'
    password = 'password'
    from anima import defaults

    assert defaults.ldap_base_dn != ''

    from ldap3 import Server, Connection  # These are mocked to use MOCK_SYNC
    server = Server(defaults.ldap_server_address)
    conn = Connection(server, login, password)
    conn.bind()

    from anima.utils import get_user_groups_from_ldap
    result = get_user_groups_from_ldap(conn, defaults.ldap_base_dn, login)
    assert result == [u'GPU Users Admin', u'Administrators']


def test_create_user_with_ldap_info_create_proper_stalker_user(ldap_server, create_db):
    """testing if create_user_with_ldap_info will create a proper Stalker user
    """
    login = 'pipeline'
    password = 'password'
    from anima import defaults

    assert defaults.ldap_base_dn != ''

    from ldap3 import Server, Connection  # These are mocked to use MOCK_SYNC
    server = Server(defaults.ldap_server_address)
    conn = Connection(server, login, password)
    conn.bind()

    from anima.utils import create_user_with_ldap_info
    new_user = create_user_with_ldap_info(conn, defaults.ldap_base_dn, login, password)

    from stalker import User
    assert isinstance(new_user, User)
    assert new_user.login == login
    assert new_user.password != password  # this should be mangled
    assert new_user.email == 'pipeline@animagpu.local'  # default email from base_dn
    assert new_user.name == 'Pipeline'  # from LDAP server

    # also do a query from Stalker DB
    new_user_from_db = User.query.filter(User.login==login).first()
    assert new_user_from_db == new_user


def test_create_user_with_ldap_info_create_proper_stalker_user_with_groups(ldap_server, create_db):
    """testing if create_user_with_ldap_info will create a proper Stalker user
    """
    login = 'pipeline'
    password = 'password'
    from anima import defaults
    assert defaults.ldap_base_dn != ''

    # create the Stalker Groups first
    stalker_group_names = [
        'admins',
        'Normal Users',
        'Power Users'
    ]
    from stalker.db.session import DBSession
    from stalker import Group
    for stalker_group_name in stalker_group_names:
        if not Group.query.filter(Group.name==stalker_group_name).first():
            new_group = Group(name=stalker_group_name)
            DBSession.add(new_group)
    DBSession.commit()

    # now get the user from LDAP Server
    from ldap3 import Server, Connection  # These are mocked to use MOCK_SYNC
    server = Server(defaults.ldap_server_address)
    conn = Connection(server, login, password)
    conn.bind()

    from anima.utils import create_user_with_ldap_info
    new_user = create_user_with_ldap_info(conn, defaults.ldap_base_dn, login, password)

    # check user groups
    assert len(new_user.groups) > 0
    assert len(new_user.groups) == 2
    assert new_user.groups[0].name == 'admins'
    assert new_user.groups[1].name == 'Power Users'
    assert new_user.groups[0].name in stalker_group_names
    assert new_user.groups[1].name in stalker_group_names


def test_authenticate_with_stalker_and_ldap_will_always_authenticate_with_ldap(ldap_server, create_db):
    """testing if the anima.utils.authenticate() function will authenticate
    fail even if the user exist in stalker when the enable_ldap_authentication
    is True
    """
    login = 'admin'
    password = 'admin'
    from anima.utils import authenticate
    result = authenticate(login, password)
    assert result is False


def test_authenticate_with_stalker_and_ldap_authenticates_an_existing_ldap_user(ldap_server, create_db, monkeypatch):
    """testing if the anima.utils.authenticate() function will authenticate a
    ldap user without a problem
    """
    from ldap3.extend import StandardExtendedOperations

    def mock_return(*arg, **kwargs):
        return "pipeline"

    monkeypatch.setattr(StandardExtendedOperations, "who_am_i", mock_return)

    login = 'pipeline'
    password = 'password'
    from anima.utils import authenticate
    result = authenticate(login, password)
    assert result is True


def test_authenticate_with_stalker_and_ldap_authenticates_a_existing_ldap_user_creates_a_stalker_user(ldap_server, create_db, monkeypatch):
    """testing if the anima.utils.authenticate() function will authenticate a
    non-existing ldap user properly
    """
    from ldap3.extend import StandardExtendedOperations

    def mock_return(*arg, **kwargs):
        return "pipeline"

    monkeypatch.setattr(StandardExtendedOperations, "who_am_i", mock_return)

    login = 'pipeline'
    password = 'password'
    from anima.utils import authenticate
    result = authenticate(login, password)
    assert result is True
    # check the user in Stalker DB
    from stalker import User
    pipeline_user = User.query.filter(User.login==login).first()
    assert pipeline_user is not None


def test_authenticate_updates_user_password_if_stalker_fails_but_ldap_successes(ldap_server, create_db, monkeypatch):
    """testing if the anima.utils.authenticate() will update the user password
    if stalker fails but ldap doesn't fail and the user exists
    """
    from ldap3.extend import StandardExtendedOperations

    def mock_return(*arg, **kwargs):
        return "pipeline"

    monkeypatch.setattr(StandardExtendedOperations, "who_am_i", mock_return)

    # This is not working with mock server
    login = 'pipeline'
    ldap_password = 'password'
    stalker_password = 'different_password'
    # create a user in Stalker with a different password
    from stalker import User
    from stalker.db.session import DBSession
    new_user = User(login=login, password=stalker_password, email='pipeline@somedifferent.com', name='Pipeline')
    DBSession.add(new_user)
    DBSession.commit()
    assert new_user.check_password(ldap_password) is False
    assert new_user.check_password(stalker_password) is True

    # now authenticate with the new password
    from anima.utils import authenticate
    result = authenticate(login, ldap_password)
    # result should be True
    assert result is True
    # and the password should be updated
    pipeline_user = User.query.filter(User.login==login).first()
    assert pipeline_user is not None
    assert new_user.check_password(ldap_password) is True
    assert new_user.check_password(stalker_password) is False
