# -*- coding: utf-8 -*-

import unittest
from anima.testing import CallInfo
from anima.ui.lib import QtGui
from anima.ui.progress_dialog import ProgressDialogManager, ProgressCaller


class ProgressDialogManagerTestCase(unittest.TestCase):
    """tests the maya.ProgressDialogManager class
    """

    original_progress_dialog = None

    @classmethod
    def setUpClass(cls):
        """set up tests in class level
        """
        # patch QtGui.QProgressDialog
        cls.original_progress_dialog = QtGui.QProgressDialog
        QtGui.QProgressDialog = CallInfo

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

        self.assertEqual(caller.max_steps, 10)
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
        caller = pm.register(5, 'test title')
        pm.step(caller, 2)

        self.assertIn('setRange', pm.dialog.call_info)

        # check the values
        self.assertEqual(pm.dialog.call_info['setRange'], [(0, 5), {}])
        self.assertEqual(pm.dialog.call_info['setValue'], [(2,), {}])

    def test_step_will_set_the_dialog_title(self):
        """testing if the step method will set the dialog title to the stepped
        caller
        """
        pm = ProgressDialogManager()
        test_title1 = 'test title 1'
        test_title2 = 'test title 2'
        caller1 = pm.register(5, test_title1)
        caller2 = pm.register(5, test_title2)
        pm.step(caller1)
        self.assertEqual(pm.dialog.call_info['setLabelText'],
                         [('%s : ' % test_title1,), {}])

        pm.step(caller2)
        self.assertEqual(pm.dialog.call_info['setLabelText'],
                         [('%s : ' % test_title2,), {}])

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
