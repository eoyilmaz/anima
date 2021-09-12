# -*- coding: utf-8 -*-

import threading

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtWidgets
from anima.publish import ProgressControllerBase


class QProgressBarWrapper(ProgressControllerBase):
    """Wrapper for QProgressBar
    """

    def __init__(self, progress_bar=None,
                 minimum=0.0, maximum=100.0, value=0.0):
        self.progress_bar = progress_bar
        super(QProgressBarWrapper, self).__init__(
            value=value,
            minimum=minimum,
            maximum=maximum
        )

    @property
    def value(self):
        return self.progress_bar.value()

    @value.setter
    def value(self, value):
        self.progress_bar.setValue(float(value))
        try:
            qApp = QtWidgets.qApp
        except AttributeError:
            qApp = QtWidgets.QApplication
        qApp.sendPostedEvents()

    @property
    def minimum(self):
        return self.progress_bar.minimum()

    @minimum.setter
    def minimum(self, minimum):
        self.progress_bar.setMaximum(float(minimum))
        try:
            qApp = QtWidgets.qApp
        except AttributeError:
            qApp = QtWidgets.QApplication
        qApp.sendPostedEvents()

    @property
    def maximum(self):
        return self.progress_bar.maximum()

    @maximum.setter
    def maximum(self, maximum):
        if maximum == 0:
            maximum = 1.0
        self.progress_bar.setMaximum(float(maximum))
        try:
            qApp = QtWidgets.qApp
        except AttributeError:
            qApp = QtWidgets.QApplication
        qApp.sendPostedEvents()


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class PublisherElement(object):
    """A wrapper for publishers and correspongind UI elements
    """
    passing_text = "Passing"
    not_passing_text = "Not Passing"

    def __init__(self, publisher=None):
        self.publisher = publisher
        self.layout = None
        self.check_push_button = None
        self.fix_push_button = None
        self.fix_identifier = '___fix'
        self.help_push_button = None
        self.publisher_name_label = None

        self.publisher_state_ok_icon = None
        self.publisher_state_not_ok_icon = None

        self.publisher_state_label = None
        self.performance_label = None
        self.exception_message = None
        self.progress_bar = None
        self.progress_bar_manager = None

        self.duration = 0.0
        self._state = False

    def create(self, parent=None):
        """Creates this publisher

        :param parent:
        :return:
        """
        # Create layout
        self.layout = QtWidgets.QHBoxLayout(parent)

        # Create Icons
        self.publisher_state_ok_icon = parent.style() \
            .standardIcon(QtWidgets.QStyle.SP_DialogYesButton)
        self.publisher_state_not_ok_icon = parent.style() \
            .standardIcon(QtWidgets.QStyle.SP_DialogNoButton)

        # Create check push button
        self.check_push_button = QtWidgets.QPushButton(parent)
        self.check_push_button.setText('Check')
        self.layout.addWidget(self.check_push_button)
        self.check_push_button.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )

        # Create fix push button
        self.fix_push_button = QtWidgets.QPushButton(parent)
        self.fix_push_button.setText('Fix')
        self.layout.addWidget(self.fix_push_button)
        self.fix_push_button.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        self.fix_push_button.setMaximumWidth(40)

        # Create Progress Bar
        self.progress_bar = QtWidgets.QProgressBar(parent)
        self.progress_bar.setFixedWidth(100)
        self.progress_bar.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )
        self.layout.addWidget(self.progress_bar)

        self.progress_bar_manager = QProgressBarWrapper(
            progress_bar=self.progress_bar,
            minimum=0, maximum=100.0, value=0.0
        )

        # Create state label
        self.publisher_state_label = QtWidgets.QLabel(parent)
        self.publisher_state_label.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        self.layout.addWidget(self.publisher_state_label)

        # Create performance label
        self.performance_label = QtWidgets.QLabel(parent)
        self.performance_label.setText('x.x sec')
        self.performance_label.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        self.layout.addWidget(self.performance_label)

        # Create name label
        self.publisher_name_label = QtWidgets.QLabel(parent)
        self.publisher_name_label.setText(
            self.publisher.__doc__.split('\n')[0].strip()
        )
        self.publisher_name_label.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.publisher_name_label.setToolTip(self.publisher.__doc__)
        self.performance_label.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        self.layout.addWidget(self.publisher_name_label)

        # Create help push button
        self.help_push_button = QtWidgets.QPushButton(parent)
        self.help_push_button.setText('?')
        self.layout.addWidget(self.help_push_button)
        self.help_push_button.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        self.help_push_button.setMaximumWidth(20)

        spacer = QtWidgets.QSpacerItem(
            20, 40,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum
        )
        self.layout.addItem(spacer)

        self.state = False

        # create button signal
        QtCore.QObject.connect(
            self.check_push_button,
            QtCore.SIGNAL("clicked()"),
            self.run_publisher
        )

        QtCore.QObject.connect(
            self.help_push_button,
            QtCore.SIGNAL('clicked()'),
            self.show_publisher_docs
        )

        QtCore.QObject.connect(
            self.fix_push_button,
            QtCore.SIGNAL('clicked()'),
            self.run_fix_definition
        )

    def run_fix_definition(self):
        """runs fix definitions for publishers
        """
        m = QtWidgets.QMessageBox()
        m.setWindowTitle('Continue?')
        m.setText(
            'This command will try to fix<br/>'
            '[ <b>%s</b> ] issue<br/>'
            'automatically.<br/><br/>'
            'Confirm ? <b>(BETA)</b>' % self.publisher.__doc__.split('\n')[0].strip()
        )
        m.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        m.setDefaultButton(QtWidgets.QMessageBox.Yes)
        m.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        m.exec_()

        if m.clickedButton() == m.defaultButton():
            fix_def_name = '%s%s' % (self.publisher.__name__, self.fix_identifier)
            try:
                from anima.env.mayaEnv import publish
                fix_func = publish.__dict__[fix_def_name]
                fix_func()
            except KeyError:
                pass
            self.check_push_button.click()

    def show_publisher_docs(self):
        """Help dialog for publishers
        """
        # TODO: Too much string interpretation. Needs improvement.
        if self.publisher:
            m = QtWidgets.QMessageBox()
            m.setWindowTitle('Help')

            import sys
            if sys.version_info.major > 2:
                stringify = str
            else:
                stringify = unicode

            # cleanup exception message format
            import re
            error = str(''.join([i for i in stringify(self.publisher_state_label.toolTip()) if ord(i) < 128]))
            publish_error = ''
            for exception in ['PublishError:', 'RuntimeError:']:
                try:
                    clean_error = error.split(exception)[1]
                    formatted_error = clean_error.replace('<br>', '\n')
                    publish_error = re.sub('<[^>]*>', '', formatted_error)
                except IndexError:
                    continue

            # display message
            message = self.publisher.__doc__
            message += '\n--------------------\n'
            message += publish_error

            m.setText(message)
            m.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            m.exec_()

    def _set_label_icon(self, label, icon):
        """sets the label icon

        :param label:
        :param icon:
        :return:
        """
        pixmap = icon.pixmap(16, 16)
        label.setPixmap(pixmap)
        label.setMask(pixmap.mask())

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        """Sets the publisher state

        :param bool state:
        :return:
        """
        # update the check icon
        if state:
            self._set_label_icon(
                self.publisher_state_label,
                self.publisher_state_ok_icon
            )
            self.publisher_state_label.setToolTip(self.passing_text)
            self.publisher_name_label.setStyleSheet('color: ;')
        else:
            self._set_label_icon(
                self.publisher_state_label,
                self.publisher_state_not_ok_icon
            )
            self.publisher_state_label.setToolTip(self.not_passing_text)
            self.publisher_name_label.setStyleSheet('color: red;')
        self._state = state

    def run_publisher(self):
        """runs the publisher
        """
        if self.publisher:
            # reset the counter and state
            self.state = False
            self.performance_label.setText('x.x sec')
            self.progress_bar.setValue(0)

            # from anima.exc import PublishError
            import sys
            import traceback
            import time

            start = time.time()
            try:
                # disable Check button
                self.check_push_button.setText('Checking...')
                self.check_push_button.setEnabled(False)
                try:
                    qApp = QtWidgets.qApp
                except AttributeError:
                    qApp = QtWidgets.QApplication
                qApp.sendPostedEvents()
                self.publisher(progress_controller=self.progress_bar_manager)
                end = time.time()
            except Exception as e:
                end = time.time()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                self.state = False
                self.publisher_state_label.setToolTip(
                    '\n'.join(
                        traceback.format_exc(exc_traceback).splitlines()[-25:]
                    )
                )
            else:
                self.state = True
                self.publisher_state_label.setToolTip('')

            # set performance label
            self.duration = end - start
            self.performance_label.setText('%0.1f sec' % self.duration)
            self.check_push_button.setText('Check')
            self.check_push_button.setEnabled(True)

            # set fix label
            if self.state is True:
                self.fix_push_button.setDisabled(True)
                self.fix_push_button.setStyleSheet('background-color: None')
            else:
                # disable fix button if fix definition does not exist
                fix_def_name = '%s%s' % (self.publisher.__name__, self.fix_identifier)

                from anima.env.mayaEnv import publish
                # disable by default
                self.fix_push_button.setDisabled(True)
                self.fix_push_button.setStyleSheet('background-color: None')
                # enable if the function exists
                if fix_def_name in publish.__dict__:
                    self.fix_push_button.setEnabled(True)
                    self.fix_push_button.setStyleSheet('background-color: green')


class PublisherRunner(threading.Thread):
    """The thread
    """
    def __init__(self, publishers=None):
        super(PublisherRunner, self).__init__()
        self.publishers = publishers

    def run(self):
        for publisher in self.publishers:
            publisher.run_publisher()


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """Runs publishers in a neat way.

    This UI filters parent tasks and displays the child tasks in a
    QTableWidget.
    """

    def __init__(self, parent=None, environment=None, publish_callback=None, version=None):
        super(MainDialog, self).__init__(parent=parent)
        self.environment = environment
        self.publishers = []
        self.publish_callback = publish_callback
        self.version = version
        self.last_run_date = 0

        self._setup_ui()
        self.fill_ui()

    def closeEvent(self, event):
        """if user tries to close the publish_checker dialog
        pop up a question dialog
        """
        answer = QtWidgets.QMessageBox.question(
            self,
            'DO NOT Close Window!!!',
            'You should <b>NOT</b> close this window!!!<br/>'
            ' <br/>'
            'Drag Publish Checker to the side and fix your scene<br/>'
            'When fixed hit Check buttons until Published!!!<br/>'
            ' <br/>'
            'Close Anyway !!!',
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No
        )

        if answer == QtWidgets.QMessageBox.Yes:
            # delete any empty published versions if created
            if self.version.is_latest_published_version() \
                    and self.version.absolute_full_path == '.' \
                    and self.version.extension == '' \
                    and not self.version.created_with:  # this means the last published version is empty
                from stalker.db.session import DBSession
                try:
                    DBSession.delete(self.version)
                    # DBSession.commit() # no need to commit
                except Exception:
                    DBSession.rollback()

            event.accept()
        else:
            event.ignore()

    def _setup_ui(self):
        """create the ui elements
        """
        self.resize(650, 850)
        # ----------------------------------------------------
        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # ----------------------------------------------------
        # Dialog Label
        self.dialog_label = QtWidgets.QLabel(self)

        self.dialog_label.setText('Publish Checker')
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);font: 18pt;")

        self.main_layout.addWidget(self.dialog_label)

        # ----------------------------------------------------
        # Title Line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(line)

        # Version Label
        self.version_label = QtWidgets.QLabel(self)
        self.version_label.setText(self.version.nice_name)
        self.version_label.setStyleSheet("color: rgb(71, 143, 202);font: 12pt;")
        self.main_layout.addWidget(self.version_label)

        # Version Line
        line1 = QtWidgets.QFrame(self)
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(line1)

        # ----------------------------------------------------
        # Fields

        # Publisher Type ComboBox
        # self.publisher_type_layout = \
        #     QtWidgets.QHBoxLayout(self.main_layout.widget())
        #
        # self.publisher_type_label = QtWidgets.QLabel(self)
        # self.publisher_type_label.setText('Publisher Type')
        # self.publisher_type_layout.addWidget(self.publisher_type_label)
        #
        # self.publisher_type_combo_box = QtWidgets.QComboBox(self)
        # self.publisher_type_layout.addWidget(self.publisher_type_combo_box)
        # self.publisher_type_layout.setStretch(0, 0)
        # self.publisher_type_layout.setStretch(1, 1)
        #
        # self.main_layout.addLayout(self.publisher_type_layout)

        # Check all push button
        self.check_all_push_button = QtWidgets.QPushButton(self)
        self.check_all_push_button.setText('CHECK ALL')
        if self.version and self.version.task.type:
            self.check_all_push_button.setText('CHECK ALL for %s' %
                                               self.version.task.type.name)

        self.main_layout.addWidget(self.check_all_push_button)

        # create the signal for check all push button
        QtCore.QObject.connect(
            self.check_all_push_button,
            QtCore.SIGNAL('clicked()'),
            self.check_all_publishers
        )

        # Publish Field
        # self.publisher_grid_layout = \
        #     QtWidgets.QGridLayout(self.main_layout.widget())
        self.scroll_area_widget = QtWidgets.QWidget(self)
        self.publisher_vertical_layout = QtWidgets.QVBoxLayout(self)
        self.scroll_area_widget.setLayout(self.publisher_vertical_layout)

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )
        self.scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)

        # self.scroll_area_layout = QtWidgets.QVBoxLayout(self)
        # self.main_layout.addLayout(self.scroll_area_layout)
        self.main_layout.addWidget(self.scroll_area)

        # performance label
        self.duration_label = QtWidgets.QLabel(self)
        self.main_layout.addWidget(self.duration_label)

        # Publish push button
        self.publish_push_button = QtWidgets.QPushButton(self)
        self.publish_push_button.setText('PUBLISH')
        self.publish_push_button.setEnabled(False)
        self.main_layout.addWidget(self.publish_push_button)

        # connect publish button signal
        QtCore.QObject.connect(
            self.publish_push_button,
            QtCore.SIGNAL('clicked()'),
            self.publish_push_button_clicked
        )

        # Add spacer
        # vertical_spacer = QtWidgets.QSpacerItem(
        #     20, 40,
        #     QtWidgets.QSizePolicy.Minimum,
        #     QtWidgets.QSizePolicy.Expanding
        # )
        # self.main_layout.addItem(vertical_spacer)
        # self.main_layout.addItem(vertical_spacer)

        # Set Main Layout Stretch
        # self.main_layout.setStretch(0, 0)
        # self.main_layout.setStretch(1, 0)
        # self.main_layout.setStretch(2, 1)
        # self.main_layout.setStretch(3, 1)

    def fill_ui(self):
        """fills the ui with default values
        """
        # just import the anima.publish module
        # if the environment is setup properly
        # the publish.publishers should have been filled with publishers
        from anima import publish
        publish.staging['version'] = self.version

        # generate generics first
        ppt = publish.PRE_PUBLISHER_TYPE

        # check if the environment has at least a couple of publishers
        if '' in publish.publishers[ppt]:
            for publisher in publish.publishers[ppt]['']:
                self.publishers.append(
                    self.create_publisher_field(publisher)
                )

        # get the current type
        if self.environment:
            # version = self.environment.get_current_version()
            if self.version and self.version.task.type:
                type_name = self.version.task.type.name.lower()

                # generate generics first
                if type_name in publish.publishers[ppt]:
                    for publisher in publish.publishers[ppt][type_name]:
                        self.publishers.append(
                            self.create_publisher_field(publisher)
                        )

        # for all publishers also connect the clicked signal of their check
        # buttons to enable or disable the publish button
        for publisher in self.publishers:
            QtCore.QObject.connect(
                publisher.check_push_button,
                QtCore.SIGNAL('clicked()'),
                self.check_publisher_states
            )

    def create_publisher_field(self, publisher):
        """Creates a publisher field
        """
        # generate one UI element per publisher
        # create the layout
        publisher_element = PublisherElement(publisher)
        publisher_element.create(parent=self)
        self.publisher_vertical_layout.addLayout(publisher_element.layout)
        return publisher_element

    def check_all_publishers(self):
        """runs all the publishers as if their check buttons are pushed one by
        one
        """
        try:
            qApp = QtWidgets.qApp
        except AttributeError:
            qApp = QtWidgets.QApplication
        qApp.processEvents()

        import time
        current_time = time.time()
        # do not run publishers if they ran less than 5 seconds ago
        if current_time - self.last_run_date > 5:
            for publisher in self.publishers:
                # move the view to this publisher
                self.scroll_area.ensureWidgetVisible(
                    publisher.check_push_button
                )
                publisher.run_publisher()
                self.update_publisher_total_duration_info()
                qApp.sendPostedEvents()
            self.last_run_date = time.time()

        return self.check_publisher_states()

    def update_publisher_total_duration_info(self):
        """updates the total duration info of publishers
        """
        # update duration info
        total_duration = 0.0
        for publisher in self.publishers:
            total_duration += publisher.duration

        minute = total_duration // 60.0
        seconds = total_duration - minute * 60.0

        if minute:
            self.duration_label.setText(
                'Publishers run in: %i min %i sec!' % (int(minute), int(seconds))
            )
        else:
            self.duration_label.setText(
                'Publishers run in: %0.1f sec!' % seconds
            )

    def check_publisher_states(self):
        """check publisher states
        """
        if self.publishers:
            self.update_publisher_total_duration_info()
            if all([publisher.state for publisher in self.publishers]) \
               and self.version:
                self.publish_push_button.setEnabled(True)
                return True
            else:
                self.publish_push_button.setEnabled(False)
                for publisher in self.publishers:
                    if not publisher.state:
                        self.scroll_area.ensureWidgetVisible(
                            publisher.check_push_button
                        )
                return False
        else:
            if self.version:
                self.publish_push_button.setEnabled(True)
                return True
        return True

    def publish_push_button_clicked(self):
        """runs when the publish button is clicked
        """
        # rerun all publishers
        if self.check_all_publishers():
            self.accept()
            if self.publish_callback:
                self.publish_callback()

    def reject(self):
        QtWidgets.QDialog.reject(self)
        from stalker.db.session import DBSession
        if self.version:
            DBSession.delete(self.version)
            DBSession.commit()
        DBSession.rollback()
