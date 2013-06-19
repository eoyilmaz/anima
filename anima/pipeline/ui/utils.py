# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Utilities for UI stuff
"""
import sys
import os
import logging

from stalker import Version

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

from anima.pipeline.ui.lib import QtCore, QtGui


class AnimaDialogBase(object):
    """A simple class to hold basic common functions for dialogs
    """

    def center_window(self):
        """centers the window to the screen
        """
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) * 0.5,
            (screen.height() - size.height()) * 0.5
        )


def UICaller(app_in, executor, DialogClass, **kwargs):
    global app
    global mainDialog
    self_quit = False
    if QtGui.QApplication.instance() is None:
        if not app_in:
            try:
                app = QtGui.QApplication(sys.argv)
            except AttributeError: # sys.argv gives argv.error
                app = QtGui.QApplication([])
        else:
            app = app_in
        self_quit = True
    else:
        app = QtGui.QApplication.instance()

    mainDialog = DialogClass(**kwargs)
    mainDialog.show()
    if executor is None:
        app.exec_()
        if self_quit:
            app.connect(
                app,
                QtCore.SIGNAL("lastWindowClosed()"),
                app,
                QtCore.SLOT("quit()")
            )
    else:
        executor.exec_(app, mainDialog)
    return mainDialog


def clear_thumbnail(gView):
    """Clears the thumbnail for the given QGraphicsView
    
    :param gView: The QGraphicsView instance
    """

    if not gView:
        return

    # clear the graphics scene in case there is no thumbnail
    scene = gView.scene()
    if not scene:
        scene = QtGui.QGraphicsScene(gView)
        gView.setScene(scene)

    scene.clear()


def update_gview_with_version_thumbnail(version, gView):
    """Updates the given QGraphicsView with the given Version thumbnail.
    
    :param version: A
      :class:`~stalker.models.version.Version` instance
    
    :param gView: A QtGui.QGraphicsView instance
    """

    if not isinstance(version, Version) or \
            not isinstance(gView, QtGui.QGraphicsView):
        # do nothing
        return

    # get the thumbnail full path
    if version.thumbnail:
        update_gview_with_image_file(
            version.thumbnail.full_path,
            gView
        )


def update_gview_with_image_file(image_full_path, gView):
    """updates the QGraphicsView with the given image
    """

    if not isinstance(gView, QtGui.QGraphicsView):
        return

    clear_thumbnail(gView)

    if image_full_path != "":
        logger.debug("creating pixmap from: %s" % image_full_path)

        # size = conf.thumbnail_size
        # width = size[0]
        # height = size[1]

        if os.path.exists(image_full_path):
            # pixmap = QtGui.QPixmap(image_full_path, format='JPG').scaled(
            #     width, height,
            #     QtCore.Qt.KeepAspectRatio,
            #     QtCore.Qt.SmoothTransformation
            # )
            pixmap = QtGui.QPixmap(image_full_path, format='JPG')

            scene = gView.scene()
            scene.addPixmap(pixmap)


def upload_thumbnail(entity, thumbnail_source_full_path):
    """Uploads the given thumbnail for the given entity
    
    :param entity: An instance of :class:`~stalker.models.entity.SimpleEntity`
      or a derivative.
    
    :param str thumbnail_source_full_path: A string which is showing the path
      of the thumbnail image
    """

    # get width height
    # width = size[0]
    # height = size[0]

    thumbnail_full_path = entity.thumbnail.full_path

    # upload the chosen image to the repo, overwrite any image present
    # create the dirs
    try:
        os.makedirs(os.path.split(thumbnail_full_path)[0])
    except OSError:
        # dir exists
        pass

    # instead of copying the item
    # just render a resized version to the output path
    pixmap = QtGui.QPixmap(thumbnail_source_full_path, format='JPG')#.scaled(
    # width, height,
    # QtCore.Qt.KeepAspectRatio,
    # QtCore.Qt.SmoothTransformation
    # )
    # now render it to the path
    # pixmap.save(
    #     thumbnail_full_path,
    #     conf.thumbnail_format,
    #     conf.thumbnail_quality
    # )
    pixmap.save(thumbnail_full_path, 'jpg', 85)


def choose_thumbnail(parent):
    """shows a dialog for thumbnail upload
    """
    # get a file from a FileDialog
    thumbnail_full_path = QtGui.QFileDialog.getOpenFileName(
        parent, "Choose Thumbnail",
        os.path.expanduser("~"),
        "Image Files (*.png *.jpg *.bmp)"
    )

    if isinstance(thumbnail_full_path, tuple):
        thumbnail_full_path = thumbnail_full_path[0]

    return thumbnail_full_path


def render_image_from_gview(gview, image_full_path):
    """renders the gview scene to an image at the given full path
    """
    assert isinstance(gview, QtGui.QGraphicsView)
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



