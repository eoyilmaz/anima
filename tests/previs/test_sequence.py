# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
from edl import List, Event
import unittest2
from anima.previs import Sequence, Media, Video, Track, Clip, File


class MediaTestCase(unittest2.TestCase):
    """tests the anima.previs.Media class
    """

    def test_to_xml_method_is_working_properly(self):
        """testing if the to xml method is working properly
        """
        s = Sequence()
        s.duration = 109.0
        s.name = 'previs_edit_v001'
        s.ntsc = False
        s.timebase = 24
        s.timecode = '00:00:00:00'

        m = Media()
        s.media = m

        v = Video()
        v.width = 1024
        v.height = 778
        m.video.append(v)

        t = Track()
        t.enabled = True
        t.locked = False

        v.tracks.append(t)

        # clip 1
        f = File()
        f.duration = 34.0
        f.name = 'shot2'
        f.pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot2.mov'

        c = Clip()
        c.id = 'shot2'
        c.start = 1.0
        c.end = 35.0
        c.name = 'shot2'
        c.enabled = True
        c.duration = 34.0
        c.in_ = 0.0
        c.out = 34.0
        c.file = f

        t.clips.append(c)

        # clip 2
        f = File()
        f.duration = 30.0
        f.name = 'shot'
        f.pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot.mov'

        c = Clip()
        c.id = 'shot'
        c.start = 35.0
        c.end = 65.0
        c.name = 'shot'
        c.enabled = True
        c.duration = 30.0
        c.in_ = 0.0
        c.out = 30.0
        c.file = f

        t.clips.append(c)

        # clip 3
        f = File()
        f.duration = 45.0
        f.name = 'shot1'
        f.pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot1.mov'

        c = Clip()
        c.id = 'shot1'
        c.start = 65.0
        c.end = 110.0
        c.name = 'shot1'
        c.enabled = True
        c.duration = 45.0
        c.in_ = 0.0
        c.out = 45.0
        c.file = f

        t.clips.append(c)

        expected_xml = \
            """<sequence>
  <duration>109.0</duration>
  <name>previs_edit_v001</name>
  <rate>
    <ntsc>FALSE</ntsc>
    <timebase>24</timebase>
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
          <end>35.0</end>
          <name>shot2</name>
          <enabled>True</enabled>
          <start>1.0</start>
          <in>0.0</in>
          <duration>34.0</duration>
          <out>34.0</out>
          <file>
            <duration>34.0</duration>
            <name>shot2</name>
            <pathurl>file:///home/eoyilmaz/maya/projects/default/data/shot2.mov</pathurl>
          </file>
        </clipitem>
        <clipitem id="shot">
          <end>65.0</end>
          <name>shot</name>
          <enabled>True</enabled>
          <start>35.0</start>
          <in>0.0</in>
          <duration>30.0</duration>
          <out>30.0</out>
          <file>
            <duration>30.0</duration>
            <name>shot</name>
            <pathurl>file:///home/eoyilmaz/maya/projects/default/data/shot.mov</pathurl>
          </file>
        </clipitem>
        <clipitem id="shot1">
          <end>110.0</end>
          <name>shot1</name>
          <enabled>True</enabled>
          <start>65.0</start>
          <in>0.0</in>
          <duration>45.0</duration>
          <out>45.0</out>
          <file>
            <duration>45.0</duration>
            <name>shot1</name>
            <pathurl>file:///home/eoyilmaz/maya/projects/default/data/shot1.mov</pathurl>
          </file>
        </clipitem>
      </track>
    </video>
  </media>
</sequence>"""

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
        duration_node.text = '109.0'
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
        end_node.text = '35.0'
        name_node = ElementTree.SubElement(clip_node, 'name')
        name_node.text = 'shot2'
        enabled_node = ElementTree.SubElement(clip_node, 'enabled')
        enabled_node.text = 'True'
        start_node = ElementTree.SubElement(clip_node, 'start')
        start_node.text = '1.0'
        in_node = ElementTree.SubElement(clip_node, 'in')
        in_node.text = '0.0'
        duration_node = ElementTree.SubElement(clip_node, 'duration')
        duration_node.text = '34.0'
        out_node = ElementTree.SubElement(clip_node, 'out')
        out_node.text = '34.0'

        file_node = ElementTree.SubElement(clip_node, 'file')
        duration_node = ElementTree.SubElement(file_node, 'duration')
        duration_node.text = '34.0'
        name_node = ElementTree.SubElement(file_node, 'name')
        name_node.text = 'shot2'
        pathurl_node = ElementTree.SubElement(file_node, 'pathurl')

        pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot2.mov'
        pathurl_node.text = pathurl

        # clip2
        clip_node = ElementTree.SubElement(track_node, 'clipitem',
                                           attrib={'id': 'shot'})
        end_node = ElementTree.SubElement(clip_node, 'end')
        end_node.text = '65.0'
        name_node = ElementTree.SubElement(clip_node, 'name')
        name_node.text = 'shot'
        enabled_node = ElementTree.SubElement(clip_node, 'enabled')
        enabled_node.text = 'True'
        start_node = ElementTree.SubElement(clip_node, 'start')
        start_node.text = '35.0'
        in_node = ElementTree.SubElement(clip_node, 'in')
        in_node.text = '0.0'
        duration_node = ElementTree.SubElement(clip_node, 'duration')
        duration_node.text = '30.0'
        out_node = ElementTree.SubElement(clip_node, 'out')
        out_node.text = '30.0'

        file_node = ElementTree.SubElement(clip_node, 'file')
        duration_node = ElementTree.SubElement(file_node, 'duration')
        duration_node.text = '30.0'
        name_node = ElementTree.SubElement(file_node, 'name')
        name_node.text = 'shot'
        pathurl_node = ElementTree.SubElement(file_node, 'pathurl')

        pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot.mov'
        pathurl_node.text = pathurl

        # clip3
        clip_node = ElementTree.SubElement(track_node, 'clipitem',
                                           attrib={'id': 'shot1'})
        end_node = ElementTree.SubElement(clip_node, 'end')
        end_node.text = '110.0'
        name_node = ElementTree.SubElement(clip_node, 'name')
        name_node.text = 'shot1'
        enabled_node = ElementTree.SubElement(clip_node, 'enabled')
        enabled_node.text = 'True'
        start_node = ElementTree.SubElement(clip_node, 'start')
        start_node.text = '65.0'
        in_node = ElementTree.SubElement(clip_node, 'in')
        in_node.text = '0.0'
        duration_node = ElementTree.SubElement(clip_node, 'duration')
        duration_node.text = '45.0'
        out_node = ElementTree.SubElement(clip_node, 'out')
        out_node.text = '45.0'

        file_node = ElementTree.SubElement(clip_node, 'file')
        duration_node = ElementTree.SubElement(file_node, 'duration')
        duration_node.text = '45.0'
        name_node = ElementTree.SubElement(file_node, 'name')
        name_node.text = 'shot1'
        pathurl_node = ElementTree.SubElement(file_node, 'pathurl')

        pathurl = 'file:///home/eoyilmaz/maya/projects/default/data/shot1.mov'
        pathurl_node.text = pathurl

        s = Sequence()
        s.from_xml(sequence_node)
        self.assertEqual(109.0, s.duration)
        self.assertEqual('previs_edit_v001', s.name)
        self.assertEqual(False, s.ntsc)
        self.assertEqual('24', s.timebase)
        self.assertEqual('00:00:00:00', s.timecode)

        m = s.media

        v = m.video[0]
        self.assertEqual(1024, v.width)
        self.assertEqual(778, v.height)

        t = v.tracks[0]
        self.assertEqual(False, t.locked)
        self.assertEqual(True, t.enabled)

        # clip1
        c = t.clips[0]
        self.assertEqual(35.0, c.end)
        self.assertEqual('shot2', c.name)
        self.assertEqual(True, c.enabled)
        self.assertEqual(1.0, c.start)
        self.assertEqual(0.0, c.in_)
        self.assertEqual(34.0, c.duration)
        self.assertEqual(34.0, c.out)

        f = c.file
        self.assertEqual(34.0, f.duration)
        self.assertEqual('shot2', f.name)
        self.assertEqual(
            'file:///home/eoyilmaz/maya/projects/default/data/shot2.mov',
            f.pathurl
        )

        # clip2
        c = t.clips[1]
        self.assertEqual(65.0, c.end)
        self.assertEqual('shot', c.name)
        self.assertEqual(True, c.enabled)
        self.assertEqual(35.0, c.start)
        self.assertEqual(0.0, c.in_)
        self.assertEqual(30.0, c.duration)
        self.assertEqual(30.0, c.out)

        f = c.file
        self.assertEqual(30.0, f.duration)
        self.assertEqual('shot', f.name)
        self.assertEqual(
            'file:///home/eoyilmaz/maya/projects/default/data/shot.mov',
            f.pathurl
        )

        # clip3
        c = t.clips[2]
        self.assertEqual(110.0, c.end)
        self.assertEqual('shot1', c.name)
        self.assertEqual(True, c.enabled)
        self.assertEqual(65.0, c.start)
        self.assertEqual(0.0, c.in_)
        self.assertEqual(45.0, c.duration)
        self.assertEqual(45.0, c.out)

        f = c.file
        self.assertEqual(45.0, f.duration)
        self.assertEqual('shot1', f.name)
        self.assertEqual(
            'file:///home/eoyilmaz/maya/projects/default/data/shot1.mov',
            f.pathurl
        )

    def test_to_edl_method_will_return_a_List_instance(self):
        """testing if to_edl method will return an edl.List instance
        """
        s = Sequence()
        result = s.to_edl()
        self.assertIsInstance(result, List)

    def test_to_edl_method_is_working_properly(self):
        """testing if the to_edl method will output a proper List object
        """
        # create Sequence instance from XML
        from anima.previs import Sequencer
        sequencer = Sequencer()
        xml_path = os.path.abspath('./test_data/test_v003.xml')
        sequence = sequencer.from_xml(xml_path)

        self.assertIsInstance(sequence, Sequence)

        edl_list = sequence.to_edl()
        self.assertIsInstance(edl_list, List)

        self.assertEqual(
            sequence.name,
            edl_list.title
        )

        # events should be clips
        self.assertEqual(3, len(edl_list.events))

        e1 = edl_list.events[0]
        e2 = edl_list.events[1]
        e3 = edl_list.events[2]

        self.assertIsInstance(e1, Event)
        self.assertIsInstance(e2, Event)
        self.assertIsInstance(e3, Event)

        # check clips
        clips = sequence.media.video[0].tracks[0].clips
        self.assertIsInstance(clips[0], Clip)

        self.assertEqual('000001', e1.num)
        self.assertEqual('shot2', e1.clip_name)
        self.assertEqual('shot2', e1.reel)
        self.assertEqual('V', e1.track)
        self.assertEqual('C', e1.tr_code)
        self.assertEqual('00:00:00:00', e1.src_start_tc)
        self.assertEqual('00:00:01:09', e1.src_end_tc)
        self.assertEqual('00:00:00:00', e1.rec_start_tc)
        self.assertEqual('00:00:01:09', e1.rec_end_tc)
        self.assertEqual('* FROM CLIP NAME: shot2', e1.comments[0])
        self.assertEqual('/home/eoyilmaz/maya/projects/default/data/shot2.mov',
                         e1.source_file)
        self.assertEqual(
            '* SOURCE FILE: /home/eoyilmaz/maya/projects/default/data/'
            'shot2.mov',
            e1.comments[1]
        )

        self.assertEqual('000002', e2.num)
        self.assertEqual('shot', e2.clip_name)
        self.assertEqual('shot', e2.reel)
        self.assertEqual('V', e2.track)
        self.assertEqual('C', e2.tr_code)
        self.assertEqual('00:00:00:00', e2.src_start_tc)
        self.assertEqual('00:00:01:05', e2.src_end_tc)
        self.assertEqual('00:00:01:10', e2.rec_start_tc)
        self.assertEqual('00:00:02:15', e2.rec_end_tc)
        self.assertEqual('/home/eoyilmaz/maya/projects/default/data/shot.mov',
                         e2.source_file)
        self.assertEqual('* FROM CLIP NAME: shot', e2.comments[0])
        self.assertEqual(
            '* SOURCE FILE: /home/eoyilmaz/maya/projects/default/data/'
            'shot.mov',
            e2.comments[1]
        )

        self.assertEqual('000003', e3.num)
        self.assertEqual('shot1', e3.clip_name)
        self.assertEqual('shot1', e3.reel)
        self.assertEqual('V', e3.track)
        self.assertEqual('C', e3.tr_code)
        self.assertEqual('00:00:00:00', e3.src_start_tc)
        self.assertEqual('00:00:01:20', e3.src_end_tc)
        self.assertEqual('00:00:02:16', e3.rec_start_tc)
        self.assertEqual('00:00:04:12', e3.rec_end_tc)
        self.assertEqual('/home/eoyilmaz/maya/projects/default/data/shot1.mov',
                         e3.source_file)
        self.assertEqual('* FROM CLIP NAME: shot1', e3.comments[0])
        self.assertEqual(
            '* SOURCE FILE: /home/eoyilmaz/maya/projects/default/data/'
            'shot1.mov',
            e3.comments[1]
        )

