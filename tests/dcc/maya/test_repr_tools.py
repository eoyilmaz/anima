"""Tests for anima.dcc.mayaEnv.toolbox representation tools
"""
import os

import pytest

from anima.dcc.mayaEnv.reference import Reference
from anima.dcc.mayaEnv.repr_tools import RepresentationGenerator, Representation

from stalker import User, LocalSession


@pytest.fixture(scope="function")
def setup_toolbox_representation_tools_tests(create_pymel, store_local_session):
    """Set up env for toolbox representation tools tests."""
    pm = create_pymel

    # first path pm.confirmDialog
    orig_confirm_dialog = pm.confirmDialog

    def patched_confirm_dialog(*args, **kwargs):
        return "Yes"

    pm.confirmDialog = patched_confirm_dialog

    yield

    # restore confirm dialog
    pm.confirmDialog = orig_confirm_dialog


def test_generating_all_representations_through_environment_layout_scene(
    create_test_data, setup_toolbox_representation_tools_tests, create_maya_env
):
    """testing if generating all representations of all references from the
    environment layout scene is working properly
    """
    data = create_test_data
    maya_env = create_maya_env

    # open up the environment | layout | hires
    maya_env.open(data["ext1_layout_main_v003"], force=True)

    # generate all from here
    Reference.generate_repr_of_all_references()

    # expect all the representations to be generated for all the
    # referenced scenes

    # start from deepest
    r = Representation()

    # Building1 | Props | YAPI | Model | Hires
    r.version = data["building1_yapi_model_main_v003"]
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")

    assert v_gpu is not None
    assert v_ass is not None

    # Building1 | Props | YAPI | LookDev
    r.version = data["building1_yapi_look_dev_main_v003"]
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")

    assert v_gpu is not None
    assert v_ass is not None

    # Building1 | Layout | Hires
    r.version = data["building1_layout_main_v003"]
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")

    assert v_gpu is not None
    assert v_ass is not None

    # Building2 | Props | YAPI | Model | Hires
    r.version = data["building2_yapi_model_main_v003"]
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")

    assert v_gpu is not None
    assert v_ass is not None

    # Building2 | Props | YAPI | LookDev
    r.version = data["building2_yapi_look_dev_main_v003"]
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")

    assert v_gpu is not None
    assert v_ass is not None

    # Building2 | Layout | Hires
    r.version = data["building2_layout_main_v003"]
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")

    assert v_gpu is not None
    assert v_ass is not None

    # Vegetation
    r.version = data["ext1_vegetation_main_v003"]
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")

    assert v_gpu is not None
    assert v_ass is not None

    # Layout | Hires
    r.version = data["ext1_layout_main_v003"]
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")

    assert v_gpu is not None
    assert v_ass is not None


# GPU
# - of a model
# - of a look dev
# - of a layout of a building
# - of a look dev of a building
# - of a layout of an environment
# - of a look dev of an environment
# - of a vegetation scene


def test_generate_gpu_will_end_up_with_an_empty_scene(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_gpu will end up with an empty scene"""
    data = create_test_data
    pm = create_pymel
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_gpu()

    # we should be on an untitled scene
    assert pm.sceneName() == ""


def test_generate_gpu_will_overwrite_previous_gpu_version(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_gpu will overwrite to the previous GPU version"""
    data = create_test_data
    gen = RepresentationGenerator()

    gen.version = data["building1_yapi_model_main_v003"]
    gen.generate_gpu()

    r = Representation(version=data["building1_yapi_model_main_v003"])
    v1 = r.find("GPU")
    assert v1 is not None

    # generate again
    gen.generate_gpu()
    v2 = r.find("GPU")
    assert v2 is not None

    # and they should be the same version
    assert v1 == v2


def test_generate_gpu_scene_with_references_before_generating_gpu_of_references_first(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if a RuntimeError will be raised when trying to generate
    the GPU Repr of a scene before generating the GPU of all the
    references
    """
    data = create_test_data
    gen = RepresentationGenerator(version=data["building1_yapi_look_dev_main_v001"])

    with pytest.raises(RuntimeError) as cm:
        gen.generate_gpu()

    assert str(
        cm.value
    ) == "Please generate the GPU Representation of the references first!!!\n{}".format(
        data["building1_yapi_model_main_v003"].absolute_full_path
    )


def test_generate_gpu_of_a_simple_model(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_gpu will generate bounding boxes for each
    object with the same name in a model scene
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_gpu()

    r = Representation(version=data["building1_yapi_model_main_v003"])
    v = r.find("GPU")
    maya_env.open(v, force=True)

    # the name of the GPU object should be the same
    node = pm.PyNode("duvarlar")

    assert node is not None

    # and the type of the shape should be gpuCache
    assert node.getShape().type() == "gpuCache"


def test_generate_gpu_of_a_simple_look_dev(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_gpu will just replace the references for a
    simple look dev scene
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_gpu()

    # building | props | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_gpu()

    r = Representation(version=data["building1_yapi_look_dev_main_v003"])
    v = r.find("GPU")
    maya_env.open(v, force=True)

    # nothing special here, the reference should be replaced with GPU repr
    for ref in pm.listReferences():
        assert ref.is_repr("GPU")


def test_generate_gpu_of_a_layout_of_a_building(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_gpu of the layout scene of a building is
    working properly
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_gpu()

    # building | props | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_gpu()

    # building | layout | hires
    gen.version = data["building1_layout_main_v003"]
    gen.generate_gpu()

    r = Representation(version=data["building1_layout_main_v003"])
    v = r.find("GPU")
    maya_env.open(v, force=True)

    # nothing special here, the reference should be replaced with GPU repr
    for ref in pm.listReferences():
        assert ref.is_repr("GPU")


def test_generate_gpu_of_a_look_dev_of_a_building(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_gpu of the look dev scene of a building is
    working properly
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_gpu()

    # building | props | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_gpu()

    # building | layout | hires
    gen.version = data["building1_layout_main_v003"]
    gen.generate_gpu()

    # building | look dev
    gen.version = data["building1_look_dev_main_v003"]
    gen.generate_gpu()

    r = Representation(version=data["building1_look_dev_main_v003"])
    v = r.find("GPU")
    maya_env.open(v, force=True)

    # nothing special here, the reference should be replaced with GPU repr
    for ref in pm.listReferences():
        assert ref.is_repr("GPU")


def test_generate_gpu_of_a_layout_of_an_environment(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_gpu of the layout scene of an environment is
    working properly
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    gen = RepresentationGenerator()
    # Prop1 (Model | Hires | Kisa)
    gen.version = data["prop1_model_kisa_v003"]
    gen.generate_all()

    # Prop1 (LookDev | Kisa)
    gen.version = data["prop1_look_dev_kisa_v003"]
    gen.generate_all()

    # Building1
    # start with building | props | yapi | model | hires
    gen.version = data["building1_yapi_model_main_v003"]
    gen.generate_gpu()

    # building | props | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_gpu()

    # building | layout | hires
    gen.version = data["building1_layout_main_v003"]
    gen.generate_gpu()

    # Building2
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building2_yapi_model_main_v003"])
    gen.generate_gpu()

    # building | props | yapi | look dev
    gen.version = data["building2_yapi_look_dev_main_v003"]
    gen.generate_gpu()

    # building | layout | hires
    gen.version = data["building2_layout_main_v003"]
    gen.generate_gpu()

    # vegetation
    gen.version = data["ext1_vegetation_main_v003"]
    gen.generate_gpu()

    # Environment
    gen.version = data["ext1_layout_main_v003"]
    gen.generate_gpu()

    r = Representation(version=data["ext1_layout_main_v003"])
    v = r.find("GPU")
    maya_env.open(v, force=True)

    # there should be no references
    assert len(pm.listReferences()) == 0


def test_generate_gpu_of_a_look_dev_of_an_environment(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_gpu of the look dev scene of an environment is
    working properly
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # Building1
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_gpu()

    # building | props | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_gpu()

    # building | layout | hires
    gen.version = data["building1_layout_main_v003"]
    gen.generate_gpu()

    # Building2
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building2_yapi_model_main_v003"])
    gen.generate_gpu()

    # building | props | yapi | look dev
    gen.version = data["building2_yapi_look_dev_main_v003"]
    gen.generate_gpu()

    # building | layout | hires
    gen.version = data["building2_layout_main_v003"]
    gen.generate_gpu()

    # vegetation
    gen.version = data["ext1_vegetation_main_v003"]
    gen.generate_gpu()

    # Environment Layout
    gen.version = data["ext1_layout_main_v003"]
    gen.generate_gpu()

    # Environment Look dev
    gen.version = data["ext1_look_dev_main_v003"]
    gen.generate_gpu()

    r = Representation(version=data["ext1_look_dev_main_v003"])
    v = r.find("GPU")
    maya_env.open(v, force=True)

    # nothing special here, the reference should be replaced with GPU repr
    for ref in pm.listReferences():
        assert ref.is_repr("GPU")


def test_generate_gpu_of_a_vegetation_scene(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_gpu of the vegetation scene is working properly"""
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    gen = RepresentationGenerator(version=data["ext1_vegetation_main_v003"])
    gen.generate_gpu()

    r = Representation(version=data["ext1_vegetation_main_v003"])
    v = r.find("GPU")
    maya_env.open(v, force=True)

    # we should have all polygons converted to a bounding box object
    root_node = pm.PyNode("kksEnv___vegetation_ALL")
    assert root_node is not None

    children = root_node.getChildren()
    # for child in children:
    #     print(child.name())
    assert len(children) == 1  # including paintableGeos group

    # pfx_polygons = children[2]
    # assert pfx_polygons.name() == 'kks___vegetation_pfxPolygons'

    # and they should have a gpuCache shape
    # assert pfx_polygons.getShape().type() == "gpuCache"


# ASS
# - of a model
# - of a look dev
# - of a layout of a building
# - of a look dev of a building
# - of a layout of an environment
# - of a look dev of an environment
# - of a vegetation scene


def test_generate_ass_will_end_up_with_an_empty_scene(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_ass will end up with a new empty scene"""
    data = create_test_data
    pm = create_pymel
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_ass()

    # we should be on an untitled scene
    assert pm.sceneName() == ""


def test_generate_ass_will_overwrite_previous_ass_version(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_ass will overwrite to the previous ASS version"""
    data = create_test_data
    gen = RepresentationGenerator()

    gen.version = data["building1_yapi_model_main_v003"]
    gen.generate_ass()

    r = Representation(version=data["building1_yapi_model_main_v003"])
    v1 = r.find("ASS")
    assert v1 is not None

    # generate again
    gen.generate_ass()
    v2 = r.find("ASS")
    assert v2 is not None

    # and they should be the same version
    assert v1 == v2


def test_generate_ass_repr_for_building_yapi_look_dev_without_creating_model_first(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if a RuntimeError will be raised when trying to generate the ASS Repr for
    a Look Dev task before generating ASS for the model first
    """
    data = create_test_data
    gen = RepresentationGenerator(version=data["building1_yapi_look_dev_main_v001"])

    with pytest.raises(RuntimeError) as cm:
        gen.generate_ass()

    assert (
        str(cm.value) == "Please generate the ASS Representation of the references "
        "first!!!\n%s" % data["building1_yapi_model_main_v003"].absolute_full_path,
    )


def test_generate_ass_repr_for_building_layout_without_creating_building_look_dev_first(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if a RuntimeError will be raised when trying to generate the ASS Repr for
    a Layout task before generating ASS for the Look Dev first
    """
    data = create_test_data
    gen = RepresentationGenerator(version=data["building1_layout_main_v003"])

    with pytest.raises(RuntimeError) as cm:
        gen.generate_ass()

    assert (
        str(cm.value) == "Please generate the ASS Representation of the references "
        "first!!!\n%s" % data["building1_yapi_look_dev_main_v003"].absolute_full_path,
    )


def test_generate_ass_repr_for_building_yapi_model(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if creating ASS repr for a model is working properly"""
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v001"])
    gen.generate_ass()

    # check if a proper ASS repr is generated
    repr_ = Representation(version=data["building1_yapi_model_main_v001"])
    ass_v = repr_.find("ASS")
    assert ass_v is not None
    assert "@ASS" in ass_v.take_name
    assert os.path.exists(ass_v.absolute_full_path)

    # open the file and check content
    maya_env.open(ass_v, force=True)
    yapi = pm.ls("building1_yapi")[0]

    # it should have only one child
    all_children = yapi.getChildren()
    assert len(all_children) == 1

    # and it should have an aiStandIn node as the shape
    bina = all_children[0]
    assert len(bina.getChildren()) == 1
    stand_in = bina.getChildren()[0]
    assert stand_in.type() == "aiStandIn"
    assert stand_in.getAttr("dso") is None


def test_generate_ass_repr_for_building_yapi_look_dev_is_working_properly(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if ASS repr generation is working properly for a look dev
    version
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # first generate for the model
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_ass()

    # then for the look dev version
    gen.version = data["building1_yapi_look_dev_main_v001"]
    gen.generate_ass()

    # open the file
    r = Representation(version=data["building1_yapi_look_dev_main_v001"])
    # get the ASS repr
    v = r.find("ASS")
    maya_env.open(v, force=True)

    # check if "alles in ordnung!"
    # the reference should be an ASS repr of the model
    ref = pm.listReferences()[0]
    assert ref.is_repr("ASS")

    # there should be Stand-In nodes under the referenced nodes
    all_stand_ins = pm.ls(type="aiStandIn")
    assert len(all_stand_ins) == 1

    # it should be a referenced node
    parent = all_stand_ins[0].getParent()
    assert parent.referenceFile() == ref

    # the standIn node itself should be coming from the model
    assert all_stand_ins[0].referenceFile() == ref

    # and the path of hte aiStandIn is pointing to an ass file under the
    # LookDev/Outputs
    assert "LookDev/Outputs" in all_stand_ins[0].getAttr("dso")
    assert ".ass.gz" in all_stand_ins[0].getAttr("dso")


def test_generate_ass_repr_for_building_layout_is_working_properly(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if a generating the ASS Repr for a Layout task is working
    properly
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # generate for the model first
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_ass()

    # then look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_ass()

    # then for the layout
    gen.version = data["building1_layout_main_v003"]
    gen.generate_ass()

    # open the Layout:Main@ASS
    r = Representation(version=data["building1_layout_main_v003"])
    v = r.find("ASS")
    assert v is not None
    maya_env.open(v, force=True)

    # there should be nothing so special, instead of the regular look dev
    # the ASS repr of the look dev should have been referenced
    ref = pm.listReferences()[0]
    assert ref.is_repr("ASS")


def test_generate_ass_repr_for_building_look_dev_is_working_properly(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_ass() will properly generate an ASS repr for the
    look dev of a building
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # Building1
    # generate for the model first
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_ass()

    # then building | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_ass()

    # then for the building | layout | hires
    gen.version = data["building1_layout_main_v003"]
    gen.generate_ass()

    # then the building | look dev
    gen.version = data["building1_look_dev_main_v003"]
    gen.generate_ass()

    # open up the ASS file
    r = Representation(version=data["building1_look_dev_main_v003"])
    v = r.find("ASS")
    maya_env.open(v, force=True)

    # now check references
    ref = pm.listReferences()[0]
    assert ref.is_repr("ASS")


def test_generate_ass_repr_for_vegetation_scene(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generating ass of a vegetation scene is working properly"""
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    gen = RepresentationGenerator(version=data["ext1_vegetation_main_v003"])
    gen.generate_ass()

    # open the ASS scene
    r = Representation(version=data["ext1_vegetation_main_v003"])
    v = r.find("ASS")
    maya_env.open(v, force=True)

    # there should be only "pfxPolygons" group
    root_node = pm.PyNode("kksEnv___vegetation_ALL")
    children = root_node.getChildren()

    assert len(children) == 1

    # and there should be 2 other
    # transform nodes under it (for our test case)
    pfx_polygons = children[0]
    assert pfx_polygons.name() == "kks___vegetation_pfxPolygons"

    children = pfx_polygons.getChildren()
    assert len(children) == 2

    # they should have a transform node with aiStandIn shape
    for child in children:
        mesh_group = child.getChildren()[0]
        assert mesh_group.getShape().type() == "aiStandIn"


def test_generate_ass_of_a_layout_of_an_environment(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_ass() will properly generate an ASS repr for the
    environment layout
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # Building1
    # generate for the model first
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_ass()

    # then building | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_ass()

    # then for the building | layout | hires
    gen.version = data["building1_layout_main_v003"]
    gen.generate_ass()

    # Building2
    # generate for the model first
    gen = RepresentationGenerator(version=data["building2_yapi_model_main_v003"])
    gen.generate_ass()

    # then building | yapi | look dev
    gen.version = data["building2_yapi_look_dev_main_v003"]
    gen.generate_ass()

    # then for the building | layout | hires
    gen.version = data["building2_layout_main_v003"]
    gen.generate_ass()

    # The vegetation
    gen.version = data["ext1_vegetation_main_v003"]
    gen.generate_ass()

    # Environment | Layout | Hires
    gen.version = data["ext1_layout_main_v003"]
    gen.generate_ass()

    # open up the ASS file
    r = Representation(version=data["ext1_layout_main_v003"])
    v = r.find("ASS")
    maya_env.open(v, force=True)

    # now check references
    assert len(pm.listReferences()) == 0

    # but there should be aiStandIn nodes
    assert len(pm.ls(type="aiStandIn")) > 0


# ALL
# - of a model
# - of a look dev
# - of a layout of a building
# - of a look dev of a building
# - of a layout of an environment
# - of a look dev of an environment
# - of a vegetation scene


def test_generate_all_will_end_up_with_an_empty_scene(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_all will end up with an empty scene"""
    data = create_test_data
    pm = create_pymel
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_all()

    # we should be on an untitled scene
    assert pm.sceneName() == ""


def test_generate_all_scene_with_references_before_generating_all_of_references_first(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if a RuntimeError will be raised when trying to generate
    the all representations of a scene before generating all the
    representations of all the references
    """
    data = create_test_data
    gen = RepresentationGenerator(version=data["building1_yapi_look_dev_main_v001"])

    with pytest.raises(RuntimeError) as cm:
        gen.generate_all()

    # BBOX will complain first
    assert (
        str(cm.value) == "Please generate the GPU Representation of the references "
        "first!!!\n%s" % data["building1_yapi_model_main_v003"].absolute_full_path,
    )


def test_generate_all_of_a_simple_model(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_all will generate all representations of a model
    scene
    """
    data = create_test_data
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_all()

    r = Representation(version=data["building1_yapi_model_main_v003"])
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")
    v_rs = r.find("RS")

    assert v_gpu is None
    assert v_ass is None
    assert v_rs is not None


def test_generate_all_of_a_simple_look_dev(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_all generate all the representations of a
    simple look dev scene
    """
    data = create_test_data
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_all()

    # building | props | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_all()

    r = Representation(version=data["building1_yapi_look_dev_main_v003"])
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")
    v_rs = r.find("RS")

    assert v_gpu is None
    assert v_ass is None
    assert v_rs is not None


def test_generate_all_of_a_layout_of_a_building(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_all the layout scene of a building is working
    properly
    """
    data = create_test_data
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_all()

    # building | props | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_all()

    # building | layout | hires
    gen.version = data["building1_layout_main_v003"]
    gen.generate_all()

    r = Representation(version=data["building1_layout_main_v003"])
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")
    v_rs = r.find("RS")

    assert v_gpu is None
    assert v_ass is None
    assert v_rs is not None


def test_generate_all_of_a_look_dev_of_a_building(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_all the look dev scene of a building is
    working properly
    """
    data = create_test_data
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_all()

    # building | props | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_all()

    # building | layout | hires
    gen.version = data["building1_layout_main_v003"]
    gen.generate_all()

    # building | look dev
    gen.version = data["building1_look_dev_main_v003"]
    gen.generate_all()

    r = Representation(version=data["building1_look_dev_main_v003"])
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")
    v_rs = r.find("RS")

    assert v_gpu is None
    assert v_ass is None
    assert v_rs is not None


def test_generate_all_of_a_layout_of_an_environment(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_all the layout scene of an environment is
    working properly
    """
    data = create_test_data
    gen = RepresentationGenerator()
    # Prop1 (Model | Hires | Kisa)
    gen.version = data["prop1_model_kisa_v003"]
    gen.generate_all()

    # Prop1 (LookDev | Kisa)
    gen.version = data["prop1_look_dev_kisa_v003"]
    gen.generate_all()

    # Building1
    # start with building | props | yapi | model | hires
    gen.version = data["building1_yapi_model_main_v003"]
    gen.generate_all()

    # building | props | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_all()

    # building | layout | hires
    gen.version = data["building1_layout_main_v003"]
    gen.generate_all()

    # Building2
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building2_yapi_model_main_v003"])
    gen.generate_all()

    # building | props | yapi | look dev
    gen.version = data["building2_yapi_look_dev_main_v003"]
    gen.generate_all()

    # building | layout | hires
    gen.version = data["building2_layout_main_v003"]
    gen.generate_all()

    # vegetation
    gen.version = data["ext1_vegetation_main_v003"]
    gen.generate_all()

    # Environment
    gen.version = data["ext1_layout_main_v003"]
    gen.generate_all()

    r = Representation(version=data["ext1_layout_main_v003"])
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")
    v_rs = r.find("RS")

    assert v_gpu is None
    assert v_ass is None
    assert v_rs is not None


def test_generate_all_of_a_look_dev_of_an_environment(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_all the look dev scene of an environment is
    working properly
    """
    data = create_test_data
    # Building1
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building1_yapi_model_main_v003"])
    gen.generate_all()

    # building | props | yapi | look dev
    gen.version = data["building1_yapi_look_dev_main_v003"]
    gen.generate_all()

    # building | layout | hires
    gen.version = data["building1_layout_main_v003"]
    gen.generate_all()

    # Building2
    # start with building | props | yapi | model | hires
    gen = RepresentationGenerator(version=data["building2_yapi_model_main_v003"])
    gen.generate_all()

    # building | props | yapi | look dev
    gen.version = data["building2_yapi_look_dev_main_v003"]
    gen.generate_all()

    # building | layout | hires
    gen.version = data["building2_layout_main_v003"]
    gen.generate_all()

    # vegetation
    gen.version = data["ext1_vegetation_main_v003"]
    gen.generate_all()

    # Environment Layout
    gen.version = data["ext1_layout_main_v003"]
    gen.generate_all()

    # Environment Look dev
    gen.version = data["ext1_look_dev_main_v003"]
    gen.generate_all()

    r = Representation(version=data["ext1_look_dev_main_v003"])
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")
    v_rs = r.find("RS")

    assert v_gpu is None
    assert v_ass is None
    assert v_rs is not None


def test_generate_all_of_a_vegetation_scene(
    create_test_data,
    store_local_session,
    create_pymel,
    create_maya_env,
):
    """testing if generate_all the vegetation scene is working properly"""
    data = create_test_data
    gen = RepresentationGenerator(version=data["ext1_vegetation_main_v003"])
    gen.generate_all()

    r = Representation(version=data["ext1_vegetation_main_v003"])
    v_gpu = r.find("GPU")
    v_ass = r.find("ASS")
    v_rs = r.find("RS")

    assert v_gpu is None
    assert v_ass is None
    assert v_rs is not None
