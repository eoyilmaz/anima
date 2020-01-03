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
from anima.utils import task_hierarchy_io
db.setup()
t = Task.query.get(12106)
data = json.dumps(t, cls=task_hierarchy_io.StalkerEntityEncoder, check_circular=False, indent=4)

#
# DECODING
#
project = Project.query.filter(Project.code == 'TD').first()
decoder = task_hierarchy_io.StalkerEntityDecoder(project=project)
entity = decoder.loads(data)
"""

import json


class StalkerEntityEncoder(json.JSONEncoder):
    """JSON Encoder for Stalker Classes
    """

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
        'schedule_seconds',
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

    def __init__(self, *args, **kwargs):
        super(StalkerEntityEncoder, self).__init__(*args, **kwargs)
        self._visited_objs = []

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


class StalkerEntityDecoder(object):
    """Decoder for Stalker classes
    """
    def __init__(self, project):
        self.project = project

    def loads(self, data):
        """Decodes Stalker data

        :param data:
        :return:
        """
        from stalker.db.session import DBSession
        from stalker import Asset, Task, Shot, Sequence, Version, Type

        if isinstance(data, str):
            data = json.loads(data)

        # get the entity_type
        entity_type = data['entity_type']

        # set default entity class to Task
        entity_class = Task
        if entity_type == 'Asset':
            entity_class = Asset
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
        DBSession.add(entity)
        DBSession.commit()

        # create Versions
        if version_data:
            for v_data in version_data:
                # get Version info
                v_data['task'] = entity
                v = Version(**v_data)
                # update version_number
                v.version_number = v_data['version_number']
                v.is_published = v_data['is_published']

        # for each child task call a new StalkerEntityDecoder
        for t in data['tasks']:
            child_task = self.loads(t)
            entity.tasks.append(child_task)

        return entity
