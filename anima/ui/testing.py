# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


class PatchedMessageBox(object):
    """A class for testing QMessageBox dialogs.

    Usage:

      - Patch QtGui.QMessageBox::

        QtGui.QMessageBox = PatchedMessageBox

      - Check ERROR

    :return:
    """
    called_function = ''
    title = ''
    message = ''

    question_return_value = None

    @classmethod
    def tear_down(cls):
        """clean up test results
        """
        cls.called_function = ''
        cls.title = ''
        cls.message = ''

    @classmethod
    def critical(cls, parent, title, message, *args, **kwargs):
        cls.called_function = 'critical'
        cls.title = title
        cls.message = message

    @classmethod
    def information(cls, parent, title, message, *args, **kwargs):
        cls.called_function = 'information'
        cls.title = title
        cls.message = message

    @classmethod
    def question(cls, parent, title, message, *args, **kwargs):
        cls.called_function = 'question'
        cls.title = title
        cls.message = message
        return cls.question_return_value
