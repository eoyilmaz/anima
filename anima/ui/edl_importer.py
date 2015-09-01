# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import shutil
import subprocess
import os
from anima.utils import do_db_setup

import anima
from anima.ui import IS_PYSIDE, IS_PYQT4
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtGui, QtCore


if IS_PYSIDE():
    from anima.ui.ui_compiled import edl_importer_UI_pyside as edl_importer_UI
elif IS_PYQT4():
    from anima.ui.ui_compiled import edl_importer_UI_pyqt4 as edl_importer_UI


def UI(app_in=None, executor=None, **kwargs):
    """
    :param environment: The
      :class:`~stalker.models.env.EnvironmentBase` can be None to let the UI to
      work in "environmentless" mode in which it only creates data in database
      and copies the resultant version file path to clipboard.

    :param mode: Runs the UI either in Read-Write (0) mode or in Read-Only (1)
      mode.

    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class LineEdit(QtGui.QLineEdit):
    """Custom Plain text edit that handles drag and drop
    """

    def __init__(self, *args, **kwargs):
        super(LineEdit, self).__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        mime_data = e.mimeData()
        if mime_data.hasFormat('text/plain') or mime_data.hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        mime_data = e.mimeData()
        path = ''
        if mime_data.hasFormat('text/plain'):
            # on linux
            path = mime_data().text().replace('file://', '').strip()
        elif mime_data.hasUrls():
            # on windows
            url = mime_data.urls()[0]
            path = url.toString().replace('file:///', '').strip()
        self.setText(path)


class MainDialog(QtGui.QDialog, edl_importer_UI.Ui_Dialog,
                 AnimaDialogBase):
    """The Main Window for EDL Importer.

    This is mainly written for AVID Media Composer. It makes it easy to import
    edl files and clips to AVID.

    For now, the editor still needs to do some manual actions to import the EDL
    content to AVID (we hate it).
    """

    def __init__(self):
        super(MainDialog, self).__init__()
        self.setupUi(self)

        self.media_files_path = ''
        self.cache_file_full_path = os.path.normpath(
            os.path.expanduser(
                os.path.expandvars(
                    os.path.join(
                        anima.local_cache_folder,
                        anima.avid_media_file_path_storage
                    )
                )
            )
        )

        self.edl_path_lineEdit = LineEdit()

        self.formLayout.setWidget(
            1,
            QtGui.QFormLayout.FieldRole,
            self.edl_path_lineEdit
        )

        self.setup_signals()
        self.restore_media_file_path()

        # connect to database
        do_db_setup()

    def setup_signals(self):
        """setting up signals
        """
        QtCore.QObject.connect(
            self.media_files_path_lineEdit,
            QtCore.SIGNAL('textChanged(QString)'),
            self.store_media_file_path
        )

        QtCore.QObject.connect(
            self.edl_path_lineEdit,
            QtCore.SIGNAL('textChanged(QString)'),
            self.open_edl
        )

        QtCore.QObject.connect(
            self.send_pushButton,
            QtCore.SIGNAL('clicked()'),
            self.send
        )

    def open_edl(self, path):
        """Opens the edl in the given path

        :param path: A string showing the EDL path
        :return:
        """
        edl_content = self.read_edl(path)
        self.edl_preview_plainTextEdit.setPlainText(edl_content)

    def read_edl(self, path):
        """Reads the content of the edl in the given path

        :param path: A string showing the EDL path
        :return: str
        """
        try:
            with open(path) as f:
                edl_content = f.read()
        except IOError:
            edl_content = ''

        return edl_content

    def send(self):
        """Sends the edl content to
        """
        edl_path = self.edl_path_lineEdit.text()
        media_path = self.media_files_path_lineEdit.text()

        # error if media_path does not exist
        if not os.path.exists(media_path):
            QtGui.QMessageBox.critical(
                self,
                "Error",
                "Media path doesn't exists"
            )
            return
        else:
            self.send_edl(edl_path, media_path)

    def send_edl(self, edl_path, media_path):
        """Sends the edl with the given path to AVID, also copies the MXF files
        to the media folder path

        :param edl_path: The edl path
        :param media_path: The AVID media files path
        """
        # get the source clips from edl
        import edl
        parser = edl.Parser('24')  # just use some random frame rate
        with open(edl_path) as f:
            l = parser.parse(f)

        total_item_count = len(l) + 1

        progress_dialog = QtGui.QProgressDialog(self)
        progress_dialog.setRange(0, total_item_count)
        progress_dialog.setLabelText('Copying MXF files...')
        progress_dialog.show()

        step = 0
        progress_dialog.setValue(step)

        for event in l:
            # assert isinstance(event, edl.Event)
            mov_full_path = event.source_file
            mxf_full_path = os.path.expandvars(
                os.path.splitext(mov_full_path)[0] + '.mxf'
            )
            target_mxf_path = os.path.expandvars(
                os.path.join(
                    media_path,
                    os.path.basename(mxf_full_path)
                )
            )

            shutil.copy(
                mxf_full_path,
                target_mxf_path
            )

            step += 1
            progress_dialog.setValue(step)

        # and call EDL_Manager.exe with the edl_path
        progress_dialog.setLabelText('Calling EDL Manager...')
        step += 1
        progress_dialog.setValue(step)
        subprocess.call(['EDL_Mgr', os.path.normcase(edl_path)], shell=False)

    def store_media_file_path(self, path):
        """stores the given path as the avid media file path in anima cache
        folder.

        :param str path: The path to be stored
        :return:
        """
        # make dirs first
        try:
            os.makedirs(os.path.dirname(self.cache_file_full_path))
        except OSError:
            pass  # file already exists
        finally:
            with open(self.cache_file_full_path, 'w') as f:
                f.write(path)

    def restore_media_file_path(self):
        """restores the media file path
        """
        try:
            with open(self.cache_file_full_path) as f:
                media_file_path = f.read()

            self.media_files_path_lineEdit.setText(media_file_path)
        except IOError:
            pass  # not stored yet
