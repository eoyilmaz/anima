# -*- coding: utf-8 -*-

from anima.ui.lib import QtCore, QtWidgets


APPROVE = "Approve"
REQUEST_REVISION = "Request Revision"


class ReviewWidget(QtWidgets.QWidget):
    """A widget for reviewing Tasks.
    """

    def __init__(self, task=None, review_type=None, reviewer=None, *args, **kwargs):
        super(ReviewWidget, self).__init__(*args, **kwargs)
        self._task = None
        self._reviewer = None
        self.review_type = review_type

        self.task_name_widget = None
        # self.latest_version_widget = None
        self.review_type_widget = None
        self.timing_widget = None
        self.description_widget = None

        self._setup_ui()

        self.task = task
        self.reviewer = reviewer

        self.fill_ui()

    def _setup_ui(self):
        """sets up the ui
        """
        from functools import partial

        self.setStyleSheet("""
        QLabel[labelField="true"] {
            font-weight: bold;
        }
        """)

        # The main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # the form layout
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight |
            QtCore.Qt.AlignTrailing |
            QtCore.Qt.AlignVCenter
        )

        # store roles
        label_role = QtWidgets.QFormLayout.LabelRole
        field_role = QtWidgets.QFormLayout.FieldRole

        self.main_layout.addLayout(self.form_layout)

        i = -1

        # Reviewer
        i += 1
        reviewer_name_label = QtWidgets.QLabel(self)
        reviewer_name_label.setText("Reviewer")
        self.form_layout.setWidget(i, label_role, reviewer_name_label)

        self.reviewer_name_widget = QtWidgets.QLabel(self)
        self.form_layout.setWidget(i, field_role, self.reviewer_name_widget)

        # Task Name field
        i += 1
        task_name_label = QtWidgets.QLabel(self)
        task_name_label.setText("Task")
        self.form_layout.setWidget(i, label_role, task_name_label)

        self.task_name_widget = QtWidgets.QLabel(self)
        self.form_layout.setWidget(i, field_role, self.task_name_widget)

        # # Version Info field
        # from anima.ui.widgets.version import VersionDetailsWidget
        # self.latest_version_widget = VersionDetailsWidget(parent=self)
        # self.main_layout.insertWidget(0, self.latest_version_widget)

        # Review Type Field
        i += 1
        review_type_label = QtWidgets.QLabel(self)
        review_type_label.setText("Review Type")
        self.form_layout.setWidget(i, label_role, review_type_label)

        self.review_type_widget = ReviewTypeWidget(self)
        self.review_type_widget.currentIndexChanged.connect(partial(self.review_type_changed_callback))

        self.form_layout.setWidget(i, field_role, self.review_type_widget)

        # Timing Field
        i += 1
        effort_label = QtWidgets.QLabel(self)
        effort_label.setText("Timing")
        self.form_layout.setWidget(i, label_role, effort_label)

        effort_layout = QtWidgets.QHBoxLayout()
        self.form_layout.setLayout(i, field_role, effort_layout)

        from anima.ui.widgets.timing import ScheduleTimingWidget
        from anima import defaults
        self.timing_widget = ScheduleTimingWidget(self, timing_resolution=defaults.timing_resolution)
        self.timing_widget.setEnabled(False)
        # set the default to 1 hour
        self.timing_widget.set_schedule_info(timing=1, unit="h")
        effort_layout.addWidget(self.timing_widget)

        # Description Field
        i += 1
        description_label = QtWidgets.QLabel(self)
        description_label.setText("Description")
        self.form_layout.setWidget(i, label_role, description_label)

        self.description_widget = QtWidgets.QTextEdit(self)
        self.form_layout.setWidget(i, field_role, self.description_widget)

    def fill_ui(self):
        """fills the ui with the given data
        """
        self.review_type_widget.set_review_type(self.review_type)

        if self.reviewer:
            self.reviewer_name_widget.setText(self.reviewer.name)

        if self.task:
            self.task_name_widget.setText("%s (%s) (%s)" % (
                self.task.name,
                ' | '.join([self.task.project.name] + [parent_task.name for parent_task in self.task.parents]),
                self.task.id
            ))

        # from stalker import Version
        # version = Version.query.filter(Version.task == self.task).order_by(Version.date_created.desc()).first()
        #
        # if version:
        #     self.latest_version_widget.version = version

    @property
    def reviewer(self):
        """getter for the reviewer property
        """
        return self._reviewer

    @reviewer.setter
    def reviewer(self, reviewer):
        """setter for the reviewer property

        :param reviewer: A Stalker User instance
        :return:
        """
        if not reviewer:
            return

        from stalker import User
        if not isinstance(reviewer, User):
            raise TypeError(
                "%s.reviewer should be a stalker.User instance, not %s" % (
                    self.__class__.__name__, reviewer.__class__.__name__
                )
            )
        self._reviewer = reviewer

        self.fill_ui()

    @property
    def task(self):
        """getter for the task property
        """
        return self._task

    @task.setter
    def task(self, task):
        """setter for the task property

        :param task: A Stalker Task instance
        :return:
        """
        if not task:
            return

        from stalker import Task
        if not isinstance(task, Task):
            raise TypeError(
                "%s.task should be a stalker.Task instance, not %s" % (
                    self.__class__.__name__, task.__class__.__name__
                )
            )
        self._task = task

        self.fill_ui()

    def review_type_changed_callback(self, index):
        """callback function for review type

        :param index:
        :return:
        """
        current_text = self.review_type_widget.currentText()
        self.review_type = current_text
        if current_text == "Approve":
            self.timing_widget.setEnabled(False)
        else:
            self.timing_widget.setEnabled(True)

    def finalize_review(self):
        """finalizes the review
        """
        if self.task:
            if self.review_type == REQUEST_REVISION:
                reviewer = self.reviewer
                description = self.description_widget.toPlainText()
                timing, unit, model = self.timing_widget.get_schedule_info()
                review = self.task.request_revision(
                    schedule_timing=timing,
                    schedule_unit=unit,
                    reviewer=reviewer,
                    description=description
                )
                return review
            elif self.review_type == APPROVE:
                # self.task.approve(reviewer)
                pass


class ReviewTypeWidget(QtWidgets.QComboBox):
    """A combo box that holds review types
    """

    def __init__(self, *args, **kwargs):
        super(ReviewTypeWidget, self).__init__(*args, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        self.clear()
        self.addItems([APPROVE, REQUEST_REVISION])

    def set_review_type(self, review_type):
        """sets the current review type

        :param review_type:
        :return:
        """
        if review_type not in [APPROVE, REQUEST_REVISION]:
            raise RuntimeError("%s.review_type should be set to either %s or %s, not %s" % (
                self.__class__.__name__, APPROVE, REQUEST_REVISION, review_type
            ))

        index = self.findText(review_type)
        if index != -1:
            self.setCurrentIndex(index)

    def get_review_type(self):
        """returns the current review type
        """
        return self.currentText()
