# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.ui.lib import QtWidgets


class VersionListView(QtWidgets.QListView):
    """A custom list view to display Version info
    """

    def __init__(self, *args, **kwargs):
        super(VersionListView, self).__init__(*args, **kwargs)
        
        # TODO: Implement this as a class with all its context menus etc.
