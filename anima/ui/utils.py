# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Utilities for UI stuff
"""
import os
import shutil

from anima import logger
from anima.ui.lib import QtCore, QtGui, QtWidgets


def get_icon(icon_name):
    """Returns an icon from ui library
    """
    here = os.path.abspath(os.path.dirname(__file__))
    images_path = os.path.join(here, 'images')
    icon_full_path = os.path.join(images_path, icon_name)
    return QtGui.QIcon(icon_full_path)


def clear_thumbnail(gview):
    """Clears the thumbnail for the given QGraphicsView

    :param gview: The QGraphicsView instance
    """

    if not gview:
        return

    # clear the graphics scene in case there is no thumbnail
    scene = gview.scene()
    if not scene:
        scene = QtWidgets.QGraphicsScene(gview)
        gview.setScene(scene)

    scene.clear()


def update_gview_with_task_thumbnail(task, gview):
    """Updates the given QGraphicsView with the given Task thumbnail

    :param task: A
      :class:`~stalker.models.task.Task` instance

    :param gview: A QtGui.QGraphicsView instance
    """
    from stalker import Task

    if not isinstance(task, Task) or \
       not isinstance(gview, QtWidgets.QGraphicsView):
        # do nothing
        logger.debug('task is not a stalker.models.task.Task instance')
        return

    # get the thumbnail full path
    full_path = None
    if task.thumbnail:
        # use the cache system to get the thumbnail
        # try to get it as a normal file
        full_path = os.path.expandvars(
            task.thumbnail.full_path
        )
        if not os.path.exists(full_path):
            full_path = None
    else:
        logger.debug('there is no thumbnail')
        # try to get the thumbnail from parents
        for parent in reversed(task.parents):
            if parent.thumbnail:
                # try to get it as a normal file
                full_path = os.path.expandvars(
                    parent.thumbnail.full_path
                )
                if not os.path.exists(full_path):
                    full_path = None
                logger.debug('found parent thumbnail at: %s' % full_path)
                break

    if full_path:
        update_gview_with_image_file(
            full_path,
            gview
        )


def update_gview_with_image_file(image_full_path, gview):
    """updates the QGraphicsView with the given image
    """

    if not isinstance(gview, QtWidgets.QGraphicsView):
        return

    clear_thumbnail(gview)

    if image_full_path != "":
        image_full_path = os.path.normpath(image_full_path)
        image_format = os.path.splitext(image_full_path)[-1].replace('.', '').upper()
        logger.debug("creating pixmap from: %s" % image_full_path)

        # size = conf.thumbnail_size
        # width = size[0]
        # height = size[1]
        size = gview.size()
        width = size.width()
        height = size.height()
        logger.debug('width: %s' % width)
        logger.debug('height: %s' % height)

        if os.path.exists(image_full_path):
            pixmap = QtGui.QPixmap(image_full_path, format=image_format).scaled(
                width, height,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            # pixmap = QtGui.QPixmap(image_full_path, format='JPG')

            scene = gview.scene()
            scene.addPixmap(pixmap)


def upload_thumbnail(task, thumbnail_full_path):
    """Uploads the given thumbnail for the given entity

    :param task: An instance of :class:`~stalker.models.entity.SimpleEntity`
      or a derivative.

    :param str thumbnail_full_path: A string which is showing the path
      of the thumbnail image
    """
    extension = os.path.splitext(thumbnail_full_path)[-1]

    # move the file to the task thumbnail folder
    # and mimic StalkerPyramids output format
    thumbnail_original_file_name = 'thumbnail%s' % extension
    thumbnail_final_full_path = os.path.join(
        task.absolute_path, 'Thumbnail', thumbnail_original_file_name
    )

    try:
        os.makedirs(os.path.dirname(thumbnail_final_full_path))
    except OSError:
        pass

    # # convert the thumbnail to jpg if it is a format that is not supported by
    # # browsers
    # ext_not_supported_by_browsers = ['.bmp', '.tga', '.tif', '.tiff', '.exr']
    # if extension in ext_not_supported_by_browsers:
    #     # use MediaManager to convert them
    #     from anima.utils import MediaManager
    #     mm = MediaManager()
    #     thumbnail_full_path = mm.generate_image_thumbnail(thumbnail_full_path)

    shutil.copy(thumbnail_full_path, thumbnail_final_full_path)

    from stalker import Link, Version, Repository

    thumbnail_os_independent_path = \
        Repository.to_os_independent_path(thumbnail_final_full_path)
    l_thumb = Link.query\
        .filter(Link.full_path == thumbnail_os_independent_path).first()

    if not l_thumb:
        l_thumb = Link(
            full_path=thumbnail_os_independent_path,
            original_filename=thumbnail_original_file_name
        )

    task.thumbnail = l_thumb

    # get a version of this Task
    from stalker.db.session import DBSession
    v = Version.query.filter(Version.task == task).first()
    if v:
        for naming_parent in v.naming_parents:
            if not naming_parent.thumbnail:
                naming_parent.thumbnail = l_thumb
                DBSession.add(naming_parent)

    DBSession.add(l_thumb)
    DBSession.commit()


def choose_thumbnail(parent):
    """shows a dialog for thumbnail upload
    """
    # get a file from a FileDialog
    thumbnail_full_path = QtWidgets.QFileDialog.getOpenFileName(
        parent, "Choose Thumbnail",
        os.path.expanduser("~"),
        # "Image Files (*.png *.jpg *.bmp *.tga *.tif *.tiff *.exr)"
        "Image Files (*.png *.jpg *.bmp)"
    )

    if isinstance(thumbnail_full_path, tuple):
        thumbnail_full_path = thumbnail_full_path[0]

    return thumbnail_full_path


def render_image_from_gview(gview, image_full_path):
    """renders the gview scene to an image at the given full path
    """
    assert isinstance(gview, QtWidgets.QGraphicsView)
    scene = gview.scene()
    # there should be only one item
    items = scene.items()
    if items:
        pixmapItem = items[0]
        pixmap = pixmapItem.pixmap()
        try:
            os.makedirs(os.path.split(image_full_path)[0])
        except OSError:
            # dir exists
            pass

        pixmap.save(
            image_full_path
        )


def load_font(font_filename):
    """loads extra fonts from the fonts folder
    """
    here = os.path.dirname(os.path.realpath(__file__))
    font_id = QtGui.QFontDatabase.addApplicationFont(
        os.path.join(here, 'fonts', font_filename)
    )
    loaded_font_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
    return loaded_font_families
