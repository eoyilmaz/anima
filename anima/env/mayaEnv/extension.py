# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import subprocess
import tempfile
import platform
from contextlib import contextmanager

import pymel.core as pm
from pymel.core.uitypes import CheckBox, TextField
from pymel.core.general import Attribute
from pymel.core.system import FileReference

from anima.edit import Sequence, Media, Video, Track, Clip, File, Rate
from anima.extension import extends
from anima.repr import Representation


default_handle_count = 15


class MayaExtension(object):
    """Extension to PyMel classes
    """

    @extends(Attribute)
    @property
    def next_available(self):
        """returns the next available attr in a multi attr

        :return: The available index as an attribute
        """
        try:
            indices = self.getArrayIndices()
        except TypeError:
            return self

        available_index = 0

        try:
            for i in xrange(max(indices) + 2):
                if not self[i].connections():
                    available_index = i
                    break
        except ValueError:
            available_index = 0

        return self[available_index]

    @extends(CheckBox)
    def value(self, value=None):
        """returns or set the check box value
        """
        from pymel.core import checkBox
        if value is not None:
            # set the value
            checkBox(self, e=1, v=value)
        else:
            # get the value
            return checkBox(self, q=1, v=1)

    @extends(TextField)
    def text(self, value=None):
        """returns or sets the text field value
        """
        from pymel.core import textField
        if value is not None:
            # set the value
            textField(self, e=1, tx=value)
        else:
            # get the value
            return textField(self, q=1, tx=1)


class FileReferenceExtension(object):
    """Extensions to Maya FileReference node.

    Manages the Referenced different representations in the current scene.

    This class helps converting references to other representations and vice
    versa.
    """

    def path(self):
        """dummy method to let the IDEs find FileReference.path and not
        complain about it.
        """
        return ''

    def replaceWith(self, path):
        """dummy method to let the IDEs find FileReference.replaceWith and not
        complain about it.
        """
        return None

    @extends(FileReference)
    def to_repr(self, repr_name):
        """Replaces the current reference with the representation with the
        given repr_name.

        :param str repr_name: The desired repr name
        :return:
        """
        rep_v = self.find_repr(repr_name)
        from stalker import Repository
        if rep_v is not None and rep_v != self.version:
            self.replaceWith(
                Repository.to_os_independent_path(rep_v.absolute_full_path)
            )

    @extends(FileReference)
    def find_repr(self, repr_name):
        """Finds the representation with the given repr_name.

        :param str repr_name: The desired repr name
        :return: :class:`.Version`
        """
        from anima.env.mayaEnv import Maya
        m = Maya()
        v = m.get_version_from_full_path(self.path)

        if v is None:
            return

        rep = Representation(version=v)
        rep_v = rep.find(repr_name)

        return rep_v

    @extends(FileReference)
    def list_all_repr(self):
        """Returns a list of strings representing all the representation names
        of this FileReference

        :return: list of str
        """
        from anima.env.mayaEnv import Maya
        m = Maya()
        v = m.get_version_from_full_path(self.path)

        if v is None:
            return []

        rep = Representation(version=v)
        return rep.list_all()

    @extends(FileReference)
    def to_base(self):
        """Loads the original version
        """
        self.to_repr(Representation.base_repr_name)

    @extends(FileReference)
    def is_base(self):
        """returns True or False depending to if this is the base
        representation for this reference
        """
        from anima.env.mayaEnv import Maya
        m = Maya()
        v = m.get_version_from_full_path(self.path)

        if v is None:
            return True

        rep = Representation(version=v)
        return rep.is_base()

    @extends(FileReference)
    def has_repr(self, repr_name):
        """checks if the reference has the given representation

        :param str repr_name: The name of the desired representation
        :return:
        """
        from anima.env.mayaEnv import Maya
        m = Maya()
        v = m.get_version_from_full_path(self.path)

        if v is None:
            return False

        rep = Representation(version=v)
        return rep.has_repr(repr_name)

    @extends(FileReference)
    def is_repr(self, repr_name):
        """returns True or False depending to if this is the requested repr

        :param str repr_name: The representation name
        :return:
        """
        from anima.env.mayaEnv import Maya
        m = Maya()
        v = m.get_version_from_full_path(self.path)

        if v is None:
            return False

        rep = Representation(version=v)
        return rep.is_repr(repr_name=repr_name)

    @extends(FileReference)
    @property
    def repr(self):
        """the representation name of the related version
        """
        from anima.env.mayaEnv import Maya
        m = Maya()
        v = m.get_version_from_full_path(self.path)

        if v is None:
            return None

        rep = Representation(version=v)
        return rep.repr

    @extends(FileReference)
    def get_base(self):
        """returns the base version instance
        """
        from anima.env.mayaEnv import Maya
        m = Maya()
        v = m.get_version_from_full_path(self.path)

        if v is None:
            return True

        rep = Representation(version=v)
        return rep.find(rep.base_repr_name)

    @extends(FileReference)
    @property
    def version(self):
        """returns the Stalker Version instance related to this reference
        """
        from anima.env.mayaEnv import Maya
        m = Maya()
        return m.get_version_from_full_path(self.path)


class SequenceManagerExtension(object):
    """Extension to the pm.nodetypes.SequenceManager class
    """

    @extends(pm.nodetypes.SequenceManager)
    def get_shot_name_template(self):
        """returns teh shot_name_template_ attribute value, creates the
        attribute if missing
        """
        if not self.hasAttr('shot_name_template'):
            default_template = '<Sequence>_<Shot>_<Version>'
            self.set_shot_name_template(default_template)

        return self.shot_name_template.get()

    @extends(pm.nodetypes.SequenceManager)
    def set_shot_name_template(self, template):
        """sets the shot_name_template attribute value
        """
        if not self.hasAttr('shot_name_template'):
            self.addAttr('shot_name_template', dt='string')

        self.shot_name_template.set(template)

    @extends(pm.nodetypes.SequenceManager)
    def get_version(self):
        """returns the version attribute value, creates the attribute if
        missing
        """
        if not self.hasAttr('version'):
            self.set_version('')
        return self.version.get()

    @extends(pm.nodetypes.SequenceManager)
    def set_version(self, template):
        """sets the version attribute value
        """
        if not self.hasAttr('version'):
            self.addAttr('version', dt='string')

        self.version.set(template)

    @extends(pm.nodetypes.SequenceManager)
    def create_sequence(self, name=None):
        """Creates a new sequence

        :return: pm.nodetypes.Sequence
        """
        sequencer = pm.createNode('sequencer')
        if name:
            sequencer.set_sequence_name(name)

        sequencer.message >> self.sequences.next_available
        return sequencer

    @extends(pm.nodetypes.SequenceManager)
    def from_seq(self, seq):
        """Generates maya shots and sequencers with the given
        :class:`anima.previs.Sequence` instance.

        This method is designed to mainly be used with :method:`.from_xml`
        and :method:`.from_edl` methods. It generates new shots or updates them
        by looking at the given :class:`anima.previs.Sequence` instance.

        :param seq: An :class:`anima.previs.Sequence` instance
        :return:
        """
        # now create or update structure
        # create first
        # generate the shot name template first
        shot_name_template = self.get_shot_name_template()
        # get current sequencer
        seqs = self.sequences.get()
        if seqs:
            # we probably need to update shots
            seq1 = seqs[0]

            # update shots
            shots = seq1.shots.get()

            # collect clips
            all_clips = [clip
                         for track in seq.media.video.tracks
                         for clip in track.clips]

            deleted_shots = []
            used_shots = []

            # for each shot sets the anchor point in a temp variable
            for shot in shots:
                shot.anchor = shot.startFrame.get()

            # find the corresponding shots in seq
            for clip in all_clips:
                #is_deleted = True
                for shot in shots:
                    if clip.id.lower() == shot.full_shot_name.lower():

                        # update with the given clip info
                        # anchor = shot.startFrame.get()
                        handle = shot.handle.get()
                        track = shot.track.get()

                        if shot in used_shots:
                            # this shot has been used once so duplicate it
                            # before doing anything
                            dup_shot = seq1.create_shot(shot.shotName.get())
                            dup_shot.startFrame.set(shot.startFrame.get())
                            dup_shot.endFrame.set(shot.endFrame.get())
                            dup_shot.handle.set(shot.handle.get())
                            dup_shot.sequenceStartFrame.set(
                                shot.sequenceStartFrame.get()
                            )
                            # do not copy sequenceEndFrame
                            # copy camera
                            dup_shot.set_camera(shot.get_camera())
                            dup_shot.anchor = shot.anchor
                            shot = dup_shot

                        start_frame = clip.in_ - handle + shot.anchor
                        end_frame = clip.out - clip.in_ + start_frame - 1

                        # print '-------------------------------'
                        # print 'clip.in     : %s' % clip.in_
                        # print 'clip.out    : %s' % clip.out
                        # print 'clip.start  : %s' % clip.start
                        # print 'clip.end    : %s' % clip.end
                        # print 'start_frame : %s' % start_frame
                        # print 'end_frame   : %s' % end_frame

                        sequence_start = clip.start

                        shot.startFrame.set(start_frame)
                        shot.endFrame.set(end_frame)

                        shot.sequenceStartFrame.set(sequence_start)

                        # set original track
                        shot.track.set(track)

                        used_shots.append(shot)
                        break

            for shot in seq1.shots.get():
                if shot not in used_shots:
                    deleted_shots.append(shot)

            # delete shots
            pm.delete(deleted_shots)

        else:
            # create sequencer
            seq1 = self.create_sequence(seq.name)

            # create shots
            media = seq.media
            for i, track in enumerate(media.video.tracks):
                for clip in track.clips:
                    # clip.id is something like SEQ001_HSNI_010_0010_v046
                    # filter the shot name
                    shot_name = clip.id.split('_')[-2]
                    shot = seq1.create_shot(shot_name)

                    shot.startFrame.set(clip.in_)
                    shot.endFrame.set(clip.out - 1)
                    shot.sequenceStartFrame.set(clip.start)
                    shot.handle.set(0)
                    if clip.file:
                        f = clip.file
                        pathurl = f.pathurl.replace('file://localhost/', '')
                        if ':' not in pathurl:  # not windows, keep '/'
                            pathurl = '/%s' % pathurl
                        shot.output.set(pathurl)

                    shot.track.set(i + 1)

    @extends(pm.nodetypes.SequenceManager)
    def from_xml(self, path):
        """Parses XML file and returns a Sequence instance which reflects the
        whole time line hierarchy.

        :param path: The path of the XML file
        :return: :class:`.Sequence`
        """
        if not isinstance(path, str):
            raise TypeError(
                'path argument in %s.from_xml should be a string, not %s' %
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

        seq.from_xml(xml_seq)

        self.from_seq(seq)

    @extends(pm.nodetypes.SequenceManager)
    def from_edl(self, path):
        """Parses EDL file and returns a Sequence instance which reflects the
        whole time line hierarchy.

        :param path: The path of the XML file
        :return: :class:`.Sequence`
        """
        if not isinstance(path, str):
            raise TypeError(
                'path argument in %s.from_edl should be a string, not %s' %
                (self.__class__.__name__, path.__class__.__name__)
            )

        from anima.env.mayaEnv import Maya
        m = Maya()
        fps = m.get_fps()

        import edl
        p = edl.Parser(str(fps))
        with open(path) as f:
            l = p.parse(f)

        seq = Sequence()
        seq.from_edl(l)

        self.from_seq(seq)

    @extends(pm.nodetypes.SequenceManager)
    def to_xml(self, indentation=2, pre_indent=0):
        """Generates an FCP compatible XML file at given path.

        :return:
        """
        seq = self.generate_sequence_structure()

        rendered_template = ''
        if seq:
            rendered_template = seq.to_xml(
                indentation=indentation,
                pre_indent=indentation + pre_indent
            )
        return rendered_template

    @extends(pm.nodetypes.SequenceManager)
    def generate_sequence_structure(self):
        """Generates a Sequence structure suitable for XML<->EDL conversion

        :return: Sequence
        """
        import timecode
        from anima.env.mayaEnv import Maya

        m = Maya()
        fps = m.get_fps()

        # export only the first sequence, ignore others
        sequencers = self.sequences.get()
        if len(sequencers) == 0:
            return None

        sequencer = sequencers[0]
        time = pm.PyNode('time1')

        seq = Sequence()
        seq.name = str(sequencer.get_sequence_name())

        seq.rate = Rate(timebase=str(fps), ntsc=False)
        seq.timecode = str(timecode.Timecode(
            framerate=seq.rate.timebase,
            frames=time.timecodeProductionStart.get() + 1
        ))
        seq.duration = sequencer.duration

        media = Media()
        video = Video()
        media.video = video

        for shot in sequencer.shots.get():
            clip = Clip()
            clip.id = str(shot.full_shot_name)
            clip.name = str(shot.full_shot_name)
            clip.duration = shot.duration + 2 * shot.handle.get()
            clip.enabled = True
            clip.start = shot.sequenceStartFrame.get()
            clip.end = shot.sequenceEndFrame.get() + 1
            # clips always start from 0 and includes the shot handle
            clip.in_ = shot.handle.get()  # handle at start
            clip.out = shot.handle.get() + shot.duration  # handle at end
            clip.type = 'Video'  # always video for now

            f = File()
            f.name = os.path.splitext(
                os.path.basename(str(shot.output.get()))
            )[0]

            f.duration = shot.duration + 2 * shot.handle.get()

            f.pathurl = str('file://localhost/%s' % shot.output.get())

            clip.file = f

            track_number = shot.track.get() - 1  # tracks should start from 0
            try:
                track = video.tracks[track_number]
            except IndexError:
                track = Track()
                video.tracks.append(track)

            track.clips.append(clip)
            # set video resolution
            video.width = shot.wResolution.get()
            video.height = shot.hResolution.get()

        seq.media = media
        return seq

    @extends(pm.nodetypes.SequenceManager)
    def to_edl(self):
        """Generates an EDL file out of the edit
        """
        seq = self.generate_sequence_structure()
        l = seq.to_edl()
        return l


class SequencerExtension(object):
    """The sequence instance.

    It is a manager that manages shot data. It is kind of the reflection of the
    Maya Sequencer instance.

    It is able to get Maya editorial XML and convert it to EDL.
    """

    @extends(pm.nodetypes.Sequencer)
    @property
    def manager(self):
        """returns the SequenceManager instance that this sequence is connected
        to
        """
        return pm.ls(self.connections(), type='sequenceManager')[0]

    @extends(pm.nodetypes.Sequencer)
    def get_sequence_name(self):
        """Gets the sequence_name attribute value, creates the attribute if it
        is missing
        """
        if not self.hasAttr('sequence_name'):
            self.set_sequence_name('')
        return self.sequence_name.get()

    @extends(pm.nodetypes.Sequencer)
    def set_sequence_name(self, name):
        """Sets the sequence name for this Sequencer

        :param name: A str holding the desired name of the sequence.
        :return: None
        """
        if not self.hasAttr('sequence_name'):
            self.addAttr('sequence_name', dt='string')
        self.sequence_name.set(name)

    @extends(pm.nodetypes.Sequencer)
    @property
    def all_shots(self):
        """return all the shots connected to this sequencer
        """
        return pm.ls(self.shots.get(), typ='shot')

    # @extends(pm.nodetypes.Sequencer)
    # @all_shots.setter
    # def all_shots(self, shots):
    #     """setter for the all_shots property
    #     """
    #     # remove the current shots first
    #     # then append the new ones
    #     for s in self.all_shots:
    #         t = s // self.shots
    #
    #     for s in shots:
    #         t = s.message >> self.shots.next_available

    @extends(pm.nodetypes.Sequencer)
    def add_shot(self, shot):
        """Adds the given shot to the current sequencer

        :param shot: a pm.nodetypes.Shot instance
        :return: None
        """
        # add the given shot to the list
        if not shot.hasAttr('handle'):
            shot.set_handle(handle=default_handle_count)

        # connect to the sequencer
        # remove it from other sequences
        for attr in shot.message.outputs(p=1):
            if isinstance(attr.node(), pm.nodetypes.Sequencer):
                shot.message // attr

        shot.message >> self.shots.next_available

    @extends(pm.nodetypes.Sequencer)
    def set_shot_handles(self, handle=default_handle_count):
        """Set shot handles

        :param int handle: An integer value for handle
        :return:
        """
        # validate arguments
        # shots
        for shot in self.all_shots:
            shot.set_handle(handle)

    @extends(pm.nodetypes.Sequencer)
    def mute_shots(self):
        """mutes all shots connected to this sequencer
        """
        for shot in self.all_shots:
            shot.mute()

    @extends(pm.nodetypes.Sequencer)
    def unmute_shots(self):
        """unmutes all shots connected to this sequencer
        """
        for shot in self.all_shots:
            shot.unmute()

    def create_sequencer_attributes(self):
        """Creates the necessary extra attributes for the sequencer in the
        current scene.

        Add attributes like:
            sequenceName
            shotNameTemplate
            defaultHandle
        """
        raise NotImplementedError()

    def set_shot_names(self, sequence_name, padding=4, increment=10,
                       template='%(sequence_name)s_%(shot_name)_%(version_number)03d'):
        """Sets all shot names according to the given template.

        :param sequence_name: The sequence name
        :param padding: Shot number padding
        :param increment: Shot number increment
        :param template: The final shot name template
        :return:
        """
        raise NotImplementedError()

    @extends(pm.nodetypes.Sequencer)
    def create_shot(self, name='', handle=default_handle_count):
        """Creates a new shot.

        :param str name: A string value for the newly created shot name, if
          skipped or given empty, the next empty shot name will be generated.
        :param int handle: An integer value for the handle attribute. Default
          is 10.
        :returns: The created :class:`~pm.nt.Shot` instance
        """
        shot = pm.createNode('shot')
        shot.shotName.set(name)
        shot.set_handle(handle=handle)
        shot.set_output('')

        # connect to the sequencer
        shot.message >> self.shots.next_available
        return shot

    @extends(pm.nodetypes.Sequencer)
    def create_shot_playblasts(self, output_path, show_ornaments=True):
        """creates the selected shot playblasts
        """
        movie_files = []
        for shot in self.all_shots:
            movie_files.append(
                shot.playblast(
                    options={'showOrnaments': show_ornaments}
                )
            )
        return movie_files

    @extends(pm.nodetypes.Sequencer)
    def to_edl(self, seq):
        """returns an EDL for the given sequence

        :param seq: A :class:`.Sequence` instance
        """
        return seq.to_edl()

    @extends(pm.nodetypes.Sequencer)
    def metafuze(self):
        """Calls "Avid Metafuze" with the given xml content to convert media
        files to MXF format.

        :return: list of file path
        """

        sm = pm.PyNode('sequenceManager1')
        seq = sm.generate_sequence_structure()
        xmls = seq.to_metafuze_xml()

        # write the given content to tmp
        for i, xml in enumerate(xmls):
            temp_file_path = tempfile.mktemp(suffix='.xml')
            yield i
            with open(temp_file_path, 'w') as f:
                f.write(xml)

            subprocess.call(
                ['metafuze',
                 '-debug',
                 temp_file_path],
                #stderr=subprocess.PIPE,
                shell=True
            )

            # remove the temp file
            #os.remove(temp_file_path)
            #print 'xml path: %s' % temp_file_path

        #if return_code:
        #    # there is an error
        #    raise RuntimeError("Something went wrong in MXF conversion")

    @extends(pm.nodetypes.Sequencer)
    def convert_to_mxf(self, path):
        """converts the given video at given path to Avid MXF DNxHD 36.

        :param path: The path of the media file
        :return: returns the generated mxf file location
        """
        raise NotImplementedError()

    @extends(pm.nodetypes.Sequencer)
    @property
    def duration(self):
        """returns the duration of this sequence
        """
        return self.maxFrame.get() - self.minFrame.get() + 1


class ShotExtension(object):
    """extensions to pm.nodetypes.Shot class
    """

    @extends(pm.nodetypes.Shot)
    def get_camera(self):
        """returns the shot camera

        :return:
        """
        return pm.PyNode(pm.shot(self, q=1, currentCamera=1))

    @extends(pm.nodetypes.Shot)
    def set_camera(self, camera):
        """sets the shot camera

        :param camera: pm.Camera instance or a string
        :return:
        """
        pm.shot(self, e=1, currentCamera=camera)

    @extends(pm.nodetypes.Shot)
    def get_output(self):
        """Gets the output attribute value of this shot, creates the attribute
        if it is missing
        """
        if not self.hasAttr('output'):
            self.set_output('')
        return self.output.get()

    @extends(pm.nodetypes.Shot)
    def set_output(self, output):
        """Sets the output of this shot. The output is generally a movie file
        automatically created by calling shot.playblast() method.

        :param str output: A string value showing the path of this shots
          output.
        :return:
        """
        if not self.hasAttr('output'):
            self.addAttr('output', dt='string')
        self.output.set(output)

    @extends(pm.nodetypes.Shot)
    def mute(self):
        """Mutes the current shot

        :return:
        """
        pm.shot(self, e=1, mute=True)

    @extends(pm.nodetypes.Shot)
    def unmute(self):
        """Unmutes the current shot.

        :return:
        """
        pm.shot(self, e=1, mute=False)

    @extends(pm.nodetypes.Shot)
    @property
    def sequence(self):
        """returns the current sequencer
        """
        return self.message.get()

    @extends(pm.nodetypes.Shot)
    @property
    @contextmanager
    def include_handles(self):
        """includes the handle values to the shot range, primarily done for
        taking playblasts with handles
        """
        try:
            handle = self.handle.get()
        except AttributeError:
            # no handle is created probably the shot setup has not been done
            # correctly
            self.set_handle()
            handle = self.handle.get()

        track = self.track.get()
        self.startFrame.set(
            self.startFrame.get() - handle
        )
        self.endFrame.set(
            self.endFrame.get() + handle
        )
        self.sequenceStartFrame.set(
            self.sequenceStartFrame.get() - handle
        )
        try:
            yield None
        finally:
            self.startFrame.set(
                self.startFrame.get() + handle
            )
            self.endFrame.set(
                self.endFrame.get() - handle
            )
            self.sequenceStartFrame.set(
                self.sequenceStartFrame.get() + handle
            )
            self.track.set(track)

    @extends(pm.nodetypes.Shot)
    def playblast(self, options=None):
        """creates the selected shot playblasts
        """
        # template vars
        sequence = self.sequence

        try:
            handle = self.handle.get()
        except AttributeError:
            # no handle is created probably the shot setup has not been done
            # correctly
            self.set_handle()
            handle = self.handle.get()

        start_frame = self.sequenceStartFrame.get() - handle
        end_frame = self.sequenceEndFrame.get() + handle
        width = self.wResolution.get()
        height = self.hResolution.get()

        extra_frame = 0

        if platform.system() == 'Windows':
            # windows Maya version drops 1 frame from end where as Linux
            # doesn't do that
            extra_frame = 1

        # store track
        track = self.track.get()

        movie_full_path = os.path.join(
            tempfile.gettempdir(),
            '%s.mov' % self.full_shot_name
        ).replace('\\', '/')

        # set the output of this shot
        self.set_output(movie_full_path)

        # mute all other shots
        sequence.mute_shots()
        self.unmute()

        default_options = {
            'fmt': 'qt',
            'sequenceTime': 1,
            'forceOverwrite': 1,
            'clearCache': 1,
            'showOrnaments': 1,
            'percent': 50,
            'offScreen': 1,
            'viewer': 0,
            'compression': 'MPEG-4 Video',
            'quality': 85,
            'startTime': start_frame,
            'endTime': end_frame + extra_frame,
            'filename': movie_full_path,
            'wh': [width, height],
            'useTraxSounds': True,
        }

        if options:
            # offset end time by one frame if t his is windows
            if 'endTime' in options:
                options['endTime'] += extra_frame
            default_options.update(options)

        # include handles
        with self.include_handles:
            pm.system.dgdirty(a=True)

            # if a sound node is specified remove useTraxSounds flag
            import pprint
            pprint.pprint(default_options)

            result = pm.playblast(**default_options)
            sequence.unmute_shots()

        # restore track
        self.track.set(track)

        return result

    @extends(pm.nodetypes.Shot)
    def convert_to_mxf(self, metafuze_xml):
        """converts a video with the given Metafuze XML to Avid MXF format.

        :return: returns the generated mxf file location
        """
        pass

    @extends(pm.nodetypes.Shot)
    def set_handle(self, handle=default_handle_count):
        """Creates handle attribute to given shot instance

        :param int handle: An integer value for handle
        :return:
        """
        if not isinstance(handle, int):
            raise TypeError(
                '"handle" argument in %(class)s.set_handle() should be '
                'a non negative integer, not %(handle_class)s' %
                {
                    'class': self.__class__.__name__,
                    'handle_class': handle.__class__.__name__
                }
            )

        if handle < 0:
            raise ValueError(
                '"handle" argument in %(class)s.set_handle() should be '
                'a non negative integer, not %(handle)s' %
                {
                    'class': self.__class__.__name__,
                    'handle': handle
                }
            )

        # create "handle" attribute in each shot and set the value
        try:
            self.addAttr('handle', at='short', k=False, min=0)
        except RuntimeError:
            # attribute is already there
            pass
        self.setAttr('handle', handle)

    @extends(pm.nodetypes.Shot)
    @property
    def duration(self):
        """returns the shot duration
        """
        return self.sequenceEndFrame.get() - self.sequenceStartFrame.get() + 1

    def add_frames_to_start(self, shot, frame_count=0):
        """Adds extra frames to the given shots start, and offsets all the
        following shots with the given frame_count.

        :param shot: A :class:`~pm.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    def add_frames_to_end(self, shot, frame_count=0):
        """Adds extra frames to the given shot, and offsets all the following
        shots with the given frame_count.

        :param shot: A :class:`~pm.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    def remove_frames_from_start(self, shot, frame_count=0):
        """Removes frames from the given shots beginning, and offsets all the
        following shots back with the given frame_count.

        :param shot: A :class:`~pm.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    def remove_frames_from_end(self, shot, frame_count=0):
        """Removes frames from the given shots end, and offsets all the
        following shots back with the given frame_count.

        :param shot: A :class:`~pm.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    @extends(pm.nodetypes.Shot)
    @property
    def full_shot_name(self):
        """returns the full shot name
        """
        seq = self.sequence
        sm = seq.manager
        camera = self.currentCamera.get()
        version = sm.get_version()
        template = sm.get_shot_name_template()

        # replace template variables
        template = template\
            .replace('<Sequence>', '%(sequence)s')\
            .replace('<Shot>', '%(shot)s')\
            .replace('<Version>', '%(version)s')\
            .replace('<Camera>', '%(camera)s')

        rendered_template = template % {
            'shot': self.shotName.get(),
            'sequence': seq.sequence_name.get(),
            'version': version,
            'camera': camera.name() if camera else None
        }

        return rendered_template
