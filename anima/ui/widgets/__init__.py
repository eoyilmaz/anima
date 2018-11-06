# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima import logger
from anima.ui.lib import QtCore, QtGui, QtWidgets


class DoubleListWidget(object):
    """This is a Widget that has two QListWidgets.
    """

    def __init__(self, dialog=None, parent_layout=None, primary_label_text='',
                 secondary_label_text=''):
        """
        :param dialog: QDialog instance that this is the child of.
        :param parent_layout: The QLayout instance to add this widgets to
        :param str primary_label_text: The label of the primary list
        :param str secondary_label_text: The label of the secondary list
        """
        self.dialog = dialog
        self.parent_layout = parent_layout

        # Layouts
        self.main_layout = None
        self.button_layout = None
        self.primary_widgets_layout = None
        self.secondary_widgets_layout = None

        # Widgets
        self.primary_list_widget = None
        self.secondary_list_widget = None
        self.primary_to_secondary_push_button = None
        self.secondary_to_primary_push_button = None

        self.primary_label = None
        self.secondary_label = None

        # Data
        self.primary_label_text = primary_label_text
        self.secondary_label_text = secondary_label_text

        self.__init__ui()

    def __init__ui(self):
        """creates the Widgets
        """
        # create a horizontal layout to hold the widgets
        self.main_layout = QtWidgets.QHBoxLayout()

        # ----------------------------------
        # Primary Widgets Layout
        self.primary_widgets_layout = QtWidgets.QVBoxLayout()

        # label
        self.primary_label = QtWidgets.QLabel(self.dialog)
        self.primary_label.setText(self.primary_label_text)
        self.primary_label.setAlignment(QtCore.Qt.AlignCenter)
        self.primary_widgets_layout.addWidget(self.primary_label)
        
        # list widget
        self.primary_list_widget = QtWidgets.QListWidget(self.dialog)
        self.primary_widgets_layout.addWidget(self.primary_list_widget)
        self.main_layout.addLayout(self.primary_widgets_layout)

        # ----------------------------------
        # Button Layout
        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.insertStretch(0, 0)
        self.primary_to_secondary_push_button = \
            QtWidgets.QPushButton('>>', parent=self.dialog)
        self.secondary_to_primary_push_button = \
            QtWidgets.QPushButton('<<', parent=self.dialog)
        
        self.primary_to_secondary_push_button.setMaximumSize(25, 16777215)
        self.secondary_to_primary_push_button.setMaximumSize(25, 16777215)
        
        self.button_layout.addWidget(self.primary_to_secondary_push_button)
        self.button_layout.addWidget(self.secondary_to_primary_push_button)
        
        self.button_layout.insertStretch(3, 0)
        self.main_layout.addLayout(self.button_layout)

        # ----------------------------------
        # Secondary Widgets Layout
        self.secondary_widgets_layout = QtWidgets.QVBoxLayout()

        # label
        self.secondary_label = QtWidgets.QLabel(self.dialog)
        self.secondary_label.setText(self.secondary_label_text)
        self.secondary_label.setAlignment(QtCore.Qt.AlignCenter)

        # list widget
        self.secondary_widgets_layout.addWidget(self.secondary_label)

        self.secondary_list_widget = QtWidgets.QListWidget(self.dialog)
        self.secondary_widgets_layout.addWidget(self.secondary_list_widget)
        self.main_layout.addLayout(self.secondary_widgets_layout)

        self.main_layout.setStretch(0, 1)
        self.main_layout.setStretch(1, 0)
        self.main_layout.setStretch(2, 1)

        self.parent_layout.addLayout(self.main_layout)

        # Create signals
        QtCore.QObject.connect(
            self.primary_to_secondary_push_button,
            QtCore.SIGNAL('clicked()'),
            self.primary_to_secondary_push_button_clicked
        )

        QtCore.QObject.connect(
            self.primary_list_widget,
            QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem*)'),
            self.primary_to_secondary_push_button_clicked
        )

        QtCore.QObject.connect(
            self.secondary_to_primary_push_button,
            QtCore.SIGNAL('clicked()'),
            self.secondary_to_primary_push_button_clicked
        )

        QtCore.QObject.connect(
            self.secondary_list_widget,
            QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem*)'),
            self.secondary_to_primary_push_button_clicked
        )

    def add_primary_items(self, items):
        """Adds the given items to the primary list

        :param items:
        :return:
        """
        self.primary_list_widget.addItems(items)

    def add_secondary_items(self, items):
        """Adds the given items to the secondary list

        :param items:
        :return:
        """
        self.secondary_list_widget.addItems(items)
    
    def clear(self):
        """clears both of the lists
        """
        self.primary_list_widget.clear()
        self.secondary_list_widget.clear()
    
    def primary_to_secondary_push_button_clicked(self):
        """runs when the primary_to_secondary_push_button is clicked
        """
        # get the current item selected in primary list
        index = self.primary_list_widget.currentRow()
        item = self.primary_list_widget.takeItem(index)
        self.secondary_list_widget.addItem(item)
    
    def secondary_to_primary_push_button_clicked(self):
        """runs when the secondary_to_primary_push_button is clicked
        """
        index = self.secondary_list_widget.currentRow()
        item = self.secondary_list_widget.takeItem(index)
        self.primary_list_widget.addItem(item)
    
    def primary_items(self):
        """returns the items in primary_list_widget
        """
        items = []
        for i in range(self.primary_list_widget.count()):
            items.append(self.primary_list_widget.item(i))
        return items
    
    def secondary_items(self):
        """returns the items in secondary_list_widget
        """
        items = []
        for i in range(self.secondary_list_widget.count()):
            items.append(self.secondary_list_widget.item(i))
        return items


class TimeEdit(QtWidgets.QTimeEdit):
    """Customized time edit widget
    """

    def __init__(self, *args, **kwargs):
        self.resolution = None
        if 'resolution' in kwargs:
            self.resolution = kwargs['resolution']
            kwargs.pop('resolution')

        super(TimeEdit, self).__init__(*args, **kwargs)

    def stepBy(self, step):
        """Custom stepBy function

        :param step:
        :return:
        """
        if self.currentSectionIndex() == 1:
            if step < 0:
                # auto update the hour section to the next hour
                minute = self.time().minute()
                if minute == 0:
                    # increment the hour section by one
                    self.setTime(
                        QtCore.QTime(
                            self.time().hour() - 1,
                            60 - self.resolution
                        )
                    )
                else:
                    self.setTime(
                        QtCore.QTime(
                            self.time().hour(),
                            minute - self.resolution
                        )
                    )

            else:
                # auto update the hour section to the next hour
                minute = self.time().minute()
                if minute == (60 - self.resolution):
                    # increment the hour section by one
                    self.setTime(
                        QtCore.QTime(
                            self.time().hour() + 1,
                            0
                        )
                    )
                else:
                    self.setTime(
                        QtCore.QTime(
                            self.time().hour(),
                            minute + self.resolution
                        )
                    )
        else:
            if step < 0:
                if self.time().hour() != 0:
                    super(TimeEdit, self).stepBy(step)
            else:
                if self.time().hour() != 23:
                    super(TimeEdit, self).stepBy(step)


class TakesListWidget(QtWidgets.QListWidget):
    """A specialized QListWidget variant used in Take names.
    """

    def __init__(self, parent=None, *args, **kwargs):
        QtWidgets.QListWidget.__init__(self, parent, *args, **kwargs)
        self._take_names = []
        self.take_names = []

    @property
    def take_names(self):
        return self._take_names

    @take_names.setter
    def take_names(self, take_names_in):
        logger.debug('setting take names')
        self.clear()
        self._take_names = take_names_in
        from anima import defaults
        main = defaults.version_take_name
        if main in self._take_names:
            logger.debug('removing default take name from list')
            index_of_main = self._take_names.index(main)
            self._take_names.pop(index_of_main)

        # insert the default take name to the start
        self._take_names.insert(0, main)

        # clear the list and new items
        logger.debug('adding supplied take names: %s' % self._take_names)
        self.addItems(self._take_names)

        # select the first item
        self.setCurrentItem(self.item(0))

    def add_take(self, take_name):
        """adds a new take to the takes list
        """
        # condition the input
        from stalker import Version
        take_name = Version._format_take_name(take_name)

        # if the given take name is in the list don't add it
        if take_name not in self._take_names:
            # add the item via property
            new_take_list = self._take_names
            new_take_list.append(take_name)
            new_take_list.sort()
            self.take_names = new_take_list

            # select the newly added take name
            items = self.findItems(take_name, QtCore.Qt.MatchExactly)
            if items:
                item = items[0]
                # set the take to the new one
                self.setCurrentItem(item)

    @property
    def current_take_name(self):
        """gets the current take name
        """
        take_name = ''
        item = self.currentItem()
        if item:
            take_name = item.text()
        return take_name

    @current_take_name.setter
    def current_take_name(self, take_name):
        """sets the current take name
        """
        logger.debug('finding take with name: %s' % take_name)
        items = self.findItems(
            take_name,
            QtCore.Qt.MatchExactly
        )
        if items:
            self.setCurrentItem(items[0])

    def clear(self):
        """overridden clear method
        """
        self._take_names = []
        # call the super
        QtWidgets.QListWidget.clear(self)


class TaskComboBox(QtWidgets.QComboBox):
    """A customized combobox that holds Tasks
    """
    
    def __init__(self, *args, **kwargs):
        super(TaskComboBox, self).__init__(*args, **kwargs)
    
    def showPopup(self, *args, **kwargs):
        self.view().setMinimumWidth(self.view().sizeHintForColumn(0))
        super(TaskComboBox, self).showPopup(*args, **kwargs)
    
    @classmethod
    def generate_task_name(cls, task):
        """Generates task names
        :param task:
        :return:
        """
        if task:
            return '%s (%s)' % (
                task.name,
                '%s | %s' % (
                    task.project.name,
                    ' | '.join(map(lambda x: x.name, task.parents))
                )
            )
        else:
            return ''
    
    def addTasks(self, tasks):
        """Overridden addItems method

        :param tasks: A list of Tasks
        :return:
        """
        # prepare task labels
        task_labels = []
        for task in tasks:
            # this is dirty
            task_label = self.generate_task_name(task)
            self.addItem(task_label, task)
    
    def currentTask(self):
        """returns the current task
        """
        return self.itemData(self.currentIndex())
    
    def setCurrentTask(self, task):
        """sets the current task to the given task
        """
        for i in range(self.count()):
            t = self.itemData(i)
            if t.id == task.id:
                self.setCurrentIndex(i)
                return
        
        raise IndexError('Task not found!')


class RecentFilesComboBox(QtWidgets.QComboBox):
    """A Fixed with popup box comboBox alternative
    """

    def showPopup(self, *args, **kwargs):
        view = self.view()
        column_size_hint = view.sizeHintForColumn(0)
        view.setMinimumWidth(column_size_hint + 20)
        super(RecentFilesComboBox, self).showPopup(*args, **kwargs)


class ValidatedLineEdit(QtWidgets.QLineEdit):
    """A custom line edit that can display an icon
    """

    def __init__(self, *args, **kwargs):
        self.message_field = kwargs.pop('message_field', None)
        super(ValidatedLineEdit, self).__init__(*args, **kwargs)
        self.message_field.setVisible(False)
        self.icon = None
        self.is_valid = True
        self.message = ''

    def set_valid(self):
        """sets the field valid
        """
        self.set_icon(None)
        self.is_valid = True
        self.message = ''

        if self.message_field:
            self.message_field.setVisible(False)

    def set_invalid(self, message=''):
        """sets the field invalid
        """
        self.icon = self.style() \
            .standardIcon(QtWidgets.QStyle.SP_MessageBoxCritical)
        self.set_icon(self.icon)

        self.is_valid = False

        if self.message_field:
            self.message_field.setText(message)
            if self.isVisible():
                self.message_field.setVisible(True)

    def set_icon(self, icon=None):
        """Sets the icon

        :param icon: QIcon instance
        :return:
        """
        self.icon = icon
        if icon is None:
            self.setTextMargins(1, 1, 1, 1)
        else:
            self.setTextMargins(1, 1, 20, 1)

    def paintEvent(self, event):
        """Overridden paint event

        :param event: QPaintEvent instance
        :return:
        """
        super(ValidatedLineEdit, self).paintEvent(event)
        if self.icon is not None:
            painter = QtGui.QPainter(self)
            pixmap = self.icon.pixmap(self.height() - 6, self.height() - 6)

            x = self.width() - self.height() + 4

            painter.drawPixmap(x, 3, pixmap)
            painter.setPen(QtGui.QColor("lightgrey"))
            painter.drawLine(x - 2, 3, x - 2, self.height() - 4)

    def setVisible(self, vis):
        """overridden shot method
        """
        super(ValidatedLineEdit, self).setVisible(vis)
        if vis:
            if not self.is_valid:
                # also show the validator message field
                self.message_field.setVisible(vis)
        else:
            self.message_field.setVisible(vis)