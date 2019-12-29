# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Anima Istanbul
#
# This module is part of anima-tools and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


def test_template_argument_accepts_only_a_json_as_text():
    """testing if a TypeError will be raised when the template argument is not
    a string containing JSON data.
    """
    from anima.utils.task_template_parser import TaskTemplateParser
    with pytest.raises(TypeError):
        TaskTemplateParser('not json data')


def test_template_argument_is_working_properly(test_data):
    """testing if the template argument value is parsed and passed to the
    template attribute
    """
    from anima.utils.task_template_parser import TaskTemplateParser
    ttp = TaskTemplateParser(test_data)
    assert ttp is not None


def test_creating_test_data(create_db, create_project):
    """testing if the test project is created correctcly
    """
    project = create_project
    from stalker import Project
    assert isinstance(project, Project)


def test_creating_tasks_from_template(create_db, create_project):
    """testing if tasks are created out of Templates
    """
    project = create_project
    from anima.utils.task_template_parser import TaskTemplateParser
    from anima import defaults
    ttp = TaskTemplateParser(task_data=defaults.task_template)
    asset = ttp.create(project, 'Asset', 'Character')

    from stalker import Asset
    assert isinstance(asset, Asset)


# def test_create_entity_type_is_not_a_string(prepare_db):
#     """testing if a TypeError will be raised if the entity_type is not
#     """
