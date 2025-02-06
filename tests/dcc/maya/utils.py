# -*- coding: utf-8 -*-
import pymel.core as pm
from anima.dcc.mayaDCC import Maya
from stalker import Version
from stalker.db.session import DBSession


def create_version(task, parent=None):
    """Create a new version.

    Args:
        task (stalker.Task): The stalker.Task instance.
        parent (Union[None, stalker.Task]): The stalker.Task or None.
    Returns:
        stalker.Version: The new version.
    """

    maya_dcc = Maya()
    maya_dcc.use_progress_window = False

    # just renew the scene
    pm.newFile(force=True)

    if parent:
        maya_dcc.open(parent, force=True)

    v = Version(task=task)

    DBSession.add(v)
    maya_dcc.save_as(v)
    return v
