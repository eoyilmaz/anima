# -*- coding: utf-8 -*-
"""Tests related to the DCCBase class."""

import logging

import unittest
from stalker import (db, Repository, Project, Structure, FilenameTemplate,
                     Status, StatusList, Task, Version)
from stalker.db.session import DBSession

from anima.dcc.base import DCCBase


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def test_get_version_from_full_path_with_multiple_repositories(create_test_db):
    """testing if the get version from full path is working fine with
    multiple repositories and with same version names
    """
    repo1 = Repository(
        name='Test Repo 1',
        code="TR1",
        linux_path='/mnt/T/',
        windows_path='T:/',
        osx_path='/Volumes/T/'
    )
    DBSession.add(repo1)

    repo2 = Repository(
        name='Test Repo 2',
        code="TR2",
        linux_path='/mnt/S/',
        windows_path='S:/',
        osx_path='/Volumes/S/'
    )
    DBSession.add(repo2)

    task_ft = FilenameTemplate(
        name='Task Filename Template',
        target_entity_type='Task',
        path='$REPO{{project.repository.code}}/{{project.code}}/'
             '{%- for parent_task in parent_tasks -%}'
             '{{parent_task.nice_name}}/{%- endfor -%}',
        filename='{{task.nice_name}}_{{version.take_name}}'
                 '_v{{"%03d"|format(version.version_number)}}',
    )
    DBSession.add(task_ft)

    structure1 = Structure(
        name='Commercial Project Structure',
        templates=[task_ft]
    )
    DBSession.add(structure1)

    status1 = Status(name='Status 1', code='STS1')
    status2 = Status(name='Status 2', code='STS2')
    status3 = Status(name='Status 3', code='STS3')
    DBSession.add_all([status1, status2, status3])

    proj_status_list = \
        StatusList.query.filter_by(target_entity_type='Project').first()

    task_status_list = \
        StatusList.query.filter_by(target_entity_type='Task').first()

    version_status_list = StatusList(
        name='Version Statuses',
        target_entity_type='Version',
        statuses=[status1, status2, status3]
    )
    DBSession.add(version_status_list)

    project1 = Project(
        name='Test Project 1',
        code='TP1',
        repositories=[repo1],
        structure=structure1,
        status_list=proj_status_list
    )
    DBSession.add(project1)

    project2 = Project(
        name='Test Project 2',
        code='TP2',
        repositories=[repo2],
        structure=structure1,
        status_list=proj_status_list
    )
    DBSession.add(project2)

    task1 = Task(
        name='Test Task 1',
        code='TT1',
        project=project1,
        status_list=task_status_list
    )
    DBSession.add(task1)

    task2 = Task(
        name='Test Task 1',
        code='TT1',
        project=project2,
        status_list=task_status_list
    )
    DBSession.add(task2)

    DBSession.commit()

    # now create versions
    version1 = Version(
        task=task1,
        status_list=version_status_list
    )
    DBSession.add(version1)
    DBSession.commit()
    version1.update_paths()

    version2 = Version(
        task=task2,
        status_list=version_status_list
    )
    DBSession.add(version2)
    DBSession.commit()
    version2.update_paths()

    DBSession.commit()
    logger.debug('version1.full_path : %s' % version1.full_path)
    logger.debug('version2.full_path : %s' % version2.full_path)

    # now try to get the versions with an DCCBase instance
    dcc = DCCBase()

    # version1
    version1_found = dcc.get_version_from_full_path(
        '/mnt/T/TP1/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert version1_found == version1

    # version2
    version2_found = dcc.get_version_from_full_path(
        '/mnt/S/TP2/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert version2_found == version2

    # version1 in windows
    version1_found = dcc.get_version_from_full_path(
        'T:/TP1/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert version1_found == version1

    # version2 in windows
    version2_found = dcc.get_version_from_full_path(
        'S:/TP2/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert version2_found == version2

    # version1 in linux
    version1_found = dcc.get_version_from_full_path(
        '/mnt/T/TP1/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert version1_found == version1

    # version2 in linux
    version2_found = dcc.get_version_from_full_path(
        '/mnt/S/TP2/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert version2_found == version2

    # version1 in osx
    version1_found = dcc.get_version_from_full_path(
        '/Volumes/T/TP1/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert version1_found == version1

    # version2 in osx
    version2_found = dcc.get_version_from_full_path(
        '/Volumes/S/TP2/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert version2_found == version2


def test_get_versions_from_path_handles_empty_and_None_path(create_test_db):
    """testing if no errors will be raised for a path which is None or an
    empty string
    """
    dcc = DCCBase()
    versions = dcc.get_versions_from_path('')
    assert versions == []

    versions = dcc.get_versions_from_path(None)
    assert versions == []


def test_get_versions_from_path_with_multiple_repositories(create_test_db):
    """testing if the get versions_from_path is working fine with multiple
    repositories and with same version names
    """
    repo0 = Repository(
        name='Test Repo 0',
        code="TR0",
        linux_path='/mnt/T/with_a_very_long_path_which_will_cause_errors/',
        windows_path='T:/with_a_very_long_path_which_will_cause_errors/',
        osx_path='/Volumes/T/'
                 'with_a_very_long_path_which_will_cause_errors/'
    )
    DBSession.add(repo0)

    repo1 = Repository(
        name='Test Repo 1',
        code="TR1",
        linux_path='/mnt/T/',
        windows_path='T:/',
        osx_path='/Volumes/T/'
    )
    DBSession.add(repo1)

    repo2 = Repository(
        name='Test Repo 2',
        code="TR2",
        linux_path='/mnt/S/',
        windows_path='S:/',
        osx_path='/Volumes/S/'
    )
    DBSession.add(repo2)

    task_ft = FilenameTemplate(
        name='Task Filename Template',
        target_entity_type='Task',
        path='$REPO{{project.repository.code}}/'
             '{{project.code}}/{%- for parent_task in parent_tasks -%}'
             '{{parent_task.nice_name}}/{%- endfor -%}',
        filename='{{task.nice_name}}_{{version.take_name}}'
                 '_v{{"%03d"|format(version.version_number)}}',
    )
    DBSession.add(task_ft)

    structure1 = Structure(
        name='Commercial Project Structure',
        templates=[task_ft]
    )
    DBSession.add(structure1)

    status1 = Status(name='Status 1', code='STS1')
    status2 = Status(name='Status 2', code='STS2')
    status3 = Status(name='Status 3', code='STS3')
    DBSession.add_all([status1, status2, status3])

    proj_status_list = \
        StatusList.query.filter_by(target_entity_type='Project').first()

    task_status_list = \
        StatusList.query.filter_by(target_entity_type='Task').first()

    project1 = Project(
        name='Test Project 1',
        code='TP1',
        repositories=[repo1],
        structure=structure1,
        status_list=proj_status_list
    )
    DBSession.add(project1)

    project2 = Project(
        name='Test Project 2',
        code='TP2',
        repositories=[repo2],
        structure=structure1,
        status_list=proj_status_list
    )
    DBSession.add(project2)

    task1 = Task(
        name='Test Task 1',
        code='TT1',
        project=project1,
        status_list=task_status_list
    )
    DBSession.add(task1)

    task2 = Task(
        name='Test Task 1',
        code='TT1',
        project=project2,
        status_list=task_status_list
    )
    DBSession.add(task2)
    DBSession.commit()

    # now create versions
    version1 = Version(
        task=task1
    )
    DBSession.add(version1)
    DBSession.commit()
    version1.update_paths()

    version2 = Version(
        task=task1
    )
    DBSession.add(version2)
    DBSession.commit()
    version2.update_paths()

    version3 = Version(
        task=task2
    )
    DBSession.add(version3)
    DBSession.commit()
    version3.update_paths()

    version4 = Version(
        task=task2
    )
    DBSession.add(version4)
    DBSession.commit()
    version4.update_paths()

    DBSession.commit()
    logger.debug('version1.full_path : %s' % version1.full_path)
    logger.debug('version2.full_path : %s' % version2.full_path)
    logger.debug('version3.full_path : %s' % version2.full_path)
    logger.debug('version4.full_path : %s' % version2.full_path)

    # now try to get the versions with an DCCBase instance
    dcc = DCCBase()

    # version1, version2
    versions_found = dcc.get_versions_from_path(
        '/mnt/T/TP1/Test_Task_1'
    )
    assert versions_found == [version1, version2]

    # version3, version4
    versions_found = dcc.get_versions_from_path(
        '/mnt/S/TP2/Test_Task_1'
    )
    assert versions_found == [version3, version4]

    # version1, version2 in windows
    versions_found = dcc.get_versions_from_path(
        'T:/TP1/Test_Task_1'
    )
    assert versions_found == [version1, version2]

    # version3, version4 in windows
    versions_found = dcc.get_versions_from_path(
        'S:/TP2/Test_Task_1'
    )
    assert versions_found == [version3, version4]

    # version1, version2 in linux
    versions_found = dcc.get_versions_from_path(
        '/mnt/T/TP1/Test_Task_1'
    )
    assert versions_found == [version1, version2]

    # version3, version4 in linux
    versions_found = dcc.get_versions_from_path(
        '/mnt/S/TP2/Test_Task_1'
    )
    assert versions_found == [version3, version4]

    # version1, version2 in osx
    versions_found = dcc.get_versions_from_path(
        '/Volumes/T/TP1/Test_Task_1'
    )
    assert versions_found == [version1, version2]

    # version3, version4 in linux
    versions_found = dcc.get_versions_from_path(
        '/Volumes/S/TP2/Test_Task_1'
    )
    assert versions_found == [version3, version4]


def test_trim_repo_path_with_multiple_repositories(create_test_db):
    """testing if the trim_repo_path is working fine with multiple
    repositories and with same version names
    """
    repo0 = Repository(
        name='Test Repo 0',
        code="TR0",
        linux_path='/mnt/T/with_a_very_long_path_which_will_cause_errors/',
        windows_path='T:/with_a_very_long_path_which_will_cause_errors/',
        osx_path='/Volumes/T/'
                 'with_a_very_long_path_which_will_cause_errors/'
    )
    DBSession.add(repo0)

    repo1 = Repository(
        name='Test Repo 1',
        code="TR1",
        linux_path='/mnt/T/',
        windows_path='T:/',
        osx_path='/Volumes/T/'
    )
    DBSession.add(repo1)

    repo2 = Repository(
        name='Test Repo 2',
        code="TR2",
        linux_path='/mnt/S/',
        windows_path='S:/',
        osx_path='/Volumes/S/'
    )
    DBSession.add(repo2)

    task_ft = FilenameTemplate(
        name='Task Filename Template',
        target_entity_type='Task',
        path='{{project.code}}/{%- for parent_task in parent_tasks -%}'
             '{{parent_task.nice_name}}/{%- endfor -%}',
        filename='{{task.nice_name}}_{{version.take_name}}'
                 '_v{{"%03d"|format(version.version_number)}}',
    )
    DBSession.add(task_ft)

    structure1 = Structure(
        name='Commercial Project Structure',
        templates=[task_ft]
    )
    DBSession.add(structure1)

    status1 = Status(name='Status 1', code='STS1')
    status2 = Status(name='Status 2', code='STS2')
    status3 = Status(name='Status 3', code='STS3')
    DBSession.add_all([status1, status2, status3])

    proj_status_list = \
        StatusList.query.filter_by(target_entity_type='Project').first()

    task_status_list = \
        StatusList.query.filter_by(target_entity_type='Task').first()
    DBSession.add(task_status_list)

    project1 = Project(
        name='Test Project 1',
        code='TP1',
        repositories=[repo1],
        structure=structure1,
        status_list=proj_status_list
    )
    DBSession.add(project1)

    project2 = Project(
        name='Test Project 2',
        code='TP2',
        repositories=[repo2],
        structure=structure1,
        status_list=proj_status_list
    )
    DBSession.add(project2)

    task1 = Task(
        name='Test Task 1',
        code='TT1',
        project=project1,
        status_list=task_status_list
    )
    DBSession.add(task1)

    task2 = Task(
        name='Test Task 1',
        code='TT1',
        project=project2,
        status_list=task_status_list
    )
    DBSession.add(task2)

    DBSession.commit()

    # now create versions
    version1 = Version(task=task1)
    DBSession.add(version1)
    DBSession.commit()
    version1.update_paths()

    version2 = Version(task=task1)
    DBSession.add(version2)
    DBSession.commit()
    version2.update_paths()

    version3 = Version(task=task2)
    DBSession.add(version3)
    DBSession.commit()
    version3.update_paths()

    version4 = Version(task=task2)
    DBSession.add(version4)
    DBSession.commit()
    version4.update_paths()

    DBSession.commit()
    logger.debug('version1.full_path : %s' % version1.full_path)
    logger.debug('version2.full_path : %s' % version2.full_path)
    logger.debug('version3.full_path : %s' % version2.full_path)
    logger.debug('version4.full_path : %s' % version2.full_path)

    # now try to get the versions with an DCCBase instance
    dcc = DCCBase()

    expected_value1 = 'TP1/Test_Task_1/Test_Task_1_Main_v001'
    expected_value2 = 'TP2/Test_Task_1/Test_Task_1_Main_v001'

    # version1 native
    trimmed_path = dcc.trim_repo_path(
        '/mnt/T/TP1/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert trimmed_path == expected_value1

    # version2 native
    trimmed_path = dcc.trim_repo_path(
        '/mnt/S/TP2/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert trimmed_path == expected_value2

    # version1 windows
    trimmed_path = dcc.trim_repo_path(
        'T:/TP1/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert trimmed_path == expected_value1

    # version2 windows
    trimmed_path = dcc.trim_repo_path(
        'S:/TP2/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert trimmed_path == expected_value2

    # version1 linux
    trimmed_path = dcc.trim_repo_path(
        '/mnt/T/TP1/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert trimmed_path == expected_value1

    # version2 linux
    trimmed_path = dcc.trim_repo_path(
        '/mnt/S/TP2/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert trimmed_path == expected_value2

    # version1 osx
    trimmed_path = dcc.trim_repo_path(
        '/Volumes/T/TP1/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert trimmed_path == expected_value1

    # version2 osx
    trimmed_path = dcc.trim_repo_path(
        '/Volumes/S/TP2/Test_Task_1/Test_Task_1_Main_v001'
    )
    assert trimmed_path == expected_value2
