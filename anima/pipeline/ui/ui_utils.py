# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Utilities for UI stuff
"""

import os
import logging
from oyProjectManager import conf
from oyProjectManager.models.entity import VersionableBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

qt_module_key = "PREFERRED_QT_MODULE"
qt_module = "PyQt4"

if os.environ.has_key(qt_module_key):
    qt_module = os.environ[qt_module_key]

if qt_module == "PySide":
    from PySide import QtGui, QtCore
elif qt_module == "PyQt4":
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtGui, QtCore

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

def update_gview_with_versionable_thumbnail(versionable, gView):
    """Updates the given QGraphicsView with the given Versionable thumbnail.
    
    :param versionable: A
      :class:`~oyProjectManager.models.entity.VersionableBase` instance
    
    :param gView: A QtGui.QGraphicsView instance
    """
    
    if not isinstance(versionable, VersionableBase) or \
       not isinstance(gView, QtGui.QGraphicsView):
        # do nothing
        return
    
    # get the thumbnail full path
    update_gview_with_image_file(
        versionable.thumbnail_full_path,
        gView
    )

def update_gview_with_image_file(image_full_path, gView):
    """updates the QGraphicsView with the given image
    """
    
    if not isinstance(gView, QtGui.QGraphicsView) and \
        not isinstance(versionable, VersionableBase):
        return
    
    clear_thumbnail(gView)
    
    if image_full_path != "":
        logger.debug("creating pixmap from: %s" % image_full_path)
        
        size = conf.thumbnail_size
        width = size[0]
        height = size[1]
        
        if os.path.exists(image_full_path):
            pixmap = QtGui.QPixmap(image_full_path, format='JPG').scaled(
                width, height,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            
            scene = gView.scene()
            scene.addPixmap(pixmap)

def upload_thumbnail(versionable, thumbnail_source_full_path, size=conf.thumbnail_size):
    """Uploads the given thumbnail for the given versionable
    
    :param versionable: An instance of
      :class:`~oyProjectManager.models.entity.VersionableBase` which in
      practice is an :class:`~oyProjectManager.models.asset.Asset` or
      a :class:`~oyProjectManager.models.shot.Shot`.
    
    :param str thumbnail_source_full_path: A string which is showing the path
      of the thumbnail image
    """
    
    # get width height
    width = size[0]
    height = size[0]
    
    thumbnail_full_path = versionable.thumbnail_full_path
    
    # upload the chosen image to the repo, overwrite any image present
    # create the dirs
    try:
        os.makedirs(os.path.split(thumbnail_full_path)[0])
    except OSError:
        # dir exists
        pass
    
    # instead of copying the item
    # just render a resized version to the output path
    pixmap = QtGui.QPixmap(thumbnail_source_full_path, format='JPG').scaled(
        width, height,
        QtCore.Qt.KeepAspectRatio,
        QtCore.Qt.SmoothTransformation
    )
    # now render it to the path
    pixmap.save(
        thumbnail_full_path,
        conf.thumbnail_format,
        conf.thumbnail_quality
    )

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
