# -*- coding: utf-8 -*-
# anima-tools
# Copyright (C) 2013 Erkan Ozgur Yilmaz
#
# This file is part of anima-tools.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA


def version_creator(lib='PySide'):
    """Initializes the version_creator UI.

    It uses with PySide by default you can opt to use PyQt4 instead by setting
    the ``lib`` argument to "PyQt4".

    :param str lib: choose a lib, one of ["PySide", "PyQt4"]
    :return: None
    """
    from stalker import db
    from stalker.db import DBSession
    DBSession.remove()
    db.setup()

    from anima.pipeline.ui import SET_PYSIDE, SET_PYQT4
    if lib == 'PySide':
        SET_PYSIDE()
    elif lib == 'PyQt4':
        SET_PYQT4()

    from anima.pipeline.env.photoshopEnv import PhotoshopEnv
    pEnv = PhotoshopEnv()

    from anima.pipeline.ui import version_creator
    # paste only warning messages
    import logging
    logging.getLogger(version_creator.__name__).setLevel(logging.WARNING)
    logging.getLogger("anima.pipeline.ui").setLevel(logging.WARNING)
    logging.getLogger("anima.pipeline.env.photoshopEnv").setLevel(logging.WARNING)
    logging.getLogger("stalker.db").setLevel(logging.WARNING)

    return version_creator.UI(pEnv)

