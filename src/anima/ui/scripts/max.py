
import MaxPlus


from anima.dcc import max as max_dcc
from anima.utils import do_db_setup


class Executor(object):
    """ """

    def __init__(self):
        self.application = None
        # from anima.ui.lib import QtCore
        # self.event_loop = QtCore.QEventLoop()

    def exec_(self, app, dialog):
        self.application = app
        # add event loop callback to processEvents
        dialog.exec_()

    # def processEvents(self):
    #     self.event_loop.processEvents()
    #     self.application.sendPostedEvents(None, 0)


def show_version_dialog():
    """Show version_dialog UI for Max."""
    do_db_setup()

    from anima.ui.dialogs import version_dialog

    m = max_dcc.Max()
    max_window = MaxPlus.GetQMaxWindow()

    version_dialog.UI(dcc=m, executor=Executor(), parent=max_window)


def show_version_updater():
    """Show version_updater UI for Max."""
    do_db_setup()

    from anima.ui.dialogs import version_updater

    m = max_dcc.Max()
    max_window = MaxPlus.GetQMaxWindow()

    version_updater.UI(dcc=m, executor=Executor(), parent=max_window)
