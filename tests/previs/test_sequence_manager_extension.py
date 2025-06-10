import os

import pytest

# prepare for test
os.environ["ANIMA_TEST_SETUP"] = ""
from anima.dcc import maya  # to setup maya extensions

import pymel.core
from anima.edit import Sequence, Media, Video, Track, Clip, File


@pytest.fixture(scope="module", autoouse=True)
def prepare_maya(self):
    """Set up the test."""
    # create a new scene and get the sequenceManager in the scene
    pymel.core.newFile(force=True)
    self.sm = pymel.core.PyNode("sequenceManager1")


def test_from_xml_path_argument_skipped(self):
    """TypeError will be raised when the path argument is skipped."""
    sm = pymel.core.PyNode("sequenceManager1")
    with pytest.raises(TypeError) as cm:
        sm.from_xml()

    assert str(cm.value) == "from_xml() takes exactly 2 arguments (1 given)"


def test_from_xml_path_argument_is_not_a_string(self):
    """TypeError will be raised when the path argument is not a string."""
    sm = pymel.core.PyNode("sequenceManager1")
    with pytest.raises(TypeError) as cm:
        sm.from_xml(30)

    assert str(cm.value) == (
        "path argument in SequenceManager.from_xml should be a string, not int"
    )


def test_from_xml_path_argument_is_not_a_valid_path(self):
    """IOError will be raised when the path argument is not a valid path."""
    sm = pymel.core.PyNode("sequenceManager1")
    with pytest.raises(IOError) as cm:
        sm.from_xml("not a valid path")

    assert str(cm.value) == "Please supply a valid path to an XML file!"


def test_from_xml_generates_correct_sequencer_hierarchy(self):
    """from_xml method will generate Sequences and shots correctly."""
    path = os.path.abspath("./test_data/test_v001.xml")

    sm = pymel.core.PyNode("sequenceManager1")
    sm.from_xml(path)

    sequences = sm.sequences.get()
    assert len(sequences) == 1

    sequencer = sequences[0]
    assert isinstance(sequencer, pymel.core.nt.Sequencer)

    assert sequencer.duration == 111
    assert sequencer.sequence_name.get() == "SEQ001_HSNI_003"

    # check scene fps
    assert pymel.core.currentUnit(q=1, t=1) == "film"

    # check timecode
    time = pymel.core.PyNode("time1")
    assert time.timecodeProductionStart.get() == 0.0

    shots = sequencer.shots.get()
    assert len(shots) == 3

    shot1 = shots[0]
    shot2 = shots[1]
    shot3 = shots[2]

    assert "0010" == shot1.shotName.get()
    assert 1024 == shot1.wResolution.get()
    assert 778 == shot1.hResolution.get()
    assert 1 == shot1.track.get()
    assert 1.0 == shot1.sequenceStartFrame.get()
    assert 34.0 == shot1.sequenceEndFrame.get()
    assert 34.0 == shot1.duration
    assert 10.0 == shot1.startFrame.get()
    assert 43.0 == shot1.endFrame.get()
    assert "/tmp/SEQ001_HSNI_003_0010_v001.mov" == shot1.output.get()

    # Clip2
    assert "0020" == shot2.shotName.get()
    assert 1024 == shot2.wResolution.get()
    assert 778 == shot2.hResolution.get()
    assert 1 == shot2.track.get()
    assert 35.0 == shot2.sequenceStartFrame.get()
    assert 65.0 == shot2.sequenceEndFrame.get()
    assert 31.0 == shot2.duration
    assert 10.0 == shot2.startFrame.get()
    assert 40.0 == shot2.endFrame.get()
    assert "/tmp/SEQ001_HSNI_003_0020_v001.mov" == shot2.output.get()

    # Clip3
    assert "0030" == shot3.shotName.get()
    assert 1024 == shot3.wResolution.get()
    assert 778 == shot3.hResolution.get()
    assert 1 == shot3.track.get()
    assert 66.0 == shot3.sequenceStartFrame.get()
    assert 111.0 == shot3.sequenceEndFrame.get()
    assert 46.0 == shot3.duration
    assert 10.0 == shot3.startFrame.get()
    assert 55.0 == shot3.endFrame.get()
    assert "/tmp/SEQ001_HSNI_003_0030_v001.mov" == shot3.output.get()


def test_from_xml_updates_sequencer_hierarchy_with_shots_expanded_and_contracted(
    self,
):
    """from_xml method will update Sequences and shots correctly with the xml file."""
    path = os.path.abspath("./test_data/test_v002.xml")

    sm = pymel.core.PyNode("sequenceManager1")
    sm.set_revision("r01")
    sm.set_version("v001")
    seq = sm.create_sequence("SEQ001_HSNI_003")

    shot1 = seq.create_shot("0010")
    shot1.startFrame.set(0)
    shot1.endFrame.set(33)
    shot1.sequenceStartFrame.set(1)
    shot1.output.set("/tmp/SEQ001_HSNI_003_0010_r01_v001.mov")
    shot1.handle.set(10)
    shot1.track.set(1)

    shot2 = seq.create_shot("0020")
    shot2.startFrame.set(34)
    shot2.endFrame.set(64)
    shot2.sequenceStartFrame.set(35)
    shot2.output.set("/tmp/SEQ001_HSNI_003_0020_r01_v001.mov")
    shot2.handle.set(10)
    shot2.track.set(1)

    shot3 = seq.create_shot("0030")
    shot3.startFrame.set(65)
    shot3.endFrame.set(110)
    shot3.sequenceStartFrame.set(66)
    shot3.output.set("/tmp/SEQ001_HSNI_003_0030_r01_v001.mov")
    shot3.handle.set(10)
    shot3.track.set(1)

    assert shot1.track.get() == 1
    assert shot2.track.get() == 1
    assert shot3.track.get() == 1

    # now update it with test_v002.xml
    sm.from_xml(path)

    # check shot data
    assert "0010" == shot1.shotName.get()
    assert 1 == shot1.track.get()
    assert 1.0 == shot1.sequenceStartFrame.get()
    assert 54.0 == shot1.sequenceEndFrame.get()
    assert -10.0 == shot1.startFrame.get()
    assert 43.0 == shot1.endFrame.get()

    # Clip2
    assert "0020" == shot2.shotName.get()
    assert 1 == shot2.track.get()
    assert 55.0 == shot2.sequenceStartFrame.get()
    assert 75.0 == shot2.sequenceEndFrame.get()
    assert 44.0 == shot2.startFrame.get()
    assert 64.0 == shot2.endFrame.get()

    # Clip3
    assert "0030" == shot3.shotName.get()
    assert 1 == shot3.track.get()
    assert 76.0 == shot3.sequenceStartFrame.get()
    assert 131.0 == shot3.sequenceEndFrame.get()
    assert 65.0 == shot3.startFrame.get()
    assert 120.0 == shot3.endFrame.get()


def test_from_edl_updates_sequencer_hierarchy_with_shots_expanded_and_contracted(
    self,
):
    """from_edl method will update Sequences and shots correctly with the edl file."""
    path = os.path.abspath("./test_data/test_v002.edl")

    sm = pymel.core.PyNode("sequenceManager1")
    sm.set_revision("r01")
    sm.set_version("v001")
    seq = sm.create_sequence("SEQ001_HSNI_003")

    shot1 = seq.create_shot("0010")
    shot1.startFrame.set(0)
    shot1.endFrame.set(33)
    shot1.sequenceStartFrame.set(1)
    shot1.output.set("/tmp/SEQ001_HSNI_003_0010_r01_v001.mov")
    shot1.handle.set(10)
    shot1.track.set(1)

    shot2 = seq.create_shot("0020")
    shot2.startFrame.set(34)
    shot2.endFrame.set(64)
    shot2.sequenceStartFrame.set(35)
    shot2.output.set("/tmp/SEQ001_HSNI_003_0020_r01_v001.mov")
    shot2.handle.set(10)
    shot2.track.set(1)

    shot3 = seq.create_shot("0030")
    shot3.startFrame.set(65)
    shot3.endFrame.set(110)
    shot3.sequenceStartFrame.set(66)
    shot3.output.set("/tmp/SEQ001_HSNI_003_0030_r01_v001.mov")
    shot3.handle.set(10)
    shot3.track.set(1)

    assert shot1.track.get() == 1
    assert shot2.track.get() == 1
    assert shot3.track.get() == 1

    # now update it with test_v002.xml
    sm.from_edl(path)

    # check shot data
    assert "0010" == shot1.shotName.get()
    assert 1 == shot1.track.get()
    assert 1.0 == shot1.sequenceStartFrame.get()
    assert 54.0 == shot1.sequenceEndFrame.get()
    assert -10.0 == shot1.startFrame.get()
    assert 43.0 == shot1.endFrame.get()

    # Clip2
    assert "0020" == shot2.shotName.get()
    assert 1 == shot2.track.get()
    assert 55.0 == shot2.sequenceStartFrame.get()
    assert 76.0 == shot2.sequenceEndFrame.get()
    assert 44.0 == shot2.startFrame.get()
    assert 65.0 == shot2.endFrame.get()

    # Clip3
    assert "0030" == shot3.shotName.get()
    assert 1 == shot3.track.get()
    assert 77.0 == shot3.sequenceStartFrame.get()
    assert 133.0 == shot3.sequenceEndFrame.get()
    assert 65.0 == shot3.startFrame.get()
    assert 121.0 == shot3.endFrame.get()


def test_from_edl_updates_sequencer_hierarchy_with_shots_used_more_than_one_times(
    self,
):
    """from_edl method will update Sequences and shots correctly with shot are used more than once."""
    path = os.path.abspath("./test_data/test_v004.edl")

    sm = pymel.core.PyNode("sequenceManager1")
    sm.set_revision("r01")
    sm.set_version("v001")
    seq = sm.create_sequence("SEQ001_HSNI_003")

    shot1 = seq.create_shot("0010")
    shot1.startFrame.set(0)
    shot1.endFrame.set(33)
    shot1.sequenceStartFrame.set(1)
    shot1.output.set("/tmp/SEQ001_HSNI_003_0010_r01_v001.mov")
    shot1.handle.set(10)
    shot1.track.set(1)

    shot2 = seq.create_shot("0020")
    shot2.startFrame.set(34)
    shot2.endFrame.set(64)
    shot2.sequenceStartFrame.set(35)
    shot2.output.set("/tmp/SEQ001_HSNI_003_0020_r01_v001.mov")
    shot2.handle.set(10)
    shot2.track.set(1)

    shot3 = seq.create_shot("0030")
    shot3.startFrame.set(65)
    shot3.endFrame.set(110)
    shot3.sequenceStartFrame.set(66)
    shot3.output.set("/tmp/SEQ001_HSNI_003_0030_r01_v001.mov")
    shot3.handle.set(10)
    shot3.track.set(1)

    # set a camera for shot4
    shot3.set_camera("persp")

    assert shot1.track.get() == 1
    assert shot2.track.get() == 1
    assert shot3.track.get() == 1

    # now update it with test_v002.xml
    sm.from_edl(path)

    # check if there are 4 shots
    assert 4 == len(seq.shots.get())

    # check shot data
    assert "0010" == shot1.shotName.get()
    assert 1 == shot1.track.get()
    assert 1.0 == shot1.sequenceStartFrame.get()
    assert 54.0 == shot1.sequenceEndFrame.get()
    assert -10.0 == shot1.startFrame.get()
    assert 43.0 == shot1.endFrame.get()

    # Clip2
    assert "0020" == shot2.shotName.get()
    assert 1 == shot2.track.get()
    assert 55.0 == shot2.sequenceStartFrame.get()
    assert 76.0 == shot2.sequenceEndFrame.get()
    assert 44.0 == shot2.startFrame.get()
    assert 65.0 == shot2.endFrame.get()

    # Clip3
    assert "0030" == shot3.shotName.get()
    assert 1 == shot3.track.get()
    assert 77.0 == shot3.sequenceStartFrame.get()
    assert 133.0 == shot3.sequenceEndFrame.get()
    assert 65.0 == shot3.startFrame.get()
    assert 121.0 == shot3.endFrame.get()

    # Clip4
    # there should be an extra shot
    shot4 = seq.shots.get()[-1]
    assert "0030" == shot4.shotName.get()
    assert 1 == shot4.track.get()
    assert 133.0 == shot4.sequenceStartFrame.get()
    assert 189.0 == shot4.sequenceEndFrame.get()
    assert 65.0 == shot4.startFrame.get()
    assert 121.0 == shot4.endFrame.get()

    # check if their cameras also the same
    assert shot3.get_camera() == shot4.get_camera()


def test_from_xml_updates_sequencer_hierarchy_with_shots_removed(self):
    """from_xml method will update Sequences and shots correctly with the xml file."""
    path = os.path.abspath("./test_data/test_v003.xml")

    sm = pymel.core.PyNode("sequenceManager1")
    sm.set_revision("r01")
    sm.set_version("v001")
    seq = sm.create_sequence("SEQ001_HSNI_003")

    shot1 = seq.create_shot("0010")
    shot1.startFrame.set(0)
    shot1.endFrame.set(33)
    shot1.sequenceStartFrame.set(1)
    shot1.output.set("/tmp/SEQ001_HSNI_003_0010_r01_v001.mov")
    shot1.handle.set(10)
    shot1.track.set(1)

    shot2 = seq.create_shot("0020")
    shot2.startFrame.set(34)
    shot2.endFrame.set(64)
    shot2.sequenceStartFrame.set(35)
    shot2.output.set("/tmp/SEQ001_HSNI_003_0020_r01_v001.mov")
    shot2.handle.set(10)
    shot2.track.set(1)

    shot3 = seq.create_shot("0030")
    shot3.startFrame.set(65)
    shot3.endFrame.set(110)
    shot3.sequenceStartFrame.set(66)
    shot3.output.set("/tmp/SEQ001_HSNI_003_0030_r01_v001.mov")
    shot3.handle.set(10)
    shot3.track.set(1)

    assert shot1.track.get() == 1
    assert shot2.track.get() == 1
    assert shot3.track.get() == 1

    # now update it with test_v002.xml
    sm.from_xml(path)

    # we should have 2 shots only
    assert 2 == len(seq.shots.get())

    # check shot data
    assert "0010" == shot1.shotName.get()
    assert 1 == shot1.track.get()
    assert 1.0 == shot1.sequenceStartFrame.get()
    assert 54.0 == shot1.sequenceEndFrame.get()
    assert -10.0 == shot1.startFrame.get()
    assert 43.0 == shot1.endFrame.get()

    # Clip2
    # removed

    # Clip3
    assert "0030" == shot3.shotName.get()
    assert 1 == shot3.track.get()
    assert 55.0 == shot3.sequenceStartFrame.get()
    assert 110.0 == shot3.sequenceEndFrame.get()
    assert 65.0 == shot3.startFrame.get()
    assert 120.0 == shot3.endFrame.get()


def test_to_xml_will_generate_proper_xml_string(self):
    """a proper xml compatible string will be generated with to_xml() method."""
    path = os.path.abspath("./test_data/test_v001.xml")

    sm = pymel.core.PyNode("sequenceManager1")
    sm.set_shot_name_template("<Sequence>_<Shot>_<Revision>_<Version>")
    sm.set_revision("r01")
    sm.set_version("v001")

    seq1 = sm.create_sequence("SEQ001_HSNI_003")

    shot1 = seq1.create_shot("0010")
    shot1.startFrame.set(0)
    shot1.endFrame.set(33)
    shot1.sequenceStartFrame.set(1)
    shot1.output.set("/tmp/SEQ001_HSNI_003_0010_r01_v001.mov")
    shot1.handle.set(10)
    shot1.track.set(1)

    shot2 = seq1.create_shot("0020")
    shot2.startFrame.set(34)
    shot2.endFrame.set(64)
    shot2.sequenceStartFrame.set(35)
    shot2.output.set("/tmp/SEQ001_HSNI_003_0020_r01_v001.mov")
    shot2.handle.set(10)
    shot2.track.set(1)

    shot3 = seq1.create_shot("0030")
    shot3.startFrame.set(65)
    shot3.endFrame.set(110)
    shot3.sequenceStartFrame.set(66)
    shot3.output.set("/tmp/SEQ001_HSNI_003_0030_r01_v001.mov")
    shot3.handle.set(10)
    shot3.track.set(1)

    assert shot1.track.get() == 1
    assert shot2.track.get() == 1
    assert shot3.track.get() == 1

    result = sm.to_xml()
    with open(path) as f:
        expected = f.read()

    self.maxDiff = None
    assert expected == result


def test_create_sequence_is_working_properly(self):
    """create_sequence is working properly."""
    seq = self.sm.create_sequence()
    assert seq.type() == "sequencer"

    self.maxDiff = None
    assert self.sm == seq.message.connections()[0]


def test_create_sequence_is_properly_setting_the_sequence_name(self):
    """create_sequence is working properly."""
    seq = self.sm.create_sequence("Test Sequence")
    assert "Test Sequence" == seq.sequence_name.get()


def test_to_edl_is_working_properly(self):
    """to_edl method is working properly."""
    import edl

    # create a sequence
    seq1 = self.sm.create_sequence("sequence1")
    seq1.create_shot("shot1")
    seq1.create_shot("shot2")
    seq1.create_shot("shot3")

    l = self.sm.to_edl()
    assert isinstance(l, edl.List)


def test_to_edl_generates_a_proper_edl_content(self):
    """to_edl() generates a proper edl content."""
    edl_path = os.path.abspath("./test_data/test_v001.edl")

    sm = pymel.core.PyNode("sequenceManager1")
    sm.set_revision("r01")
    sm.set_version("v001")

    sm = pymel.core.PyNode("sequenceManager1")
    sm.set_shot_name_template("<Sequence>_<Shot>_<Revision>_<Version>")
    self.set_revision("r01")
    sm.set_version("v001")

    seq1 = sm.create_sequence("SEQ001_HSNI_003")

    shot1 = seq1.create_shot("0010")
    shot1.startFrame.set(0)
    shot1.endFrame.set(33)
    shot1.sequenceStartFrame.set(1)
    shot1.output.set("/tmp/SEQ001_HSNI_003_0010_r01_v001.mov")
    shot1.handle.set(10)
    shot1.track.set(1)

    shot2 = seq1.create_shot("0020")
    shot2.startFrame.set(34)
    shot2.endFrame.set(64)
    shot2.sequenceStartFrame.set(35)
    shot2.output.set("/tmp/SEQ001_HSNI_003_0020_r01_v001.mov")
    shot2.handle.set(10)
    shot2.track.set(1)

    shot3 = seq1.create_shot("0030")
    shot3.startFrame.set(65)
    shot3.endFrame.set(110)
    shot3.sequenceStartFrame.set(66)
    shot3.output.set("/tmp/SEQ001_HSNI_003_0030_r01_v001.mov")
    shot3.handle.set(10)
    shot3.track.set(1)

    assert shot1.track.get() == 1
    assert shot2.track.get() == 1
    assert shot3.track.get() == 1

    l = sm.to_edl()
    result = l.to_string()

    with open(edl_path) as f:
        expected_edl_content = f.read()

    assert expected_edl_content == result


def test_generate_sequence_structure_returns_a_sequence_instance(self):
    """generate_sequence_structure() returns a Sequence instance."""
    sm = pymel.core.PyNode("sequenceManager1")
    seq1 = sm.create_sequence("sequence1")

    shot1 = seq1.create_shot("shot1")
    shot1.output.set("/tmp/shot1.mov")

    shot2 = seq1.create_shot("shot2")
    shot2.output.set("/tmp/shot2.mov")

    result = sm.generate_sequence_structure()
    assert isinstance(result, Sequence)


def test_generate_sequence_structure_generates_sequences_and_shots_with_correct_number_of_tracks(
    self,
):
    """generate_sequence_structure() generates proper sequence structure."""
    path = os.path.abspath("./test_data/test_v001.xml")

    sm = pymel.core.PyNode("sequenceManager1")
    sm.from_xml(path)

    seq1 = sm.sequences.get()[0]
    shots = seq1.shots.get()
    shot1 = shots[0]
    shot2 = shots[1]
    shot3 = shots[2]

    assert shot1.track.get() == 1
    assert shot2.track.get() == 1
    assert shot3.track.get() == 1

    seq = sm.generate_sequence_structure()

    tracks = seq.media.video.tracks
    assert len(tracks) == 1
    track1 = tracks[0]

    clips = track1.clips
    assert len(clips) == 3


def test_set_shot_name_template_is_working_properly(self):
    """set_shot_name_template() is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("shot_name_template") is False
    test_template = "<Sequence>_<Shot>_<Revision>_<Version>"
    sm.set_shot_name_template(test_template)
    assert sm.hasAttr("shot_name_template") is True
    assert sm.shot_name_template.get() == test_template


def test_get_shot_name_template_is_working_properly(self):
    """set_shot_name_template() is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("shot_name_template") is False
    test_template = "<Sequence>_<Shot>_<Revision>_<Version>"
    sm.set_shot_name_template(test_template)
    assert sm.hasAttr("shot_name_template") is True
    assert sm.get_shot_name_template() == test_template


def test_get_shot_name_template_creates_shot_name_template_attr_if_missing(self):
    """set_shot_name_template() creates the shot_name_template attr if missing."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("shot_name_template") is False
    result = sm.get_shot_name_template()
    assert sm.hasAttr("shot_name_template") is True
    assert result == "<Sequence>_<Shot>_<Version>"


def test_set_revision_is_working_properly(self):
    """set_revision() is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("revision") is False
    test_revision = "r01"
    sm.set_revision(test_revision)
    assert sm.hasAttr("revision") is True
    assert sm.revision.get() == test_revision


def test_get_revision_is_working_properly(self):
    """set_revision() is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("revision") is False
    test_revision = "r01"
    sm.set_revision(test_revision)
    assert sm.hasAttr("revision") is True
    assert sm.get_revision() == test_revision


def test_get_revision_will_create_attribute_if_missing(self):
    """get_revision() will create the missing revision attribute."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("revision") is False
    result = sm.get_revision()
    assert sm.hasAttr("revision") is True
    assert result == ""


def test_set_version_is_working_properly(self):
    """set_version() is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("version") is False
    test_version = "v001"
    sm.set_version(test_version)
    assert sm.hasAttr("version") is True
    assert sm.version.get() == test_version


def test_get_version_is_working_properly(self):
    """set_version() is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("version") is False
    test_version = "v001"
    sm.set_version(test_version)
    assert sm.hasAttr("version") is True
    assert sm.get_version() == test_version


def test_get_version_will_create_attribute_if_missing(self):
    """get_version() will create the missing version attribute."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("version") is False
    result = sm.get_version()
    assert sm.hasAttr("version") is True
    assert result == ""


def test_set_task_name_is_working_properly(self):
    """set_task_name() is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("task_name") is False
    test_task_name = "Animation"
    sm.set_task_name(test_task_name)
    assert sm.hasAttr("task_name") is True
    assert sm.task_name.get() == test_task_name


def test_get_task_name_is_working_properly(self):
    """set_task_name() is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("task_name") is False
    test_task_name = "Animation"
    sm.set_task_name(test_task_name)
    assert sm.hasAttr("task_name") is True
    assert sm.get_task_name() == test_task_name


def test_get_task_name_will_create_attribute_if_missing(self):
    """get_task_name() will create the missing task_name attribute."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("task_name") is False
    result = sm.get_task_name()
    assert sm.hasAttr("task_name") is True
    assert result == ""


def test_set_variant_name_is_working_properly(self):
    """set_variant_name() is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("variant_name") is False
    test_variant_name = "Main"
    sm.set_variant_name(test_variant_name)
    assert sm.hasAttr("variant_name") is True
    assert sm.variant_name.get() == test_variant_name


def test_get_variant_name_is_working_properly(self):
    """set_variant_name() is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("variant_name") is False
    test_variant_name = "Main"
    sm.set_variant_name(test_variant_name)
    assert sm.hasAttr("variant_name") is True
    assert sm.get_variant_name() == test_variant_name


def test_get_variant_name_will_create_attribute_if_missing(self):
    """get_variant_name() will create the missing variant_name attribute."""
    sm = pymel.core.PyNode("sequenceManager1")
    assert sm.hasAttr("variant_name") is False
    result = sm.get_variant_name()
    assert sm.hasAttr("variant_name") is True
    assert result == ""


def test_generate_sequence_structure_is_working_properly(self):
    """generate_sequence_structure() method is working properly."""
    sm = pymel.core.PyNode("sequenceManager1")
    from anima.dcc.maya import common

    common.Maya.set_fps(fps=24)

    sm.set_shot_name_template("<Sequence>_<Shot>_<Revision>_<Version>")
    sm.set_revision("r01")
    sm.set_version("v001")
    seq1 = sm.create_sequence("SEQ001_HSNI_003")

    shot1 = seq1.create_shot("0010")
    shot1.startFrame.set(0)
    shot1.endFrame.set(24)
    shot1.sequenceStartFrame.set(0)
    shot1.track.set(1)
    shot1.output.set("/tmp/SEQ001_HSNI_003_0010_r01_v001.mov")
    shot1.handle.set(10)

    shot2 = seq1.create_shot("0020")
    shot2.startFrame.set(10)
    shot2.endFrame.set(35)
    shot2.sequenceStartFrame.set(25)
    shot2.track.set(1)
    shot2.output.set("/tmp/SEQ001_HSNI_003_0020_r01_v001.mov")
    shot2.handle.set(15)

    shot3 = seq1.create_shot("0030")
    shot3.startFrame.set(25)
    shot3.endFrame.set(50)
    shot3.sequenceStartFrame.set(45)
    shot3.track.set(2)
    shot3.output.set("/tmp/SEQ001_HSNI_003_0030_r01_v001.mov")
    shot3.handle.set(20)

    seq = sm.generate_sequence_structure()
    assert isinstance(seq, Sequence)

    rate = seq.rate
    assert "24" == rate.timebase
    assert False == rate.ntsc

    assert "00:00:00:00" == seq.timecode
    assert False == seq.ntsc

    media = seq.media
    assert isinstance(media, Media)

    video = media.video
    assert isinstance(video, Video)
    assert media.audio is None

    assert 2 == len(video.tracks)

    track1 = video.tracks[0]
    assert isinstance(track1, Track)
    assert len(track1.clips) == 2
    assert track1.enabled == True

    track2 = video.tracks[1]
    assert isinstance(track2, Track)
    assert len(track2.clips) == 1
    assert track2.enabled == True

    clip1 = track1.clips[0]
    assert isinstance(clip1, Clip)
    assert "Video" == clip1.type
    assert "SEQ001_HSNI_003_0010_v001" == clip1.id
    assert "SEQ001_HSNI_003_0010_v001" == clip1.name
    assert 10 == clip1.in_  # handle
    assert 35 == clip1.out  # handle + duration
    assert 0 == clip1.start  # sequenceStartFrame
    assert 25 == clip1.end  # sequenceEndFrame + 1

    clip2 = track1.clips[1]
    assert isinstance(clip2, Clip)
    assert "Video" == clip2.type
    assert "SEQ001_HSNI_003_0020_v001" == clip2.id
    assert "SEQ001_HSNI_003_0020_v001" == clip2.name
    assert 15 == clip2.in_  # handle
    assert 41 == clip2.out  # handle + duration
    assert 25 == clip2.start  # sequenceStartFrame
    assert 51 == clip2.end  # sequenceEndFrame + 1

    clip3 = track2.clips[0]
    assert isinstance(clip3, Clip)
    assert "Video" == clip3.type
    assert "SEQ001_HSNI_003_0030_v001" == clip3.id
    assert "SEQ001_HSNI_003_0030_v001" == clip3.name
    assert 20 == clip3.in_  # startFrame
    assert 46 == clip3.out  # endFrame + 1
    assert 45 == clip3.start  # sequenceStartFrame
    assert 71 == clip3.end  # sequenceEndFrame + 1

    file1 = clip1.file
    assert isinstance(file1, File)
    assert "SEQ001_HSNI_003_0010_v001" == file1.name
    assert "file://localhost/tmp/SEQ001_HSNI_003_0010_v001.mov" == file1.pathurl
    assert 45 == file1.duration  # including handles

    file2 = clip2.file
    assert isinstance(file2, File)
    assert "SEQ001_HSNI_003_0020_v001" == file2.name
    assert "file://localhost/tmp/SEQ001_HSNI_003_0020_v001.mov" == file2.pathurl
    assert 56 == file2.duration  # including handles

    file3 = clip3.file
    assert isinstance(file3, File)
    assert "SEQ001_HSNI_003_0030_v001" == file3.name
    assert "file://localhost/tmp/SEQ001_HSNI_003_0030_v001.mov" == file3.pathurl
    assert 66 == file3.duration  # including handles
