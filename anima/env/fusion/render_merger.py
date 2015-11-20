# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Merges sliced renders in to one big plate
"""


import PeyeonScript

fusion = PeyeonScript.scriptapp("Fusion")
comp = fusion.GetCurrentComp()

path = r'T:\PROJECTS\GOBEKLITEPE\Sequences\3d_render\References\Others\murat_gelenler\2015_11_17_render\Gobeklitepe_C_16112015\images\C_look_workshop_0014.ma.151117-131518-256_0000.exr'

slice_cnt = 10

# width = 4720
# height = 3310
width = 32000
height = 22450


bg = comp.Background()

# set resolution
bg.GetInputList()[20][0] = width
bg.GetInputList()[21][0] = height


prev_merge = bg

t = 0
for i in range(slice_cnt):
    # vertical staff
    for j in range(slice_cnt):
        # horizontal staff
        comp.Lock()
        loader = comp.Loader()
        loader.Filename = path
        # set input
        loader.GetInputList()[10][0] = path
        # set clip time start
        loader.GetInputList()[15][0] = t
        # set clip time end
        loader.GetInputList()[16][0] = t
        comp.Unlock()

        merge = comp.Merge()
        # set center offset
        merge.GetInputList()[29][0] = {
            1.0: 0.5 / slice_cnt + j * 1.0 / slice_cnt,
            2.0: 0.5 / slice_cnt + i * 1.0 / slice_cnt,
            3.0: 0.0
        }

        # connect it to the previous merges output
        merge.Background = prev_merge
        merge.Foreground = loader

        prev_merge = merge
        t += 1