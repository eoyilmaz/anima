# -*- coding: utf-8 -*-

from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtWidgets, QtGui


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The TimeLog Dialog
    """

    def __init__(self, parent=None, task=None, timelog=None):
        logger.debug("initializing the interface")
        super(MainDialog, self).__init__(parent)

        # store the logged in user
        self.logged_in_user = None
        self.no_time_left = False
        self.extended_hours = None
        self.extended_minutes = None

        self.timelog = timelog
        self.timelog_created = False
        self.task = task

        # ui element storage
        self.main_layout = None
        self.left_layout = None
        self.right_layout = None
        self.form_layout = None
        self.tasks_label = None
        self.task_progress_bar = None
        self.resources_label = None
        self.resource_combo_box = None
        self.date_label = None
        self.calendar_widget = None

        self.effort_label = None
        self.effort_time_edit = None
        self.show_advanced_time_controls_check_box = None
        self.start_time_label = None
        self.end_time_label = None
        self.start_time_edit = None
        self.end_time_edit = None
        self.updating_timings = False

        self.info_area_label = None
        self.revision_label = None
        self.revision_type_combo_box = None
        self.description_label = None
        self.description_plain_text_edit = None
        self.status_label = None
        self.not_finished_yet_radio_button = None
        self.submit_for_final_review_radio_button = None
        self.dialog_button_box = None
        self.tasks_combo_box = None
        self.formatted_date_label = None
        self.time_log_info_label = None

        self._setup_ui()

    def _setup_ui(self):
        """create UI widgets
        """
        self.resize(447, 546)
        self.setWindowTitle("TimeLog Dialog")

        # -----------------------------
        # Setup Main Layout
        self.main_layout = QtWidgets.QHBoxLayout(self)

        # create the left column
        self.left_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.left_layout)

        # create the right column
        # this will list the previously entered time logs
        self.right_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.right_layout)

        # -----------------------------
        # Setup Form Layout
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.AllNonFixedFieldsGrow
        )
        self.left_layout.addLayout(self.form_layout)

        i = 0
        # -----------------------------
        # Tasks
        self.tasks_label = QtWidgets.QLabel(self)
        self.tasks_label.setText("Task")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.tasks_label
        )

        from anima.ui.widgets import TaskComboBox
        self.tasks_combo_box = TaskComboBox(self)
        self.tasks_combo_box.setObjectName("tasks_combo_box")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.tasks_combo_box
        )

        # -----------------------------
        # Tasks Progress Bar
        i += 1
        self.task_progress_bar = QtWidgets.QProgressBar(self)
        self.task_progress_bar.setProperty("value", 24)
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.task_progress_bar
        )

        # -----------------------------
        # Resources
        i += 1
        self.resources_label = QtWidgets.QLabel(self)
        self.resources_label.setText("Resource")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.resources_label
        )

        self.resource_combo_box = QtWidgets.QComboBox(self)
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.resource_combo_box
        )

        # -----------------------------
        # Calendar, Start & End Time
        i += 1

        # Label
        self.date_label = QtWidgets.QLabel(self)
        self.date_label.setText("Date")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.date_label
        )

        # Calendar Widget
        self.calendar_widget = QtWidgets.QCalendarWidget(self)
        self.calendar_widget.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.calendar_widget
        )

        # -----------------------------
        # Start Time
        from anima.ui.widgets import TimeEdit

        i += 1
        self.start_time_label = QtWidgets.QLabel(self)
        self.start_time_label.setText("Start")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.start_time_label
        )

        from anima import TIMING_RESOLUTION
        self.start_time_edit = TimeEdit(self, resolution=TIMING_RESOLUTION)
        self.start_time_edit.setCurrentSection(QtWidgets.QDateTimeEdit.MinuteSection)
        self.start_time_edit.setCalendarPopup(True)
        self.start_time_edit.setObjectName("start_time_edit")
        self.start_time_edit.setWrapping(True)
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.start_time_edit
        )
        self.start_time_edit.setDisplayFormat("HH:mm")

        # -----------------------------
        # End Time
        i += 1
        self.end_time_label = QtWidgets.QLabel(self)
        self.end_time_label.setText("End")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.end_time_label
        )

        self.end_time_edit = TimeEdit(self, resolution=TIMING_RESOLUTION)
        self.end_time_edit.setCurrentSection(
            QtWidgets.QDateTimeEdit.MinuteSection
        )
        self.end_time_edit.setCalendarPopup(True)
        self.end_time_edit.setObjectName("end_time_edit")
        self.end_time_edit.setWrapping(True)
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.end_time_edit
        )
        self.end_time_edit.setDisplayFormat("HH:mm")

        # -----------------------------
        # Effort
        i += 1

        # Label
        self.effort_label = QtWidgets.QLabel(self)
        self.effort_label.setText("Effort")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.effort_label
        )

        effort_layout = QtWidgets.QHBoxLayout(self)
        self.form_layout.setLayout(
            i,
            QtWidgets.QFormLayout.FieldRole,
            effort_layout
        )

        self.effort_time_edit = TimeEdit(self, resolution=TIMING_RESOLUTION)
        self.effort_time_edit.setCurrentSection(QtWidgets.QDateTimeEdit.MinuteSection)
        self.effort_time_edit.setCalendarPopup(True)
        self.effort_time_edit.setObjectName("effort_time_edit")
        self.effort_time_edit.setWrapping(True)
        # self.form_layout.setWidget(
        #     i,
        #     QtWidgets.QFormLayout.FieldRole,
        #     self.effort_time_edit
        # )
        effort_layout.addWidget(self.effort_time_edit)
        self.effort_time_edit.setDisplayFormat("HH:mm")

        # -----------------------------
        # Advanced Time Controls
        self.show_advanced_time_controls_check_box = QtWidgets.QCheckBox(self)
        self.show_advanced_time_controls_check_box.setText('Advanced Controls')
        effort_layout.addWidget(self.show_advanced_time_controls_check_box)

        # -----------------------------
        # Time Left Info
        i += 1
        self.info_area_label = QtWidgets.QLabel(self)
        self.info_area_label.setText("INFO")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.info_area_label
        )

        # -----------------------------
        # Status
        i += 1
        self.status_label = QtWidgets.QLabel(self)
        self.status_label.setText("Status")
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.status_label
        )

        self.not_finished_yet_radio_button = QtWidgets.QRadioButton(self)
        self.not_finished_yet_radio_button.setText("Not Finished Yet")
        self.not_finished_yet_radio_button.setChecked(True)
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.not_finished_yet_radio_button
        )

        i += 1
        self.submit_for_final_review_radio_button = \
            QtWidgets.QRadioButton(self)
        self.submit_for_final_review_radio_button.setText(
            "Submit For Final Review"
        )
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.submit_for_final_review_radio_button
        )

        # -----------------------------
        # Dialog Button Box
        self.dialog_button_box = QtWidgets.QDialogButtonBox(self)
        self.dialog_button_box.setOrientation(QtCore.Qt.Horizontal)
        self.dialog_button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.left_layout.addWidget(self.dialog_button_box)

        # create the right column which is the current date details
        self.formatted_date_label = QtWidgets.QLabel(self)
        self.formatted_date_label.setText("")
        self.right_layout.addWidget(self.formatted_date_label)

        # create the right column which is the current date details
        self.time_log_info_label = QtWidgets.QLabel(self)
        self.time_log_info_label.setText("")
        self.right_layout.addWidget(self.time_log_info_label)

        # set stretch
        self.main_layout.setStretchFactor(self.left_layout, 0)
        self.main_layout.setStretchFactor(self.right_layout, 1)

        # setup signals
        self._setup_signals()

        # setup defaults
        self._set_defaults()

        # center window
        self.center_window()

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

    def _setup_signals(self):
        """sets up the signals
        """
        logger.debug("start setting up interface signals")

        # Dialog buttons
        QtCore.QObject.connect(
            self.dialog_button_box,
            QtCore.SIGNAL("accepted()"),
            self.accept
        )
        QtCore.QObject.connect(
            self.dialog_button_box,
            QtCore.SIGNAL("rejected()"),
            self.reject
        )

        # tasks_combo_box
        QtCore.QObject.connect(
            self.tasks_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.tasks_combo_box_index_changed
        )

        # start_time_edit
        QtCore.QObject.connect(
            self.start_time_edit,
            QtCore.SIGNAL('timeChanged(QTime)'),
            self.start_time_changed
        )

        # end_time_edit
        QtCore.QObject.connect(
            self.end_time_edit,
            QtCore.SIGNAL('timeChanged(QTime)'),
            self.end_time_changed
        )

        # effort_time_edit
        self.effort_time_edit.timeChanged.connect(self.effort_time_changed)

        # resource changed
        QtCore.QObject.connect(
            self.resource_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.resource_changed
        )

        # calendar day selected
        QtCore.QObject.connect(
            self.calendar_widget,
            QtCore.SIGNAL("selectionChanged()"),
            self.calendar_widget_selection_changed
        )

        self.show_advanced_time_controls_check_box.stateChanged.connect(self.show_advanced_time_controls)

    def _set_defaults(self):
        """sets the defaults for the ui
        """
        logger.debug("started setting up interface defaults")

        from anima import TIMING_RESOLUTION

        # Set Default Value for time
        current_time = QtCore.QTime.currentTime()
        # round the minutes to the resolution
        # minute = current_time.minute()
        # hour = current_time.hour()
        # minute = int(minute / float(TIMING_RESOLUTION)) * TIMING_RESOLUTION

        current_time = QtCore.QTime(9, 0)

        self.start_time_edit.setTime(current_time)
        self.end_time_edit.setTime(current_time.addSecs(TIMING_RESOLUTION * 60))
        self.show_advanced_time_controls(True)

        self.calendar_widget.resource_id = -1

        # # enter revision types
        # revision_types = [
        #     'Yetistiremedim',
        #     'Ajans',
        #     'Yonetmen',
        #     'Ic Revizyon',
        # ]
        #
        # self.revision_type_combo_box.addItems(revision_types)

        if not self.logged_in_user:
            self.logged_in_user = self.get_logged_in_user()

        # fill the tasks comboBox
        from stalker import Status, Task
        status_wfd = Status.query.filter(Status.code == 'WFD').first()
        status_cmpl = Status.query.filter(Status.code == 'CMPL').first()
        status_prev = Status.query.filter(Status.code == 'PREV').first()

        if not self.timelog:
            # dialog is in create TimeLog mode
            # if a task has been given just feed that task to the comboBox
            if self.task:
                all_tasks = [self.task]
            else:
                # no Task is given nor updating a TimeLog
                # show all the suitable tasks of the logged_in_user
                all_tasks = Task.query \
                    .filter(Task.resources.contains(self.logged_in_user)) \
                    .filter(Task.status != status_wfd) \
                    .filter(Task.status != status_cmpl) \
                    .filter(Task.status != status_prev) \
                    .all()
                # sort the task labels
                all_tasks = sorted(
                    all_tasks,
                    key=lambda task:
                    '%s | %s' % (
                        task.project.name.lower(),
                        ' | '.join(map(lambda x: x.name.lower(), task.parents))
                    )
                )
        else:
            # dialog is working in update TimeLog mode
            all_tasks = [self.timelog.task]

        self.tasks_combo_box.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToContentsOnFirstShow
        )
        self.tasks_combo_box.setFixedWidth(360)
        self.tasks_combo_box.clear()
        self.tasks_combo_box.addTasks(all_tasks)

        self.tasks_combo_box.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.Minimum
        )

        # if a time log is given set the fields from the given time log
        if self.timelog:
            # first update Task
            try:
                self.tasks_combo_box.setCurrentTask(self.timelog.task)
            except IndexError as e:
                return

            # set the resource

            # and disable the tasks_combo_box and resource_combo_box
            self.tasks_combo_box.setEnabled(False)
            self.resource_combo_box.setEnabled(False)

            # set the start and end time
            from anima.utils import utc_to_local
            start_date = utc_to_local(self.timelog.start)
            end_date = utc_to_local(self.timelog.end)

            # set the date
            self.calendar_widget.setSelectedDate(
                QtCore.QDate(start_date.year, start_date.month, start_date.day)
            )

            # first reset the start and end time values
            self.start_time_edit.setTime(QtCore.QTime(0, 0))
            self.end_time_edit.setTime(QtCore.QTime(23, 50))

            # now set the timelog time
            self.start_time_edit.setTime(
                QtCore.QTime(
                    start_date.hour,
                    start_date.minute
                )
            )
            self.end_time_edit.setTime(
                QtCore.QTime(
                    end_date.hour,
                    end_date.minute
                )
            )

        self.fill_calendar_with_time_logs()

        # also trigger an update to the side info bar
        self.calendar_widget_selection_changed()

    def fill_calendar_with_time_logs(self):
        """fill the calendar with daily time log info
        """
        resource_id = self.get_current_resource_id()
        # do not update if the calendar is showing the same user
        if self.calendar_widget.resource_id == resource_id or resource_id == -1:
            return

        tool_tip_text_format = u'{start:%H:%M} - {end:%H:%M} | {task_name}'

        # import time
        # start = time.time()
        # get all the TimeLogs grouped daily
        sql = """-- TOP DOWN SEARCH --
select
    "TimeLogs".start::date as date,
    array_agg(task_rec_data.full_path) as task_name,
    array_agg("TimeLogs".start) as start,
    array_agg("TimeLogs".end) as end,
    sum(extract(epoch from ("TimeLogs".end - "TimeLogs".start)))

from "TimeLogs"

join (
    with recursive recursive_task(id, parent_id, path_names) as (
        select
        task.id,
        task.project_id,
        -- task.project_id::text as path,
        ("Projects".code || '') as path_names
        from "Tasks" as task
        join "Projects" on task.project_id = "Projects".id
        where task.parent_id is NULL
    union all
        select
        task.id,
        task.parent_id,
        -- (parent.path || '|' || task.parent_id:: text) as path,
        (parent.path_names || ' | ' || "Parent_SimpleEntities".name) as path_names
        from "Tasks" as task
        inner join recursive_task as parent on task.parent_id = parent.id
        inner join "SimpleEntities" as "Parent_SimpleEntities" on parent.id = "Parent_SimpleEntities".id
    ) select
        recursive_task.id,
        "SimpleEntities".name || ' (' || recursive_task.path_names || ')' as full_path
    from recursive_task
    join "SimpleEntities" on recursive_task.id = "SimpleEntities".id
) as task_rec_data on "TimeLogs".task_id = task_rec_data.id

-- getting all the data is as fast as getting one, so get all the TimeLogs of this user
where "TimeLogs".resource_id = :resource_id
group by cast("TimeLogs".start as date)
order by cast("TimeLogs".start as date)
        """
        from sqlalchemy import text
        from stalker.db.session import DBSession
        result = DBSession.connection().execute(
            text(sql),
            resource_id=resource_id
        ).fetchall()
        # end = time.time()
        # print('getting data from sql: %0.3f sec' % (end - start))

        # TODO: Remove this in a later version
        from anima.utils import utc_to_local
        time_shifter = utc_to_local
        from distutils.version import LooseVersion
        import stalker
        if LooseVersion(stalker.__version__) >= LooseVersion('0.2.18'):
            def time_shifter(x):
                return x

        last_end_date = None
        for r in result:
            calendar_day = r[0]
            year = calendar_day.year
            month = calendar_day.month
            day = calendar_day.day
            daily_logged_seconds = r[4]
            daily_logged_hours = daily_logged_seconds // 3600
            daily_logged_minutes = \
                (daily_logged_seconds - daily_logged_hours * 3600) // 60

            tool_tip_text_data = [
                u'Total: %i h %i min logged' %
                (daily_logged_hours, daily_logged_minutes)
                if daily_logged_hours
                else u'Total: %i min logged' % daily_logged_minutes
            ]

            for task_name, start, end in sorted(zip(r[1], r[2], r[3]), key=lambda x: x[1]):
                time_log_tool_tip_text = tool_tip_text_format.format(
                    start=time_shifter(start),
                    end=time_shifter(end),
                    task_name=task_name
                )
                tool_tip_text_data.append(time_log_tool_tip_text)
                # store the last_end_date
                last_end_date = end

            merged_tool_tip = u'\n'.join(tool_tip_text_data)

            date_format = QtGui.QTextCharFormat()
            bg_brush = QtGui.QBrush()
            bg_brush.setColor(
                QtGui.QColor(0, 255.0 / 86400.0 * daily_logged_seconds, 0)
            )

            date_format.setBackground(bg_brush)
            date_format.setToolTip(merged_tool_tip)

            date = QtCore.QDate(year, month, day)

            self.calendar_widget.setDateTextFormat(date, date_format)

        # set the start time in the UI to the last_end_date's time value
        # so the UI will automatically be set to the start of the next
        # available slot
        import pytz
        import datetime
        from anima.utils import local_to_utc
        utc_now = local_to_utc(datetime.datetime.now())
        utc_now = utc_now.replace(tzinfo=pytz.utc)
        start_of_today = datetime.datetime(utc_now.year, utc_now.month, utc_now.day, tzinfo=utc_now.tzinfo)
        if last_end_date and last_end_date > start_of_today:
            from anima import TIMING_RESOLUTION
            last_end_time = QtCore.QTime(last_end_date.hour, last_end_date.minute)
            self.start_time_edit.setTime(last_end_time)
            self.end_time_edit.setTime(last_end_time.addSecs(TIMING_RESOLUTION * 60))

    def calendar_widget_selection_changed(self):
        """runs when selection changed
        """
        selected_date = self.calendar_widget.selectedDate()
        assert isinstance(selected_date, QtCore.QDate)

        date_format = u"""<div>
    <div style="width: 100px; height: 100px; font-size: 60pt; float: initial">
        <span><strong>{day_number}</strong></span>
    </div>
    <div style="position: relative; left: 60px; top: -95px;">
        <div>
            <span style="font-size: 24pt;"><strong>{month_name} {year}</strong></span>
            <br>
            <span style="font-size: 32pt;">{day_name}</span>
        </div>
    </div>
</div>""".format(
            day_number=selected_date.day(),
            day_name=selected_date.longDayName(selected_date.dayOfWeek()),
            month_name=selected_date.longMonthName(selected_date.month()),
            year=selected_date.year()
        )

        assert isinstance(self.formatted_date_label, QtWidgets.QLabel)
        self.formatted_date_label.setText(date_format)

        # create new labels for time logs in that day
        date = self.calendar_widget.selectedDate()
        date_text_format = self.calendar_widget.dateTextFormat()
        try:
            time_log_data = date_text_format[date].toolTip()
            self.time_log_info_label.setText(time_log_data)
        except KeyError:
            self.time_log_info_label.setText('')

    def tasks_combo_box_index_changed(self, task_label):
        """runs when another task has been selected
        """
        # task = self.get_current_task()
        task = self.tasks_combo_box.currentTask()
        self.update_percentage()
        self.update_info_text()

        # update resources comboBox
        resource_names = []
        if self.logged_in_user in task.resources:
            resource_names = [self.logged_in_user.name]

        for r in task.resources:
            if r != self.logged_in_user:
                resource_names.append(r.name)

        self.resource_combo_box.clear()
        self.resource_combo_box.addItems(resource_names)

    def get_current_resource(self):
        """returns the current resource
        """
        resource_name = self.resource_combo_box.currentText()
        from stalker import User
        return User.query.filter(User.name == resource_name).first()

    def get_current_resource_id(self):
        """returns the current resource
        """
        resource_name = self.resource_combo_box.currentText()
        from stalker import User
        from stalker.db.session import DBSession
        return DBSession.query(User.id)\
            .filter(User.name == resource_name)\
            .first()

    @classmethod
    def round_to_timing_resolution(cls, q_time):
        """rounds to the TIMING_RESOLUTION

        :param q_time:
        :return:
        """
        logger.debug("q_time(RAW)    : %s" % q_time)
        from anima import TIMING_RESOLUTION

        start_of_today = QtCore.QTime(0, 0)
        secs = start_of_today.secsTo(q_time)

        logger.debug('secs       : %s' % secs)
        logger.debug("TIMING_RESOLUTION: %s" % TIMING_RESOLUTION)
        rounded_secs = (secs // (TIMING_RESOLUTION * 60)) * TIMING_RESOLUTION * 60

        logger.debug("rounded_secs: %s" % rounded_secs)
        rounded_q_time = start_of_today.addSecs(rounded_secs)

        logger.debug("q_time(Rounded): %s" % rounded_q_time)

        return rounded_q_time

    def start_time_changed(self, q_time):
        """validates the start time
        """
        if self.updating_timings:
            return

        self.updating_timings = True

        # q_time should be a multiple of the TIMING_RESOLUTION
        q_time = self.round_to_timing_resolution(q_time)
        self.start_time_edit.setTime(q_time)

        end_time = self.end_time_edit.time()
        if q_time >= end_time:
            from anima import TIMING_RESOLUTION
            logger.debug("updating end_time with set_time")
            self.end_time_edit.setTime(q_time.addSecs(TIMING_RESOLUTION * 60))
            logger.debug("updated end_time with set_time")

        start_time = self.start_time_edit.time()
        end_time = self.end_time_edit.time()

        secs = start_time.secsTo(end_time)
        logger.debug("secs: %s" % secs)
        new_time = QtCore.QTime(0, 0)
        new_time = new_time.addSecs(secs)
        logger.debug("new_time: %s" % new_time)
        logger.debug("updating end_time with set_time")
        self.effort_time_edit.setTime(new_time)
        logger.debug("updated end_time with set_time")

        self.updating_timings = False

        self.update_percentage()
        self.update_info_text()

    def end_time_changed(self, q_time):
        """validates the end time
        """
        if self.updating_timings:
            return

        self.updating_timings = True
        logger.debug("end_time_changed event is triggered!")

        # q_time should be a multiple of the TIMING_RESOLUTION
        q_time = self.round_to_timing_resolution(q_time)
        self.end_time_edit.setTime(q_time)

        start_time = self.start_time_edit.time()
        if q_time <= start_time:
            from anima import TIMING_RESOLUTION
            if q_time.hour() == 0 and q_time.minute() == 0:
                start_time = q_time
                end_time = q_time.addSecs(TIMING_RESOLUTION * 60)
                self.end_time_edit.setTime(end_time)
            else:
                start_time = q_time.addSecs(-TIMING_RESOLUTION * 60)
            self.start_time_edit.setTime(start_time)

        start_time = self.start_time_edit.time()
        end_time = self.end_time_edit.time()
        secs = start_time.secsTo(end_time)
        logger.debug("secs: %s" % secs)
        new_time = QtCore.QTime(0, 0)
        new_time = new_time.addSecs(secs)
        logger.debug("new_time: %s" % new_time)
        self.effort_time_edit.setTime(new_time)

        self.updating_timings = False

        self.update_percentage()
        self.update_info_text()

    def effort_time_changed(self, q_time):
        """runs when the effort has been changed
        """
        if self.updating_timings:
            return

        self.updating_timings = True

        # q_time should be a multiple of the TIMING_RESOLUTION
        q_time = self.round_to_timing_resolution(q_time)
        self.effort_time_edit.setTime(q_time)

        # q_time can not be smaller thane TIMING_RESOLUTION
        from anima import TIMING_RESOLUTION

        start_of_today = QtCore.QTime(0, 0)
        secs_since_start_of_day = start_of_today.secsTo(q_time)

        if secs_since_start_of_day < TIMING_RESOLUTION * 60:
            # clip to TIMING_RESOLUTION
            q_time = QtCore.QTime(0, 0)
            q_time = q_time.addSecs(TIMING_RESOLUTION * 60)
            self.effort_time_edit.setTime(q_time)

        start_time = self.start_time_edit.time()
        end_time = start_time.addSecs(start_of_today.secsTo(q_time))
        self.end_time_edit.setTime(end_time)

        self.updating_timings = False

        self.update_percentage()
        self.update_info_text()

    def resource_changed(self, resource_name):
        """runs when the selected resource has changed
        """
        self.fill_calendar_with_time_logs()

    def calculate_percentage(self):
        # task = self.get_current_task()
        task = self.tasks_combo_box.currentTask()
        if not task:
            return 0

        schedule_seconds = task.schedule_seconds
        logged_seconds = task.total_logged_seconds
        start_time = self.start_time_edit.time()
        end_time = self.end_time_edit.time()
        time_log_seconds = start_time.secsTo(end_time)
        percentage = (logged_seconds + time_log_seconds) / float(schedule_seconds) * 100
        return percentage

    def update_percentage(self):
        """updates the percentage
        """
        percentage = self.calculate_percentage()
        self.task_progress_bar.setMinimum(0)
        self.task_progress_bar.setMaximum(100)
        self.task_progress_bar.setValue(percentage)

    def update_info_text(self):
        """updated the info text
        """
        # task = self.get_current_task()
        task = self.tasks_combo_box.currentTask()
        if not task:
            return

        schedule_seconds = task.schedule_seconds
        logged_seconds = task.total_logged_seconds
        start_time = self.start_time_edit.time()
        end_time = self.end_time_edit.time()
        time_log_seconds = start_time.secsTo(end_time)

        remaining_seconds = \
            schedule_seconds - (logged_seconds + time_log_seconds)

        # if a time log given add its seconds
        if self.timelog:
            remaining_seconds += self.timelog.total_seconds

        # calculate the remaining minutes and hours
        self.no_time_left = False
        if remaining_seconds < 0:
            self.no_time_left = True
            remaining_seconds = abs(remaining_seconds)

        hours = remaining_seconds // 3600
        minutes = (remaining_seconds - hours * 3600) // 60
        if self.no_time_left:
            self.info_area_label.setText(
                '<b style="color: red;">%i h %i min</b> extra time.' %
                (hours, minutes)
            )
            # self.show_revision_fields()
            self.extended_hours = hours
            self.extended_minutes = minutes
        else:
            # self.hide_revision_fields()
            self.info_area_label.setText(
                '<b style="color: green;">%i h %i min</b> will remain to '
                'complete this task.' %
                (hours, minutes)
            )
            self.extended_hours = None
            self.extended_minutes = None

    # def show_revision_fields(self):
    #     """shows the revision fields
    #     """
    #     self.revision_label.show()
    #     self.revision_type_combo_box.show()
    #
    # def hide_revision_fields(self):
    #     """hides the revision fields
    #     """
    #     self.revision_label.hide()
    #     self.revision_type_combo_box.hide()

    def show_advanced_time_controls(self, state):
        """shows the advanced time controls
        :param state:
        """
        logger.debug("state: %s" % state)
        if state:
            self.start_time_edit.show()
            self.start_time_label.show()
            self.end_time_edit.show()
            self.end_time_label.show()
        else:
            self.start_time_edit.hide()
            self.start_time_label.hide()
            self.end_time_edit.hide()
            self.end_time_label.hide()

    def accept(self):
        """overridden accept method
        """
        # get the info
        task = self.tasks_combo_box.currentTask()
        resource = self.get_current_resource()

        submit_to_final_review = self.submit_for_final_review_radio_button.isChecked()

        # get the revision Types
        from stalker import Type

        date = self.calendar_widget.selectedDate()
        start = self.start_time_edit.time()
        end = self.end_time_edit.time()

        # construct proper datetime.DateTime instances
        import datetime
        start_date = datetime.datetime(
            date.year(), date.month(), date.day(),
            start.hour(), start.minute()
        )
        end_date = datetime.datetime(
            date.year(), date.month(), date.day(),
            end.hour(), end.minute()
        )

        today_midnight = datetime.datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=999
        )

        # raise an error if the user is trying to enter a TimeLog to the future
        if start_date > today_midnight or end_date > today_midnight:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Cannot enter TimeLog to a future date!!!',
            )
            return

        # convert them to utc
        from anima.utils import local_to_utc
        utc_start_date = local_to_utc(start_date)
        utc_end_date = local_to_utc(end_date)

        # create a TimeLog
        # print('Task          : %s' % task.name)
        # print('Resource      : %s' % resource.name)
        # print('utc_start_date: %s' % utc_start_date)
        # print('utc_end_date  : %s' % utc_end_date)

        # now if we are not using extra time just create the TimeLog
        from stalker import TimeLog
        from stalker.db.session import DBSession
        from stalker.exceptions import (OverBookedError,
                                        DependencyViolationError)
        utc_now = local_to_utc(datetime.datetime.now())

        # TODO: Remove this in a later version
        import stalker
        from distutils.version import LooseVersion
        if LooseVersion(stalker.__version__) >= LooseVersion('0.2.18'):
            # inject timezone info
            import pytz
            utc_start_date = utc_start_date.replace(tzinfo=pytz.utc)
            utc_end_date = utc_end_date.replace(tzinfo=pytz.utc)
            utc_now = utc_now.replace(tzinfo=pytz.utc)

        from sqlalchemy.exc import IntegrityError
        if not self.timelog:
            try:
                new_time_log = TimeLog(
                    task=task,
                    resource=resource,
                    start=utc_start_date,
                    end=utc_end_date,
                    # description=description,
                    date_created=utc_now
                )
            except (OverBookedError, DependencyViolationError) as e:
                # inform the user that it can not do that
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    '%s' % e
                )
                DBSession.rollback()
                return

            try:
                DBSession.add(new_time_log)
                DBSession.commit()
                self.timelog_created = True
            except IntegrityError as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    'Database Error!!!'
                    '<br>'
                    '%s' % e
                )
                return
        else:
            # just update the date values
            self.timelog.start = utc_start_date
            self.timelog.end = utc_end_date
            self.timelog.date_updated = utc_now
            DBSession.add(self.timelog)
            DBSession.commit()

        if self.no_time_left:
            # we have no time left so automatically extend the task
            from stalker import Task
            schedule_timing, schedule_unit = \
                task.least_meaningful_time_unit(
                    task.total_logged_seconds
                )

            if schedule_timing != 0:
                task.schedule_timing = schedule_timing
                task.schedule_unit = schedule_unit

            # also create a Note
            from stalker import Note
            new_note = Note(
                content='Extending timing of the task <b>%s h %s min.</b>' % (
                    self.extended_hours,
                    self.extended_minutes
                ),
                # type=revision_type,
                created_by=self.logged_in_user,
                date_created=utc_now
            )
            DBSession.add(new_note)
            task.notes.append(new_note)

            try:
                DBSession.commit()
            except IntegrityError as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    'Database Error!!!'
                    '<br>'
                    '%s' % e
                )
                DBSession.rollback()
                return

        if submit_to_final_review:
            # clip the Task timing to current time logs
            from stalker import Task
            schedule_timing, schedule_unit = task.least_meaningful_time_unit(task.total_logged_seconds)

            task.schedule_timing = schedule_timing
            task.schedule_unit = schedule_unit
            DBSession.add(task)

            try:
                DBSession.commit()
            except IntegrityError as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    'Database Error!!!'
                    '<br>'
                    '%s' % e
                )
                DBSession.rollback()
                return

            # request a review
            reviews = task.request_review()
            for review in reviews:
                review.created_by = review.updated_by = self.logged_in_user
                review.date_created = utc_now
                review.date_updated = utc_now

                review.description = "<b>%(resource_name)s:</b> %(note)s" % {
                    'resource_name': self.logged_in_user.name,
                    'note': "Created with TimeLog dialog"
                }

            DBSession.add_all(reviews)

            # and create a Note for the Task
            request_review_note_type = Type.query\
                .filter(Type.target_entity_type == 'Note')\
                .filter(Type.name == 'Request Review')\
                .first()

            from stalker import Note
            request_review_note = Note(
                type=request_review_note_type,
                created_by=self.logged_in_user,
                date_created=utc_now
            )
            DBSession.add(request_review_note)
            DBSession.add(task)
            task.notes.append(request_review_note)

            try:
                DBSession.commit()
            except IntegrityError as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    'Database Error!!!'
                    '<br>'
                    '%s' % e
                )
                return

        # Fix statuses
        from anima import utils
        utils.fix_task_statuses(task)
        try:
            DBSession.commit()
        except IntegrityError as e:
            DBSession.rollback()
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Database Error!!!'
                '<br>'
                '%s' % e
            )
            return

        # if nothing bad happens close the dialog
        super(MainDialog, self).accept()
