# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os


class EditBase(object):
    """The base for other Edit classes
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
        if not isinstance(name, (str, unicode)):
            raise TypeError(
                '%(class)s.name should be a string or unicode, not %(name_class)s' % {
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

        duration = int(duration)

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


class Sequence(EditBase, NameMixin, DurationMixin):
    """XML compatibility class for Sequence

    This class is mainly created to reflect the XML structure of Maya
    Sequencer.

    It is also the bridge to EDL. So using this class it is possible to convert
    Maya Sequencer XML to a meaningful EDL.

    :param str name: The name of this sequence.
    :param float duration: The duration of this sequence.
    :param Rate rate: The frame rate setting for this sequence. Default
      value is '25', can be anything in ['23.98', '24', '25', '29.97', '30',
      '50', '59.94', '60']. Without setting this converting to EDL will result
      wrong timecode values in EDL.
    :param str timecode: The stating timecode of this Sequence. Default value
      is '00:00:00:00'. This will be used to calculate the clip in and out
      points. Maya exports in and out points as frames, Sequence converts them
      to a timecode by using this parameter as the base.
    """

    def __init__(self, name='', duration=0.0, rate=None,
                 timecode='00:00:00:00'):
        NameMixin.__init__(self, name=name)
        DurationMixin.__init__(self, duration=duration)
        self.ntsc = False
        # replace this with pytimecode.PyTimeCode instance
        self.timecode = timecode

        if rate is None:
            rate = Rate(timebase='25', ntsc=False)
        self.rate = rate

        self.media = None

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        self.duration = int(xml_node.find('duration').text)
        self.name = xml_node.find('name').text
        rate_tag = xml_node.find('rate')
        if rate_tag is not None:
            rate = Rate()
            rate.from_xml(rate_tag)
            self.rate = rate

        self.timecode = xml_node.find('timecode').find('string').text

        xml_media = xml_node.find('media')
        media = Media()
        media.from_xml(xml_media)

        self.media = media

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Sequence object
        """
        template = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5">
%(pre_indent)s<sequence>
%(pre_indent)s%(indentation)s<duration>%(duration)s</duration>
%(pre_indent)s%(indentation)s<name>%(name)s</name>
%(rate)s
%(pre_indent)s%(indentation)s<timecode>
%(pre_indent)s%(indentation)s%(indentation)s<string>%(timecode)s</string>
%(pre_indent)s%(indentation)s</timecode>
%(media)s
%(pre_indent)s</sequence>
</xmeml>"""

        return template % {
            'duration': self.duration,
            'name': self.name,
            'ntsc': str(self.ntsc).upper(),
            'rate': self.rate.to_xml(
                indentation=indentation,
                pre_indent=indentation + pre_indent
            ),
            'timecode': self.timecode,
            'media': self.media.to_xml(
                indentation=indentation,
                pre_indent=indentation + pre_indent
            ),
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
        self.media.video = v

        video_track = Track()
        v.tracks.append(video_track)
        # no audio tracks fow now

        # read Events in to Clips
        sequence_start = 1e20
        sequence_end = -1
        for e in edl_list.events:
            assert isinstance(e, edl.Event)
            clip = Clip()

            clip.name = e.reel
            clip.id = e.clip_name
            clip.type = 'Video' if e.track == 'V' else 'Audio'

            clip.in_ = e.src_start_tc.frame_number
            clip.out = e.src_end_tc.frame_number

            clip.duration = clip.out - clip.in_

            clip.start = e.rec_start_tc.frame_number
            clip.end = e.rec_end_tc.frame_number

            # check in and out points relative to each other
            if clip.start > clip.end:
                # a possible negative number
                from timecode import Timecode
                # get the last timecode like 23:59:59:xx
                tc_24_hours = Timecode(
                    edl_list.fps,
                    '23:59:59:%s' % edl_list.fps
                )
                clip.start -= tc_24_hours.frame_number  # + 1

            if clip.start < sequence_start:
                sequence_start = clip.start
            if clip.end > sequence_end:
                sequence_end = clip.end

            f = File()
            f.name = clip.name

            # include the handle at start,
            # but we can not have any idea about the
            # handle at end
            #
            # a possible solution is to look to the original media
            # but we may not be able to reach the media itself
            f.duration = e.src_end_tc.frame_number

            f.pathurl = 'file://%s' % e.source_file

            clip.file = f

            if clip.type == 'Video':
                video_track.clips.append(clip)

        self.duration = sequence_end - sequence_start
        # TODO: fix this later, timecode always 00:00:00:00 for now
        self.timecode = '00:00:00:00'
        # TODO: can not read sequence.timebase from edl

    def to_edl(self):
        """Returns an edl.List instance equivalent of this Sequence instance
        """
        from edl import List, Event
        from timecode import Timecode

        l = List(self.rate.timebase)
        l.title = self.name

        # convert clips to events
        if not self.media:
            raise RuntimeError(
                'Can not run %(class)s.to_edl() without a Media instance, '
                'please add a Media instance to this %(class)s instance.' % {
                    'class': self.__class__.__name__
                }
            )

        video = self.media.video
        if video is not None:
            i = 0
            for track in video.tracks:
                for clip in track.clips:
                    i += 1
                    e = Event({})
                    e.num = '%06i' % i
                    e.clip_name = clip.id
                    e.reel = clip.name
                    e.track = 'V' if clip.type == 'Video' else 'A'
                    e.tr_code = 'C'  # TODO: for now use C (Cut) later on
                    # expand it to add other transition codes

                    src_start_tc = Timecode(self.rate.timebase,
                                            frames=clip.in_ + 1)
                    # 1 frame after last frame shown
                    src_end_tc = Timecode(self.rate.timebase,
                                          frames=clip.out + 1)

                    e.src_start_tc = str(src_start_tc)
                    e.src_end_tc = str(src_end_tc)

                    rec_start_tc = Timecode(self.rate.timebase,
                                            frames=clip.start + 1)
                    # 1 frame after last frame shown
                    rec_end_tc = Timecode(self.rate.timebase,
                                          frames=clip.end + 1)

                    e.rec_start_tc = str(rec_start_tc)
                    e.rec_end_tc = str(rec_end_tc)

                    source_file = \
                        clip.file.pathurl.replace('file://localhost', '')
                    if ':' in source_file and source_file.startswith('/'):
                        # remove the leading '/'
                        source_file = source_file[1:]

                    e.source_file = source_file

                    e.comments.extend([
                        '* FROM CLIP NAME: %s' % clip.name,
                        '* SOURCE FILE: %s' % source_file
                    ])

                    l.append(e)
        return l

    def to_metafuze_xml(self):
        """Generates a MetaFuze compatible XML content per clip.

        :returns: list of strings
        """
        metafuze_xml_template = """<?xml version='1.0' encoding='UTF-8'?>
<MetaFuze_BatchTranscode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="MetaFuzeBatchTranscode.xsd">
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
         <TapeName>%(clip_name)s</TapeName>
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
         <OutputPreset>DNxHD 36</OutputPreset>
         <OutputPreset>
            <Version>2.0</Version>
            <Name>DNxHD 36</Name>
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
        video = self.media.video
        if video is not None:
            for track in video.tracks:
                for clip in track.clips:
                    raw_file_path = \
                        clip.file.pathurl.replace('file://localhost', '')
                    raw_mxf_path = '%s%s' % (
                        os.path.splitext(raw_file_path)[0],
                        '.mxf'
                    )

                    kwargs = {
                        'file_pathurl': os.path.normpath(
                            os.path.expandvars(raw_file_path)
                        ),
                        'mxf_pathurl': os.path.normpath(
                            os.path.expandvars(raw_mxf_path)
                        ),
                        'sequence_name': self.name,
                        'sequence_timecode': self.timecode,
                        'clip_id': clip.id,
                        'clip_name': clip.name,
                        # metafuze likes frame number
                        'clip_duration': clip.duration - 1,
                        'width': video.width,
                        'height': video.height
                    }

                    rendered_xmls.append(metafuze_xml_template % kwargs)

        return rendered_xmls


class Media(EditBase):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.video = None
        self.audio = None

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        xml_video_tag = xml_node.find('video')
        video = Video()
        video.from_xml(xml_video_tag)
        self.video = video

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Media object
        """
        template = """%(pre_indent)s<media>
%(video)s
%(pre_indent)s</media>"""

        video_data = self.video.to_xml(
            indentation=indentation,
            pre_indent=indentation + pre_indent
        )

        return template % {
            'video': video_data,
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class Video(EditBase):
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
        for track_tag in xml_node.findall('track'):
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


class Track(EditBase):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.locked = False
        self.enabled = True
        self.clips = []

    def optimize_clips(self):
        """optimizes files across all clips to use the same file node if two or
        more clips are using the same files
        """
        # check all clip files and set to the same file node if the path is
        # the same
        for i in range(len(self.clips)):
            clip = self.clips[i]
            # go over the rest of the clips
            for j in range(i + 1, len(self.clips)):
                compare_clip = self.clips[j]
                if clip.file.pathurl == compare_clip.file.pathurl:
                    compare_clip.file = clip.file

                # also check the ids
                if clip.id == compare_clip.id:
                    # get the id randomized part
                    random_part = clip.id.split(' ')[-1]
                    if random_part != clip.id:
                        random_id = int(random_part) + 1
                        compare_clip.id = '%s %s' % (
                            clip.id.split(' ')[0],
                            random_id
                        )
                    else:
                        random_id = 2
                        compare_clip.id = '%s %s' % (clip.id, random_id)

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


class Clip(EditBase, NameMixin, DurationMixin):
    """XML compatibility class for Clip
    """

    def __init__(self, id=None, name='', start=0.0, end=0.0, duration=0.0,
                 enabled=True, in_=0, out=0, type_='Video', rate=None):
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
        self._rate = None
        self.rate = rate

    @classmethod
    def _validate_rate(cls, rate):
        """validates the rate value
        """
        return rate

    @property
    def rate(self):
        """getter for the _rate attribute
        """
        return self._rate

    @rate.setter
    def rate(self, rate):
        """setter for the _rate attribute
        """
        self._rate = self._validate_rate(rate)

    @classmethod
    def _validate_id(cls, id_):
        """validates the given id value
        """
        if id_ is None:
            id_ = ''

        if not isinstance(id_, (str, unicode)):
            raise TypeError(
                '%(class)s.id should be a string or unicode, not %(id_class)s' %
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
        self.start = int(xml_node.find('start').text)
        self.end = int(xml_node.find('end').text)
        self.name = xml_node.find('name').text
        self.enabled = xml_node.find('enabled').text == 'True'
        self.duration = int(xml_node.find('duration').text)
        self.in_ = int(xml_node.find('in').text)
        self.out = int(xml_node.find('out').text)

        file_tag = xml_node.find('file')
        if file_tag:
            f = File()
            f.from_xml(file_tag)

            self.file = f

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Clip object
        """
        template = """%(pre_indent)s<clipitem id="%(id)s">
%(pre_indent)s%(indentation)s<end>%(end)i</end>
%(pre_indent)s%(indentation)s<name>%(name)s</name>
%(pre_indent)s%(indentation)s<enabled>%(enabled)s</enabled>
%(pre_indent)s%(indentation)s<start>%(start)i</start>
%(pre_indent)s%(indentation)s<in>%(in)i</in>
%(pre_indent)s%(indentation)s<duration>%(duration)i</duration>%(rate)s
%(pre_indent)s%(indentation)s<out>%(out)i</out>
%(file)s
%(pre_indent)s</clipitem>"""

        rate_xml = ''
        if self.rate:
            rate_xml = '\n%s' % self.rate.to_xml(
                indentation=indentation,
                pre_indent=pre_indent + indentation
            )

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
            'indentation': ' ' * indentation,
            'rate': rate_xml
        }


class File(EditBase, NameMixin, DurationMixin):
    """XML compatibility class for Sequencer
    """

    def __init__(self, duration=0, name='', pathurl=''):
        NameMixin.__init__(self, name=name)
        DurationMixin.__init__(self, duration=duration)
        self._pathurl = self._validate_pathurl(pathurl)
        self._id = None
        self.id = self._pathurl
        self.exported_once = False

    @property
    def id(self):
        """the getter for the _id attribute
        """
        return self._id

    @id.setter
    def id(self, id_):
        """the setter for the _id attribute
        """
        self._id = self._validate_id(id_)

    @classmethod
    def _validate_id(cls, id_):
        part = id_.split('/')[-1]
        return part.replace('%5B', '[').replace('%5D', ']')

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

        # expand any environment vars
        if pathurl:
            if 'file://localhost/' in pathurl:
                split_from = 'file://localhost/'
            else:
                split_from = 'file://'

            pathurl = 'file://localhost/%s' % os.path.normpath(
                os.path.expandvars(
                    pathurl.split(split_from)[-1]
                )
            ).replace('\\', '/')

            # remove double slashes after "localhost"
            # (happens in Linux and OSX only)
            pathurl = \
                pathurl.replace('file://localhost//', 'file://localhost/')

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
        # also set the id attribute
        self.id = self._pathurl

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        duration_node = xml_node.find('duration')
        if duration_node is not None:
            self.duration = int(duration_node.text)

        name_node = xml_node.find('name')
        if name_node is not None:
            self.name = name_node.text

        pathurl_node = xml_node.find('pathurl')
        if pathurl_node is not None:
            self.pathurl = pathurl_node.text

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this File object
        """
        if self.exported_once:
            template = """%(pre_indent)s<file id="%(id)s"/>"""
        else:
            template = """%(pre_indent)s<file id="%(id)s">
%(pre_indent)s%(indentation)s<duration>%(duration)i</duration>
%(pre_indent)s%(indentation)s<name>%(name)s</name>
%(pre_indent)s%(indentation)s<pathurl>%(pathurl)s</pathurl>
%(pre_indent)s</file>"""
            self.exported_once = True

        return template % {
            'id': self.id,
            'duration': self.duration,
            'name': self.name,
            'pathurl': self.pathurl,
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class Rate(EditBase):
    """XML compatibility class for Rate

    :param str timebase: The frame rate setting for this sequence.
      Default value is '25', can be anything in ['12', '23.98', '24', '25',
      '29.97', '30', '50', '59.94', '60']. Without setting this converting to
      EDL will result wrong timecode values in EDL.

    :param bool ntsc: A bool value showing if this is a dropframe rate. Default
      value is False.
    """
    __timebase_default_value = '25'

    def __init__(self, timebase=None, ntsc=False):
        self._timebase = None
        self._ntsc = None
        self.timebase = self._validate_timebase(timebase)
        self.ntsc = self._validate_ntsc(ntsc)

    @classmethod
    def _validate_timebase(cls, timebase):
        """validates the given timebase value
        """
        if timebase is None:
            timebase = cls.__timebase_default_value

        if not isinstance(timebase, str):
            raise TypeError(
                '%(class)s.timebase should be a str, not '
                '%(timebase_class)s' % {
                    'class': cls.__name__,
                    'timebase_class': timebase.__class__.__name__
                }
            )

        return timebase

    @property
    def timebase(self):
        """returns the _timebase attribute value
        """
        return self._timebase

    @timebase.setter
    def timebase(self, timebase):
        self._timebase = self._validate_timebase(timebase)

    @classmethod
    def _validate_ntsc(cls, ntsc):
        """validates the given ntsc value
        """
        if ntsc is None:
            ntsc = False

        if not isinstance(ntsc, bool):
            raise TypeError(
                '%(class)s.ntsc should be a bool value, not '
                '%(ntsc_class)s' % {
                    'class': cls.__name__,
                    'ntsc_class': ntsc.__class__.__name__
                }
            )

        return bool(ntsc)

    @property
    def ntsc(self):
        """returns the _ntsc attribute value
        """
        return self._ntsc

    @ntsc.setter
    def ntsc(self, ntsc):
        self._ntsc = self._validate_ntsc(ntsc)

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        rate_tag = xml_node
        if rate_tag is not None:
            self.timebase = rate_tag.find('timebase').text
            self.ntsc = rate_tag.find('ntsc').text.title() == 'True'

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Media object
        """
        template = """%(pre_indent)s<rate>
%(pre_indent)s%(indentation)s<timebase>%(timebase)s</timebase>
%(pre_indent)s%(indentation)s<ntsc>%(ntsc)s</ntsc>
%(pre_indent)s</rate>"""
        return template % {
            'timebase': self.timebase,
            'ntsc': 'TRUE' if self.ntsc else 'FALSE',
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }
