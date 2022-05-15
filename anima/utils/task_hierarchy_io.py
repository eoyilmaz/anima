# -*- coding: utf-8 -*-
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
    """JSON Encoder for Stalker Classes"""

    ignore_fields = [
        # Generic
        "defaults",
        # SimpleEntity
        "id",
        "entity_id",
        "nice_name",
        # Task
        "absolute_path",
        "allocation_strategy",
        "alternative_resources",
        "bid_timing",
        "bid_unit",
        "children",
        "computed_duration",
        "computed_end",
        "computed_resources",
        "computed_start",
        "computed_total_seconds",
        "create_time_log",
        "created_by",
        "created_by_id",
        "date_created",
        "date_updated",
        "dependent_of",
        "depends",
        "duration",
        "end",
        "entity_groups",
        "generic_data",
        "generic_text",
        "good",
        "good_id",
        "hold",
        "html_class",
        "html_style",
        "is_container",
        "is_leaf",
        "is_milestone",
        "is_root",
        "is_scheduled",
        "least_meaningful_time_unit",
        "level",
        "notes",
        "open_tickets",
        "parent",
        "parent_id",
        "parents",
        "percent_complete",
        "persistent_allocation",
        "plural_class_name",
        "priority",
        "project",
        "project_id",
        "query",
        "references",
        "remaining_seconds",
        "resources",
        "responsible",
        "review_number",
        "reviews",
        "schedule_seconds",
        "start",
        "status",
        "status_id",
        "status_list",
        "status_list_id",
        "tags",
        "task_dependent_of",
        "task_depends_to",
        "thumbnail",
        "thumbnail_id",
        "tickets",
        "time_logs",
        "tjp_abs_id",
        "tjp_id",
        "to_tjp",
        "total_logged_seconds",
        "total_seconds",
        "updated_by",
        "updated_by_id",
        "walk_dependencies",
        "walk_hierarchy",
        "walk_inputs",
        "watchers",
        # Shot
        "image_format",
        "image_format_id",
        "source_in",
        "source_out",
        "sequences",
        # Version
        "absolute_full_path",
        "inputs",
        "latest_published_version",
        "latest_version",
        "link_id",
        "max_version_number",
        "naming_parents",
        "task",
        "task_id",
        "outputs",
        "version_id",
    ]

    def __init__(self, *args, **kwargs):
        super(StalkerEntityEncoder, self).__init__(*args, **kwargs)
        self._visited_obj_ids = []

    def default(self, obj):
        from sqlalchemy.ext.declarative import DeclarativeMeta

        if isinstance(obj.__class__, DeclarativeMeta):
            # don't re-visit self
            if obj.id in self._visited_obj_ids:
                return {"$ref": obj.id}

            # do not append if this is a type instance
            if obj.entity_type != "Type":
                self._visited_obj_ids.append(obj.id)

            # an SQLAlchemy class
            fields = {}
            for field in [
                x for x in dir(obj) if not x.startswith("_") and x != "metadata"
            ]:
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
            # return json.JSONEncoder.default(self, obj)
            return super(StalkerEntityEncoder, self).default(obj)
        except TypeError:
            return None


class StalkerEntityDecoder(object):
    """Decoder for Stalker classes"""

    def __init__(self, project, parent=None):
        self.project = project
        self.parent = parent
        self._created_obj = {}

    def loads(self, data, parent=None):
        """Decodes Stalker data

        :param data: Raw json data.
        :param parent: The parent node to attach the newly created data to.
        :return:
        """
        from stalker.db.session import DBSession
        from stalker import Asset, Task, Shot, Sequence, Version, Type

        if isinstance(data, str):
            data = json.loads(data)

        json_id = None
        if "id" in data:
            json_id = data.pop("id")

        if json_id is not None and json_id in self._created_obj:
            return self._created_obj[json_id]

        # get the entity_type
        try:
            entity_type = data["entity_type"]
        except KeyError:
            return None

        # set default entity class to Task
        entity_class = Task
        # entity_type_dict = {
        #     'Asset': Asset,
        #     'Shot': Shot,
        #     'Sequence': Sequence
        # }
        if entity_type == "Asset":
            entity_class = Asset
        elif entity_type == "Shot":
            entity_class = Shot
            # TODO: this is a bug
            data["sequences"] = []
        elif entity_type == "Sequence":
            entity_class = Sequence

        # TODO: We shouldn't need the following code for Type anymore
        # get the type
        if "type" in data:
            type_data = data["type"]
            if type_data and not isinstance(type_data, Type):
                type_name = type_data["name"]
                type_ = Type.query.filter(Type.name == type_name).first()
                if not type_:
                    # create a Type
                    type_ = Type(**type_data)
                data["type"] = type_

        # store version data
        version_data = sorted(data["versions"], key=lambda x: x["version_number"])
        data["versions"] = []

        data["project"] = self.project

        # check if the data exists before creating it
        entity = (
            entity_class.query.filter(entity_class.project == self.project)
            .filter(entity_class.parent == parent)
            .filter(entity_class.name == data["name"])
            .first()
        )

        if not entity:
            # then create it
            entity = entity_class(**data)
            DBSession.add(entity)
            DBSession.commit()

        if json_id:
            self._created_obj[json_id] = entity

        # create Versions
        if version_data:
            for v_data in version_data:

                v_json_id = None
                if "id" in v_data:
                    v_json_id = v_data.pop("id")

                # check version number and take name
                # if there is a version with the same version_number
                # don't create it
                take_name = v_data["take_name"]
                version_number = v_data["version_number"]

                v = (
                    Version.query.filter(Version.task == entity)
                    .filter(Version.take_name == take_name)
                    .filter(Version.version_number == version_number)
                    .first()
                )

                if not v:
                    # then create it
                    # get Version info
                    v_data["task"] = entity
                    v = Version(**v_data)
                    # update version_number
                    v.version_number = v_data["version_number"]
                    v.is_published = v_data["is_published"]

                self._created_obj[v_json_id] = v

            DBSession.commit()

        # for each child task call a new StalkerEntityDecoder
        for t in data["tasks"]:
            self.loads(t, parent=entity)

        if parent:
            entity.parent = parent

        return entity
