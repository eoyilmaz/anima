# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import edl


class Sequence(object):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.duration = None
        self.name = None
        self.rate = False
        self.timecode = '00:00:00:00'
        self.ntsc = False
        self.timebase = '24'
        self.media = None


class Media(object):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.video = []
        self.audio = []


class Video(object):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.width = 0
        self.height = 0
        self.tracks = []


class Track(object):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.locked = False
        self.enabled = True
        self.clips = []


class Clip(object):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.id = None
        self.name = ''
        self.start = 0
        self.end = 0
        self.duration = 0
        self.enabled = True
        self.in_ = 0
        self.out = 0
        self.file = None


class File(object):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.duration = 0
        self.name = ''
        self.pathurl = ''


class Sequencer(object):
    """The sequence instance.

    It is a manager that manages shot data. It is kind of the reflection of the
    Maya CameraSequencer.

    It is able to get Maya editorial XML and convert it to EDL.
    """

    @classmethod
    def create_shot_playblasts(cls, handle=10, show_ornaments=True):
        """creates the selected shot playblasts
        """
        import pymel.core

        shots = pymel.core.ls(sl=1, type=pymel.core.nt.Shot)
        #active_panel = pymel.core.playblast(activeEditor=1)

        path_template = os.path.join(
            pymel.core.workspace.name,
            'Outputs/Playblast/AllShots/'
        ).replace('\\', '/')

        filename_template = '%(scene)s_%(shot)s.mov'

        # template vars
        scene_name = os.path.basename(pymel.core.env.sceneName()).split('.')[0]

        for shot in shots:
            shot_name = shot.name()
            start_frame = shot.startFrame.get() - handle
            end_frame = shot.endFrame.get() + handle
            width = shot.wResolution.get()
            height = shot.hResolution.get()

            rendered_path = path_template % {}
            rendered_filename = filename_template % {
                'shot': shot_name,
                'scene': scene_name
            }

            movie_full_path = os.path.join(
                rendered_path,
                rendered_filename
            ).replace('\\', '/')

            pymel.core.playblast(
                fmt="qt",
                startTime=start_frame,
                endTime=end_frame,
                sequenceTime=1,
                forceOverwrite=1,
                filename=movie_full_path,
                clearCache=True,
                showOrnaments=show_ornaments,
                percent=100,
                wh=[width, height],
                offScreen=True,
                viewer=0,
                useTraxSounds=True,
                compression="PNG",
                quality=70
            )

    def parse_xml(self, path):
        """Parses XML file and returns a Sequence instance which reflects the
        whole timeline hierarchy.

        :param path: The path of the XML file
        :return: :class:`.Sequence`
        """
        if not isinstance(path, str):
            raise TypeError(
                'path argument in %s.parse_xml should be a string, not %s' %
                (self.__class__.__name__, path.__class__.__name__)
            )

        from xml.etree import ElementTree
        try:
            tree = ElementTree.parse(path)
        except IOError:
            raise IOError('Please supply a valid path to an XML file!')

        root = tree.getroot()
        seq = Sequence()

        xml_seq = root.getchildren()[0]

        media = Media()
        seq.media = media

        seq.duration = float(xml_seq.find('duration').text)
        seq.name = xml_seq.find('name').text
        rate_tag = xml_seq.find('rate')
        if rate_tag is not None:
            seq.ntsc = rate_tag.find('ntsc').text.title() == 'True'
            seq.timebase = rate_tag.find('timebase').text

        seq.timecode = xml_seq.find('timecode').find('string').text

        xml_media = xml_seq.find('media')

        xml_video_tags = xml_media.findall('video')

        for xml_video_tag in xml_video_tags:
            video = Video()
            media.video.append(video)

            format = xml_video_tag.find('format')
            video.width = int(
                format.find('samplecharacteristics').find('width').text
            )
            video.height = int(
                format.find('samplecharacteristics').find('height').text
            )

            # create tracks
            track_tag = xml_video_tag.find('track')
            track = Track()
            track.locked = track_tag.find('locked').text.title() == 'True'
            track.enabled = \
                track_tag.find('enabled').text.title() == 'True'
            video.tracks.append(track)

            # find clips
            for clip_tag in track_tag.findall('clipitem'):
                clip = Clip()
                clip.id = clip_tag.attrib['id']
                clip.start = float(clip_tag.find('start').text)
                clip.end = float(clip_tag.find('end').text)
                clip.name = clip_tag.find('name').text
                clip.enabled = clip_tag.find('enabled').text == 'True'
                clip.duration = float(clip_tag.find('duration').text)
                clip.in_ = float(clip_tag.find('in').text)
                clip.out = float(clip_tag.find('out').text)

                f = File()
                file_tag = clip_tag.find('file')
                f.duration = float(file_tag.find('duration').text)
                f.name = file_tag.find('name').text
                f.pathurl = file_tag.find('pathurl').text
                clip.file = f

                track.clips.append(clip)

        return seq

    def to_xml(self, seq):
        """Converts the given Sequence instance to an xml file

        :param seq: A :class:`.Sequence` instance
        :return: str
        """
        pass


