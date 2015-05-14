# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import glob
import os
from edl import Parser
import re
import pyseq


class Avid2Resolve(object):
    """Converts AVID edl files to Resolve also replaces render outputs
    """
    scene_number_regex = re.compile(r'[0-9]+')

    def __init__(self):
        self.avid_edl_path = ''
        self.events = []

    def read_avid_edl(self, avid_eld_path, fps='24'):
        """
        """
        p = Parser(fps)
        with open(avid_eld_path) as f:
            self.events = p.parse(f)

    def get_shot_name(self, s):
        """returns the shot code from the given string
        """

        parts = s.split('_')
        seq_name = parts[0].title()

        if self.scene_number_regex.match(parts[1]):
            scene_number = parts[1]
            env_code = parts[2]
        else:
            scene_number = parts[2]
            env_code = parts[1]

        shot_number = parts[3]

        shot_name = '%s_%s_%s_%s' % (
            seq_name, scene_number, env_code, shot_number
        )

        return shot_name

    def find_latest_outputs(self, shot, task_type='Comp'):
        """finds the latest outputs of the given task type of the given Shot
        """
        from stalker import Task
        task = Task.query\
            .filter(Task.parent==shot)\
            .filter(Task.name==task_type)\
            .first()

        # this part is not very parametric, and depends highly to out
        # project structure
        if task:
            # get the task folder
            output_path = '%s/Outputs/Main' % task.absolute_path

            # check the folder and get the latest output folder
            all_files = sorted(
                glob.glob(
                    os.path.join(output_path, '*')
                )
            )
            if all_files:
                latest_version_path = all_files[-1]

                exr_path = '%s/exr/*' % latest_version_path
                seqs = pyseq.get_sequences(exr_path)
                # png_path = '%s/png/*' % latest_version_path

                return seqs[0].format('')

        return None

    def convert_paths(self):
        """converts event paths with proper ones
        """
        from stalker import Shot
        # do a db connection
        for e in self.events:
            # get the reel which shows the shot name
            # (or something similar to it)
            shot_name = self.get_shot_name(e.reel)

            # find the shot in Stalker
            shot = Shot.query.filter(Shot.name == shot_name).first()
            if shot:
                # get the shot path
                latest_output = self.find_latest_outputs(shot)
                if latest_output:
                    e.source_file = str(latest_output)
                else:
                    e.source_file = ''

    def to_xml(self):
        """return an eml version of this edl
        """
        from anima.edit import Sequence
        s = Sequence(timebase='24')
        s.from_edl(self.events)
        xml_data = s.to_xml()
        return xml_data
