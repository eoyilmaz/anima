# -*- coding: utf-8 -*-
"""Merges sliced renders in to one big plate
"""
from anima.dcc.fusion.toolbox import GenericTools

try:
    # for Fusion 6 and 7
    import PeyeonScript as bmf
except ImportError:
    # for Fusion 8+
    import BlackmagicFusion as bmf

from anima.dcc.fusion.utils import NodeUtils


class RenderMerger(object):
    """A tool to merge sliced renders"""

    def __init__(
        self, path="", slices_in_x=5, slices_in_y=5, plate_width=0, plate_height=0
    ):
        self.fusion = bmf.scriptapp("Fusion")
        self.comp = self.fusion.GetCurrentComp()

        self.fusion_version = float(
            self.fusion.GetAttrs("FUSIONS_Version").split(".")[0]
        )

        self.path = path
        self.slices_in_x = slices_in_x
        self.slices_in_y = slices_in_y
        self.plate_width = plate_height
        self.plate_height = plate_width

    def ui(self):
        """the UI for the script"""
        result = self.comp.AskUser(
            "Chose Slices",
            {
                1: {1: "Slice Sequence", 2: "FileBrowse", "Save": False},
                2: {
                    1: "Slice In Width",
                    2: "Slider",
                    "Min": 1,
                    "Max": 10,
                    "Default": 5,
                    "Integer": True,
                },
                3: {
                    1: "Slice In Height",
                    2: "Slider",
                    "Min": 1,
                    "Max": 10,
                    "Default": 5,
                    "Integer": True,
                },
            },
        )

        self.path = result["Slice Sequence"]
        self.slices_in_x = int(result["Slice In Width"])
        self.slices_in_y = int(result["Slice In Height"])

        self.do_merge()

    def calculate_total_width_height(self):
        """Calculates the total width and height of the resulting plate

        :return (int, int): Returns the width and height of the resulting plate
        """
        # calculate total width and height
        # instead of lock/unlock disable AutoClipBrowse temporarily
        auto_browse = GenericTools.disable_auto_clip_browse()
        loader = self.comp.Loader()
        GenericTools.set_auto_clip_browse(auto_browse)

        NodeUtils.set_node_attr(loader, "Clip", self.path)

        # set input
        loader.GetInputList()[10][0] = self.path
        # set clip time start
        loader.GetInputList()[15][0] = 0
        # set clip time end
        loader.GetInputList()[16][0] = 0

        attrs = loader.GetAttrs()
        plate_width = attrs["TOOLIT_Clip_Width"][1] * self.slices_in_x
        plate_height = attrs["TOOLIT_Clip_Height"][1] * self.slices_in_y

        # loader.Delete()

        return plate_width, plate_height

    def do_merge(self):
        """merges slices together"""
        width, height = self.calculate_total_width_height()

        bg = self.comp.Background()

        # set resolution
        NodeUtils.set_node_attr(bg, "Width", width)
        NodeUtils.set_node_attr(bg, "Height", height)

        # make it black with no alpha
        NodeUtils.set_node_attr(bg, "TopLeftRed", 0)
        NodeUtils.set_node_attr(bg, "TopLeftGreen", 0)
        NodeUtils.set_node_attr(bg, "TopLeftBlue", 0)
        NodeUtils.set_node_attr(bg, "TopLeftAlpha", 0)

        prev_merge = bg

        t = 0
        # instead of lock/unlock disable AutoClipBrowse temporarily
        auto_browse = GenericTools.disable_auto_clip_browse()
        for i in range(self.slices_in_y):
            # vertical stuff
            for j in range(self.slices_in_x):
                # horizontal stuff
                loader = self.comp.Loader()

                NodeUtils.set_node_attr(loader, "Clip", self.path)
                NodeUtils.set_node_attr(loader, "ClipTimeStart", t)
                NodeUtils.set_node_attr(loader, "ClipTimeEnd", t)

                merge = self.comp.Merge()

                # set center offset
                h_offset = 0.5 / self.slices_in_x + j * 1.0 / self.slices_in_x
                v_offset = 0.5 / self.slices_in_y + i * 1.0 / self.slices_in_y

                NodeUtils.set_node_attr(
                    merge, "Center", {1.0: h_offset, 2.0: v_offset, 3.0: 0.0}
                )

                # connect it to the previous merges output
                merge.Background = prev_merge
                merge.Foreground = loader

                prev_merge = merge
                t += 1
        GenericTools.set_auto_clip_browse(auto_browse)
