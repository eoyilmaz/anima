# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018, Erkan Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtWidgets


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The Project Users Dialog
    """

    def __init__(self, parent=None, project=None):
        super(MainDialog, self).__init__(parent)

        self.project = project

        self._setup_ui()
        self._setup_signals()
        self._set_defaults()

        if self.project:
            self.fill_ui_with_project(self.project)

    def _setup_ui(self):
        """create UI elements
        """
        self.resize(520, 550)
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        # -------------------------
        # Dialog Label
        self.dialog_label = QtWidgets.QLabel(self)
        self.dialog_label.setText('Set Project Users')
        self.dialog_label.setStyleSheet(
            "color: rgb(71, 143, 202);\nfont: 18pt;"
        )
        self.vertical_layout.addWidget(self.dialog_label)
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(self.line)

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight |
            QtCore.Qt.AlignTrailing |
            QtCore.Qt.AlignVCenter
        )
        self.vertical_layout.addLayout(self.form_layout)

        i = -1

        # create Project Combo box
        i += 1
        self.projects_label = QtWidgets.QLabel(self)
        self.projects_label.setText('Projects')
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.projects_label
        )

        self.projects_combo_box = QtWidgets.QComboBox(self)
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.projects_combo_box
        )

        # create DoubleListWidget
        i += 1
        self.users_label = QtWidgets.QLabel(self)
        self.users_label.setText('Users')
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.users_label
        )

        self.users_fields_vertical_layout = QtWidgets.QVBoxLayout()
        self.form_layout.setLayout(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.users_fields_vertical_layout
        )

        from anima.ui.widgets import DoubleListWidget
        self.users_double_list_widget = DoubleListWidget(
            dialog=self,
            parent_layout=self.users_fields_vertical_layout,
            primary_label_text='Users From DB',
            secondary_label_text='Selected Users'
        )
        # set the tooltip
        self.users_double_list_widget\
            .primary_list_widget.setToolTip(
                "Right Click to Create/Update FilenameTemplates"
            )
        self.users_double_list_widget\
            .secondary_list_widget.setToolTip(
                "Right Click to Create/Update FilenameTemplates"
            )

        # Button Box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.vertical_layout.addWidget(self.button_box)
        self.vertical_layout.setStretch(2, 1)

    def _setup_signals(self):
        """setup ui signals
        """
        QtCore.QObject.connect(
            self.projects_combo_box,
            QtCore.SIGNAL("currentIndexChanged(QString)"),
            self.project_changed
        )

        QtCore.QObject.connect(
            self.button_box,
            QtCore.SIGNAL("accepted()"),
            self.accept
        )
        QtCore.QObject.connect(
            self.button_box,
            QtCore.SIGNAL("rejected()"),
            self.reject
        )

    def _set_defaults(self):
        """set defaults
        """
        # fill with projects
        from stalker.db.session import DBSession
        from stalker import Project
        projects_data = \
            DBSession\
                .query(Project.id, Project.name)\
                .order_by(Project.name)\
                .all()

        self.projects_combo_box.clear()
        for p_data in projects_data:
            self.projects_combo_box.addItem(p_data.name, p_data.id)

    def fill_ui_with_project(self, project):
        """

        :param project: A Stalker Project instance
        :return:
        """
        # no project no gain
        if project is None:
            return

        # select the given project in the UI
        index = self.projects_combo_box.findData(project.id)
        if index:
            self.projects_combo_box.setCurrentIndex(index)

    def project_changed(self, project_name):
        """runs when the project in the combo box changed
        """
        project_id = self.projects_combo_box.currentData()

        # refresh the items on the double list widget
        self.users_double_list_widget.clear()

        # get users not in the project
        from stalker.db.session import DBSession
        from stalker import User
        from stalker.models.project import ProjectUser

        project_users = DBSession.query(User.id, User.name).join(ProjectUser)\
            .filter(ProjectUser.project_id == project_id)\
            .filter(User.id == ProjectUser.user_id)\
            .all()

        project_user_ids = [u.id for u in project_users]

        if project_user_ids:
            users_not_in_project = [
                u.name
                for u in DBSession.query(User.name)
                    .filter(~User.id.in_(project_user_ids)).all()
            ]
        else:
            users_not_in_project = [
                u.name
                for u in DBSession.query(User.name).all()
            ]

        self.users_double_list_widget.add_primary_items(
            users_not_in_project
        )

        users_in_project = \
            [u.name for u in project_users]

        self.users_double_list_widget.add_secondary_items(
            users_in_project
        )

    def accept(self):
        """overridden accept method
        """
        # get the project
        project_id = self.projects_combo_box.currentData()

        from stalker import Project
        project = Project.query.get(project_id)

        # get the users
        user_names = [
            item.text() for item in
            self.users_double_list_widget.secondary_items()
        ]

        from stalker import User
        if user_names:
            users = User.query.filter(User.name.in_(user_names))
        else:
            users = []

        # set the project users
        project.users = users
        from stalker.db.session import DBSession
        DBSession.commit()

        super(MainDialog, self).accept()
