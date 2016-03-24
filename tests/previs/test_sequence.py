# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import unittest

# prepare for test
os.environ['ANIMA_TEST_SETUP'] = ""

from anima.env import mayaEnv  # to setup maya extensions
import pymel.core as pm

from edl import List, Event
from anima.edit import Sequence, Media, Video, Track, Clip, File, Rate


class SequenceTestCase(unittest.TestCase):
    """tests the anima.previs.Sequence class
    """

    def test_to_xml_method_is_working_properly(self):
        """testing if the to xml method is working properly
        """
        s = Sequence()
        s.duration = 109
        s.name = 'previs_edit_v001'

        s.rate = Rate(timebase='24', ntsc=False)

        s.timecode = '00:00:00:00'

        m = Media()
        s.media = m

        v = Video()
        v.width = 1024
        v.height = 778
        m.video = v

        t = Track()
        t.enabled = True
        t.locked = False

        v.tracks.append(t)

        # clip 1
        f = File()
        f.duration = 34
        f.name = 'shot2'
        f.pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot2.mov'

        c = Clip()
        c.id = 'shot2'
        c.start = 1
        c.end = 35
        c.name = 'shot2'
        c.enabled = True
        c.duration = 34
        c.in_ = 0
        c.out = 34
        c.file = f

        t.clips.append(c)

        # clip 2
        f = File()
        f.duration = 30
        f.name = 'shot'
        f.pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot.mov'

        c = Clip()
        c.id = 'shot'
        c.start = 35
        c.end = 65
        c.name = 'shot'
        c.enabled = True
        c.duration = 30
        c.in_ = 0
        c.out = 30
        c.file = f

        t.clips.append(c)

        # clip 3
        f = File()
        f.duration = 45
        f.name = 'shot1'
        f.pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot1.mov'

        c = Clip()
        c.id = 'shot1'
        c.start = 65
        c.end = 110
        c.name = 'shot1'
        c.enabled = True
        c.duration = 45
        c.in_ = 0
        c.out = 45
        c.file = f

        t.clips.append(c)

        expected_xml = \
            """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5">
<sequence>
  <duration>109</duration>
  <name>previs_edit_v001</name>
  <rate>
    <timebase>24</timebase>
    <ntsc>FALSE</ntsc>
  </rate>
  <timecode>
    <string>00:00:00:00</string>
  </timecode>
  <media>
    <video>
      <format>
        <samplecharacteristics>
          <width>1024</width>
          <height>778</height>
        </samplecharacteristics>
      </format>
      <track>
        <locked>FALSE</locked>
        <enabled>TRUE</enabled>
        <clipitem id="shot2">
          <end>35</end>
          <name>shot2</name>
          <enabled>True</enabled>
          <start>1</start>
          <in>0</in>
          <duration>34</duration>
          <out>34</out>
          <file id="shot2.mov">
            <duration>34</duration>
            <name>shot2</name>
            <pathurl>file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov</pathurl>
          </file>
        </clipitem>
        <clipitem id="shot">
          <end>65</end>
          <name>shot</name>
          <enabled>True</enabled>
          <start>35</start>
          <in>0</in>
          <duration>30</duration>
          <out>30</out>
          <file id="shot.mov">
            <duration>30</duration>
            <name>shot</name>
            <pathurl>file://localhost/home/eoyilmaz/maya/projects/default/data/shot.mov</pathurl>
          </file>
        </clipitem>
        <clipitem id="shot1">
          <end>110</end>
          <name>shot1</name>
          <enabled>True</enabled>
          <start>65</start>
          <in>0</in>
          <duration>45</duration>
          <out>45</out>
          <file id="shot1.mov">
            <duration>45</duration>
            <name>shot1</name>
            <pathurl>file://localhost/home/eoyilmaz/maya/projects/default/data/shot1.mov</pathurl>
          </file>
        </clipitem>
      </track>
    </video>
  </media>
</sequence>
</xmeml>"""

        self.assertEqual(
            expected_xml,
            s.to_xml()
        )

    def test_from_xml_method_is_working_properly(self):
        """testing if the from_xml method will fill object attributes from the
        given xml node
        """
        from xml.etree import ElementTree
        sequence_node = ElementTree.Element('sequence')
        duration_node = ElementTree.SubElement(sequence_node, 'duration')
        duration_node.text = '109'
        name_node = ElementTree.SubElement(sequence_node, 'name')
        name_node.text = 'previs_edit_v001'
        rate_node = ElementTree.SubElement(sequence_node, 'rate')
        ntsc_node = ElementTree.SubElement(rate_node, 'ntsc')
        ntsc_node.text = 'FALSE'
        timebase_node = ElementTree.SubElement(rate_node, 'timebase')
        timebase_node.text = '24'
        timecode_node = ElementTree.SubElement(sequence_node, 'timecode')
        string_node = ElementTree.SubElement(timecode_node, 'string')
        string_node.text = '00:00:00:00'

        media_node = ElementTree.SubElement(sequence_node, 'media')

        video_node = ElementTree.SubElement(media_node, 'video')
        format_node = ElementTree.SubElement(video_node, 'format')
        sc_node = ElementTree.SubElement(format_node, 'samplecharacteristics')
        width_node = ElementTree.SubElement(sc_node, 'width')
        width_node.text = 1024
        height_node = ElementTree.SubElement(sc_node, 'height')
        height_node.text = 778

        track_node = ElementTree.SubElement(video_node, 'track')
        locked_node = ElementTree.SubElement(track_node, 'locked')
        locked_node.text = 'FALSE'
        enabled_node = ElementTree.SubElement(track_node, 'enabled')
        enabled_node.text = 'TRUE'

        # clip1
        clip_node = ElementTree.SubElement(track_node, 'clipitem',
                                           attrib={'id': 'shot2'})
        end_node = ElementTree.SubElement(clip_node, 'end')
        end_node.text = '35'
        name_node = ElementTree.SubElement(clip_node, 'name')
        name_node.text = 'shot2'
        enabled_node = ElementTree.SubElement(clip_node, 'enabled')
        enabled_node.text = 'True'
        start_node = ElementTree.SubElement(clip_node, 'start')
        start_node.text = '1'
        in_node = ElementTree.SubElement(clip_node, 'in')
        in_node.text = '0'
        duration_node = ElementTree.SubElement(clip_node, 'duration')
        duration_node.text = '34'
        out_node = ElementTree.SubElement(clip_node, 'out')
        out_node.text = '34'

        file_node = ElementTree.SubElement(clip_node, 'file')
        duration_node = ElementTree.SubElement(file_node, 'duration')
        duration_node.text = '34'
        name_node = ElementTree.SubElement(file_node, 'name')
        name_node.text = 'shot2'
        pathurl_node = ElementTree.SubElement(file_node, 'pathurl')

        pathurl = 'file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov'
        pathurl_node.text = pathurl

        # clip2
        clip_node = ElementTree.SubElement(track_node, 'clipitem',
                                           attrib={'id': 'shot'})
        end_node = ElementTree.SubElement(clip_node, 'end')
        end_node.text = '65'
        name_node = ElementTree.SubElement(clip_node, 'name')
        name_node.text = 'shot'
        enabled_node = ElementTree.SubElement(clip_node, 'enabled')
        enabled_node.text = 'True'
        start_node = ElementTree.SubElement(clip_node, 'start')
        start_node.text = '35'
        in_node = ElementTree.SubElement(clip_node, 'in')
        in_node.text = '0'
        duration_node = ElementTree.SubElement(clip_node, 'duration')
        duration_node.text = '30'
        out_node = ElementTree.SubElement(clip_node, 'out')
        out_node.text = '30'

        file_node = ElementTree.SubElement(clip_node, 'file')
        duration_node = ElementTree.SubElement(file_node, 'duration')
        duration_node.text = '30'
        name_node = ElementTree.SubElement(file_node, 'name')
        name_node.text = 'shot'
        pathurl_node = ElementTree.SubElement(file_node, 'pathurl')

        pathurl = 'file://localhost/home/eoyilmaz/maya/projects/default/data/shot.mov'
        pathurl_node.text = pathurl

        # clip3
        clip_node = ElementTree.SubElement(
            track_node, 'clipitem', attrib={'id': 'shot1'}
        )
        end_node = ElementTree.SubElement(clip_node, 'end')
        end_node.text = '110'
        name_node = ElementTree.SubElement(clip_node, 'name')
        name_node.text = 'shot1'
        enabled_node = ElementTree.SubElement(clip_node, 'enabled')
        enabled_node.text = 'True'
        start_node = ElementTree.SubElement(clip_node, 'start')
        start_node.text = '65'
        in_node = ElementTree.SubElement(clip_node, 'in')
        in_node.text = '0'
        duration_node = ElementTree.SubElement(clip_node, 'duration')
        duration_node.text = '45'

        rate_node = ElementTree.SubElement(clip_node, 'rate')
        ntsc_node = ElementTree.SubElement(rate_node, 'ntsc')
        ntsc_node.text = 'FALSE'
        timebase_node = ElementTree.SubElement(rate_node, 'timebase')
        timebase_node.text = '24'

        out_node = ElementTree.SubElement(clip_node, 'out')
        out_node.text = '45'

        file_node = ElementTree.SubElement(clip_node, 'file')
        duration_node = ElementTree.SubElement(file_node, 'duration')
        duration_node.text = '45'
        name_node = ElementTree.SubElement(file_node, 'name')
        name_node.text = 'shot1'
        pathurl_node = ElementTree.SubElement(file_node, 'pathurl')

        pathurl = 'file://localhost/home/eoyilmaz/maya/projects/default/data/shot1.mov'
        pathurl_node.text = pathurl

        s = Sequence()
        s.from_xml(sequence_node)
        self.assertEqual(109, s.duration)
        self.assertEqual('previs_edit_v001', s.name)

        r = s.rate
        self.assertEqual(False, r.ntsc)
        self.assertEqual('24', r.timebase)

        self.assertEqual('00:00:00:00', s.timecode)

        m = s.media

        v = m.video
        self.assertEqual(1024, v.width)
        self.assertEqual(778, v.height)

        t = v.tracks[0]
        self.assertEqual(False, t.locked)
        self.assertEqual(True, t.enabled)

        # clip1
        c = t.clips[0]
        self.assertEqual(35, c.end)
        self.assertEqual('shot2', c.name)
        self.assertEqual(True, c.enabled)
        self.assertEqual(1, c.start)
        self.assertEqual(0, c.in_)
        self.assertEqual(34, c.duration)
        self.assertEqual(34, c.out)

        f = c.file
        self.assertEqual(34, f.duration)
        self.assertEqual('shot2', f.name)
        self.assertEqual(
            'file://localhost/home/eoyilmaz/maya/projects/default/data/shot2.mov',
            f.pathurl
        )

        # clip2
        c = t.clips[1]
        self.assertEqual(65, c.end)
        self.assertEqual('shot', c.name)
        self.assertEqual(True, c.enabled)
        self.assertEqual(35, c.start)
        self.assertEqual(0, c.in_)
        self.assertEqual(30, c.duration)
        self.assertEqual(30, c.out)

        f = c.file
        self.assertEqual(30, f.duration)
        self.assertEqual('shot', f.name)
        self.assertEqual(
            'file://localhost/home/eoyilmaz/maya/projects/default/data/shot.mov',
            f.pathurl
        )

        # clip3
        c = t.clips[2]
        self.assertEqual(110, c.end)
        self.assertEqual('shot1', c.name)
        self.assertEqual(True, c.enabled)
        self.assertEqual(65, c.start)
        self.assertEqual(0, c.in_)
        self.assertEqual(45, c.duration)
        self.assertEqual(45, c.out)

        f = c.file
        self.assertEqual(45, f.duration)
        self.assertEqual('shot1', f.name)
        self.assertEqual(
            'file://localhost/home/eoyilmaz/maya/projects/default/data/shot1.mov',
            f.pathurl
        )

    def test_to_edl_will_raise_RuntimeError_if_no_Media_instance_presents(self):
        """testing if a RuntimeError will be raised when there is no Media
        instance present in Sequence
        """
        s = Sequence()
        with self.assertRaises(RuntimeError) as cm:
            s.to_edl()

        self.assertEqual(
            'Can not run Sequence.to_edl() without a Media instance, please '
            'add a Media instance to this Sequence instance.',
            cm.exception.message
        )

    def test_to_edl_method_will_return_a_List_instance(self):
        """testing if to_edl method will return an edl.List instance
        """
        s = Sequence()
        m = Media()
        s.media = m

        result = s.to_edl()
        self.assertTrue(isinstance(result, List))

    def test_to_edl_method_is_working_properly(self):
        """testing if the to_edl method will output a proper edl.List object
        """
        # create Sequence instance from XML
        sm = pm.PyNode('sequenceManager1')
        sm.set_version('v001')
        xml_path = os.path.abspath('./test_data/test_v001.xml')
        sm.from_xml(xml_path)

        sequence = sm.generate_sequence_structure()

        edl_list = sm.to_edl()
        self.assertTrue(isinstance(edl_list, List))

        self.assertEqual(
            sequence.name,
            edl_list.title
        )

        # events should be clips
        self.assertEqual(3, len(edl_list.events))

        e1 = edl_list.events[0]
        e2 = edl_list.events[1]
        e3 = edl_list.events[2]

        self.assertTrue(isinstance(e1, Event))
        self.assertTrue(isinstance(e2, Event))
        self.assertTrue(isinstance(e3, Event))

        # check clips
        clips = sequence.media.video.tracks[0].clips
        self.assertTrue(isinstance(clips[0], Clip))

        self.assertEqual('000001', e1.num)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', e1.clip_name)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', e1.reel)
        self.assertEqual('V', e1.track)
        self.assertEqual('C', e1.tr_code)
        self.assertEqual('00:00:00:00', e1.src_start_tc)
        self.assertEqual('00:00:01:10', e1.src_end_tc)
        self.assertEqual('00:00:00:01', e1.rec_start_tc)
        self.assertEqual('00:00:01:11', e1.rec_end_tc)
        self.assertEqual(
            '* FROM CLIP NAME: SEQ001_HSNI_003_0010_v001',
            e1.comments[0]
        )
        self.assertEqual('/tmp/SEQ001_HSNI_003_0010_v001.mov', e1.source_file)
        self.assertEqual(
            '* SOURCE FILE: /tmp/SEQ001_HSNI_003_0010_v001.mov', e1.comments[1]
        )

        self.assertEqual('000002', e2.num)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', e2.clip_name)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', e2.reel)
        self.assertEqual('V', e2.track)
        self.assertEqual('C', e2.tr_code)
        self.assertEqual('00:00:00:00', e2.src_start_tc)
        self.assertEqual('00:00:01:07', e2.src_end_tc)
        self.assertEqual('00:00:01:11', e2.rec_start_tc)
        self.assertEqual('00:00:02:18', e2.rec_end_tc)
        self.assertEqual('/tmp/SEQ001_HSNI_003_0020_v001.mov',
                         e2.source_file)
        self.assertEqual(
            '* FROM CLIP NAME: SEQ001_HSNI_003_0020_v001',
            e2.comments[0]
        )
        self.assertEqual(
            '* SOURCE FILE: /tmp/SEQ001_HSNI_003_0020_v001.mov',
            e2.comments[1]
        )

        self.assertEqual('000003', e3.num)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', e3.clip_name)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', e3.reel)
        self.assertEqual('V', e3.track)
        self.assertEqual('C', e3.tr_code)
        self.assertEqual('00:00:00:00', e3.src_start_tc)
        self.assertEqual('00:00:01:22', e3.src_end_tc)
        self.assertEqual('00:00:02:18', e3.rec_start_tc)
        self.assertEqual('00:00:04:16', e3.rec_end_tc)
        self.assertEqual('/tmp/SEQ001_HSNI_003_0030_v001.mov',
                         e3.source_file)
        self.assertEqual(
            '* FROM CLIP NAME: SEQ001_HSNI_003_0030_v001',
            e3.comments[0]
        )
        self.assertEqual(
            '* SOURCE FILE: /tmp/SEQ001_HSNI_003_0030_v001.mov',
            e3.comments[1]
        )

    def test_from_edl_method_is_working_properly(self):
        """testing if the from_edl method will return an anima.previs.Sequence
        instance with proper hierarchy
        """
        # first supply an edl
        from edl import Parser
        p = Parser('24')
        edl_path = os.path.abspath('./test_data/test_v001.edl')

        with open(edl_path) as f:
            edl_list = p.parse(f)

        r = Rate(timebase='24')

        s = Sequence(rate=r)
        s.from_edl(edl_list)

        self.assertEqual('SEQ001_HSNI_003', s.name)

        self.assertEqual(111, s.duration)

        r = s.rate
        self.assertEqual('24', r.timebase)
        self.assertEqual('00:00:00:00', s.timecode)

        m = s.media
        self.assertTrue(isinstance(m, Media))

        v = m.video
        self.assertTrue(isinstance(v, Video))

        t = v.tracks[0]
        self.assertEqual(False, t.locked)
        self.assertEqual(True, t.enabled)

        clips = t.clips
        self.assertEqual(3, len(clips))

        clip1 = clips[0]
        clip2 = clips[1]
        clip3 = clips[2]

        self.assertTrue(isinstance(clip1, Clip))
        self.assertTrue(isinstance(clip2, Clip))
        self.assertTrue(isinstance(clip3, Clip))

        # clip1
        self.assertEqual(34, clip1.duration)
        self.assertEqual(True, clip1.enabled)
        self.assertEqual(35, clip1.end)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', clip1.id)
        self.assertEqual(10, clip1.in_)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', clip1.name)
        self.assertEqual(44, clip1.out)
        self.assertEqual(1, clip1.start)
        self.assertEqual('Video', clip1.type)

        f = clip1.file
        self.assertTrue(isinstance(f, File))
        self.assertEqual(44, f.duration)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', f.name)
        self.assertEqual(
            'file://localhost/tmp/SEQ001_HSNI_003_0010_v001.mov',
            f.pathurl
        )

        # clip2
        self.assertEqual(31, clip2.duration)
        self.assertEqual(True, clip2.enabled)
        self.assertEqual(66, clip2.end)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', clip2.id)
        self.assertEqual(10, clip2.in_)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', clip2.name)
        self.assertEqual(41, clip2.out)
        self.assertEqual(35, clip2.start)
        self.assertEqual('Video', clip2.type)

        f = clip2.file
        self.assertTrue(isinstance(f, File))
        self.assertEqual(41, f.duration)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', f.name)
        self.assertEqual(
            'file://localhost/tmp/SEQ001_HSNI_003_0020_v001.mov',
            f.pathurl
        )

        # clip3
        self.assertEqual(46, clip3.duration)
        self.assertEqual(True, clip3.enabled)
        self.assertEqual(112, clip3.end)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', clip3.id)
        self.assertEqual(10, clip3.in_)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', clip3.name)
        self.assertEqual(56, clip3.out)
        self.assertEqual(66, clip3.start)
        self.assertEqual('Video', clip3.type)

        f = clip3.file
        self.assertTrue(isinstance(f, File))
        self.assertEqual(56, f.duration)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', f.name)
        self.assertEqual(
            'file://localhost/tmp/SEQ001_HSNI_003_0030_v001.mov',
            f.pathurl
        )

    def test_from_edl_method_is_working_properly_with_negative_timecodes(self):
        """testing if the from_edl method will return an anima.previs.Sequence
        instance with proper hierarchy event with clips that has negative
        timecode values (timecodes with in point is bigger than out point and
        around 23:59:59:XX as a result)
        """
        # first supply an edl
        from edl import Parser
        p = Parser('24')
        edl_path = os.path.abspath('./test_data/test_v003.edl')

        with open(edl_path) as f:
            edl_list = p.parse(f)

        r = Rate(timebase='24')

        s = Sequence(rate=r)
        s.from_edl(edl_list)

        self.assertEqual('SEQ001_HSNI_003', s.name)

        self.assertEqual(247, s.duration)
        self.assertEqual('24', s.rate.timebase)
        self.assertEqual('00:00:00:00', s.timecode)

        m = s.media
        self.assertTrue(isinstance(m, Media))

        v = m.video
        self.assertTrue(isinstance(v, Video))

        t = v.tracks[0]
        self.assertEqual(False, t.locked)
        self.assertEqual(True, t.enabled)

        clips = t.clips
        self.assertEqual(3, len(clips))

        clip1 = clips[0]
        clip2 = clips[1]
        clip3 = clips[2]

        self.assertTrue(isinstance(clip1, Clip))
        self.assertTrue(isinstance(clip2, Clip))
        self.assertTrue(isinstance(clip3, Clip))

        # clip1
        self.assertEqual(176, clip1.duration)
        self.assertEqual(True, clip1.enabled)
        self.assertEqual(153, clip1.end)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', clip1.id)
        self.assertEqual(15, clip1.in_)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', clip1.name)
        self.assertEqual(191, clip1.out)
        self.assertEqual(-23, clip1.start)
        self.assertEqual('Video', clip1.type)

        f = clip1.file
        self.assertTrue(isinstance(f, File))
        self.assertEqual(191, f.duration)
        self.assertEqual('SEQ001_HSNI_003_0010_v001', f.name)
        self.assertEqual(
            'file://localhost/tmp/SEQ001_HSNI_003_0010_v001.mov',
            f.pathurl
        )

        # clip2
        self.assertEqual(55, clip2.duration)
        self.assertEqual(True, clip2.enabled)
        self.assertEqual(208, clip2.end)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', clip2.id)
        self.assertEqual(45, clip2.in_)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', clip2.name)
        self.assertEqual(100, clip2.out)
        self.assertEqual(153, clip2.start)
        self.assertEqual('Video', clip2.type)

        f = clip2.file
        self.assertTrue(isinstance(f, File))
        self.assertEqual(100, f.duration)
        self.assertEqual('SEQ001_HSNI_003_0020_v001', f.name)
        self.assertEqual(
            'file://localhost/tmp/SEQ001_HSNI_003_0020_v001.mov',
            f.pathurl
        )

        # clip3
        self.assertEqual(1, clip3.duration)
        self.assertEqual(True, clip3.enabled)
        self.assertEqual(224, clip3.end)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', clip3.id)
        self.assertEqual(0, clip3.in_)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', clip3.name)
        self.assertEqual(1, clip3.out)
        self.assertEqual(208, clip3.start)
        self.assertEqual('Video', clip3.type)

        f = clip3.file
        self.assertTrue(isinstance(f, File))
        self.assertEqual(1, f.duration)
        self.assertEqual('SEQ001_HSNI_003_0030_v001', f.name)
        self.assertEqual(
            'file://localhost/tmp/SEQ001_HSNI_003_0030_v001.mov',
            f.pathurl
        )

    def test_to_metafuze_xml_is_working_properly(self):
        """testing if to_metafuze_xml method is working properly
        """
        s = Sequence()
        s.duration = 109
        s.name = 'SEQ001_HSNI_003'
        s.timecode = '00:00:00:00'

        r = Rate()
        s.rate = r
        r.ntsc = False
        r.timebase = '24'

        m = Media()
        s.media = m

        v = Video()
        v.width = 1024
        v.height = 778
        m.video = v

        t = Track()
        t.enabled = True
        t.locked = False

        v.tracks.append(t)

        # clip 1
        f = File()
        f.duration = 34
        f.name = 'SEQ001_HSNI_003_0010_v001'
        f.pathurl = 'file://localhost/tmp/SEQ001_HSNI_003_0010_v001.mov'

        c = Clip()
        c.id = '0010'
        c.start = 1
        c.end = 35
        c.name = 'SEQ001_HSNI_003_0010_v001'
        c.enabled = True
        c.duration = 34
        c.in_ = 0
        c.out = 34
        c.file = f

        t.clips.append(c)

        # clip 2
        f = File()
        f.duration = 30
        f.name = 'SEQ001_HSNI_003_0020_v001'
        f.pathurl = 'file://localhost/tmp/SEQ001_HSNI_003_0020_v001.mov'

        c = Clip()
        c.id = '0020'
        c.start = 35
        c.end = 65
        c.name = 'SEQ001_HSNI_003_0020_v001'
        c.enabled = True
        c.duration = 30
        c.in_ = 0
        c.out = 30
        c.file = f

        t.clips.append(c)

        # clip 3
        f = File()
        f.duration = 45
        f.name = 'SEQ001_HSNI_003_0030_v001'
        f.pathurl = 'file://localhost/tmp/SEQ001_HSNI_003_0030_v001.mov'

        c = Clip()
        c.id = '0030'
        c.start = 65
        c.end = 110
        c.name = 'SEQ001_HSNI_003_0030_v001'
        c.enabled = True
        c.duration = 45
        c.in_ = 0
        c.out = 45
        c.file = f

        t.clips.append(c)

        expected_xmls = [
            """<?xml version='1.0' encoding='UTF-8'?>
<MetaFuze_BatchTranscode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="MetaFuzeBatchTranscode.xsd">
   <Configuration>
      <Local>8</Local>
      <Remote>8</Remote>
   </Configuration>
   <Group>
      <FileList>
         <File>\\tmp\\SEQ001_HSNI_003_0010_v001.mov</File>
      </FileList>
      <Transcode>
         <Version>1.0</Version>
         <File>\\tmp\\SEQ001_HSNI_003_0010_v001.mxf</File>
         <ClipName>SEQ001_HSNI_003_0010_v001</ClipName>
         <ProjectName>SEQ001_HSNI_003</ProjectName>
         <TapeName>SEQ001_HSNI_003_0010_v001</TapeName>
         <TC_Start>00:00:00:00</TC_Start>
         <DropFrame>false</DropFrame>
         <EdgeTC>** TimeCode N/A **</EdgeTC>
         <FilmType>35.4</FilmType>
         <KN_Start>AAAAAAAA-0000+00</KN_Start>
         <Frames>33</Frames>
         <Width>1024</Width>
         <Height>778</Height>
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
</MetaFuze_BatchTranscode>""",
            """<?xml version='1.0' encoding='UTF-8'?>
<MetaFuze_BatchTranscode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="MetaFuzeBatchTranscode.xsd">
   <Configuration>
      <Local>8</Local>
      <Remote>8</Remote>
   </Configuration>
   <Group>
      <FileList>
         <File>\\tmp\\SEQ001_HSNI_003_0020_v001.mov</File>
      </FileList>
      <Transcode>
         <Version>1.0</Version>
         <File>\\tmp\\SEQ001_HSNI_003_0020_v001.mxf</File>
         <ClipName>SEQ001_HSNI_003_0020_v001</ClipName>
         <ProjectName>SEQ001_HSNI_003</ProjectName>
         <TapeName>SEQ001_HSNI_003_0020_v001</TapeName>
         <TC_Start>00:00:00:00</TC_Start>
         <DropFrame>false</DropFrame>
         <EdgeTC>** TimeCode N/A **</EdgeTC>
         <FilmType>35.4</FilmType>
         <KN_Start>AAAAAAAA-0000+00</KN_Start>
         <Frames>29</Frames>
         <Width>1024</Width>
         <Height>778</Height>
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
</MetaFuze_BatchTranscode>""",
            """<?xml version='1.0' encoding='UTF-8'?>
<MetaFuze_BatchTranscode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="MetaFuzeBatchTranscode.xsd">
   <Configuration>
      <Local>8</Local>
      <Remote>8</Remote>
   </Configuration>
   <Group>
      <FileList>
         <File>\\tmp\\SEQ001_HSNI_003_0030_v001.mov</File>
      </FileList>
      <Transcode>
         <Version>1.0</Version>
         <File>\\tmp\\SEQ001_HSNI_003_0030_v001.mxf</File>
         <ClipName>SEQ001_HSNI_003_0030_v001</ClipName>
         <ProjectName>SEQ001_HSNI_003</ProjectName>
         <TapeName>SEQ001_HSNI_003_0030_v001</TapeName>
         <TC_Start>00:00:00:00</TC_Start>
         <DropFrame>false</DropFrame>
         <EdgeTC>** TimeCode N/A **</EdgeTC>
         <FilmType>35.4</FilmType>
         <KN_Start>AAAAAAAA-0000+00</KN_Start>
         <Frames>44</Frames>
         <Width>1024</Width>
         <Height>778</Height>
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
</MetaFuze_BatchTranscode>""",
        ]

        result = s.to_metafuze_xml()

        self.maxDiff = None
        self.assertEqual(
            expected_xmls[0],
            result[0]
        )
        self.assertEqual(
            expected_xmls[1],
            result[1]
        )
        self.assertEqual(
            expected_xmls[2],
            result[2]
        )
