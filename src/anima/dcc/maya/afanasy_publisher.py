# -*- coding: utf-8 -*-
import os

import af

import pymel.core as pm

from anima.dcc.maya import animation, auxiliary, playblast
from anima.dcc.maya.common import Maya


def submit_job(
    job_name : str,
    block_name : str,
    command : str,
    host_mask : str = ""
) -> None:
    """Submit an Afanasy job.

    Args:
        job_name (str): The job name.
        block_name (str): The block name.
        command (str): The render command.
        host_mask (str): The host mask.

    Raises:
        RuntimeError: If something went wrong.
    """
    block = af.Block(block_name, "maya")
    block.setCommand(" ".join(command))
    block.setNumeric(1, 1, 1, 1)

    job = af.Job(job_name)
    job.blocks = [block]
    if host_mask != "":
        host_mask = host_mask.replace('"', "")
        job.setHostsMask(host_mask)
    status, data = job.send()

    if not status:
        RuntimeError("Something went wrong!")


def submit_alembic_job(
    path : str,
    project_code : str = "",
    host_mask : str = ""
) -> None:
    """Create an Afanasy job that exports the alembics on a given scene

    Args:
        path (str): Path to a maya file
        project_code (str): Project.code
        host_mask (str): The host mask.
    """
    job_name = "{}:{} - Alembic Export".format(project_code, os.path.basename(path))
    block_name = job_name

    if "REZ_USED_RESOLVE" in os.environ:
        # this is a rez configured environment
        # use the same rez request to build the render command
        command = ["rez-env {} -- mayapy".format(os.environ["REZ_USED_RESOLVE"])]
    else:
        # use the default command
        command = ["mayapy{}".format(os.getenv("MAYA_VERSION", ""))]

    command += [
        "-c",
        '"import pymel.core as pm;'
        "from anima.dcc.maya import afanasy_publisher;"
        "afanasy_publisher.export_alembics('{path}');\"".format(path=path),
    ]
    submit_job(job_name, block_name, command, host_mask=host_mask)


def submit_playblast_job(
    path : str,
    project_code : str = "",
    host_mask : str = ""
) -> None:
    """Create an Afanasy job that exports the alembics on a given scene.

    Args:
        path (str): Path to a maya file
        project_code (str): Project.code
        host_mask (str): The host mask.
    """
    job_name = "{}:{} - Playblast".format(project_code, os.path.basename(path))
    block_name = job_name
    command = [
        "mayapy{}".format(os.getenv("MAYA_VERSION", "")),
        "-c",
        '"import pymel.core as pm;'
        "from anima.dcc.maya import afanasy_publisher;"
        "afanasy_publisher.export_playblast('{path}');\"".format(path=path),
    ]
    submit_job(job_name, block_name, command, host_mask=host_mask)


def export_alembics(path : str) -> None:
    """Create alembic files.

    Args:
        path (str): The path of the file version.
    """
    m = Maya()
    m.use_progress_window = False  # Maya sets that automatically but let's be sure!
    v = m.get_version_from_full_path(path)
    if not v:
        raise RuntimeError("version not found!")

    m.open(v, force=True, skip_update_check=True, prompt=False)
    animation.Animation.set_range_from_shot()
    auxiliary.export_cache_of_all_cacheable_nodes(
        handles=1, isolate=False, unload_refs=False
    )
    print("Alembic Export Done!")


def export_playblast(
    path: str,
    force_batch_mode : str = False,
    reference_depth : str = 0
):
    """Playblast the current scene.

    Args:
        path (str): The path of the file version.
        force_batch_mode (bool): Force to run in batch mode.
        reference_depth (int): See anima.dcc.maya.Maya.open().

    Raises:
        RuntimeError: If something went wrong.
    """
    m = Maya()
    m.use_progress_window = False  # Maya sets that automatically but let's be sure!
    v = m.get_version_from_full_path(path)
    if not v:
        raise RuntimeError("version not found!")

    m.open(
        v,
        force=True,
        skip_update_check=True,
        prompt=False,
        reference_depth=reference_depth,
    )
    animation.Animation.set_range_from_shot()

    # delete any focusPlane shape nodes to prevent them from being shown in the playblast
    pm.delete(pm.ls(["focusPlane*Shape", "frustumGeo*Shape"]))

    shots = pm.ls(type="shot")
    if shots:
        shot = shots[0]

        camera = None
        if shot:
            camera = pm.PyNode(shot.getCurrentCamera())

        # set only the camera renderable and the rest non renderable
        for cam in pm.ls(type="camera"):
            cam.renderable.set(0)
        if camera:
            camera.renderable.set(1)

            # also create a distant light to fix Maya 2022 bug
            if not pm.ls(type=pm.nt.DirectionalLight):
                light_shape = pm.nt.DirectionalLight()
                light_shape.useRayTraceShadows.set(1)
                light_tra = light_shape.getParent()
                camera_tra = camera.getParent()
                pm.parent(light_tra, camera_tra)
                light_tra.t.set(0, 0, 0)
                light_tra.r.set(0, 0, 0)

    default_view_options = playblast.get_default_playblast_view_options()
    playblast.perform_playblast(
        0,
        resolution=100,
        playblast_view_options=default_view_options,
        upload_to_server=True,
        force_batch_mode=True,
    )
    print("Playblast Done!")
