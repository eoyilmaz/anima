# -*- coding: utf-8 -*-

from anima.dcc.base import generate_empty_reference_resolution
from anima.dcc.base import DCCBase
from anima.testing import count_calls


class TestDCC(DCCBase):
    """Test DCC which just raises errors to check if the correct method has been called."""

    name = "TestDCC"
    representations = ["Base", "BBox", "GPU", "ASS"]

    test_data = {}

    def __init__(self, name="TestDCC"):
        DCCBase.__init__(self, name=name)
        # initialize test_data counter
        for f in dir(self):
            if callable(f):
                self.test_data[f.__name__] = {"call count": 0, "data": None}
        self._version = None

    @count_calls
    def export_as(self, version):
        pass

    @count_calls
    def save_as(self, version, run_pre_publishers=True):
        pass

    @count_calls
    def open(
        self,
        version,
        force=False,
        representation=None,
        reference_depth=0,
        skip_update_check=False,
    ):
        self._version = version
        return self.check_references()

    @count_calls
    def reference(self, version):
        pass

    @count_calls
    def import_(self, version):
        pass

    @count_calls
    def get_last_version(self):
        """mock version of the original this returns None all the time"""
        return None

    @count_calls
    def get_current_version(self):
        return self._version

    @count_calls
    def get_referenced_files(self):
        return self._version.inputs

    @count_calls
    def check_references(self):
        """Deeply checks all the references in the scene and returns a
        dictionary which uses the ids of the Versions as key and the action as
        value.

        Uses the top level references to get a Stalker Version instance and
        then tracks all the changes from these Version instances.

        :return: list
        """
        # reverse walk in DFS
        dfs_version_references = []
        version = self.get_current_version()
        resolution_dictionary = generate_empty_reference_resolution(
            root=self.get_referenced_files()
        )

        # TODO: with Stalker v0.2.5 replace this with Version.walk_inputs()

        for v in version.walk_hierarchy():
            dfs_version_references.append(v)

        # pop the first element which is the current scene
        dfs_version_references.pop(0)

        # iterate back in the list
        for v in reversed(dfs_version_references):
            # check inputs first
            to_be_updated_list = []
            for ref_v in v.inputs:
                if not ref_v.is_latest_published_version():
                    to_be_updated_list.append(ref_v)

            if to_be_updated_list:
                action = "create"
                # check if there is a new published version of this version
                # that is using all the updated versions of the references
                latest_published_version = v.latest_published_version
                if latest_published_version and not v.is_latest_published_version():
                    # so there is a new published version
                    # check if its children needs any update
                    # and the updated child versions are already
                    # referenced to the this published version
                    if all(
                        [
                            ref_v.latest_published_version
                            in latest_published_version.inputs
                            for ref_v in to_be_updated_list
                        ]
                    ):
                        # so all new versions are referenced to this published
                        # version, just update to this latest published version
                        action = "update"
                    else:
                        # not all references are in the inputs
                        # so we need to create a new version as usual
                        # and update the references to the latest versions
                        action = "create"
            else:
                # nothing needs to be updated,
                # so check if this version has a new version,
                # also there could be no reference under this referenced
                # version
                if v.is_latest_published_version():
                    # do nothing
                    action = "leave"
                else:
                    # update to latest published version
                    action = "update"

                # before setting the action check all the inputs in
                # resolution_dictionary, if any of them are update, or create
                # then set this one to 'create'
                if any(
                    rev_v in resolution_dictionary["update"]
                    or rev_v in resolution_dictionary["create"]
                    for rev_v in v.inputs
                ):
                    action = "create"

            # so append this v to the related action list
            resolution_dictionary[action].append(v)

        return resolution_dictionary

    @count_calls
    def update_first_level_versions(self, reference_resolution):
        """Updates the versions to the latest version.

        :param reference_resolution: A dictionary with keys 'leave', 'update'
          and 'create' with a list of :class:`~stalker.models.version.Version`
          instances in each of them. Only 'update' key is used and if the
          Version instance is in the 'update' list the reference is updated to
          the latest version.
        """
        latest = []
        for version in self._version.inputs:
            latest_published_version = version.latest_published_version
            latest.append(latest_published_version)

        self._version.inputs = latest

    @count_calls
    def update_reference_versions_to_latest(self, reference_resolution):
        """Mock update_reference_versions implementation.
        
        Does the update indeed but partially.

        Args
            reference_resolution (Dict): The reference_resolution dictionary
        
        Returns:
            List[File]: A list of new files.
        """
        # first get the resolution list
        new_versions = []
        from stalker import Version

        # store the current version
        current_version = self.get_current_version()

        # loop through 'create' versions and update their references
        # and create a new version for each of them
        for version in reference_resolution["create"]:
            local_reference_resolution = self.open(version, force=True)

            # save as a new version
            new_version = Version(
                task=version.task,
                variant_name=version.variant_name,
                parent=version,
                description="Automatically created with " "Deep Reference Update",
            )
            new_version.is_published = True

            for v in self._version.inputs:
                new_version.inputs.append(v.latest_published_version)

            new_versions.append(new_version)

        # check if we are still in the same scene
        current_version_after_create = self.get_current_version()

        if current_version:
            if current_version != current_version_after_create:
                # so we are in a different scene just reopen the previous scene
                self.open(current_version)
            # we got a new local_reference_resolution but we should have given
            # a previous one, so use it,
            #
            # append all the 'create' items to 'update' items,
            # so we can update them with update_first_level_versions()
            reference_resolution["update"].extend(reference_resolution["create"])
            self.update_first_level_versions(reference_resolution)

        return new_versions
