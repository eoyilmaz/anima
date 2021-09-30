# -*- coding: utf-8 -*-


from anima.ui.lib import QtCore, QtWidgets


class ScheduleTimingWidget(QtWidgets.QWidget):
    """A widget for entering schedule timing related information

    :param timing_resolution: Timing resolution as a Datetime.TimeDelta instance.
    """

    def __init__(self, *args, **kwargs):
        timing_resolution = kwargs.pop("timing_resolution", None)
        super(ScheduleTimingWidget, self).__init__(*args, **kwargs)
        self._timing_resolution = None

        self.main_layout = None
        self.schedule_timing_widget = None
        self.schedule_unit_widget = None
        self.schedule_model_widget = None

        self._updating_schedule_info = False

        self._setup_ui()

        self.timing_resolution = timing_resolution

        self._setup_signals()

    def _setup_ui(self):
        """set up the ui
        """
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.schedule_timing_widget = QtWidgets.QSpinBox(self)
        self.schedule_timing_widget.setMinimum(1)
        self.schedule_timing_widget.setMaximum(9999999)
        self.main_layout.addWidget(self.schedule_timing_widget)

        self.schedule_unit_widget = QtWidgets.QComboBox(self)
        from stalker import defaults
        for datetime_unit_name, datetime_unit in zip(defaults.datetime_unit_names, defaults.datetime_units):
            self.schedule_unit_widget.addItem(datetime_unit_name.title(), datetime_unit)

        self.main_layout.addWidget(self.schedule_unit_widget)

        self.schedule_model_widget = QtWidgets.QComboBox(self)
        from stalker.models.mixins import DateRangeMixin
        for task_schedule_model in defaults.task_schedule_models:
            self.schedule_model_widget.addItem(task_schedule_model.title(), task_schedule_model)

        self.main_layout.addWidget(self.schedule_model_widget)

        self.main_layout.setStretch(0, 1)
        self.main_layout.setStretch(1, 2)
        self.main_layout.setStretch(2, 2)

    def _setup_signals(self):
        """set up the signals
        """
        from functools import partial
        self.schedule_timing_widget.valueChanged.connect(partial(self.update_timing_info))
        self.schedule_unit_widget.currentIndexChanged.connect(partial(self.update_timing_info))

    def update_timing_info(self, *args):
        """updates the timing information
        """
        self.set_schedule_info(*self.get_schedule_info())

    def get_schedule_info(self):
        """getter for the schedule_info
        """
        schedule_timing = self.schedule_timing_widget.value()
        schedule_unit = self.schedule_unit_widget.itemData(self.schedule_unit_widget.currentIndex())
        schedule_model = self.schedule_model_widget.itemData(self.schedule_model_widget.currentIndex())
        return schedule_timing, schedule_unit, schedule_model

    def set_schedule_info(self, timing=1, unit='h', model='effort'):
        """setter for the schedule_info

        :param int timing:
        :param str unit:
        :param str model:
        :return:
        """
        if self._updating_schedule_info:
            return

        self._updating_schedule_info = True

        from stalker.models.mixins import ScheduleMixin
        seconds = ScheduleMixin.to_seconds(timing, unit, model)

        # round the seconds to the timing resolution
        trs = self.timing_resolution.days * 86400 + self.timing_resolution.seconds

        # adjust the step of the schedule_timing to the current unit
        from anima import utils
        step = max(1, utils.to_unit(trs, unit, model))
        self.schedule_timing_widget.setSingleStep(step)

        # round the seconds to the timing resolution
        seconds = (max(1, round(seconds / trs))) * trs

        # get the timing value in this unit
        timing = utils.to_unit(seconds, unit, model)

        self.schedule_timing_widget.setValue(timing)

        index = self.schedule_unit_widget.findData(unit)
        if index:
            self.schedule_unit_widget.setCurrentIndex(index)

        index = self.schedule_model_widget.findData(model)
        if index:
            self.schedule_model_widget.setCurrentIndex(index)

        self._updating_schedule_info = False

    @property
    def timing_resolution(self):
        """the getter for the timing_resolution property
        """
        return self._timing_resolution

    @timing_resolution.setter
    def timing_resolution(self, timing_resolution=None):
        """setter for the timing_resolution property

        :param DateTime.TimeDelta timing_resolution: datetime.timedelta instance showing the timing resolution. If not
          given or None is given the anima.default.timing_resolution value will be used.
        :return:
        """
        import datetime
        if timing_resolution is None:
            from anima import defaults
            timing_resolution = defaults.timing_resolution
        elif not isinstance(timing_resolution, datetime.timedelta):
            raise TypeError("%s.timing_resolution should be set to a datetime.timedelta instance, not %s" % (
                self.__class__.__name__, timing_resolution.__class__.__name__
            ))

        self._timing_resolution = timing_resolution

        # update the timing information
        self.update_timing_info()
