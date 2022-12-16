# -*- coding: utf-8 -*-
from anima import logger

import pymel.core as pm


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
            {asset.id}: {
                # Asset Data
                "new_parent_id": new_parent_task.id,
                "tasks": {
                    {direct_child_task.id}: [  # Task data
                        {old_take_name_1}: {  # Take data
                            "new_take_name": {new_take_name},  # Optional
                            "versions": [version1, version2]
                        },
                        {old_take_name_2}: {  # Take data
                            "new_take_name": {new_take_name},  # Optional
                            "versions": [version1, version2]
                        }

                    ]
                }
            }
        }
    ```

    As seen in the recipe, the keys are Asset ids, and the value dictionary contains the
    new parent task id and one another dictionary for the selected takes of the child
    tasks. Thus, with this tool, it is not possible to carry very complex task
    hierarchies (i.e. old style environment layouts).

    For an Asset, the immediate child tasks will be carried over. But, it is possible to
    manually traverse the Asset hierarchy and create a recipe that contains all the
    assets in the hierarchy. And because the recipe can have self referencing data, for
    example, an asset can reference another asset that is being carried over the other
    project as their new parent, it is possible to partially create complex hierarchies
    to a degree at least.

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

    def add_asset(self, asset):
        """Add the given asset.

        Args:
            asset (stalker.Asset): The stalker.Asset instance to add in to the list of
                assets in to the data list.
        """
        raise NotImplementedError("Not implemented yet!")

    def set_target_parent(self, asset, new_parent):
        """Set target parent.

        Args:
            asset (stalker.Asset): A stalker.Asset instance.
            new_parent (stalker.Task): A stalker.Task instance to set as the new parent.
        """
        raise NotImplementedError("Not implemented yet!")

    def add_take(self, task, old_take_name, new_take_name=None):
        """Add a take to the list.

        Args:
            task (stalker.Task): The task to add the take to. The parent Asset needs to
                be in the list.
            old_take_name (str): The take name to add.
            new_take_name (str): The new take name, can be skipped in which case the
                ``old_take_name`` argument value will be used.
        """
        raise NotImplementedError("Not implemented yet!")

    def add_version_alternative(self, source_version, alternative_version):
        """Add an alternative to the given source_version.

        This is used for augmenting the self.versions_lut dictionary and allowing
        previously moved assets to be replaced on referencing scenes.

        Args:
            source_version (stalker.Version): The source version.
            alternative_version (stalker.Version): The alternative version.
        """
        raise NotImplementedError("Not implemented yet!")

    def migrate(self):
        """Do the migration."""
        # traverse the asset child task_ids
        from stalker.db.session import DBSession
        from stalker import Asset, Repository, Task, Version
        from anima.dcc import mayaEnv
        m = mayaEnv.Maya()

        # create an unordered list of versions to move
        inordered_list_of_versions_to_move = []
        ordered_list_of_versions_to_move = []
        version_centric_migration_recipe = {}
        for source_asset_id in self.migration_recipe:
            task_ids = self.migration_recipe[source_asset_id]["tasks"]
            for task_id in task_ids:
                for take_name in task_ids[task_id]:
                    for v in task_ids[task_id][take_name]["versions"]:
                        inordered_list_of_versions_to_move.append(v)

        # create the new asset under the target
        for source_asset_id in self.migration_recipe:
            source_asset = Asset.query.filter(Asset.id == source_asset_id).first()
            new_parent_id = self.migration_recipe[source_asset_id]["new_parent_id"]
            new_parent = Task.query.filter(Task.id == new_parent_id).first()

            new_asset = Asset(
                name=source_asset.name,
                code=source_asset.code,
                parent=new_parent,
                type=source_asset.type,
                description="Migrated from {} under {}".format(
                    source_asset.name,
                    source_asset.project.name
                )
            )
            DBSession.add(new_asset)
            DBSession.commit()

            # We kind of need a versions list that is in
            # reverse-breadth-first order in their dependencies to each other
            task_ids = self.migration_recipe[source_asset_id]["tasks"]
            for task_id in task_ids:
                task = Task.query.filter(Task.id == task_id).first()
                new_task = Task(
                    parent=new_asset,
                    name=task.name,
                    type=task.type,
                )
                DBSession.add(new_task)
                DBSession.commit()

                for take_name in task_ids[task_id]:
                    for v in task_ids[task_id][take_name]["versions"]:
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
                                        ordered_list_of_versions_to_move.index(other_v) + 1
                                    )
                                else:
                                    # other_v is not in the ordered list
                                    # so append the v to the end of the list
                                    order_index = len(ordered_list_of_versions_to_move)
                        # insert the v to the ordered list to the order_index position
                        ordered_list_of_versions_to_move.insert(order_index, v)
                        # add the version to the version centric migration recipe
                        version_centric_migration_recipe[v] = {
                            "new_task": new_task,
                            "take_name": task_ids[task_id][take_name].get("new_take_name", take_name),
                        }

        # We now should have sorted list of source versions
        # and a corresponding version centric migration recipe
        # go over the list and create new versions,
        for v in ordered_list_of_versions_to_move:
            recipe = version_centric_migration_recipe[v]
            new_version = Version(
                task=recipe["new_task"],
                take_name=recipe["take_name"],
                description=v.description
            )
            m.open(version=v, force=True, skip_update_check=True, prompt=False)

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
            m.save_as(version=new_version)

            # because publish scripts may fail, set the publish status after
            # saving the file
            DBSession.add(new_version)
            DBSession.commit()
            new_version.is_published = v.is_published
            self.version_lut[v] = new_version

        logger.debug("Asset migrated successfully!")
