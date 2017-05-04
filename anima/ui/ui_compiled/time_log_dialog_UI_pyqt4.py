# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\time_log_dialog.ui'
#
# Created: Thu May 04 11:01:53 2017
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(447, 546)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.tasks_label = QtGui.QLabel(Dialog)
        self.tasks_label.setObjectName(_fromUtf8("tasks_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.tasks_label)
        self.task_progressBar = QtGui.QProgressBar(Dialog)
        self.task_progressBar.setProperty("value", 24)
        self.task_progressBar.setObjectName(_fromUtf8("task_progressBar"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.task_progressBar)
        self.resources_label = QtGui.QLabel(Dialog)
        self.resources_label.setObjectName(_fromUtf8("resources_label"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.resources_label)
        self.resource_comboBox = QtGui.QComboBox(Dialog)
        self.resource_comboBox.setObjectName(_fromUtf8("resource_comboBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.resource_comboBox)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_5)
        self.calendarWidget = QtGui.QCalendarWidget(Dialog)
        self.calendarWidget.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.calendarWidget.setObjectName(_fromUtf8("calendarWidget"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.calendarWidget)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label_2)
        self.info_area_label = QtGui.QLabel(Dialog)
        self.info_area_label.setObjectName(_fromUtf8("info_area_label"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.info_area_label)
        self.revision_label = QtGui.QLabel(Dialog)
        self.revision_label.setObjectName(_fromUtf8("revision_label"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.revision_label)
        self.revision_type_comboBox = QtGui.QComboBox(Dialog)
        self.revision_type_comboBox.setObjectName(_fromUtf8("revision_type_comboBox"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.FieldRole, self.revision_type_comboBox)
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.LabelRole, self.label_7)
        self.description_plainTextEdit = QtGui.QPlainTextEdit(Dialog)
        self.description_plainTextEdit.setObjectName(_fromUtf8("description_plainTextEdit"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.FieldRole, self.description_plainTextEdit)
        self.label_9 = QtGui.QLabel(Dialog)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.formLayout.setWidget(9, QtGui.QFormLayout.LabelRole, self.label_9)
        self.not_finished_yet_radioButton = QtGui.QRadioButton(Dialog)
        self.not_finished_yet_radioButton.setChecked(True)
        self.not_finished_yet_radioButton.setObjectName(_fromUtf8("not_finished_yet_radioButton"))
        self.formLayout.setWidget(9, QtGui.QFormLayout.FieldRole, self.not_finished_yet_radioButton)
        self.set_as_complete_radioButton = QtGui.QRadioButton(Dialog)
        self.set_as_complete_radioButton.setObjectName(_fromUtf8("set_as_complete_radioButton"))
        self.formLayout.setWidget(10, QtGui.QFormLayout.FieldRole, self.set_as_complete_radioButton)
        self.submit_for_final_review_radioButton = QtGui.QRadioButton(Dialog)
        self.submit_for_final_review_radioButton.setObjectName(_fromUtf8("submit_for_final_review_radioButton"))
        self.formLayout.setWidget(11, QtGui.QFormLayout.FieldRole, self.submit_for_final_review_radioButton)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.tasks_label.setText(QtGui.QApplication.translate("Dialog", "Task", None, QtGui.QApplication.UnicodeUTF8))
        self.resources_label.setText(QtGui.QApplication.translate("Dialog", "Resource", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Date", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "End", None, QtGui.QApplication.UnicodeUTF8))
        self.info_area_label.setText(QtGui.QApplication.translate("Dialog", "INFO", None, QtGui.QApplication.UnicodeUTF8))
        self.revision_label.setText(QtGui.QApplication.translate("Dialog", "<html><head/><body><p align=\"right\">Revision<br/>Type</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Dialog", "Status", None, QtGui.QApplication.UnicodeUTF8))
        self.not_finished_yet_radioButton.setText(QtGui.QApplication.translate("Dialog", "Not Finished Yet", None, QtGui.QApplication.UnicodeUTF8))
        self.set_as_complete_radioButton.setText(QtGui.QApplication.translate("Dialog", "Set As Complete", None, QtGui.QApplication.UnicodeUTF8))
        self.submit_for_final_review_radioButton.setText(QtGui.QApplication.translate("Dialog", "Submit For Final Review", None, QtGui.QApplication.UnicodeUTF8))

