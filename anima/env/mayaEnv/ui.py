# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Anima Previs Editor
"""

import os
import pymel

import anima

from anima.env.mayaEnv import Maya

from pymel import core


class PrevisUI(object):
    """Main class for managing the previs UI
    """

    def __init__(self):
        self.mEnv = Maya()

        self.width = 265
        self.height = 300
        self.row_spacing = 3
        self.window = None
        self.window_name = 'Previz_Window'
        self.window_title = "Previz Tools v%s" % anima.__version__

        self.edl_checkBox = None
        self.mxf_checkBox = None

    def init_ui(self):
        if core.window(self.window_name, q=True, ex=True):
            core.deleteUI(self.window_name, wnd=True)

        self.window = core.window(
            self.window_name,
            wh=(self.width, self.height),
            mnb = False,
            mxb=False,
            sizeable=False,
            title=self.window_title
        )

        #the layout
        main_formLayout = core.formLayout(
            'main_formLayout',
            nd=100,
            parent=self.window
        )

        prog_columnLayout = core.columnLayout(
            'prog_columnLayout',
            columnAttach=('both', 3),
            rowSpacing=10,
            columnWidth=265,
            parent=main_formLayout
        )

        top_rowLayout = core.rowLayout(
            'top_rowLayout',
            numberOfColumns=2,
            columnWidth2=(85, 180),
            adjustableColumn=2,
            columnAlign=(1, 'right'),
            columnAttach=[(1, 'both', 0), (2, 'both', 0)],
            parent= prog_columnLayout
        )

        topleft_columnLayout = core.columnLayout(
            'topleft_columnLayout',
             w=85,
             columnAttach=('left' , 5),
             cal='left',
             rowSpacing=17,
             columnWidth=85,
             parent=top_rowLayout
        )

        core.text(label='Scene Code', parent=topleft_columnLayout)
        core.text(label='File Version', parent=topleft_columnLayout)
        core.text(label='Handle Lenght', parent=topleft_columnLayout)
        core.text(label='Export', parent=topleft_columnLayout)
        core.text(label='Convert MOVs', parent=topleft_columnLayout)

        right_columnLayout = core.columnLayout(
            'right_columnLayout',
            columnAttach=('left' , 5),
            cal='left',
            rowSpacing=10,
            columnWidth=85,
            parent=top_rowLayout
        )

        Seqname_rowLayout = core.rowLayout(
            'seqNameRow',
            numberOfColumns=3,
            columnWidth3=(40,60,55),
            columnAttach=[(1, 'both', 5), (2, 'both', 10), (3, 'both', 5)],
            parent=right_columnLayout
        )

        seq = core.textField(pht="SEQ" , parent=Seqname_rowLayout)
        loc = core.textField(pht="LOC" , parent=Seqname_rowLayout)
        script = core.textField(pht= "Script", parent=Seqname_rowLayout)

        topRight_columnLayout = core.columnLayout(
            'topRight_columnLayout',
            w=170,
            columnAttach=('both', 5),
            rowSpacing=10,
            columnWidth=160,
            parent=right_columnLayout
        )

        current_version = self.mEnv.get_current_version()
        if current_version:
            version_number = current_version.version_number
        else:
            version_number = 1
        version_string = 'v%03d' % version_number

        version = core.textField(text=version_string)
        lenght_slider_grp = core.intSliderGrp(field= True, cw2= (30,70), cc=self.set_handle, min=0, v=15, max=50 )
        self.edl_checkBox = core.checkBox('EDL', value=True)
        self.mxf_checkBox = core.checkBox('to MXF', value=True)

        core.separator (h=20, parent= prog_columnLayout)

        bottom_columnLayout = core.columnLayout(
            'bottom_rowLayout',
            w = 260,
            columnAttach=('both', 5),
            rowSpacing=10,
            columnWidth=260,
            parent= prog_columnLayout
        )

        core.button(label='Export' , bgc=(0.1, 0.4, 0.1), w=250, parent=bottom_columnLayout, c=self.export)
        core.button(
            label='Close Window',
            command=self.close,
            bgc= (0.3, 0.1, 0.1), w=250,
            parent= bottom_columnLayout
        )

    def show(self):
        if not self.window:
            self.init_ui()

        try:
            core.showWindow(self.window)
        except RuntimeError:
            self.init_ui
            core.showWindow(self.window)

        core.window(self.window, edit=True, w=self.width, h=self.height)

    def close(self, value):
        """closes the UI
        """
        core.deleteUI(self.window_name, window=True)

    ### learning Scene Version
    def set_ver(self):
        scVer = 'v001'
        sm.set_version(scVer)

    def set_handle(self, value):
        """sets handles from UI
        """
        sm = core.ls('sequenceManager1')[0]
        seq1 = sm.sequences.get()[0]
        seq1.set_shot_handles(value)

    def set_seq_name(name):
        """sets sequence name
        """
        sm.get_shot_name_template()  # sets the default shot name template
        seq1.set_sequence_name('SEQ001_TNGI_Scr_010')

    def export(self, button_value):
        """
        """
        ### get sequenceManager1
        sm = pymel.core.PyNode('sequenceManager1')

        ### get sequencer
        seq1 = sm.sequences.get()[0]
        # set path values
        current_workspace_path = pymel.core.workspace.path
        playblast_output_path = os.path.normpath(
            os.path.join(current_workspace_path, 'Outputs', 'All_Shots')
        )

        edl_path = os.path.normpath(
            os.path.join(
                playblast_output_path,
                '%s_%s.%s' % (seq1.get_sequence_name(), sm.get_version(), 'edl')
            )
        )

        # create shot playblast
        seq1.create_shot_playblasts(playblast_output_path)

        # convert to MXF
        if self.mxf_checkBox.value():
            shot_count = len(seq1.shots.get())
            step = int(100.0/shot_count)
            import time
            core.progressWindow(
                title='Converting To MXFs',
                progress=0,
                status='',
                isInterruptable=True
            )
            for i in seq1.metafuze():
                core.progressWindow(e=1, step=step)
            core.progressWindow(endProgress=1)

        if self.edl_checkBox.value():
            # create EDL file
            l = sm.to_edl()
            with open(edl_path, 'w') as f:
                f.write(l.to_string())

