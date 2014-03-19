# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.ui import IS_PYSIDE, IS_PYQT4
from anima.ui.utils import UICaller, AnimaDialogBase
from anima.ui.lib import QtGui, QtCore


if IS_PYSIDE():
    from anima.ui.ui_compiled import edl_importer_UI_pyside as edl_importer_UI
elif IS_PYQT4():
    from anima.ui.ui_compiled import edl_importer_UI_pyqt4 as edl_importer_UI


def UI(app_in=None, executor=None, **kwargs):
    """
    :param environment: The
      :class:`~stalker.models.env.EnvironmentBase` can be None to let the UI to
      work in "environmentless" mode in which it only creates data in database
      and copies the resultant version file path to clipboard.

    :param mode: Runs the UI either in Read-Write (0) mode or in Read-Only (1)
      mode.

    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return UICaller(app_in, executor, MainWindow, **kwargs)


class MainWindow(QtGui.QMainWindow, edl_importer_UI.Ui_MainWindow,
                 AnimaDialogBase):
    """The Main Window for EDL Importer.

    This is mainly written for AVID Media Composer. It makes it easy to import
    edl files and clips to AVID.

    For now, the editor still needs to do some manual actions to import the EDL
    content to AVID (we hate it).
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setup_signals()

    def setup_signals(self):
        """setting up signals
        """
        pass
