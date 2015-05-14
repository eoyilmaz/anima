# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Selection Manager

v0.1.0

A selection list manager, stores the active selection list and then you can
replace, add, deselect, save or update the stored list as quick selection list.
It also supports restoring of previously saved selection sets..

ChangeLog :
-----------

v0.1.0
- initial version

"""

import pymel.core as pm

__version__ = "0.1.0"


class SelectionSet(object):
    """Custom SelectionSet

    Ex::

      from anima.env.mayaEnv import selection_manager

      selM1 = selection_manager.SelectionSet()
      selM1.name = 'My_Sel_List'

      # select some objects in Maya scene
      selM1.update()

      # now store the objects in an ObjectSet
      selM1.save()

      # then do some fancy selections with it
      selM1.replace()
      selM1.add()
      selM1.subtract()

      # restore a new SelectionSet from an ObjectSet instance
      selM2 = selection_manager.SelectionSet()
      selM2.restore(selM1.__selectionSet__)
    """

    def __init__(self):
        self.__storedSelList__ = []
        self.__selectionSet__ = None
        self.__name__ = 'SelectionSet#'

    @property
    def name(self):
        """getter for the self.__name__
        """
        return self.__name__

    @name.setter
    def name(self, new_name):
        """setter for the self.__name__
        """
        self.__name__ = new_name
        if self.__selectionSet__:
            pm.rename(self.__selectionSet__, new_name)

    def replace(self):
        pm.select(self.__storedSelList__, replace=True)

    def add(self):
        """adds the given list of objects to the set

        :param objectList[]: A list of maya objects
        """
        pm.select(self.__storedSelList__, add=1)

    def subtract(self):
        """
        """
        pm.select(self.__storedSelList__, d=1)

    def save(self):
        """creates a new SelectionSet instance with the stored objects
        """
        self.__storedSelList__ = pm.ls(sl=1)
        if self.__storedSelList__:
            self.__selectionSet__ = pm.sets(
                self.__storedSelList__,
                name=self.name
            )
        else:
            self.__selectionSet__ = pm.sets(name=self.name)

        if self.__selectionSet__.hasAttr('selectionManagerData'):
            pass
        else:
            self.__selectionSet__.addAttr('selectionManagerData', at='compound', nc=1)

            self.__selectionSet__.addAttr(
                'version', dt='string', p='selectionManagerData'
            )
            self.__selectionSet__.selectionManagerData.version.set(
                __version__, type="string"
            )

    def restore(self, selection_set):
        """restores set with the given set
        """
        self.__selectionSet__ = selection_set
        self.__storedSelList__ = pm.sets(selection_set, q=True)
        self.__name__ = selection_set.name()

    def update(self):
        """updates the storedSelList with the selection from maya
        """
        self.__storedSelList__ = pm.ls(sl=1)
        if self.__selectionSet__:
            pm.delete(self.__selectionSet__)
            self.save()


class SelectionRow(object):
    """Handles the buttons R/+/-/S/U/D along with a :ckBass:`.SelectionSet`

    :param parent:
    """

    def __init__(self, parent, selection_set):
        self.replaceButton = None
        self.addButton = None
        self.descriptionField = None
        self.subtractButton = None
        self.saveButton = None
        self.updateButton = None
        self.deleteButton = None
        self.layout = None

        self.parent = parent

        self._description = ''
        self._selectionSet = None
        self.selection_set = selection_set

    @property
    def selection_set(self):
        """getter for the self._selectionSet
        """
        return self._selectionSet

    @selection_set.setter
    def selection_set(self, selection_set):
        """setter for the self._selectionSet
        """
        self._selectionSet = selection_set
        if selection_set:
            self.description = self._selectionSet.name

    @property
    def description(self):
        """getter for the self._description
        """
        return self._description

    @description.setter
    def description(self, desc):
        """setter for the self._description
        """
        self._description = desc
        if self.descriptionField:
            self.descriptionField.text = desc

    def _draw(self):
        # create buttons under parent and save them in local variables
        grid_layout_width = pm.gridLayout(
            "selectionManager_gridLayout1",
            q=True,
            w=True
        )
        form_layout = pm.formLayout(
            p="selectionManager_gridLayout1",
            w=grid_layout_width,
            nd=100
        )
        with form_layout:
            self.replaceButton = pm.button(ann="Replace", l="R", w=17)
            self.addButton = pm.button(ann="Add", l="+", w=17)
            self.subtractButton = pm.button(ann="Subtract", l="-", w=17)
            self.saveButton = pm.button(
                ann="Save as quick selection set with the description as the "
                    "name of the set",
                l="S",
                w=17
            )
            self.updateButton = pm.button(
                ann="Updates the list with the current selection",
                l="U",
                w=17
            )
            self.deleteButton = pm.button(
                ann="Deletes this button set",
                l="D",
                w=17
            )
            self.descriptionField = pm.textField(text=self.description, w=204)

        self.description = self.description

        self.layout = pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (self.replaceButton, "left", 0), (self.replaceButton, "top", 0),
                (self.replaceButton, "bottom", 0),
                (self.addButton, "top", 0), (self.addButton, "bottom", 0),
                (self.subtractButton, "top", 0), (self.subtractButton, "bottom", 0),
                (self.saveButton, "top", 0), (self.saveButton, "bottom", 0),
                (self.updateButton, "top", 0), (self.updateButton, "bottom", 0),
                (self.deleteButton, "top", 0), (self.deleteButton, "bottom", 0),
                (self.descriptionField, "top", 0), (self.descriptionField, "bottom", 0),
                (self.descriptionField, "right", 0)
            ],
            attachControl=[
                (self.addButton, "left", 0, self.replaceButton),
                (self.subtractButton, "left", 0, self.addButton),
                (self.saveButton, "left", 0, self.subtractButton),
                (self.updateButton, "left", 0, self.saveButton),
                (self.deleteButton, "left", 0, self.updateButton),
                (self.descriptionField, "left", 0, self.deleteButton)
            ],
            attachPosition=[
                (self.replaceButton, "right", 0, 5),
                (self.addButton, "right", 0, 10),
                (self.subtractButton, "right", 0, 15),
                (self.saveButton, "right", 0, 20),
                (self.updateButton, "right", 0, 25),
                (self.deleteButton, "right", 0, 30)
            ]
        )

        self.replaceButton.setCommand(pm.Callback(self.selection_set.replace))
        self.addButton.setCommand(pm.Callback(self.selection_set.add))
        self.subtractButton.setCommand(pm.Callback(self.selection_set.subtract))
        self.saveButton.setCommand(pm.Callback(self.save_button))
        self.updateButton.setCommand(pm.Callback(self.selection_set.update))
        self.deleteButton.setCommand(pm.Callback(self.delete_button))

    def save_button(self):
        self.selection_set.__name__ = pm.textField(
            self.descriptionField,
            q=True,
            tx=True
        )
        self.selection_set.save()

    def delete_button(self):
        """delete rows
        """
        pm.deleteUI(self.layout, layout=True)


class SelectionRowFactory(object):
    """reads maya sets and generates SelectionRow instances
    """

    @classmethod
    def create_row(cls, parent):
        """creates a selection_set and a row
        """
        selectionSet = SelectionSet()
        selectionSet.update()
        row = SelectionRow(parent, selectionSet)
        return row

    @classmethod
    def restore_rows(cls, parent):
        """
        :returns: list of SelectionRows
        """
        # get all the selection sets
        # find sets with selectionManager_version attribute
        # read the members
        # create a SelectionRow instance
        rows = []
        for node in pm.ls(type=pm.nt.ObjectSet):

            # do something with node
            if node.hasAttr('selectionManagerData'):
                # this is a SelectionSet
                sel_set = SelectionSet()
                sel_set.restore(node)
                row = SelectionRow(parent, sel_set)
                rows.append(row)

        return rows


def UI():
    """The UI
    """
    if pm.window("selectionManagerWindow", ex=True):
        pm.deleteUI("selectionManagerWindow", wnd=True)

    selection_manager_window = pm.window(
        'selectionManagerWindow',
        wh=(300, 200),
        title=("Selection Manager %s" % __version__)
    )
    form_layout1 = pm.formLayout("selectionManager_formLayout1", nd=100)
    with form_layout1:
        button1 = pm.button(l="Add selection to List")
        scroll_layout1 = pm.scrollLayout("selectionManager_scrollLayout1", cr=True)
        with scroll_layout1:
            pm.gridLayout(
                "selectionManager_gridLayout1",
                nc=1,
                cwh=(((17 * 4) + 204), 22),
                aec=False,
                cr=False
            )

    pm.formLayout(
        form_layout1, edit=True,
        attachForm=[
            (button1, "left", 0),
            (button1, "right", 0),
            (button1, "top", 0),
            (scroll_layout1, "left", 0),
            (scroll_layout1, "right", 0),
            (scroll_layout1, "bottom", 0)
        ],
        attachControl=[(scroll_layout1, "top", 0, button1)],
        attachNone=[(button1, "bottom")])

    def create_row(parent):
        row = SelectionRowFactory.create_row(parent)
        row._draw()

    button1.setCommand(pm.Callback(create_row, scroll_layout1))

    # restore rows from Maya scene
    for row in SelectionRowFactory.restore_rows(scroll_layout1):
        row._draw()

    pm.showWindow(selection_manager_window)
