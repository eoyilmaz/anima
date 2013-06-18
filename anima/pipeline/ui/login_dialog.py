# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import logging
from sqlalchemy import or_

import anima
from anima.pipeline.ui import (UICaller, AnimaDialogBase, IS_PYQT4, IS_PYSIDE,
                               QtGui, QtCore)

# create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

if IS_PYSIDE():
    from anima.pipeline.ui.ui_compiled import login_dialog_UI_pyside as login_dialog_UI
elif IS_PYQT4():
    from anima.pipeline.ui.ui_compiled import login_dialog_UI_pyqt4 as login_dialog_UI


def UI(app_in=None, executor=None):
    """the UI to call the dialog by itself

    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.
    """
    return UICaller(app_in, executor, MainDialog)


class MainDialog(QtGui.QDialog, login_dialog_UI.Ui_Dialog, AnimaDialogBase):
    """This is a simple login dialog which connects to Stalker to authenticate
    the username/password couple.
    """

    def __init__(self, parent=None):
        logger.debug("initializing the interface")

        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        window_title = 'Login Dialog | ' + \
                       'Anima v' + anima.__version__

        # change the window title
        self.setWindowTitle(window_title)

        # create some default data
        self.success = False

        # setup signals
        self._setup_signals()

        # center window
        self.center_window()

        logger.debug("finished initializing the interface")

    def _setup_signals(self):
        """sets up the signals
        """

        logger.debug("start setting up interface signals")

        # cancel button
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL('rejected()'),
            self.close
        )

        # Ok button
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL('accepted()'),
            self.login
        )

        logger.debug("finished setting up interface signals")

    def login(self):
        """does the nasty details for user to login
        """

        # check the given user password
        from stalker import db, User

        # connect to the default database
        db.setup()

        # get the user first
        login = self.login_or_email_lineEdit.text()
        password = self.password_lineEdit.text()

        # check with the login or email attribute
        user = User.query \
            .filter(or_(User.login == login, User.email == login)) \
            .first()

        if user:
            self.success = user.check_password(password)

        if self.success:
            from stalker.models.auth import LocalSession

            session = LocalSession()
            session.store_user(user)
            session.save()

            self.accept()
        else:
            QtGui.QMessageBox.critical(
                self,
                "Error",
                "login or password is incorrect"
            )

