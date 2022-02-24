# -*- coding: utf-8 -*-
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

      from anima.dcc.mayaEnv import selection_manager

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
        self.__stored_selection_list__ = []
        self.__selection_set__ = None
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
        if self.__selection_set__:
            pm.rename(self.__selection_set__, new_name)

    def replace(self):
        try:
            pm.select(self.__stored_selection_list__, replace=True)
        except pm.MayaNodeError:
            # nodes should have been deleted
            # remove anything that doesn't exist
            pass

    def add(self):
        """adds the given list of objects to the set
        """
        pm.select(self.__stored_selection_list__, add=1)

    def subtract(self):
        """
        """
        pm.select(self.__stored_selection_list__, d=1)

    def and_(self):
        """returns the selected and the ones on the selection set
        """
        pm.select(set(self.__stored_selection_list__).intersection(pm.ls(sl=1)))

    def or_(self):
        """returns the selected and the ones on the selection set
        """
        pm.select(set(self.__stored_selection_list__).remove(pm.ls(sl=1)))

    def save(self):
        """creates a new SelectionSet instance with the stored objects
        """
        # self.__stored_selection_list__ = pm.ls(sl=1)
        if self.__stored_selection_list__:
            self.__selection_set__ = pm.sets(
                self.__stored_selection_list__,
                name=self.name
            )
        else:
            self.__selection_set__ = pm.sets(name=self.name)

        if self.__selection_set__.hasAttr('selectionManagerData'):
            pass
        else:
            self.__selection_set__.addAttr('selectionManagerData', at='compound', nc=1)

            self.__selection_set__.addAttr(
                'version', dt='string', p='selectionManagerData'
            )
            self.__selection_set__.selectionManagerData.version.set(
                __version__, type="string"
            )

    def restore(self, selection_set):
        """restores set with the given set
        """
        self.__selection_set__ = selection_set
        self.__stored_selection_list__ = pm.sets(selection_set, q=True)
        self.__name__ = selection_set.name()

    def update(self):
        """updates the storedSelList with the selection from maya
        """
        self.__stored_selection_list__ = pm.ls(sl=1)
        if self.__selection_set__:
            pm.delete(self.__selection_set__)
            self.save()


class SelectionRow(object):
    """Handles the buttons R/+/-/&&/|/S/U/D along with a :ckBass:`.SelectionSet`

    :param parent:
    """

    def __init__(self, parent, selection_set):
        self.replace_button = None
        self.add_button = None
        self.and_button = None
        self.or_button = None
        self.description_field = None
        self.subtract_button = None
        self.save_button = None
        self.update_button = None
        self.del_button = None
        self.layout = None

        self.parent = parent

        self._description = ''
        self._selection_set = None
        self.selection_set = selection_set

    @property
    def selection_set(self):
        """getter for the self._selectionSet
        """
        return self._selection_set

    @selection_set.setter
    def selection_set(self, selection_set):
        """setter for the self._selectionSet
        """
        self._selection_set = selection_set
        if selection_set:
            self.description = self._selection_set.name

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
        if self.description_field:
            self.description_field.text = desc

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
            self.replace_button = pm.button(ann="Replace", l="R", w=17)
            self.add_button = pm.button(ann="Add", l="+", w=17)
            self.subtract_button = pm.button(ann="Subtract", l="-", w=17)
            self.and_button = pm.button(ann="And", l="&&", w=17)
            self.or_button = pm.button(ann="Or", l="|", w=17)
            self.save_button = pm.button(
                ann="Save as quick selection set with the description as the "
                    "name of the set",
                l="S",
                w=17
            )
            self.update_button = pm.button(
                ann="Updates the list with the current selection",
                l="U",
                w=17
            )
            self.del_button = pm.button(
                ann="Deletes this button set",
                l="D",
                w=17
            )
            self.description_field = pm.textField(text=self.description, w=204)

        self.description = self.description

        self.layout = pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (self.replace_button, "left", 0), (self.replace_button, "top", 0),
                (self.replace_button, "bottom", 0),
                (self.add_button, "top", 0), (self.add_button, "bottom", 0),
                (self.subtract_button, "top", 0), (self.subtract_button, "bottom", 0),
                (self.and_button, "top", 0), (self.and_button, "bottom", 0),
                (self.or_button, "top", 0), (self.or_button, "bottom", 0),
                (self.save_button, "top", 0), (self.save_button, "bottom", 0),
                (self.update_button, "top", 0), (self.update_button, "bottom", 0),
                (self.del_button, "top", 0), (self.del_button, "bottom", 0),
                (self.description_field, "top", 0), (self.description_field, "bottom", 0),
                (self.description_field, "right", 0)
            ],
            attachControl=[
                (self.add_button, "left", 0, self.replace_button),
                (self.subtract_button, "left", 0, self.add_button),
                (self.and_button, "left", 0, self.subtract_button),
                (self.or_button, "left", 0, self.and_button),
                (self.save_button, "left", 0, self.or_button),
                (self.update_button, "left", 0, self.save_button),
                (self.del_button, "left", 0, self.update_button),
                (self.description_field, "left", 0, self.del_button)
            ],
            attachPosition=[
                (self.replace_button, "right", 0, 5),
                (self.add_button, "right", 0, 10),
                (self.subtract_button, "right", 0, 15),
                (self.add_button, "right", 0, 10),
                (self.or_button, "right", 0, 10),
                (self.save_button, "right", 0, 20),
                (self.update_button, "right", 0, 25),
                (self.del_button, "right", 0, 30)
            ]
        )

        self.replace_button.setCommand(pm.Callback(self.selection_set.replace))
        self.add_button.setCommand(pm.Callback(self.selection_set.add))
        self.subtract_button.setCommand(pm.Callback(self.selection_set.subtract))
        self.and_button.setCommand(pm.Callback(self.selection_set.and_))
        self.or_button.setCommand(pm.Callback(self.selection_set.or_))
        self.save_button.setCommand(pm.Callback(self.save_button_callback))
        self.update_button.setCommand(pm.Callback(self.selection_set.update))
        self.del_button.setCommand(pm.Callback(self.delete_button_callback))

    def save_button_callback(self):
        self.selection_set.__name__ = pm.textField(
            self.description_field,
            q=True,
            tx=True
        )
        self.selection_set.save()

    def delete_button_callback(self):
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
        selection_set = SelectionSet()
        selection_set.update()
        row = SelectionRow(parent, selection_set)
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
