# -*- coding: utf-8 -*-

from anima.ui.base import ui_caller, QtCore, QtWidgets


def UI(environment=None, app_in=None, executor=None):
    """ """
    return ui_caller(app_in, executor, MainDialog, environment=environment)


class MainDialog(QtWidgets.QDialog):
    def __init__(self, environment=None, parent=None):
        super(MainDialog, self).__init__(parent)
        self.use_selection_check_box = None
        self.references_tab = None
        self.references_tree_view = None
        self.ticket_text_edit = None
        self.create_ticket_push_button = None
        self.update_to_latest_version_push_button = None
        self.save_edits_as_new_version_push_button = None
        self.textures_tab = None
        self.animation_cache_tab = None
        self.button_box = None
        self.setup_ui()

    def setup_ui(self):
        """Create UI elements."""
        self.setWindowTitle("Reference Editor")
        self.resize(853, 608)
        main_layout = QtWidgets.QVBoxLayout(self)
        vertical_layout_1 = QtWidgets.QVBoxLayout()

        # Use Selection Check Box
        self.use_selection_check_box = QtWidgets.QCheckBox(self)
        self.use_selection_check_box.setText("Use Selection")
        vertical_layout_1.addWidget(self.use_selection_check_box)

        tab_widget = QtWidgets.QTabWidget(self)
        self.references_tab = QtWidgets.QWidget()
        horizontal_layout_1 = QtWidgets.QHBoxLayout(self.references_tab)
        self.references_tree_view = QtWidgets.QTreeView(self.references_tab)
        horizontal_layout_1.addWidget(self.references_tree_view)
        frame = QtWidgets.QFrame(self.references_tab)
        frame.setFrameShape(QtWidgets.QFrame.Box)
        frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        vertical_layout_2 = QtWidgets.QVBoxLayout(frame)

        # Ref Info
        ref_info_label = QtWidgets.QLabel(frame)
        ref_info_label.setText("Ref Info")
        vertical_layout_2.addWidget(ref_info_label)

        # Ticket
        self.ticket_text_edit = QtWidgets.QTextEdit(frame)
        vertical_layout_2.addWidget(self.ticket_text_edit)

        self.create_ticket_push_button = QtWidgets.QPushButton(frame)
        self.create_ticket_push_button.setText("Create Ticket")
        vertical_layout_2.addWidget(self.create_ticket_push_button)

        # Update To Latest Version
        self.update_to_latest_version_push_button = QtWidgets.QPushButton(frame)
        vertical_layout_2.addWidget(self.update_to_latest_version_push_button)
        self.update_to_latest_version_push_button.setText("Update To Latest Version")

        # Save Edits As New Version
        self.save_edits_as_new_version_push_button = QtWidgets.QPushButton(frame)
        vertical_layout_2.addWidget(self.save_edits_as_new_version_push_button)
        self.save_edits_as_new_version_push_button.setText("Save Edits as New Version")

        horizontal_layout_1.addWidget(frame)
        horizontal_layout_1.setStretch(0, 1)
        tab_widget.addTab(self.references_tab, "")

        # Textures Tab
        self.textures_tab = QtWidgets.QWidget()
        tab_widget.addTab(self.textures_tab, "")

        # Animation Cache Tab
        self.animation_cache_tab = QtWidgets.QWidget()
        tab_widget.addTab(self.animation_cache_tab, "")

        vertical_layout_1.addWidget(tab_widget)
        main_layout.addLayout(vertical_layout_1)
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        main_layout.addWidget(self.button_box)

        tab_widget.setCurrentIndex(0)

        # Signals
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Tab Order
        self.setTabOrder(self.use_selection_check_box, tab_widget)
        self.setTabOrder(tab_widget, self.button_box)

        tab_widget.setTabText(tab_widget.indexOf(self.references_tab), "References")
        tab_widget.setTabText(tab_widget.indexOf(self.textures_tab), "Textures")
        tab_widget.setTabText(
            tab_widget.indexOf(self.animation_cache_tab), "Animation Caches"
        )
