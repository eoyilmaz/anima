# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import unittest2
from anima.previs import Media, Video, Track, Clip, File


class MediaTestCase(unittest2.TestCase):
    """tests the anima.previs.Media class
    """

    def test_to_xml_method_is_working_properly(self):
        """testing if the to xml method is working properly
        """
        m = Media()

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
            """<media>
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
</media>"""

        self.assertEqual(
            expected_xml,
            m.to_xml()
        )
