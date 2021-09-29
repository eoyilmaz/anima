# -*- coding: utf-8 -*-
"""
import datetime
from anima import defaults
defaults.timing_resolution = datetime.timedelta(minutes=10)

from anima.ui import SET_PYSIDE2
SET_PYSIDE2()

from anima.ui.widgets.review import APPROVE, REQUEST_REVISION
from anima.ui import review_dialog

review_dialog.UI(review_type=REQUEST_REVISION)
"""

from anima.ui.lib import QtCore, QtWidgets
from anima.ui.base import ui_caller, AnimaDialogBase


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, ReviewDialog, **kwargs)


class ReviewDialog(QtWidgets.QDialog, AnimaDialogBase):
    """review dialog
    """

    def __init__(self, task=None, reviewer=None, review_type=None, parent=None):
        super(ReviewDialog, self).__init__(parent=parent)
        self.task = task
        self.reviewer = reviewer
        self.review_type = review_type
        self.main_layout = None
        self.button_box = None
        self._setup_ui()

    def _setup_ui(self):
        """set up the ui elements
        """
        self.setWindowTitle("Review Dialog")
        self.resize(550, 350)
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Review
        from anima.ui.widgets.review import ReviewWidget
        self.review_widget = ReviewWidget(
            parent=self,
            task=self.task,
            reviewer=self.reviewer,
            review_type=self.review_type,
        )
        self.main_layout.addWidget(self.review_widget)

        # Button Box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel |
            QtWidgets.QDialogButtonBox.Ok
        )
        self.main_layout.addWidget(self.button_box)

        # setup signals
        from functools import partial
        self.button_box.accepted.connect(partial(self.accept))
        self.button_box.rejected.connect(partial(self.reject))

    def accept(self):
        """runs when the dialog is accepted
        """
        # finalize the review
        review = self.review_widget.finalize_review()

        if review:
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                "Review is created!"
            )

        # do the default behaviour
        super(ReviewDialog, self).accept()
