# -*- coding: utf-8 -*-

import os


def submit_job(job_name, block_name, command):
    """Submits an Afanasy job

    :param job_name:
    :param block_name:
    :param command:
    :return:
    """

    import af

    block = af.Block(block_name, 'maya')
    block.setCommand(" ".join(command))
    block.setNumeric(1, 1, 1, 1)

    job = af.Job(job_name)
    job.blocks = [block]
    status, data = job.send()

    if not status:
        RuntimeError('Something went wrong!')


def submit_alembic_job(path, project_code=''):
    """creates a afanasy job that exports the alembics on a given scene

    :param str path: Path to a maya file
    :param project_code: Project.code
    """
    job_name = "%s:%s - Alembic Export" % (project_code, os.path.basename(path))
    block_name = job_name
    command = [
        "mayapy",
        "-c",
        "\"import pymel.core as pm;"
        "from anima.dcc.mayaEnv import afanasy_publisher;"
        "afanasy_publisher.export_alembics('{path}');\"".format(path=path)
    ]
    submit_job(job_name, block_name, command)


def submit_playblast_job(path, project_code=''):
    """creates a afanasy job that exports the alembics on a given scene

    :param str path: Path to a maya file
    :param project_code: Project.code
    """
    job_name = "%s:%s - Playblast" % (project_code, os.path.basename(path))
    block_name = job_name
    command = [
        "mayapy",
        "-c",
        "\"import pymel.core as pm;"
        "from anima.dcc.mayaEnv import afanasy_publisher;"
        "afanasy_publisher.export_playblast('{path}');\"".format(path=path)
    ]
    submit_job(job_name, block_name, command)


def export_alembics(path):
    """Creates alembic files

    :param str path: The path of the file version
    :return:
    """
    from anima.dcc import mayaEnv
    m = mayaEnv.Maya()
    m.use_progress_window = False  # Maya sets that automatically but let's be sure!
    v = m.get_version_from_full_path(path)
    if not v:
        raise RuntimeError("version not found!")

    m.open(v, force=True, skip_update_check=True, prompt=False)

    from anima.dcc.mayaEnv import animation
    animation.Animation.set_range_from_shot()

    from anima.dcc.mayaEnv import auxiliary
    auxiliary.export_alembic_from_cache_node(handles=1, isolate=False, unload_refs=False)
    print("Alembic Export Done!")


def export_playblast(path):
    """Playblasts the current scene

    :param str path: The path of the file version
    :return:
    """
    import pymel.core as pm
    from anima.dcc import mayaEnv
    m = mayaEnv.Maya()
    m.use_progress_window = False  # Maya sets that automatically but let's be sure!
    v = m.get_version_from_full_path(path)
    if not v:
        raise RuntimeError("version not found!")

    m.open(v, force=True, skip_update_check=True, prompt=False)

    from anima.dcc.mayaEnv import animation
    animation.Animation.set_range_from_shot()

    # delete any focusPlane shape nodes to prevent them from being shown in the playblast
    pm.delete(pm.ls("focusPlane*Shape"))

    shots = pm.ls(type='shot')
    if shots:
        shot = shots[0]

        camera = None
        if shot:
            camera = pm.PyNode(shot.getCurrentCamera())

        # set only the camera renderable and the rest non renderable
        for cam in pm.ls(type='camera'):
            cam.renderable.set(0)
        if camera:
            camera.renderable.set(1)

    from anima.dcc.mayaEnv import auxiliary
    default_view_options = auxiliary.get_default_playblast_view_options()
    auxiliary.perform_playblast(0, resolution=100, playblast_view_options=default_view_options, upload_to_server=True)
    print("Playblast Done!")
