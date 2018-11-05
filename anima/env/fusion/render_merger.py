# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Merges sliced renders in to one big plate
"""

try:
    # for Fusion 6 and 7
    import PeyeonScript as bmf
except ImportError:
    # for Fusion 8+
    import BlackmagicFusion as bmf

fusion = bmf.scriptapp("Fusion")
comp = fusion.GetCurrentComp()

fusion_version = float(fusion.GetAttrs("FUSIONS_Version"))


class RenderMerger(object):
    """A tool to merge sliced renders
    """

    def __init__(self, path="", slices_in_x=5, slices_in_y=5, plate_width=0, plate_height=0):
        self.path = path
        self.slices_in_x = slices_in_x
        self.slices_in_y = slices_in_y
        self.plate_width = plate_height
        self.plate_height = plate_width

    def ui(self):
        """the UI for the script
        """
        result = comp.AskUser(
            'Chose Slices',
            {
                1: {
                    1: 'Slice Sequence',
                    2: 'FileBrowse',
                    'Save': False
                },
                2: {
                    1: 'Slice In Width',
                    2: 'Slider',
                    'Min': 1,
                    'Max': 10,
                    'Default': 5
                },
                3: {
                    1: 'Slice In Height',
                    2: 'Slider',
                    'Min': 1,
                    'Max': 10,
                    'Default': 5
                }
            }
        )

        self.path = result['Slice Sequence']
        self.slices_in_x = int(result['Slice In Width'])
        self.slices_in_y = int(result['Slice In Height'])

        self.do_merge()

    def calculate_total_width_height(self):
        """Calculates the total width and height of the resulting plate

        :return (int, int): Returns the width and height of the resulting plate
        """
        # calculate total width and height
        comp.Lock()
        loader = comp.Loader()
        loader.Filename = self.path
        # set input
        loader.GetInputList()[10][0] = self.path
        # set clip time start
        loader.GetInputList()[15][0] = 0
        # set clip time end
        loader.GetInputList()[16][0] = 0
        comp.Unlock()

        attrs = loader.GetAttrs()

        plate_width = attrs['TOOLIT_Clip_Width'][1] * self.slices_in_x
        plate_height = attrs['TOOLIT_Clip_Height'][1] * self.slices_in_y

        # loader.Delete()

        return plate_width, plate_height

    def do_merge(self):
        """merges slices together
        """
        width, height = self.calculate_total_width_height()

        bg = comp.Background()

        # set resolution
        bg.GetInputList()[20][0] = width
        bg.GetInputList()[21][0] = height

        # make it black with no alpha
        bg.GetInputList()[25][0] = 0
        bg.GetInputList()[26][0] = 0
        bg.GetInputList()[27][0] = 0
        bg.GetInputList()[28][0] = 0

        prev_merge = bg

        t = 0
        for i in range(self.slices_in_y):
            # vertical stuff
            for j in range(self.slices_in_x):
                # horizontal stuff
                comp.Lock()
                loader = comp.Loader()
                loader.Filename = self.path
                # set input
                loader.GetInputList()[10][0] = self.path
                # set clip time start
                loader.GetInputList()[15][0] = t
                # set clip time end
                loader.GetInputList()[16][0] = t
                comp.Unlock()

                merge = comp.Merge()

                h_offset = 0.5 / self.slices_in_x + j * 1.0 / self.slices_in_x
                v_offset = 0.5 / self.slices_in_y + i * 1.0 / self.slices_in_y
                # set center offset

                # center input id is 29 for fusion 6
                # and .. for fusion 7+
                center_id = 29
                if fusion_version > 7:
                    center_id = 33

                merge.GetInputList()[center_id][0] = {
                    1.0: h_offset,
                    2.0: v_offset,
                    3.0: 0.0
                }

                # connect it to the previous merges output
                merge.Background = prev_merge
                merge.Foreground = loader

                prev_merge = merge
                t += 1
