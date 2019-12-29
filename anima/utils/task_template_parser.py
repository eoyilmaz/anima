# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Anima Istanbul
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
"""
#
# ENCODING
#
import json
from stalker import db, Task, Project
from anima.utils import task_template_parser
db.setup()
t = Task.query.get(12106)
data = json.dumps(t, cls=task_template_parser.StalkerEncoder, check_circular=False, indent=4)

#
# DECODING
#
project = Project.query.filter(Project.code == 'TD').first()
decoder = task_template_parser.StalkerDecoder(project=project)
entity = decoder.loads(data)
"""

import json


class StalkerEncoder(json.JSONEncoder):
    """JSON Encoder for Stalker Classes
    """
    _visited_objs = []
    ignore_fields = [
        # Generic
        'defaults',

        # SimpleEntity
        'id',
        'entity_id',
        'nice_name',

        # Task
        'absolute_path',
        'allocation_strategy',
        'alternative_resources',
        'bid_timing',
        'bid_unit',
        'children',
        'computed_duration',
        'computed_end',
        'computed_resources',
        'computed_start',
        'computed_total_seconds',
        'create_time_log',
        'created_by',
        'created_by_id',
        'date_created',
        'date_updated',
        'dependent_of',
        'depends',
        'duration',
        'end',
        'entity_groups',
        'generic_data',
        'generic_text',
        'good',
        'good_id',
        'hold',
        'html_class',
        'html_style',
        'is_container',
        'is_leaf',
        'is_milestone',
        'is_root',
        'is_scheduled',
        'least_meaningful_time_unit',
        'level',
        'notes',
        'open_tickets',
        'parent',
        'parent_id',
        'parents',
        'percent_complete',
        'persistent_allocation',
        'plural_class_name',
        'priority',
        'project',
        'project_id',
        'query',
        'references',
        'remaining_seconds',
        'resources',
        'responsible',
        'review_number',
        'reviews',
        'start',
        'status',
        'status_id',
        'status_list',
        'status_list_id',
        'tags',
        'task_dependent_of',
        'task_depends_to',
        'thumbnail',
        'thumbnail_id',
        'tickets',
        'time_logs',
        'tjp_abs_id',
        'tjp_id',
        'to_tjp',
        'total_logged_seconds',
        'total_seconds',
        'updated_by',
        'updated_by_id',
        'walk_dependencies',
        'walk_hierarchy',
        'walk_inputs',
        'watchers',

        # Shot
        'image_format',
        'image_format_id',
        'source_in',
        'source_out',
        'sequences',

        # Version
        'absolute_full_path',
        'inputs',
        'latest_published_version',
        'latest_version',
        'link_id',
        'max_version_number',
        'naming_parents',
        'task',
        'task_id',
        'outputs',
        'version_id',
    ]

    def default(self, obj):
        from sqlalchemy.ext.declarative import DeclarativeMeta

        if isinstance(obj.__class__, DeclarativeMeta):
            # don't re-visit self
            if obj in self._visited_objs:
                return None
            # do not append if this is a type instance
            if obj.entity_type != 'Type':
                self._visited_objs.append(obj)

            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                # skip ignore fields
                if field in self.ignore_fields:
                    continue

                # skip callables
                if callable(obj.__getattribute__(field)):
                    continue

                try:
                    fields[field] = obj.__getattribute__(field)
                except (AttributeError, TypeError, NotImplementedError, RuntimeError):
                    pass

            # a json-encodable dict
            return fields

        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            return None


class StalkerDecoder(object):
    """Decoder for Stalker classes
    """
    def __init__(self, project):
        self.project = project

    def loads(self, data):
        """Decodes Stalker data

        :param data:
        :return:
        """
        from stalker import Asset, Task, Shot, Sequence, Version, Type

        if isinstance(data, str):
            data = json.loads(data)

        # get the entity_type
        entity_type = data['entity_type']

        if entity_type == 'Asset':
            entity_class = Asset
        elif entity_type == 'Task':
            entity_class = Task
        elif entity_type == 'Shot':
            entity_class = Shot
            # this is a bug
            data['sequences'] = []
        elif entity_type == 'Sequence':
            entity_class = Sequence

        version_data = data['versions']
        data['versions'] = []
        # get the type
        if 'type' in data:
            type_data = data['type']
            if type_data:
                type_name = type_data['name']
                type_ = Type.query.filter(Type.name == type_name).first()
                if not type_:
                    # create a Type
                    type_ = Type(**type_data)
                data['type'] = type_

        data['project'] = self.project
        entity = entity_class(**data)

        # create Versions
        if version_data:
            repo = self.project.repository
            repo_id = 0
            if repo:
                repo_id = repo.id

            for v_data in version_data:
                # get Version info
                v_data['task'] = entity
                v = Version(**v_data)
                # update version_number
                v.version_number = v_data['version_number']
                # update REPO path
                v.full_path = '/'.join(
                    ['$REPO%s' % repo_id] + v.full_path.split('/')[1:]
                )

        # for each child task call a new StalkerDecoder
        for t in data['tasks']:
            child_task = self.loads(t)
            entity.tasks.append(child_task)

        return entity


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
                parent=''
            )
