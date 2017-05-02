# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui import IS_PYSIDE, IS_PYSIDE2, IS_PYQT4
from anima.ui.lib import QtCore, QtWidgets, QtGui


if IS_PYSIDE():
    from anima.ui.ui_compiled import task_dialog_UI_pyside as task_dialog_UI
elif IS_PYSIDE2():
    from anima.ui.ui_compiled import task_dialog_UI_pyside2 as task_dialog_UI
elif IS_PYQT4():
    from anima.ui.ui_compiled import task_dialog_UI_pyqt4 as task_dialog_UI
reload(task_dialog_UI)


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, task_dialog_UI.Ui_Dialog, AnimaDialogBase):
    """The Task Dialog
    """

    def __init__(self, parent=None, parent_task=None, task=None):
        logger.debug("initializing the interface")
        # store the logged in user
        self.logged_in_user = None

        self.parent_task = parent_task
        self.task = task

        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        self._set_defaults()

    def close(self):
        logger.debug('closing the ui')
        QtWidgets.QDialog.close(self)

    def show(self):
        """overridden show method
        """
        logger.debug('MainDialog.show is started')
        self.logged_in_user = self.get_logged_in_user()
        if not self.logged_in_user:
            self.close()
            return_val = None
        else:
            return_val = super(MainDialog, self).show()

        logger.debug('MainDialog.show is finished')
        return return_val

    def _set_defaults(self):
        """sets the defaults fro the ui
        """
        # fill projects list
        self.projects_comboBox.clear()
        from stalker import Project
        self.projects_comboBox.addItems(
            sorted([p.name for p in Project.query.all()])
        )
