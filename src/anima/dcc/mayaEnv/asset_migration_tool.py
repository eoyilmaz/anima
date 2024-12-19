# -*- coding: utf-8 -*-
import shutil

from anima import logger
from anima.dcc import mayaEnv

from stalker import Asset, Repository, Sequence, Shot, Task, Version
from stalker.db.session import DBSession

import pymel.core as pm

from anima.publish import run_publishers, POST_PUBLISHER_TYPE
from anima.ui.dialogs import progress_dialog
from anima.utils import get_task_hierarchy_name
from anima.utils.progress import ProgressManagerFactory


class AssetMigrationTool(object):
    """A tool to help migrating Assets from one project to another.

    The AssetMigrationTool as the name suggests migrates assets from one project to
    another. It carries all the source files along with the asset metadata (the data
    kept in Stalker).

    To define which asset(s) need to be carried, a dictionary called
    ``migration_recipe`` is used. The dictionary can be filled either manually
    (setting the dictionary content directly) or by using the AssetMigrationTool API
    (AssetMigrationTool class methods) which is a safer way of doing it.

    The ``AssetMigrationTool.migration_recipe`` needs to be in the following format:

    ```python
        self.migration_recipe = {
            {task.id}: {  # Task data
                "new_name": "New Asset Name",  # optional asset new name
                "new_code": "New Asset Code",  # optional asset new name
                "new_parent_id": new_parent_task.id,
                "takes": {  # Take data
                    {old_variant_name_1}: {  # Version data
                        "new_name": {new_name},  # Optional
                        "versions": [version1.version_number, version2.version_number]
                    },
                    {old_variant_name_2}: {  # Version data
                        "new_name": {new_name},  # Optional
                        "versions": [version1.version_number, version2.version_number]
                    }
                }
            }
        }
    ```

    As seen in the recipe, the keys are Task (or Asset, Shot, Sequence) ids, and the
    value dictionary contains the new parent task id and one another dictionary for the
    selected takes of the versions. Thus, with this tool, it is possible to carry very
    complex task hierarchies (i.e. old style environment layouts).

    It is possible to manually traverse the child Task hierarchy and create a recipe
    that contains all the tasks, assets, shots, sequences in the hierarchy. And because
    the recipe can have self referencing data, for example, an asset can reference
    another asset that is yet being carried over the other project as their new parent,
    it is possible to fully create complex hierarchies.

    In the migration recipe, versions with two different takes can be moved under the
    same take. In this case, the versions list will be concatenated, and the versions
    streams will be merged alphabetically to their take names.

    The AssetMigrationTool is currently written for asset files created with Maya. In
    the future the tool will be generalized to cover all the supported DCC's.
    """

    def __init__(self):
        self.migration_recipe = {}
        self.source_data = {}
        self.version_lut = {}

    def add_task(self, task):
        """Add the given task.

        Args:
            task (stalker.Task): The stalker.Task instance to add in to the list of
                tasks in to the data list.
        """
        raise NotImplementedError("Not implemented yet!")

    def set_target_parent(self, task, new_parent):
        """Set target parent.

        Args:
            task (stalker.Task): A stalker.Task instance.
            new_parent (stalker.Task): A stalker.Task instance to set as the new parent.
        """
        raise NotImplementedError("Not implemented yet!")

    def add_take(self, task, old_variant_name, new_variant_name=None):
        """Add a take to the list.

        Args:
            task (stalker.Task): The task to add the take to. The parent Asset needs to
                be in the list.
            old_variant_name (str): The take name to add.
            new_variant_name (str): The new take name, can be skipped in which case the
                ``old_variant_name`` argument value will be used.
        """
        raise NotImplementedError("Not implemented yet!")

    def add_version_alternative(self, source_version, alternative_version):
        """Add an alternative to the given source_version.

        This is used for augmenting the self.versions_lut dictionary and allowing
        previously moved tasks to be replaced on referencing scenes.

        Args:
            source_version (stalker.Version): The source version.
            alternative_version (stalker.Version): The alternative version.
        """
        raise NotImplementedError("Not implemented yet!")

    def migrate(self):
        """Do the migration."""
        # create an unordered list of versions to move
        inordered_list_of_versions_to_move = []
        ordered_list_of_versions_to_move = []
        version_centric_migration_recipe = {}

        progress_count = 0
        for task_id in self.migration_recipe:
            progress_count += 1
            takes = self.migration_recipe[task_id].get("takes", {})
            for variant_name in takes:
                versions = takes[variant_name].get("versions", [])
                for i, version_number in enumerate(versions):
                    progress_count += 1

        progress_manager = ProgressManagerFactory.get_progress_manager()
        progress_manager._dialog = None
        progress_manager.dialog_class = progress_dialog.ProgressDialog
        progress_caller = progress_manager.register(progress_count, "Migrate Versions")

        for task_id in self.migration_recipe:
            takes = self.migration_recipe[task_id].get("takes", {})
            for variant_name in takes:
                versions = takes[variant_name].get("versions", [])
                for i, version_number in enumerate(versions):
                    progress_caller.step(
                        message="Sort versions: {task_id}-{variant_name}-"
                        "v{version_number:03d}".format(
                            task_id=task_id,
                            variant_name=variant_name,
                            version_number=version_number,
                        )
                    )
                    v = (
                        Version.query.filter(Version.task_id == task_id)
                        .filter(Version.variant_name == variant_name)
                        .filter(Version.version_number == version_number)
                        .first()
                    )
                    if not v:
                        continue
                    # store the version in the migration_recipe for later use
                    takes[variant_name]["versions"][i] = v
                    inordered_list_of_versions_to_move.append(v)

        # fill new_parent_id, new_name and new_code for all items
        for task_id in self.migration_recipe:
            task = Task.query.filter(Task.id == task_id).first()
            progress_caller.step(
                message="Generate args for {task_name}".format(task_name=task.name)
            )
            if not task:
                continue
            if "new_parent_id" not in self.migration_recipe[task_id]:
                # use the current task.parent_id as the new_parent,
                # hopping the parents are also getting carried over.
                self.migration_recipe[task_id]["new_parent_id"] = (
                    task.parent.id if task.parent else None
                )
            if "new_name" not in self.migration_recipe[task_id]:
                self.migration_recipe[task_id]["new_name"] = task.name

            if (
                isinstance(task, (Asset, Shot, Sequence))
                and "new_code" not in self.migration_recipe[task_id]
            ):
                # also fill the code attr
                self.migration_recipe[task_id]["new_code"] = task.code

        # We need to get a proper list with a proper order,
        # so that when the tasks are processed in that order,
        entity_ids_to_carry_over = list(self.migration_recipe.keys())
        new_tasks_lut = {}

        progress_caller2 = progress_manager.register(
            max_iteration=len(entity_ids_to_carry_over),
            title="Generate Ordered Versions",
        )
        progress_caller.end_progress()

        while entity_ids_to_carry_over:
            source_entity_id = entity_ids_to_carry_over.pop(0)
            # check if the new_parent_id is one of the tasks
            # that is getting carried over
            new_parent_id = self.migration_recipe[source_entity_id]["new_parent_id"]
            if new_parent_id in self.migration_recipe:
                # yes, this task is also getting carried
                # check if we have already created a corresponding new task for this
                # parent task
                if new_parent_id in new_tasks_lut:
                    # greate, we have already carried this task over and have created
                    # a new task, use this new task as the new_parent and continue work
                    new_parent_id = new_tasks_lut[new_parent_id]
                else:
                    # this task has not been carried yet
                    # put this task back in to the end of the list
                    entity_ids_to_carry_over.append(source_entity_id)
                    # and get in to other tasks in the list
                    logger.debug("skipping: {}".format(source_entity_id))
                    continue
            else:
                # no, this task is not in the migration list,
                # then don't do anything and keep working on carrying this task
                pass

            new_parent = Task.query.filter(Task.id == new_parent_id).first()
            source_entity = Task.query.filter(Task.id == source_entity_id).first()
            progress_caller2.step(message="Sort Versions {}".format(source_entity.name))
            new_entity_class_lut = {
                "Task": Task,
                "Asset": Asset,
                "Shot": Shot,
                "Sequence": Sequence,
            }
            kwargs = {
                "name": self.migration_recipe[source_entity_id]["new_name"],
                "parent": new_parent,
                "type": source_entity.type,
                "description": "Migrated from {} under {}".format(
                    source_entity.name, source_entity.project.name
                ),
            }
            if source_entity.entity_type in ["Asset", "Shot", "Sequence"]:
                kwargs["code"] = self.migration_recipe[source_entity_id]["new_code"]

            new_task = new_entity_class_lut[source_entity.entity_type](**kwargs)
            DBSession.add(new_task)
            DBSession.commit()
            new_tasks_lut[source_entity_id] = new_task.id

            # We kind of need a versions list that is in
            # reverse-breadth-first order in their dependencies to each other
            takes = self.migration_recipe[source_entity_id].get("takes", {})
            for variant_name in takes:
                versions = takes[variant_name].get("versions", [])
                for v in versions:  # at this point we should have normal versions
                    # check if something referencing this v has already moved this v
                    # to the ordered list.
                    order_index = 0
                    for other_v in v.inputs:
                        # check if we need to move the other_v first
                        if other_v in inordered_list_of_versions_to_move:
                            # na-na-na-naaa
                            # we need to move other_v before v
                            # insert the v accordingly
                            if other_v in ordered_list_of_versions_to_move:
                                order_index = max(
                                    order_index,
                                    ordered_list_of_versions_to_move.index(other_v) + 1,
                                )
                            else:
                                # other_v is not in the ordered list
                                # so append the v preferably to the start of the list
                                order_index = max(order_index, 0)
                    # insert the v to the ordered list to the order_index position
                    ordered_list_of_versions_to_move.insert(order_index, v)
                    # add the version to the version centric migration recipe
                    version_centric_migration_recipe[v] = {
                        "new_task": new_task,
                        "variant_name": takes[variant_name].get("new_name", variant_name),
                    }

        progress_caller3 = progress_manager.register(
            max_iteration=len(ordered_list_of_versions_to_move)
        )
        progress_caller2.end_progress()

        # We now should have sorted list of source versions
        # and a corresponding version centric migration recipe
        # go over the list and create new versions,
        dcc_env = mayaEnv.Maya()
        publish_errors = []
        for v in ordered_list_of_versions_to_move:
            recipe = version_centric_migration_recipe[v]
            new_version = Version(
                task=recipe["new_task"],
                variant_name=recipe["variant_name"],
                description=v.description,
            )
            if "maya" in v.created_with.lower():
                dcc_env.open(version=v, force=True, skip_update_check=True, prompt=False)
                # replace all top level references with the versions from version_lut
                for ref in pm.listReferences():
                    # all refs must be base version
                    if not ref.is_base():
                        ref.to_base()
                    ref_version = ref.version
                    if ref_version in self.version_lut:
                        ref.replaceWith(
                            Repository.to_os_independent_path(
                                self.version_lut[ref_version].absolute_full_path
                            )
                        )
                # TODO: Before saving check external files like textures, audio etc.
                dcc_env.save_as(version=new_version)
            else:
                # this file is not created with Maya,
                # copy it over to the new place directly
                new_version.extension = v.extension
                new_version.created_with = v.created_with
                shutil.copy2(v.absolute_full_path, new_version.absolute_full_path)

            # because publish scripts may fail, set the "publish" status after
            # saving the file
            new_version.is_published = v.is_published
            DBSession.add(new_version)
            DBSession.commit()
            self.version_lut[v] = new_version

            if new_version.is_published and "maya" in v.created_with.lower():
                try:
                    # run the post publishers here
                    type_name = ""
                    if new_version.task.type:
                        type_name = new_version.task.type.name
                    run_publishers(type_name, publisher_type=POST_PUBLISHER_TYPE)
                except Exception as e:
                    # prevent any exception to cut the process in the middle
                    publish_errors.append((new_version, e))
            progress_caller3.step(
                message="Moved {}_v{:03d}".format(
                    get_task_hierarchy_name(new_version.task),
                    new_version.version_number,
                )
            )

        progress_caller3.end_progress()
        progress_manager.end_progress()
        pm.newFile(force=True)

        if publish_errors:
            print("During migration {} errors occurred".format(len(publish_errors)))
            print("=================================================")
            for version, error in publish_errors:
                print("------")
                print(version.full_path)
                print(error)
            print("=================================================")

        logger.debug("Asset migrated successfully!")
