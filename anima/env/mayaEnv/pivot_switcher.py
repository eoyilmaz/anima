"""
oyPivotSwitcher.py by Erkan Ozgur Yilmaz (c) 2009

v10.5.17

Description :
-------------
A tool for easy animating of switching of pivots

Version History :
-----------------
v10.5.17
- modifications for Maya 2011 and PyMel 1.0.2

v9.12.25
- removed oyAxialCorrectionGroup script import
- moved to new versioning scheme

v1.0.1
- setup check: now the objects pivot attributes are checked for safe setup

v1.0.0
- initial working version

v1.0.0.preAlpha
- development version

TODO List :
-----------
----------------------------------------------------------------------------
"""

__version__ = "10.5.17"

import pymel.core as pm
from anima.env.mayaEnv import auxiliary


class PivotSwitcher(object):
    """A utility class to help dynamically switch pivot positions in maya
    """

    def __init__(self, _object):
        # the object
        self._object = auxiliary.get_valid_dag_node(_object)

        assert (isinstance(self._object, pm.nodetypes.Transform))

        # the data
        self._futurePivot = pm.nodetypes.Transform

        self._isSetup = False

        # read the settings
        self._read_settings()

    def _read_settings(self):
        """reads the settings from the objects pivotData attribute
        """

        # check if the object has pivotData attribute
        if self._object.hasAttr("pivotData"):
            # get the future pivot object
            self._futurePivot = auxiliary.get_valid_dag_node(
                pm.listConnections(
                    self._object.attr("pivotData.futurePivot")
                )[0]
            )

            # set isSetup flag to True
            self._isSetup = True

            return True

        return False

    def _save_settings(self):
        """save settings inside objects pivotData attribute
        """
        # data to be save :
        # -----------------
        # futurePivot node

        # create attributes
        self._create_data_attribute()

        # connect futurePivot node
        pm.connectAttr(
            '%s%s' % (self._futurePivot.name(), ".message"),
            self._object.attr("pivotData.futurePivot"),
            f=True
        )

    def _create_data_attribute(self):
        """creates attribute in self._object to hold the data
        """
        if not self._object.hasAttr("pivotData"):
            pm.addAttr(self._object, ln="pivotData", at="compound", nc=1)

        if not self._object.hasAttr("futurePivot"):
            pm.addAttr(
                self._object,
                ln="futurePivot",
                at="message",
                p="pivotData"
            )

    def _create_future_pivot(self):
        """creates the futurePivot locator
        """
        if self._isSetup:
            return

        # create a locator and move it to the current pivot
        # parent the locator under the object

        locator_name = self._object.name() + "_futurePivotLocator#"

        self._futurePivot = \
            auxiliary.get_valid_dag_node(pm.spaceLocator(n=locator_name))

        pm.parent(self._futurePivot, self._object)

        current_pivot_pos = pm.xform(self._object, q=True, ws=True, piv=True)

        pm.xform(self._futurePivot, ws=True, t=current_pivot_pos[0:3])

        # change the color
        self._futurePivot.setAttr("overrideEnabled", 1)
        self._futurePivot.setAttr("overrideColor", 13)

        # set translate and visibility to non-keyable
        self._futurePivot.setAttr("tx", k=False, channelBox=True)
        self._futurePivot.setAttr("ty", k=False, channelBox=True)
        self._futurePivot.setAttr("tz", k=False, channelBox=True)

        self._futurePivot.setAttr("v", k=False, channelBox=True)

        # lock scale and rotate
        self._futurePivot.setAttr("rx", lock=True, k=False, channelBox=False)
        self._futurePivot.setAttr("ry", lock=True, k=False, channelBox=False)
        self._futurePivot.setAttr("rz", lock=True, k=False, channelBox=False)

        self._futurePivot.setAttr("sx", lock=True, k=False, channelBox=False)
        self._futurePivot.setAttr("sy", lock=True, k=False, channelBox=False)
        self._futurePivot.setAttr("sz", lock=True, k=False, channelBox=False)

        # hide it
        self._futurePivot.setAttr("v", 0)

    def setup(self):
        """setups specified object for pivot switching
        """

        # if it is setup before, don't do anything
        if self._isSetup:
            return

        if not self.is_good_for_setup():
            pm.PopupError(
                "the objects pivots are connected to something\n"
                "THE OBJECT CANNOT BE SETUP!!!"
            )
            return

        # create the parent constraint
        self._create_future_pivot()

        # create attributes for data holding
        self._create_data_attribute()

        # save the settings
        self._save_settings()

        self._isSetup = True

    def toggle(self):
        """toggles pivot visibility
        """
        if not self._isSetup:
            return

        # toggle the pivot visibility
        current_vis = self._futurePivot.getAttr("v")
        current_vis = (current_vis + 1) % 2
        self._futurePivot.setAttr("v", current_vis)

    def switch(self):
        """switches the pivot to the futurePivot
        """
        if not self._isSetup:
            return

        # get the current frame
        frame = pm.currentTime(q=True)

        # get the current position of the object
        current_object_pos = pm.xform(self._object, q=True, ws=True, t=True)

        current_pivot_pos = pm.xform(self._object, q=True, ws=True, piv=True)
        future_pivot_pos = pm.xform(self._futurePivot, q=True, ws=True, t=True)

        displacement = (future_pivot_pos[0] - current_pivot_pos[0],
                        future_pivot_pos[1] - current_pivot_pos[1],
                        future_pivot_pos[2] - current_pivot_pos[2])

        # move the pivot to the future_pivot
        pm.xform(self._object, ws=True, piv=future_pivot_pos[0:3])

        # set keyframes
        pm.setKeyframe(self._object, at="rotatePivotX", t=frame, ott="step")
        pm.setKeyframe(self._object, at="rotatePivotY", t=frame, ott="step")
        pm.setKeyframe(self._object, at="rotatePivotZ", t=frame, ott="step")

        pm.setKeyframe(self._object, at="scalePivotX", t=frame, ott="step")
        pm.setKeyframe(self._object, at="scalePivotY", t=frame, ott="step")
        pm.setKeyframe(self._object, at="scalePivotZ", t=frame, ott="step")

        # set pivot translations
        self._object.setAttr("rotatePivotTranslate", -1 * displacement)
        self._object.setAttr("scalePivotTranslate", -1 * displacement)

        # set keyframes
        pm.setKeyframe(self._object, at="rotatePivotTranslateX", t=frame,
                       ott="step")
        pm.setKeyframe(self._object, at="rotatePivotTranslateY", t=frame,
                       ott="step")
        pm.setKeyframe(self._object, at="rotatePivotTranslateZ", t=frame,
                       ott="step")

        pm.setKeyframe(self._object, at="scalePivotTranslateX", t=frame,
                       ott="step")
        pm.setKeyframe(self._object, at="scalePivotTranslateY", t=frame,
                       ott="step")
        pm.setKeyframe(self._object, at="scalePivotTranslateZ", t=frame,
                       ott="step")

    def _set_dg_dirty(self):
        """sets the DG to dirty for _object, currentPivot and futurePivot
        """
        pm.dgdirty(self._object, self._futurePivot)

    def fix_jump(self):
        """fixes the jumps after editing the keyframes
        """
        pass

    def is_good_for_setup(self):
        """checks if the objects rotatePivot, scalePivot, rotatePivotTranslate
        and scalePivotTranslate is not connected to anything
        """
        attributes = [
            "rotatePivot",
            "scalePivot",
            "rotatePivotTranslate",
            "scalePivotTranslate"
        ]

        for attrStr in attributes:
            connections = self._object.attr(attrStr).connections()
            if len(connections) > 0:
                return False

        return True


def get_one_switcher():
    """returns a generator that generates a PivotSwitcher object for every
    transform node in the selection
    """
    for node in pm.ls(sl=True):
        try:
            node = auxiliary.get_valid_dag_node(node)

            if node.type() == "transform":
                my_pivot_switcher = PivotSwitcher(node)
                yield my_pivot_switcher
        except TypeError:
            pass


def setup_pivot():
    """setups pivot switching for selected objects
    """
    for piv_switcher in get_one_switcher():
        piv_switcher.setup()


def switch_pivot():
    """switches pivot for selected objects
    """
    for piv_switcher in get_one_switcher():
        piv_switcher.switch()


def toggle_pivot():
    """toggles pivot visibilities for selected objects
    """
    for piv_switcher in get_one_switcher():
        piv_switcher.toggle()


