# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import unittest2
from anima.ui.lib import QtGui
from anima.ui.progress_dialog import ProgressDialogManager, ProgressCaller


class PatchedProgressDialog(object):
    """A dummy class for patching QtGui.QProgressDialog
    """

    def __init__(self):
        self.call_info = {}
        self.patched_func_names = [
            'setRange', 'setValue', 'setLabelText', 'show', 'close'
        ]

        self.register_functions()

    def __call_recorder__(self, *args, **kwargs):
        """records the call to a function with arguments and keyword arguments
        """
        self.call_info['setRange'] = [args, kwargs]

    def register_functions(self):
        for f in self.patched_func_names:
            setattr(self, f, self.__call_recorder__)


class ProgressDialogManagerTestCase(unittest2.TestCase):
    """tests the maya.ProgressDialogManager class
    """

    original_progress_dialog = None

    @classmethod
    def setUpClass(cls):
        """set up tests in class level
        """
        # patch QtGui.QProgressDialog
        cls.original_progress_dialog = QtGui.QProgressDialog
        QtGui.QProgressDialog = PatchedProgressDialog

    @classmethod
    def tearDownClass(cls):
        """clean up tests in class level
        """
        # restore the QtGui.QProgressDialog
        QtGui.QProgressDialog = cls.original_progress_dialog

    def setUp(self):
        """set up the test
        """
        pm = ProgressDialogManager()
        # re initialize for each test
        pm.__init__()

    def test_being_singleton(self):
        """testing if the ProgressDialogManager is a Singleton class.
        """
        pm1 = ProgressDialogManager()
        pm2 = ProgressDialogManager()
        self.assertEqual(id(pm1), id(pm2))

    def test_register_will_return_a_progress_caller_instance(self):
        """testing if the ProgressDialogManager.register() method will return a
        ProgressCaller instance
        """
        pm = ProgressDialogManager()
        caller = pm.register(10)
        self.assertIsInstance(caller, ProgressCaller)

        self.assertEqual(caller.max_iterations, 10)
        self.assertEqual(caller.current_step, 0)

    def test_register_will_store_the_given_caller(self):
        """testing if ProgressWindow.register() method will store the given
        name as a key in the ProgressWindow.callers dictionary
        """
        pm = ProgressDialogManager()
        caller = pm.register(100)
        self.assertIn(caller, pm.callers)

    def test_register_will_create_the_window_if_it_is_not_created_yet(self):
        """testing if the register method will create the progressWindow if it
        is not created yet
        """
        pm = ProgressDialogManager()
        self.assertFalse(pm.in_progress)
        pm.register(5)
        self.assertTrue(pm.in_progress)

    def test_step_will_increment_the_call_count_of_the_given_caller(self):
        """testing if the step method will increment the step of the caller
        """
        pm = ProgressDialogManager()
        caller = pm.register(100)
        self.assertEqual(caller.current_step, 0)

        pm.step(caller)
        self.assertEqual(caller.current_step, 1)

        pm.step(caller)
        self.assertEqual(caller.current_step, 2)

    def test_step_removes_the_given_caller_if_it_is_at_maximum(self):
        """testing if the step method will automatically remove the caller from
        the list if the caller reached to its maximum
        """
        pm = ProgressDialogManager()
        self.assertFalse(pm.in_progress)
        caller = pm.register(5)
        self.assertTrue(pm.in_progress)
        self.assertEqual(caller.current_step, 0)
        self.assertTrue(pm.in_progress)
        self.assertIn(caller, pm.callers)

        for i in range(5):
            caller.step()

        self.assertNotIn(caller, pm.callers)
        self.assertFalse(pm.in_progress)

    def test_step_will_step_the_progress_dialog(self):
        """testing if the step method will call QProgressDialog.setRange()
        properly
        """
        pm = ProgressDialogManager()
        caller = pm.register(5)
        pm.step(caller, 2)

        self.assertIn('setRange', pm.dialog.call_info)

        # check the value
        self.assertEqual(pm.dialog.call_info['setRange'], [(2,), {}])

    def test_end_progress_method_removes_the_given_caller_from_list(self):
        """testing if the end_progress method will remove the given caller from
        the callers list
        """
        pm = ProgressDialogManager()
        caller = pm.register(5)
        caller.step()
        self.assertIn(caller, pm.callers)
        pm.end_progress(caller)
        self.assertNotIn(caller, pm.callers)

    def test_end_progress_will_close_dialog_if_there_are_no_callers_left(self):
        """testing if the end_progress method will close the progress dialog
        it there are no callers left
        """
        pm = ProgressDialogManager()
        caller = pm.register(5)
        caller.step()
        self.assertIn(caller, pm.callers)
        pm.end_progress(caller)
        self.assertNotIn(caller, pm.callers)
