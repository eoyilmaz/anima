# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import re


class Avid2Resolve(object):
    """Converts AVID edl files to Resolve also replaces render outputs
    """
    scene_number_regex = re.compile(r'[0-9]+')

    def __init__(self):
        self.avid_edl_path = ''
        self.events = []
        self.fps = ''

    def read_avid_edl(self, avid_eld_path, fps='24'):
        """
        """
        self.fps = fps
        from edl import Parser
        p = Parser(fps)
        with open(avid_eld_path) as f:
            self.events = p.parse(f)

    def get_shot_name(self, s):
        """returns the shot code from the given string
        """
        # fix some issues with shot name
        # replace "__" with "_"
        s = s.replace('__', '_')

        # filter shot names
        # KKS_SEQ002_013_CZRI_0030_COMP_MA
        if s.startswith('KKS_'):
            s = s.replace('KKS_', '')

        parts = s.split('_')
        if not len(parts) >= 4:
            return ''

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

            import os
            import glob
            import pyseq
            # check the folder and get the latest output folder
            version_folders = reversed(
                sorted(
                    glob.glob(
                        os.path.join(output_path, '*')
                    )
                )
            )
            for version_folder in version_folders:
                # check if the current version folder has exr files
                exr_path = ('%s/exr/*.exr' % version_folder).replace('\\', '/')
                png_path = ('%s/png/*.png' % version_folder).replace('\\', '/')
                seqs = pyseq.getSequences(exr_path)

                # and if not go to a previous version
                # until you check all the version paths
                if seqs:
                    return 'localhost/%s/%s' % (
                        os.path.normpath(os.path.split(seqs[0].path())[0]).replace('\\', '/'),
                        seqs[0].format('%h|5B%03s-%03e|5D%t').replace('|', '%')
                    )
                else:
                    # also check png sequences
                    png_seqs = pyseq.getSequences(png_path)
                    if png_seqs:
                        print(
                            "%s %s has PNG but no EXR" %
                            (shot.name, version_folder.split('/')[-1])
                        )

            return ''

        return None

    def convert_paths(self):
        """converts event paths with proper ones
        """
        from stalker import Shot
        import timecode
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

            # set the in and out points correctly
            # stupid AVID places the source clips to either 8th or 1st hour
            first_hour = timecode.Timecode(self.fps, start_timecode='01:00:00:00')
            eigth_hour = timecode.Timecode(self.fps, start_timecode='07:59:00:00')
            twelfth_hour = timecode.Timecode(self.fps, start_timecode='11:59:00:00')
            if e.src_start_tc.frames >= twelfth_hour.frames:
                e.src_start_tc -= twelfth_hour - 1
                e.src_end_tc -= twelfth_hour - 1
            elif e.src_start_tc.frames >= eigth_hour.frames:
                e.src_start_tc -= eigth_hour - 1
                e.src_end_tc -= eigth_hour - 1
            elif e.src_start_tc.frames >= first_hour.frames:
                e.src_start_tc -= first_hour - 1
                e.src_end_tc -= first_hour - 1

    def to_xml(self):
        """return an eml version of this edl
        """
        from anima.edit import Sequence, Rate
        s = Sequence(rate=Rate(timebase='24'))
        s.from_edl(self.events)

        # optimize clips
        for track in s.media.video.tracks:
            track.optimize_clips()

        xml_data = s.to_xml()
        return xml_data
