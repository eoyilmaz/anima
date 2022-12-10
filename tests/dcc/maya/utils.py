# -*- coding: utf-8 -*-


def create_version(task, take_name, parent=None):
    """Create a new version.

    Args:
        task (stalker.Task): The stalker.Task instance.
        take_name (str): the take_name name
        parent (Union[None, stalker.Task]): The stalker.Task or None.
    Returns:
        stalker.Version: The new version.
    """
    import pymel.core as pm
    from anima.dcc.mayaEnv import Maya
    from stalker import Version
    from stalker.db.session import DBSession

    maya_env = Maya()
    maya_env.use_progress_window = False

    # just renew the scene
    pm.newFile(force=True)

    if parent:
        maya_env.open(parent, force=True)

    v = Version(task=task, take_name=take_name)

    DBSession.add(v)
    maya_env.save_as(v)
    return v
