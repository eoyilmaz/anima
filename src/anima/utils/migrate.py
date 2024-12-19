# -*- coding: utf-8 -*-
"""Migration related utility classes and functions."""


class MigrateDataBase(object):
    """Base class for all the other migrate data classes."""

    def to_dict(self):
        """Return a dictionary representing migration the data."""
        raise NotImplementedError

    def validate(self):
        """Validate the data.

        Returns:
            bool: True if the data is valid in this migrate data object or
                False.
        """
        raise NotImplementedError


class ProjectMigrateData(MigrateDataBase):
    """Project related migration data and functionalities."""

    def __init__(self):
        self.assets = []

    def add_assets(self, assets):
        """Add the given assets to this migration data object.

        Args:
            assets (list): A list of stalker.Asset instances to be added to
                this migration data object.
        """
        raise NotImplementedError

    def add_asset(self, asset):
        """Add the given asset to this migration data object.

        Args:
            asset (stalker.Asset): A stalker.Asset instance to be added to this
                migration data object.
        """
        raise NotImplementedError

    def remove_asset(self, asset):
        """Remove the given asset from this migration data object.

        Args:
            asset (stalker.Asset): A stalker.Asset instance to be removed from
                his migration data object.
        """
        raise NotImplementedError

    def to_dict(self):
        """Return a dictionary representing migration the data."""
        raise NotImplementedError

    def validate(self):
        """Validate the data.

        Returns:
            bool: True if the data is valid in this migrate data object or
                False.
        """
        raise NotImplementedError


class AssetMigrateData(MigrateDataBase):
    """Asset rated migration data and functionalities."""

    def __init__(self, asset=None):
        self.asset = asset
        self._tasks = []

    @property
    def tasks(self):
        """Return the tasks.

        Returns:
            list: The tasks
        """
        return self._tasks

    def add_task(self, task=None):
        """Add the given task to the tasks list."""
        raise NotImplementedError

    def remove_task(self, task=None):
        """Remove the given task from the tasks list."""

    def to_dict(self):
        """Return a dictionary representing migration the data."""
        raise NotImplementedError

    def validate(self):
        """Validate the data.

        Returns:
            bool: True if the data is valid in this migrate data object or
                False.
        """
        raise NotImplementedError


class TaskMigrateData(MigrateDataBase):
    """Task related migrate data."""

    def __init__(self, task=None):
        self.task = None
        self._takes = []

    def to_dict(self):
        """Return a dictionary representing the migration data."""
        raise NotImplementedError

    def validate(self):
        """Validate the data.

        Returns:
            bool: True if the data is valid in this migrate data object or
                False.
        """
        raise NotImplementedError


class TakeMigrateData(MigrateDataBase):
    """Take related migrate data."""

    def __init__(self, take=None):
        self.take = take
        self._versions = []

    def to_dict(self):
        """Return a dictionary representing the migration data."""
        raise NotImplementedError

    def validate(self):
        """Validate the data.

        Returns:
            bool: True if the data is valid in this migrate data object or
                False.
        """
        raise NotImplementedError


class VersionMigrateData(MigrateDataBase):
    """Version related migrate data."""

    def __init__(self, version=None):
        self.version = version
        self.inputs = []

    def to_dict(self):
        """Return a dictionary representing the migration data."""
        raise NotImplementedError

    def validate(self):
        """Validate the data.

        Returns:
            bool: True if the data is valid in this migrate data object or
                False.
        """
        raise NotImplementedError
