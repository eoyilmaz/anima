# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


class TaskTemplateParser(object):
    """Parses JSON files to create tasks out of it.

    TaskTemplateParser accept a Project instance as an input and when given a
    JSON template it can create tasks out of it.

    The user can tell the parser to create an Asset with a certain name under a
    given project. Then depending on to the Project.type variable a certain
    task hierarchy has been created and the resultant container tasks (assets
    in this case) is returned.

    The template is in the following format:

    {
        'Asset': {  # Contains templates for Assets
            'Character': {  # The desired asset type.
                'Default': {  # The default template which is used when the
                              # Project.type doesn't exist in the JSON file
                    'child_tasks: {  # Define the child tasks here
                        'Model': {   # An example child task with
                            'type': 'Model'  # The type of the task
                        },
                        'LookDev': {
                            'type': 'Look Development',  # The Type again
                            'depends': ['Model']  # Inter asset dependencies
                        },
                        'Rig': {
                            'type': 'Rig',
                            'depends': ['Model']
                        }
                    }
                }
            }
        },
        'Sequence': {
            'Default": {
            
            }
        },
        'Shot': {
            'Default': {
            
            }
        }
    }

    So in the root there can be only be three elements: Asset, Shot and
    Sequence. Under each element there can be a Type element which is only
    meaningful for Assets but is also added to Shot and Sequence for code
    consistency (or may be some day it can be used for differentiating Shot and
    Sequence types which is missing currently).

    Under each Asset/Shot/Sequence Type entry there is one entry named
    'Default' which will be used for Projects with no type or the type of the
    project can not be found in the JSON and then the other Project.type
    entries. Only the Project.type.code is accepted as the name.

    Under each Project.type entry there is one ``child_tasks`` entry holding
    the task names.

    Under each Child Task Name entry there are several other entries which can
    define the ``type`` of the task or other attributes like the
    ``schedule_model`` or inter task dependency (only referencing the tasks
    created at the same level.

    :param task_data: A dictionary containing the task data
    """

    def __init__(self, task_data=None):
        self.task_data = self._validate_task_data(task_data)

    def _validate_task_data(self, data):
        """Validates the given task data

        :param str data: JSON data
        :return:
        """
        if not isinstance(data, dict):
            raise TypeError(
                '%s.task_data should be a dictionary, not %s' % (
                    self.__class__.__name__, data.__class__.__name__
                )
            )

        return data

    def create(self, project, entity_type, task_type, task_name):
        """Creates data according to the template

        :param stalker.models.project.Project project: A stalker Project
          instance
        :param str entity_type: Type type of entity to be created. Should be
           one of 'Asset', 'Shot' or 'Sequence'
        :param str task_type: The type of task.
        :param str task_name: The name of the task.
        :return:
        """
        data = self.task_data[entity_type][task_type]
        child_task_data = None
        if project.type and project.type.name in data:
            child_task_data = data[project.type.name]
        else:
            child_Task_data = data['Default']

        from stalker import Task, Asset, Shot, Sequence
        entity_class = Task
        if entity_type == 'Asset':
            entity = Asset(
                name=task_name,
                code=task_name,
                parent=
            )
