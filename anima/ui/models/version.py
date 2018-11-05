# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


from anima import logger
from anima.ui.lib import QtGui, QtCore


def set_item_color(item, color):
    """sets the item color

    :param item: the item
    :param color: the color
    """
    foreground = item.foreground()
    foreground.setColor(color)
    item.setForeground(foreground)


class VersionItem(QtGui.QStandardItem):
    """Implements the Version as a QStandardItem
    """

    def __init__(self, *args, **kwargs):
        QtGui.QStandardItem.__init__(self, *args, **kwargs)
        logger.debug(
            'VersionItem.__init__() is started for item: %s' % self.text()
        )
        self.loaded = False
        self.version = None
        self.parent = None
        self.pseudo_model = None
        self.fetched_all = False
        self.setEditable(False)
        logger.debug(
            'VersionItem.__init__() is finished for item: %s' % self.text()
        )

    def clone(self):
        """returns a copy of this item
        """
        logger.debug(
            'VersionItem.clone() is started for item: %s' % self.text()
        )
        new_item = VersionItem()
        new_item.version = self.version
        new_item.parent = self.parent
        new_item.fetched_all = self.fetched_all
        logger.debug(
            'VersionItem.clone() is finished for item: %s' % self.text()
        )
        return new_item

    def canFetchMore(self):
        logger.debug(
            'VersionItem.canFetchMore() is started for item: %s' % self.text()
        )
        if self.version and not self.fetched_all:
            return_value = bool(self.version.inputs)
        else:
            return_value = False
        logger.debug(
            'VersionItem.canFetchMore() is finished for item: %s' % self.text()
        )
        return return_value
    
    @classmethod
    def generate_version_row(cls, parent, pseudo_model, version):
        """Generates a new version row

        :return:
        """
        # column 0
        version_item = VersionItem(0, 0)
        version_item.parent = parent
        version_item.pseudo_model = pseudo_model
        
        version_item.version = version
        version_item.setEditable(False)
        reference_resolution = pseudo_model.reference_resolution
        
        if version in reference_resolution['update']:
            action = 'update'
            font_color = QtGui.QColor(192, 128, 0)
            if version in reference_resolution['root']:
                version_item.setCheckable(True)
                version_item.setCheckState(QtCore.Qt.Checked)
        elif version in reference_resolution['create']:
            action = 'create'
            font_color = QtGui.QColor(192, 0, 0)
            if version in reference_resolution['root']:
                version_item.setCheckable(True)
                version_item.setCheckState(QtCore.Qt.Checked)
        else:
            font_color = QtGui.QColor(0, 192, 0)
            action = ''
        
        version_item.action = action
        
        set_item_color(version_item, font_color)
        
        # thumbnail
        thumbnail_item = QtGui.QStandardItem()
        thumbnail_item.setEditable(False)
        # thumbnail_item.setText('no thumbnail')
        thumbnail_item.version = version
        thumbnail_item.action = action
        set_item_color(thumbnail_item, font_color)
        
        # Nice Name
        nice_name_item = QtGui.QStandardItem()
        nice_name_item.toolTip()
        nice_name_item.setText(
            '%s_v%s' % (
                version.nice_name,
                ('%s' % version.version_number).zfill(3)
            )
        )
        nice_name_item.setEditable(False)
        nice_name_item.version = version
        nice_name_item.action = action
        set_item_color(nice_name_item, font_color)
        
        # Take
        take_item = QtGui.QStandardItem()
        take_item.setEditable(False)
        take_item.setText(version.take_name)
        take_item.version = version
        take_item.action = action
        set_item_color(take_item, font_color)
        
        # Current
        current_version_item = QtGui.QStandardItem()
        current_version_item.setText('%s' % version.version_number)
        current_version_item.setEditable(False)
        current_version_item.version = version
        current_version_item.action = action
        set_item_color(current_version_item, font_color)
        
        # Latest
        latest_published_version = version.latest_published_version
        
        latest_published_version_item = QtGui.QStandardItem()
        latest_published_version_item.version = version
        latest_published_version_item.action = action
        latest_published_version_item.setEditable(False)
        
        latest_published_version_text = 'No Published Version'
        if latest_published_version:
            latest_published_version_text = '%s' % \
                                            latest_published_version.version_number
        latest_published_version_item.setText(
            latest_published_version_text
        )
        set_item_color(latest_published_version_item, font_color)
        
        # Action
        action_item = QtGui.QStandardItem()
        action_item.setEditable(False)
        action_item.setText(action)
        action_item.version = version
        action_item.action = action
        set_item_color(action_item, font_color)
        
        # Updated By
        updated_by_item = QtGui.QStandardItem()
        updated_by_item.setEditable(False)
        updated_by_text = ''
        if latest_published_version.updated_by:
            updated_by_text = latest_published_version.updated_by.name
        updated_by_item.setText(updated_by_text)
        updated_by_item.version = version
        updated_by_item.action = action
        set_item_color(updated_by_item, font_color)
        
        # Description
        description_item = QtGui.QStandardItem()
        if latest_published_version:
            description_item.setText(latest_published_version.description)
        description_item.setEditable(False)
        description_item.version = version
        description_item.action = action
        set_item_color(description_item, font_color)
        
        # # Path
        # path_item = QtGui.QStandardItem()
        # if latest_published_version:
        #     path_item.setText(version.absolute_full_path)
        # path_item.setEditable(True)
        # set_item_color(path_item, font_color)
        
        return [version_item, thumbnail_item, nice_name_item, take_item,
                current_version_item, latest_published_version_item,
                action_item, updated_by_item, description_item]
    
    def fetchMore(self):
        logger.debug(
            'VersionItem.fetchMore() is started for item: %s' % self.text()
        )
        
        if self.canFetchMore():
            # model = self.model() # This will cause a SEGFAULT
            versions = sorted(self.version.inputs, key=lambda x: x.full_path)
            
            for version in versions:
                self.appendRow(
                    self.generate_version_row(self, self.pseudo_model, version)
                )
            
            self.fetched_all = True
        logger.debug(
            'VersionItem.fetchMore() is finished for item: %s' % self.text()
        )
    
    def hasChildren(self):
        logger.debug(
            'VersionItem.hasChildren() is started for item: %s' % self.text()
        )
        if self.version:
            return_value = bool(self.version.inputs)
        else:
            return_value = False
        logger.debug(
            'VersionItem.hasChildren() is finished for item: %s' % self.text()
        )
        return return_value
    
    def type(self, *args, **kwargs):
        """
        """
        return QtGui.QStandardItem.UserType + 2


class VersionTreeModel(QtGui.QStandardItemModel):
    """Implements the model view for the version hierarchy
    """
    
    def __init__(self, flat_view=False, *args, **kwargs):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        logger.debug('VersionTreeModel.__init__() is started')
        self.root = None
        self.root_versions = []
        self.reference_resolution = None
        self.flat_view = flat_view
        logger.debug('VersionTreeModel.__init__() is finished')
    
    def populateTree(self, versions):
        """populates tree with root versions
        """
        logger.debug('VersionTreeModel.populateTree() is started')
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            ['Do Update?', 'Thumbnail', 'Task', 'Take', 'Current', 'Latest',
             'Action', 'Updated By', 'Notes']
        )
        
        self.root_versions = versions
        for version in versions:
            self.appendRow(
                VersionItem.generate_version_row(None, self, version)
            )
        
        logger.debug('VersionTreeModel.populateTree() is finished')
    
    def canFetchMore(self, index):
        logger.debug(
            'VersionTreeModel.canFetchMore() is started for index: %s' % index
        )
        if not index.isValid():
            return_value = False
        else:
            item = self.itemFromIndex(index)
            return_value = item.canFetchMore()
        logger.debug(
            'VersionTreeModel.canFetchMore() is finished for index: %s' % index
        )
        return return_value
    
    def fetchMore(self, index):
        """fetches more elements
        """
        logger.debug(
            'VersionTreeModel.canFetchMore() is started for index: %s' % index
        )
        if index.isValid():
            item = self.itemFromIndex(index)
            item.fetchMore()
        logger.debug(
            'VersionTreeModel.canFetchMore() is finished for index: %s' % index
        )
    
    def hasChildren(self, index):
        """returns True or False depending on to the index and the item on the
        index
        """
        logger.debug(
            'VersionTreeModel.hasChildren() is started for index: %s' % index
        )
        if not index.isValid():
            return_value = len(self.root_versions) > 0
        else:
            if self.flat_view:
                return False
            else:
                item = self.itemFromIndex(index)
                return_value = False
                if item:
                    return_value = item.hasChildren()
        logger.debug(
            'VersionTreeModel.hasChildren() is finished for index: %s' % index
        )
        return return_value
