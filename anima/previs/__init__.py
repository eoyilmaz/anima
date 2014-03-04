# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os


class PrevisBase(object):
    """The base for other Previs classes
    """

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        raise NotImplementedError

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this PrevisBase object
        """
        raise NotImplementedError

    def from_edl(self, edl_list):
        """Fills attributes with the given edl.List instance

        :param edl_list: an edl.List instance
        """
        raise NotImplementedError

    def to_edl(self):
        """returns an EDL version of this PrevisBase object
        """
        raise NotImplementedError


class NameMixin(object):
    """A mixin for name attribute
    """

    def __init__(self, name=''):
        self._name = self._validate_name(name)

    @classmethod
    def _validate_name(cls, name):
        """validates the given name value
        """
        if not isinstance(name, str):
            raise TypeError(
                '%(class)s.name should be a string, not %(name_class)s' % {
                    'class': cls.__name__,
                    'name_class': name.__class__.__name__
                }
            )
        return name

    @property
    def name(self):
        """returns the _name attribute
        """
        return self._name

    @name.setter
    def name(self, name):
        """setter for the name property
        """
        self._name = self._validate_name(name)


class DurationMixin(object):
    """A mixin for duration attribute
    """

    def __init__(self, duration=0.0):
        self._duration = self._validate_duration(duration)

    @classmethod
    def _validate_duration(cls, duration):
        """validates the given duration value
        """
        if duration is None:
            duration = 0.0

        if not isinstance(duration, (int, float)):
            raise TypeError(
                '%(class)s.duration should be an non-negative float, not '
                '%(duration_class)s' % {
                    'class': cls.__name__,
                    'duration_class': duration.__class__.__name__
                }
            )

        duration = float(duration)

        if duration < 0:
            raise ValueError(
                '%(class)s.duration should be an non-negative float' % {
                    'class': cls.__name__
                }
            )

        return duration

    @property
    def duration(self):
        """returns the _duration attribute value
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        self._duration = self._validate_duration(duration)


class Sequence(PrevisBase, NameMixin, DurationMixin):
    """XML compatibility class for Sequence

    This class is mainly created to reflect the XML structure of Maya
    Sequencer.

    It is also the bridge to EDL. So using this class it is possible to convert
    Maya Sequencer XML to a meaningful EDL.

    :param str name: The name of this sequence.
    :param float duration: The duration of this sequence.
    :param str timebase: The frame rate setting for this sequence. Default
      value is '25', can be anything in ['23.98', '24', '25', '29.97', '30',
      '50', '59.94', '60']. Without setting this converting to EDL will result
      wrong timecode values in EDL.
    :param str timecode: The stating timecode of this Sequence. Default value
      is '00:00:00:00'. This will be used to calculate the clip in and out
      points. Maya exports in and out points as frames, Sequence converts them
      to a timecodes by using this parameter as the base.
    """

    def __init__(self, name='', duration=0.0, timebase='25',
                 timecode='00:00:00:00'):
        NameMixin.__init__(self, name=name)
        DurationMixin.__init__(self, duration=duration)
        self.ntsc = False
        # replace this with pytimecode.PyTimeCode instance
        self.timecode = timecode
        self.timebase = timebase
        self.media = None

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        self.duration = float(xml_node.find('duration').text)
        self.name = xml_node.find('name').text
        rate_tag = xml_node.find('rate')
        if rate_tag is not None:
            self.ntsc = rate_tag.find('ntsc').text.title() == 'True'
            self.timebase = rate_tag.find('timebase').text

        self.timecode = xml_node.find('timecode').find('string').text

        xml_media = xml_node.find('media')
        media = Media()
        media.from_xml(xml_media)

        self.media = media

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Sequence object
        """
        template = """%(pre_indent)s<sequence>
%(pre_indent)s%(indentation)s<duration>%(duration)s</duration>
%(pre_indent)s%(indentation)s<name>%(name)s</name>
%(pre_indent)s%(indentation)s<rate>
%(pre_indent)s%(indentation)s%(indentation)s<ntsc>%(ntsc)s</ntsc>
%(pre_indent)s%(indentation)s%(indentation)s<timebase>%(timebase)s</timebase>
%(pre_indent)s%(indentation)s</rate>
%(pre_indent)s%(indentation)s<timecode>
%(pre_indent)s%(indentation)s%(indentation)s<string>%(timecode)s</string>
%(pre_indent)s%(indentation)s</timecode>
%(media)s
%(pre_indent)s</sequence>"""

        return template % {
            'duration': self.duration,
            'name': self.name,
            'ntsc': str(self.ntsc).upper(),
            'timebase': self.timebase,
            'timecode': self.timecode,
            'media': self.media.to_xml(indentation=indentation,
                                       pre_indent=indentation + pre_indent),
            'indentation': ' ' * indentation,
            'pre_indent': ' ' * pre_indent
        }

    def from_edl(self, edl_list):
        """Fills attributes with the given edl.List instance

        :param edl_list: an edl.List instance
        """
        import edl
        assert isinstance(edl_list, edl.List)

        self.name = edl_list.title

        # create a Media instance
        self.media = Media()

        v = Video()
        self.media.video.append(v)

        video_track = Track()
        v.tracks.append(video_track)
        # no audio tracks fow now

        # read Events in to Clips
        sequence_start = 1e20
        sequence_end = -1
        for e in edl_list.events:
            assert isinstance(e, edl.Event)
            clip = Clip()

            clip.name = e.clip_name
            clip.id = clip.name
            clip.type = 'Video' if e.track == 'V' else 'Audio'

            clip.in_ = e.src_start_tc.frames - 1
            clip.out = e.src_end_tc.frames - 1
            clip.duration = clip.out - clip.in_

            clip.start = e.rec_start_tc.frames
            clip.end = e.rec_end_tc.frames

            if clip.start < sequence_start:
                sequence_start = clip.start
            if clip.end > sequence_end:
                sequence_end = clip.end

            f = File()
            f.name = clip.name
            f.duration = clip.duration
            f.pathurl = 'file://%s' % e.source_file

            clip.file = f

            if clip.type == 'Video':
                video_track.clips.append(clip)

        self.duration = sequence_end - sequence_start
        # TODO: fix this latest, timecode always 00:00:00:00 for now
        self.timecode = '00:00:00:00'
        # TODO: can not read sequence.timebase from edl

    def to_edl(self):
        """Returns an edl.List instance equivalent of this Sequence instance
        """
        from edl import List, Event
        from pytimecode import PyTimeCode

        l = List(self.timebase)
        l.title = self.name

        # convert clips to events
        if not self.media:
            raise RuntimeError(
                'Can not run %(class)s.to_edl() without a Media instance, '
                'please add a Media instance to this %(class)s instance.' % {
                    'class': self.__class__.__name__
                }
            )

        for video in self.media.video:
            for track in video.tracks:
                for i, clip in enumerate(track.clips):
                    e = Event({})
                    e.num = '%06i' % (i + 1)
                    e.clip_name = clip.name
                    e.reel = clip.name
                    e.track = 'V' if clip.type == 'Video' else 'A'
                    e.tr_code = 'C'  # TODO: for now use C (Cut) later on
                    # expand it to add other transition codes

                    src_start_tc = PyTimeCode(self.timebase,
                                              frames=clip.in_ + 1)
                    # 1 frame after last frame shown
                    src_end_tc = PyTimeCode(self.timebase,
                                            frames=clip.out + 1)

                    e.src_start_tc = str(src_start_tc)
                    e.src_end_tc = str(src_end_tc)

                    rec_start_tc = PyTimeCode(self.timebase,
                                              frames=clip.start)
                    # 1 frame after last frame shown
                    rec_end_tc = PyTimeCode(self.timebase, frames=clip.end)

                    e.rec_start_tc = str(rec_start_tc)
                    e.rec_end_tc = str(rec_end_tc)

                    source_file = clip.file.pathurl.replace('file://', '')
                    e.source_file = source_file

                    e.comments.extend([
                        '* FROM CLIP NAME: %s' % source_file,
                        '* SOURCE FILE: %s' % source_file
                    ])

                    l.append(e)
        return l

    def to_metafuze_xml(self):
        """Generates a MetaFuze compatible XML content per clip.

        :returns: list of strings
        """
        metafuze_xml_template = """<?xml version='1.0' encoding='UTF-8'?>
<MetaFuze_BatchTranscode>
   <Configuration>
      <Local>8</Local>
      <Remote>8</Remote>
   </Configuration>
   <Group>
      <FileList>
         <File>%(file_pathurl)s</File>
      </FileList>
      <Transcode>
         <Version>1.0</Version>
         <File>%(mxf_pathurl)s</File>
         <ClipName>%(clip_name)s</ClipName>
         <ProjectName>%(sequence_name)s</ProjectName>
         <TapeName>%(clip_id)s</TapeName>
         <TC_Start>%(sequence_timecode)s</TC_Start>
         <DropFrame>false</DropFrame>
         <EdgeTC>** TimeCode N/A **</EdgeTC>
         <FilmType>35.4</FilmType>
         <KN_Start>AAAAAAAA-0000+00</KN_Start>
         <Frames>%(clip_duration)i</Frames>
         <Width>%(width)i</Width>
         <Height>%(height)i</Height>
         <PixelRatio>1.0000</PixelRatio>
         <UseFilmInfo>false</UseFilmInfo>
         <UseTapeInfo>true</UseTapeInfo>
         <AudioChannelCount>0</AudioChannelCount>
         <UseMXFAudio>false</UseMXFAudio>
         <UseWAVAudio>false</UseWAVAudio>
         <SrcBitsPerChannel>8</SrcBitsPerChannel>
         <OutputPreset>DNxHD 36 - 1080 24p (8 bits)</OutputPreset>
         <OutputPreset>
            <Version>2.0</Version>
            <Name>DNxHD 36 - 1080 24p (8 bits)</Name>
            <ColorModel>YCC 709</ColorModel>
            <BitDepth>8</BitDepth>
            <Format>1080 24p</Format>
            <Compression>DNxHD 36</Compression>
            <Conversion>Letterbox (center)</Conversion>
            <VideoFileType>.mxf</VideoFileType>
            <IsDefault>false</IsDefault>
         </OutputPreset>
         <Eye></Eye>
         <Scene></Scene>
         <Comment></Comment>
      </Transcode>
   </Group>
</MetaFuze_BatchTranscode>"""
        rendered_xmls = []
        for video in self.media.video:
            for track in video.tracks:
                for clip in track.clips:
                    raw_file_path = clip.file.pathurl.replace('file://', '')
                    raw_mxf_path = '%s%s' % (
                        os.path.splitext(raw_file_path)[0],
                        '.mxf'
                    )

                    kwargs = {
                        'file_pathurl': raw_file_path,
                        'mxf_pathurl': raw_mxf_path,
                        'clip_name': clip.id,
                        'sequence_name': self.name,
                        'clip_id': clip.id,
                        'sequence_timecode': self.timecode,
                        'clip_duration': clip.duration,
                        'width': video.width,
                        'height': video.height
                    }

                    rendered_xmls.append(metafuze_xml_template % kwargs)

        return rendered_xmls


class Media(PrevisBase):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.video = []
        self.audio = []

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        xml_video_tags = xml_node.findall('video')
        for xml_video_tag in xml_video_tags:
            video = Video()
            video.from_xml(xml_video_tag)
            self.video.append(video)

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Media object
        """
        template = """%(pre_indent)s<media>
%(videos)s
%(pre_indent)s</media>"""

        video_data = []
        for video in self.video:
            video_data.append(
                video.to_xml(indentation=indentation,
                             pre_indent=indentation + pre_indent)
            )
        video_data_as_str = '\n'.join(video_data)

        return template % {
            'videos': video_data_as_str,
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class Video(PrevisBase):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.width = 0
        self.height = 0
        self.tracks = []

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        format_node = xml_node.find('format')
        self.width = int(
            format_node.find('samplecharacteristics').find('width').text
        )
        self.height = int(
            format_node.find('samplecharacteristics').find('height').text
        )

        # create tracks
        track_tag = xml_node.find('track')
        track = Track()
        track.from_xml(track_tag)

        self.tracks.append(track)

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Video object
        """
        template = """%(pre_indent)s<video>
%(pre_indent)s%(indentation)s<format>
%(pre_indent)s%(indentation)s%(indentation)s<samplecharacteristics>
%(pre_indent)s%(indentation)s%(indentation)s%(indentation)s<width>%(width)s</width>
%(pre_indent)s%(indentation)s%(indentation)s%(indentation)s<height>%(height)s</height>
%(pre_indent)s%(indentation)s%(indentation)s</samplecharacteristics>
%(pre_indent)s%(indentation)s</format>
%(tracks)s
%(pre_indent)s</video>"""

        track_data = []
        for track in self.tracks:
            track_data.append(
                track.to_xml(indentation=indentation,
                             pre_indent=indentation + pre_indent)
            )
        track_data_as_str = '\n'.join(track_data)

        return template % {
            'width': self.width,
            'height': self.height,
            'tracks': track_data_as_str,
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class Track(PrevisBase):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.locked = False
        self.enabled = True
        self.clips = []

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        self.locked = xml_node.find('locked').text.title() == 'True'
        self.enabled = xml_node.find('enabled').text.title() == 'True'

        # find clips
        for clip_tag in xml_node.findall('clipitem'):
            clip = Clip()
            clip.from_xml(clip_tag)
            self.clips.append(clip)

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Track object
        """
        template = """%(pre_indent)s<track>
%(pre_indent)s%(indentation)s<locked>%(locked)s</locked>
%(pre_indent)s%(indentation)s<enabled>%(enabled)s</enabled>
%(clips)s
%(pre_indent)s</track>"""

        clip_data = []
        for clip in self.clips:
            clip_data.append(
                clip.to_xml(indentation=indentation,
                            pre_indent=indentation + pre_indent)
            )
        clip_data_as_str = '\n'.join(clip_data)

        return template % {
            'locked': str(self.locked).upper(),
            'enabled': str(self.enabled).upper(),
            'clips': clip_data_as_str,
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class Clip(PrevisBase, NameMixin, DurationMixin):
    """XML compatibility class for Sequencer
    """

    def __init__(self, id=None, name='', start=0.0, end=0.0, duration=0.0,
                 enabled=True, in_=0, out=0, type_='Video'):
        NameMixin.__init__(self, name=name)
        DurationMixin.__init__(self, duration=duration)
        self._id = self._validate_id(id)
        self.start = start
        self.end = end
        self.enabled = enabled
        self.in_ = in_
        self.out = out
        self.file = None
        self.type = type_

    @classmethod
    def _validate_id(cls, id_):
        """validates the given id value
        """
        if id_ is None:
            id_ = ''

        if not isinstance(id_, str):
            raise TypeError(
                '%(class)s.id should be a string, not %(id_class)s' %
                {
                    'class': cls.__name__,
                    'id_class': id_.__class__.__name__
                }
            )

        return id_

    @property
    def id(self):
        """returns the _id attribute value
        """
        return self._id

    @id.setter
    def id(self, id_):
        """setter for the _id attribute
        """
        self._id = self._validate_id(id_)

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        self.id = xml_node.attrib['id']
        self.start = float(xml_node.find('start').text)
        self.end = float(xml_node.find('end').text)
        self.name = xml_node.find('name').text
        self.enabled = xml_node.find('enabled').text == 'True'
        self.duration = float(xml_node.find('duration').text)
        self.in_ = float(xml_node.find('in').text)
        self.out = float(xml_node.find('out').text)

        f = File()
        file_tag = xml_node.find('file')
        f.from_xml(file_tag)

        self.file = f

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Clip object
        """
        template = """%(pre_indent)s<clipitem id="%(id)s">
%(pre_indent)s%(indentation)s<end>%(end)s</end>
%(pre_indent)s%(indentation)s<name>%(name)s</name>
%(pre_indent)s%(indentation)s<enabled>%(enabled)s</enabled>
%(pre_indent)s%(indentation)s<start>%(start)s</start>
%(pre_indent)s%(indentation)s<in>%(in)s</in>
%(pre_indent)s%(indentation)s<duration>%(duration)s</duration>
%(pre_indent)s%(indentation)s<out>%(out)s</out>
%(file)s
%(pre_indent)s</clipitem>"""

        return template % {
            'id': self.id,
            'start': self.start,
            'end': self.end,
            'name': self.name,
            'enabled': self.enabled,
            'duration': self.duration,
            'in': self.in_,
            'out': self.out,
            'file': self.file.to_xml(indentation=indentation,
                                     pre_indent=pre_indent + indentation),
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class File(PrevisBase, NameMixin, DurationMixin):
    """XML compatibility class for Sequencer
    """

    def __init__(self, duration=0, name='', pathurl=''):
        NameMixin.__init__(self, name=name)
        DurationMixin.__init__(self, duration=duration)
        self._pathurl = self._validate_pathurl(pathurl)

    @classmethod
    def _validate_pathurl(cls, pathurl):
        """validates the given pathurl value
        """
        if not isinstance(pathurl, str):
            raise TypeError(
                '%(class)s.pathurl should be a string, not '
                '%(pathurl_class)s' % {
                    'class': cls.__name__,
                    'pathurl_class': pathurl.__class__.__name__
                }
            )
        return pathurl

    @property
    def pathurl(self):
        """returns the _pathurl attribute
        """
        return self._pathurl

    @pathurl.setter
    def pathurl(self, pathurl):
        """setter for the pathurl property
        """
        self._pathurl = self._validate_pathurl(pathurl)

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        self.duration = float(xml_node.find('duration').text)
        self.name = xml_node.find('name').text
        self.pathurl = xml_node.find('pathurl').text

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this File object
        """
        template = """%(pre_indent)s<file>
%(pre_indent)s%(indentation)s<duration>%(duration)s</duration>
%(pre_indent)s%(indentation)s<name>%(name)s</name>
%(pre_indent)s%(indentation)s<pathurl>%(pathurl)s</pathurl>
%(pre_indent)s</file>"""
        return template % {
            'duration': self.duration,
            'name': self.name,
            'pathurl': self.pathurl,
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class Sequencer(object):
    """The sequence instance.

    It is a manager that manages shot data. It is kind of the reflection of the
    Maya Sequencer instance.

    It is able to get Maya editorial XML and convert it to EDL.
    """

    def __init__(self):
        self._sequencer = None

    def create_sequencer_attributes(self):
        """Creates the necessary extra attributes for the sequencer in the
        current scene.

        Add attributes like:
            sequenceName
            shotNameTemplate
            defaultHandle
        """
        pass

    @classmethod
    def set_shot_names(
            cls, sequence_name, padding=4, increment=10,
            template='%(sequence_name)s_%(shot_name)_%(version_number)03d'):
        """Sets all shot names according to the given template.

        :param sequence_name: The sequence name
        :param padding: Shot number padding
        :param increment: Shot number increment
        :param template: The final shot name template
        :return:
        """
        pass

    @classmethod
    def create_shot(cls, name='', handle=10):
        """Creates a new shot

        :param str name: A string value for the newly created shot name, if
          skipped or given empty, the next empty shot name will be generated.
        :param int handle: An integer value for the handle attribute. Default
          is 10.
        :returns: The created :class:`~pymel.core.nt.Shot` instance
        """
        pass

    @classmethod
    def set_shot_handles(cls, shots, handle=10):
        """Creates handle attribute to given shot instance

        :param shots: a list of :class:`pymel.core.nt.Shot` instances
        :param int handle: An integer value for handle
        :return:
        """
        # validate arguments
        import pymel.core

        # shots
        if not isinstance(shots, list):
            raise TypeError(
                '"shots" argument in %(class)s.set_shot_handles() should be a '
                'list of pymel.core.nt.Shot instances, not %(shots_class)s' %
                {
                    'class': cls.__name__,
                    'shots_class': shots.__class__.__name__
                }
            )

        if not all([isinstance(s, pymel.core.nt.Shot) for s in shots]):
            raise TypeError(
                'All elements in "shots" argument in '
                '%(class)s.set_shot_handles() should be a pymel.core.nt.Shot '
                'instances' %
                {
                    'class': cls.__name__,
                    'shots_class': shots.__class__.__name__
                }
            )

        # handle argument
        if not isinstance(handle, int):
            raise TypeError(
                '"handle" argument in %(class)s.set_shot_handles() should be '
                'a non negative integer, not %(handle_class)s' %
                {
                    'class': cls.__name__,
                    'handle_class': handle.__class__.__name__
                }
            )

        if handle < 0:
            raise ValueError(
                '"handle" argument in %(class)s.set_shot_handles() should be '
                'a non negative integer, not %(handle)s' %
                {
                    'class': cls.__name__,
                    'handle': handle
                }
            )

        # create "handle" attribute in each shot and set the value
        for s in shots:
            try:
                s.addAttr('handle', at='short', k=True, min=0)
            except RuntimeError:
                # attribute is already there
                pass
            s.setAttr('handle', handle)

    def add_frames_to_start(self, shot, frame_count=0):
        """Adds extra frames to the given shots start, and offsets all the
        following shots with the given frame_count.

        :param shot: A :class:`~pymel.core.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    def add_frames_to_end(self, shot, frame_count=0):
        """Adds extra frames to the given shot, and offsets all the following
        shots with the given frame_count.

        :param shot: A :class:`~pymel.core.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    def remove_frames_from_start(self, shot, frame_count=0):
        """Removes frames from the given shots beginning, and offsets all the
        following shots back with the given frame_count.

        :param shot: A :class:`~pymel.core.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    def remove_frames_from_end(self, shot, frame_count=0):
        """Removes frames from the given shots end, and offsets all the
        following shots back with the given frame_count.

        :param shot: A :class:`~pymel.core.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    @classmethod
    def create_shot_playblasts(cls, shots, handle=10, show_ornaments=True):
        """creates the selected shot playblasts
        """
        import pymel.core

        #shots = pymel.core.ls(sl=1, type=pymel.core.nt.Shot)
        #active_panel = pymel.core.playblast(activeEditor=1)

        # get current version and then the output folder
        path_template = os.path.join(
            pymel.core.workspace.name,
            'Outputs/Playblast/AllShots/'
        ).replace('\\', '/')

        filename_template = '%(scene)s_%(shot)s.mov'

        # template vars
        scene_name = os.path.basename(pymel.core.env.sceneName()).split('.')[0]

        for shot in shots:
            shot_name = shot.shotName.get()
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

    @classmethod
    def from_xml(cls, path):
        """Parses XML file and returns a Sequence instance which reflects the
        whole timeline hierarchy.

        :param path: The path of the XML file
        :return: :class:`.Sequence`
        """
        if not isinstance(path, str):
            raise TypeError(
                'path argument in %s.from_xml should be a string, not %s' %
                (cls.__name__, path.__class__.__name__)
            )

        from xml.etree import ElementTree

        try:
            tree = ElementTree.parse(path)
        except IOError:
            raise IOError('Please supply a valid path to an XML file!')

        root = tree.getroot()
        seq = Sequence()
        xml_seq = root.getchildren()[0]

        seq.from_xml(xml_seq)

        return seq

    @classmethod
    def to_xml(cls, seq, indentation=2, pre_indent=0):
        """Converts the given Sequence instance to an xml file

        :param seq: A :class:`.Sequence` instance
        :return: str
        """
        if not isinstance(seq, Sequence):
            raise TypeError(
                '"seq" argument in %s.to_xml should be an instance of'
                'anima.previs.Sequence, not %s' % (
                    cls.__name__, seq.__class__.__name__
                )
            )

        template = """<xmeml version="1.0">\n%(sequence)s\n</xmeml>\n"""

        return template % {
            'sequence': seq.to_xml(indentation=indentation,
                                   pre_indent=indentation + pre_indent)
        }

    @classmethod
    def to_edl(cls, seq):
        """returns an EDL for the given sequence

        :param seq: A :class:`.Sequence` instance
        """
        return seq.to_edl()
