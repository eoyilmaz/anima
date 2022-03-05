# -*- coding: utf-8 -*-

from anima import logger
from anima.ui.lib import QtCore, QtGui, QtWidgets


class VersionsTableWidget(QtWidgets.QTableWidget):
    """A QTableWidget derivative specialized to hold version data"""

    def __init__(self, parent=None, *args, **kwargs):
        QtWidgets.QTableWidget.__init__(self, parent, *args, **kwargs)

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setShowGrid(False)
        self.setColumnCount(5)
        self.setObjectName("previous_versions_table_widget")
        self.setColumnCount(5)
        self.setRowCount(0)
        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem())
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem())
        self.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem())
        self.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem())
        self.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem())
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setStretchLastSection(False)

        tool_tip_html = (
            '<html><head/><body><p>Right click to:</p><ul style="'
            "margin-top: 0px; margin-bottom: 0px; margin-left: 0px; "
            'margin-right: 0px; -qt-list-indent: 1;"><li><span style=" '
            'font-weight:600;">Copy Path</span></li><li><span style=" '
            'font-weight:600;">Browse Path</span></li><li><span style=" '
            'font-weight:600;">Change Description</span></li></ul>'
            '<p>Double click to:</p><ul style="margin-top: 0px; '
            "margin-bottom: 0px; margin-left: 0px; margin-right: 0px; "
            '-qt-list-indent: 1;"><li style=" margin-top:12px; '
            "margin-bottom:12px; margin-left:0px; margin-right:0px; "
            '-qt-block-indent:0; text-indent:0px;"><span style=" '
            'font-weight:600;">Open</span></li></ul></body></html>'
        )

        try:
            self.setToolTip(
                QtWidgets.QApplication.translate(
                    "Dialog", tool_tip_html, None, QtWidgets.QApplication.UnicodeUTF8
                )
            )
        except AttributeError:
            self.setToolTip(
                QtWidgets.QApplication.translate("Dialog", tool_tip_html, None)
            )

        self.versions = []
        self.labels = [
            "#",
            "App",
            "Created By",
            "Updated By",
            "Size",
            "Date",
            "Description",
        ]
        self.setColumnCount(len(self.labels))

    def clear(self):
        """overridden clear method"""
        QtWidgets.QTableWidget.clear(self)
        self.versions = []

        # reset the labels
        self.setHorizontalHeaderLabels(self.labels)

    def select_version(self, version):
        """selects the given version in the list"""
        # select the version in the previous version list
        index = -1
        for i, prev_version in enumerate(self.versions):
            if self.versions[i].id == version.id:
                index = i
                break

        logger.debug("current index: %s" % index)

        # select the row
        if index != -1:
            item = self.item(index, 0)
            logger.debug("item : %s" % item)
            self.setCurrentItem(item)

    @property
    def current_version(self):
        """returns the current selected version from the table"""
        index = self.currentRow()
        try:
            version = self.versions[index]
            return version
        except IndexError:
            return None

    def update_content(self, versions):
        """updates the content with the given versions data"""
        import os
        import datetime

        logger.debug("VersionsTableWidget.update_content() is started")

        self.clear()
        self.versions = versions
        self.setRowCount(len(versions))

        def set_published_font(item):
            """sets the font for the given item

            :param item: the a QTableWidgetItem
            """
            my_font = item.font()
            my_font.setBold(True)

            item.setFont(my_font)

            foreground = item.foreground()
            foreground.setColor(QtGui.QColor(0, 192, 0))
            item.setForeground(foreground)

        # update the previous versions list
        from anima import defaults

        for i, version in enumerate(versions):
            is_published = version.is_published
            absolute_full_path = os.path.normpath(
                os.path.expandvars(version.full_path)
            ).replace("\\", "/")
            version_file_exists = os.path.exists(absolute_full_path)

            c = 0

            # ------------------------------------
            # version_number
            item = QtWidgets.QTableWidgetItem(str(version.version_number))
            # align to center and vertical center
            item.setTextAlignment(0x0004 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # created_with
            item = QtWidgets.QTableWidgetItem()
            if version.created_with:
                from anima.ui import utils as ui_utils

                app_icon = ui_utils.get_icon(version.created_with.lower())
                if app_icon:
                    item.setIcon(app_icon)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # user.name
            created_by = ""
            if version.created_by_id:
                created_by = defaults.user_names_lut[version.created_by_id]
            item = QtWidgets.QTableWidgetItem(created_by)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # user.name
            updated_by = ""
            if version.updated_by_id:
                updated_by = defaults.user_names_lut[version.updated_by_id]
            item = QtWidgets.QTableWidgetItem(updated_by)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # file size

            # get the file size
            # file_size_format = "%.2f MB"
            file_size = -1
            if version_file_exists:
                file_size = float(os.path.getsize(absolute_full_path)) / 1048576

            from anima import defaults

            item = QtWidgets.QTableWidgetItem(defaults.file_size_format % file_size)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # date

            # get the file date
            file_date = datetime.datetime.today()
            if version_file_exists:
                file_date = datetime.datetime.fromtimestamp(
                    os.path.getmtime(absolute_full_path)
                )
            item = QtWidgets.QTableWidgetItem(
                file_date.strftime(defaults.date_time_format)
            )

            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # description
            item = QtWidgets.QTableWidgetItem(version.description)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

        # resize the first column
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        logger.debug("VersionsTableWidget.update_content() is finished")


class VersionDetailsWidget(QtWidgets.QWidget):
    """Shows details about a Stalker Version"""

    def __init__(self, version=None, *args, **kwargs):
        super(VersionDetailsWidget, self).__init__(*args, **kwargs)

        self._version = None

        self.task_name_widget = None
        self.version_file_name_widget = None
        self.date_info_widget = None
        self.created_by_widget = None
        self.description_label_widget = None
        self.warning_field = None

        self._setup_ui()
        self.version = version

    def _setup_ui(self):
        """set the ui"""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.main_layout.addLayout(self.form_layout)

        self.setStyleSheet(
            """
            QLabel[labelField="true"] {
                font-weight: bold;
            }
        """
        )

        label_role = QtWidgets.QFormLayout.LabelRole
        field_role = QtWidgets.QFormLayout.FieldRole

        i = -1

        # Task Name
        i += 1
        task_name_label = QtWidgets.QLabel(self)
        task_name_label.setText("Task")
        self.form_layout.setWidget(i, label_role, task_name_label)

        self.task_name_widget = QtWidgets.QLabel(self)
        self.form_layout.setWidget(i, field_role, self.task_name_widget)

        # Version File
        i += 1
        version_label = QtWidgets.QLabel(self)
        version_label.setText("File")
        self.form_layout.setWidget(i, label_role, version_label)

        self.version_file_name_widget = QtWidgets.QLabel(self)
        self.form_layout.setWidget(i, field_role, self.version_file_name_widget)

        # Date
        i += 1
        date_label = QtWidgets.QLabel(self)
        date_label.setText("Date")
        self.form_layout.setWidget(i, label_role, date_label)

        self.date_info_widget = QtWidgets.QLabel(self)
        self.form_layout.setWidget(i, field_role, self.date_info_widget)

        # Created By
        i += 1
        created_by_label = QtWidgets.QLabel(self)
        created_by_label.setText("Created By")
        self.form_layout.setWidget(i, label_role, created_by_label)

        self.created_by_widget = QtWidgets.QLabel(self)
        self.form_layout.setWidget(i, field_role, self.created_by_widget)

        # Description
        i += 1
        description_label = QtWidgets.QLabel(self)
        description_label.setText("Description")
        self.form_layout.setWidget(i, label_role, description_label)

        self.description_label_widget = QtWidgets.QLabel(self)
        self.form_layout.setWidget(i, field_role, self.description_label_widget)

        # Warning
        i += 1
        self.warning_field = QtWidgets.QLabel(self)
        self.main_layout.addWidget(self.warning_field)

    def fill_ui(self):
        """fills the ui with version info"""
        if not self.version:
            return

        import os

        self.task_name_widget.setText(self.version.task.name)
        self.version_file_name_widget.setText(os.path.basename(self.version.fullpath))
        self.date_info_widget.setText(
            self.version.date_created.strftime("%d-%m-%Y %H:%M")
        )
        self.created_by_widget.setText(
            self.version.created_by.name
            if self.version.created_by
            else "-- creator missing --"
        )
        self.description_label_widget.setText(self.version.description)

    @property
    def version(self):
        """getter of the version property"""
        return self._version

    @version.setter
    def version(self, version):
        """setter for the version property

        :param version: A Stalker Version instance
        :return:
        """
        if not version:
            return

        from stalker import Version

        if not isinstance(version, Version):
            raise TypeError(
                "%s.version should be set to a Stalker Version instance, not %s"
                % (self.__class__.__name__, version.__class__.__name__)
            )

        self._version = version

        # update ui elements
        self.fill_ui()
