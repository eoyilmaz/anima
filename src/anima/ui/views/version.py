# -*- coding: utf-8 -*-

from anima.ui.lib import QtWidgets


class VersionListView(QtWidgets.QListView):
    """A custom list view to display Version info"""

    def __init__(self, *args, **kwargs):
        super(VersionListView, self).__init__(*args, **kwargs)

        # TODO: Implement this as a class with all its context menus etc.
