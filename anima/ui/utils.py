# -*- coding: utf-8 -*-
"""Utilities for UI stuff
"""
import os

from anima import logger
from anima.ui.lib import QtCore, QtGui, QtWidgets


def get_icon(icon_name):
    """Returns an icon from ui library
    """
    import time
    start_time = time.time()
    # get the icon from cache if possible
    from anima.ui import ICON_CACHE
    q_icon = ICON_CACHE.get(icon_name)
    if not q_icon:
        logger.debug("getting icon from the cache!")
        # use the local icon cache
        import os
        from anima import defaults
        local_icon_cache_path = os.path.normpath(
            os.path.expanduser(
                os.path.join(defaults.local_cache_folder, "icons")
            )
        )
        local_icon_full_path = os.path.join(local_icon_cache_path, "%s.png" % icon_name)
        logger.debug("local_icon_full_path: %s" % local_icon_full_path)
        if not os.path.exists(local_icon_full_path):
            logger.debug("local icon cache not found: %s" % icon_name)
            logger.debug("retrieving icon from library!")
            here = os.path.abspath(os.path.dirname(__file__))
            images_path = os.path.join(here, 'images')
            icon_full_path = os.path.join(images_path, "%s.png" % icon_name)
            logger.debug("icon_full_path: %s" % icon_full_path)

            # copy to local cache folder
            try:
                os.makedirs(local_icon_cache_path)
            except OSError:
                pass

            import shutil
            try:
                shutil.copy(icon_full_path, local_icon_full_path)
            except (OSError, IOError):
                # original icon doesn't exist
                return None
        q_icon = QtGui.QIcon(local_icon_full_path)
        ICON_CACHE[icon_name] = q_icon
    logger.debug("get_icon took: %0.6f s" % (time.time() - start_time))
    return q_icon


def clear_thumbnail(graphics_view):
    """Clears the thumbnail for the given QGraphicsView

    :param graphics_view: The QGraphicsView instance
    """

    if not graphics_view:
        return

    # clear the graphics scene in case there is no thumbnail
    scene = graphics_view.scene()
    if not scene:
        scene = QtWidgets.QGraphicsScene(graphics_view)
        graphics_view.setScene(scene)

    scene.clear()


def update_graphics_view_with_task_thumbnail(task, graphics_view):
    """Updates the given QGraphicsView with the given Task thumbnail

    :param task: A
      :class:`~stalker.models.task.Task` instance

    :param graphics_view: A QtGui.QGraphicsView instance
    """
    from stalker import Task

    if not isinstance(task, Task) or \
       not isinstance(graphics_view, QtWidgets.QGraphicsView):
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
        update_graphics_view_with_image_file(full_path, graphics_view)


def update_graphics_view_with_image_file(image_full_path, graphics_view):
    """updates the QGraphicsView with the given image
    """

    if not isinstance(graphics_view, QtWidgets.QGraphicsView):
        return

    clear_thumbnail(graphics_view)

    if image_full_path != "":
        image_full_path = os.path.normpath(image_full_path)
        image_format = os.path.splitext(image_full_path)[-1].replace('.', '').upper()
        logger.debug("creating pixmap from: %s" % image_full_path)

        # size = conf.thumbnail_size
        # width = size[0]
        # height = size[1]
        size = graphics_view.size()
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

            scene = graphics_view.scene()
            scene.addPixmap(pixmap)


def choose_thumbnail(parent, start_path=None, dialog_title="Choose Thumbnail"):
    """shows a dialog for thumbnail upload
    """

    if start_path is None:
        start_path = os.path.expanduser("~")

    # get a file from a FileDialog
    thumbnail_full_path = QtWidgets.QFileDialog.getOpenFileName(
        parent, dialog_title,
        start_path,
        # "Image Files (*.png *.jpg *.bmp *.tga *.tif *.tiff *.exr)"
        "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
    )

    if isinstance(thumbnail_full_path, tuple):
        thumbnail_full_path = thumbnail_full_path[0]

    return thumbnail_full_path


def render_image_from_graphics_view(graphics_view, image_full_path):
    """renders the graphics view scene to an image at the given full path
    """
    assert isinstance(graphics_view, QtWidgets.QGraphicsView)
    scene = graphics_view.scene()
    # there should be only one item
    items = scene.items()
    if items:
        pixmap_item = items[0]
        pixmap = pixmap_item.pixmap()
        try:
            os.makedirs(os.path.split(image_full_path)[0])
        except OSError:
            # dir exists
            pass

        pixmap.save(
            image_full_path
        )


def initialize_post_publish_dialog():
    """
    A frameless, staysOnTop dialog to be initialized during post publish process
    for locking its application and actually show user that post publishes are in progress.
    """
    try:
        _fromUtf8 = QtCore.QString.fromUtf8
    except AttributeError:
        def direct_drive(s):
            return s
        _fromUtf8 = direct_drive

    dialog = QtWidgets.QDialog()
    dialog.vertical_layout = QtWidgets.QVBoxLayout(dialog)
    dialog.label = QtWidgets.QLabel(dialog.vertical_layout.widget())
    dialog.label.setText('POST PUBLISH IN PROGRESS')
    dialog.label.setStyleSheet(_fromUtf8("color: rgb(20, 255, 20);\n""font: 16pt;"))
    dialog.vertical_layout.addWidget(dialog.label)
    dialog.label1 = QtWidgets.QLabel(dialog.vertical_layout.widget())
    dialog.label1.setText('PLEASE WAIT...')
    dialog.label1.setAlignment(QtCore.Qt.AlignCenter)
    dialog.vertical_layout.addWidget(dialog.label1)
    dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    dialog.setWindowModality(QtCore.Qt.ApplicationModal)

    return dialog


def load_font(font_filename):
    """loads extra fonts from the fonts folder
    """
    import time
    start_time = time.time()
    # get the font from cache if possible
    from anima.ui import FONT_CACHE
    font_family = FONT_CACHE.get(font_filename)
    if not font_family:
        logger.debug("font not found in runtime cache!")
        logger.debug("getting font from local cache!")
        # use the local font cache
        import os
        from anima import defaults
        local_font_cache_path = os.path.normpath(
            os.path.expanduser(
                os.path.join(
                    defaults.local_cache_folder, "fonts"
                )
            )
        )
        local_font_full_path = os.path.join(local_font_cache_path, font_filename)
        logger.debug("local_font_full_path: %s" % local_font_full_path)
        if not os.path.exists(local_font_full_path):
            logger.debug("local font cache not found: %s" % font_filename)
            logger.debug("retrieving font from library!")
            here = os.path.dirname(os.path.realpath(__file__))
            font_full_path = os.path.join(here, 'fonts', font_filename)
            logger.debug("font_full_path: %s" % font_full_path)

            # copy to local cache folder
            try:
                os.makedirs(local_font_cache_path)
            except OSError:
                pass

            import shutil
            try:
                shutil.copy(font_full_path, local_font_full_path)
            except OSError:
                # original font doesn't exist either
                pass

        font_id = QtGui.QFontDatabase.addApplicationFont(local_font_full_path)
        font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        FONT_CACHE[font_filename] = font_family
    else:
        logger.debug("font found in runtime cache!")

    logger.debug("load_font took: %0.6f s" % (time.time() - start_time))
    return font_family


def add_button(label, layout, callback, tooltip='', callback_kwargs=None):
    """A wrapper for button creation

    :param label: The label of the button
    :param layout: The layout that the button is going to be placed under.
    :param callback: The callable that will be called when the button is
      clicked.
    :param str tooltip: Optional tooltip for the button
    :param callback_kwargs: Callback arguments
    :return:
    """
    if tooltip == '':
        tooltip = callback.__doc__

    # button
    button = QtWidgets.QPushButton(layout.parentWidget())
    button.setText(label)
    layout.addWidget(button)

    button.setToolTip(tooltip)

    # Signal
    if callback_kwargs:
        import functools
        callback = functools.partial(callback, **callback_kwargs)

    QtCore.QObject.connect(
        button,
        QtCore.SIGNAL("clicked()"),
        callback
    )

    return button


def add_line(layout):
    """Adds a horizontal line

    :param layout:
    :return:
    """

    line = QtWidgets.QFrame(layout.parent())
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    layout.addWidget(line)


class ColorList(object):
    """a simple color list class

    :param int index: The start index.
    :param float gamma: The gamma. Defaults to 1.0.
    """
    colors = [
        (1.000, 0.500, 0.666),
        (1.000, 0.833, 0.500),
        (0.666, 1.000, 0.500),
        (0.500, 1.000, 0.833),
        (0.500, 0.666, 1.000),
        (0.833, 0.500, 1.000)
    ]

    def __init__(self, index=0, gamma=1.0):
        self.index = index
        self.gamma = gamma
        self.max_colors = len(self.colors)

    def next(self):
        """updates the index to the next one
        """
        self.index = int((self.index + 1) % self.max_colors)

    def reset(self):
        """resets the color index
        """
        self.index = 0

    @property
    def color(self):
        """returns the current color values
        """
        return list(map(lambda x: pow(x, self.gamma), self.colors[self.index]))


def set_widget_bg_color(widget, color):
    """Sets the bg color of the given widget to the given ColorList instance

    :param widget: A QtWidget instance
    :param color: A ColorList instance
    :return:
    """
    widget.setStyleSheet(
        "background-color: rgba(%s, %s, %s, 1);" % (
            int(color.color[0] * 255),
            int(color.color[1] * 255),
            int(color.color[2] * 255)
        )
    )
