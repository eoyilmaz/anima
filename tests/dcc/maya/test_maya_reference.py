# -*- coding: utf-8 -*-
import os

from stalker.db.session import DBSession


def test_update_versions_is_working_properly_case_1(
    create_test_data, create_pymel, create_maya_env
):
    """testing if update_versions is working properly in following
    condition:

    Start Condition:

    version12
      version5
        version2 -> has new published version (version3)

    Expected Result:

    version12 (no new version based on version12)
      version5 (no new version based on version5)
        version2 (do not update version2)
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env

    # create a deep relation
    data["asset2_model_main_v002"].is_published = True

    # new scene
    # version5 references version2
    maya_env.open(data["asset2_model_take1_v002"])
    maya_env.reference(data["asset2_model_main_v002"])
    pm.saveFile()
    data["asset2_model_take1_v002"].is_published = True
    pm.newFile(force=True)

    # version12 references version5
    maya_env.open(data["version12"])
    maya_env.reference(data["asset2_model_take1_v002"])
    pm.saveFile()
    data["version12"].is_published = True
    pm.newFile(force=True)

    # version3 set published
    data["asset2_model_main_v003"].is_published = True

    # check the setup
    visited_versions = []
    for v in data["version12"].walk_inputs():
        visited_versions.append(v)
    expected_visited_versions = [data["version12"], data["asset2_model_take1_v002"], data["asset2_model_main_v002"]]
    assert expected_visited_versions == visited_versions

    reference_resolution = maya_env.open(data["version12"])
    updated_versions = maya_env.update_versions(reference_resolution)

    # we should be still in version12 scene
    assert data["version12"] == maya_env.get_current_version()

    # check references
    # we shouldn't have a new version5 referenced
    refs = pm.listReferences()
    assert data["asset2_model_take1_v002"] == maya_env.get_version_from_full_path(refs[0].path)

    # and it should still have referencing version2
    refs = pm.listReferences(refs[0])
    assert data["asset2_model_main_v002"] == maya_env.get_version_from_full_path(refs[0].path)


def test_update_versions_is_working_properly_case_2(
    create_test_data, create_pymel, create_maya_env
):
    """testing if update_versions is working properly in following
    condition:

    Start Condition:

    version6 -> new version of version5 is already referencing version6
      version3 (so version6 is already using version3 and both are
                published)

    version12
      version5 -> has new published version (version6)
        version2 -> has new published version (version3)

    Expected Final Result
    version12
      version6 -> 1st level reference is updated correctly
        version3
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env

    # create a deep relation
    data["asset2_model_main_v002"].is_published = True

    # new scene
    # version5 references version2
    maya_env.open(data["asset2_model_take1_v002"])
    maya_env.reference(data["asset2_model_main_v002"])
    pm.saveFile()
    data["asset2_model_take1_v002"].is_published = True
    pm.newFile(force=True)

    # version6 references version3
    maya_env.open(data["asset2_model_take1_v003"])
    maya_env.reference(data["asset2_model_main_v003"])
    pm.saveFile()
    data["asset2_model_take1_v003"].is_published = True
    pm.newFile(force=True)

    # version12 references version5
    maya_env.open(data["version12"])
    maya_env.reference(data["asset2_model_take1_v002"])
    pm.saveFile()
    data["version12"].is_published = True
    pm.newFile(force=True)

    # version3 set published
    data["asset2_model_main_v003"].is_published = True
    data["asset2_model_take1_v003"].is_published = True

    # check the setup
    visited_versions = []
    for v in data["version12"].walk_inputs():
        visited_versions.append(v)

    expected_visited_versions = [data["version12"], data["asset2_model_take1_v002"], data["asset2_model_main_v002"]]

    assert expected_visited_versions == visited_versions

    reference_resolution = maya_env.open(data["version12"])
    created_versions = maya_env.update_versions(reference_resolution)

    # no new versions should have been created
    assert 0 == len(created_versions)

    # check if we are still in version12 scene
    assert data["version12"] == maya_env.get_current_version()

    # and expect maya have the updated references
    refs = pm.listReferences()
    assert data["asset2_model_take1_v003"] == maya_env.get_version_from_full_path(refs[0].path)

    # and it should have referenced version3
    refs = pm.listReferences(refs[0])
    assert data["asset2_model_main_v003"] == maya_env.get_version_from_full_path(refs[0].path)


def test_update_versions_is_working_properly_case_3(
    create_test_data, create_pymel, create_maya_env
):
    """testing if update_versions is working properly in following
    condition:

    Start Condition:

    version15
      version12
        version5
          version2 -> has new published version (version3)
      version12 -> referenced a second time
        version5
          version2 -> has new published version (version3)

    Expected Final Result
    version15
      version12
        version5
          version2 -> it is not a 1st level reference, nothing is updated
      version12
        version5
          version2 -> nothing is updated
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env

    # create a deep relation
    data["asset2_model_main_v002"].is_published = True
    data["asset2_model_main_v003"].is_published = True

    # new scene
    # version5 references version2
    maya_env.open(data["asset2_model_take1_v002"])
    maya_env.reference(data["asset2_model_main_v002"])
    pm.saveFile()
    data["asset2_model_take1_v002"].is_published = True
    pm.newFile(force=True)

    # version12 references version5
    maya_env.open(data["version12"])
    maya_env.reference(data["asset2_model_take1_v002"])
    pm.saveFile()
    data["version12"].is_published = True
    pm.newFile(force=True)

    # version15 references version12 two times
    maya_env.open(data["version15"])
    maya_env.reference(data["version12"])
    maya_env.reference(data["version12"])
    pm.saveFile()
    pm.newFile(force=True)

    # check the setup
    visited_versions = []
    for v in data["version15"].walk_inputs():
        visited_versions.append(v)
    expected_visited_versions = [
        data["version15"],
        data["version12"],
        data["asset2_model_take1_v002"],
        data["asset2_model_main_v002"],
    ]

    assert expected_visited_versions == visited_versions
    reference_resolution = maya_env.open(data["version15"])

    # check reference resolution
    assert sorted(reference_resolution["root"], key=lambda x: x.name) == sorted(
        [data["version12"]], key=lambda x: x.name
    )
    assert sorted(reference_resolution["create"], key=lambda x: x.name) == sorted(
        [data["asset2_model_take1_v002"], data["version12"]], key=lambda x: x.name
    )
    assert sorted(reference_resolution["update"], key=lambda x: x.name) == sorted(
        [data["asset2_model_main_v002"]], key=lambda x: x.name
    )
    assert reference_resolution["leave"] == []

    updated_versions = maya_env.update_versions(reference_resolution)

    assert 0 == len(updated_versions)

    # check if we are still in version15 scene
    assert data["version15"] == maya_env.get_current_version()

    # and expect maya have the updated references
    refs_level1 = pm.listReferences()
    assert data["version12"] == maya_env.get_version_from_full_path(refs_level1[0].path)
    assert data["version12"] == maya_env.get_version_from_full_path(refs_level1[1].path)

    # and it should have referenced version5A
    refs_level2 = pm.listReferences(refs_level1[0])
    assert data["asset2_model_take1_v002"] == maya_env.get_version_from_full_path(refs_level2[0].path)

    # and it should have referenced version5A
    refs_level3 = pm.listReferences(refs_level2[0])
    assert data["asset2_model_main_v002"] == maya_env.get_version_from_full_path(refs_level3[0].path)

    # the other version5A
    refs_level2 = pm.listReferences(refs_level1[1])
    assert data["asset2_model_take1_v002"] == maya_env.get_version_from_full_path(refs_level2[0].path)

    # and it should have referenced version5A
    refs_level3 = pm.listReferences(refs_level2[0])
    assert data["asset2_model_main_v002"] == maya_env.get_version_from_full_path(refs_level3[0].path)


def test_update_versions_is_working_properly_case_4(
    create_test_data, create_pymel, create_maya_env
):
    """testing if update_versions is working properly in following
    condition:

    Start Condition:

    version15
      version12
        version5
          version2 -> has new published version (version3)
        version5 -> Referenced a second time
          version2 -> has new published version (version3)
      version12 -> Referenced a second time
        version5
          version2 -> has new published version (version3)
        version5
          version2 -> has new published version (version3)

    Expected Final Result
    version15
      version12
        version5
          version2 -> nothing is updated
        version5
          version2 -> nothing is updated
      version12
        version5
          version2 -> nothing is updated
        version5
          version2 -> nothing is updated
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env

    # create a deep relation
    data["asset2_model_main_v002"].is_published = True
    data["asset2_model_main_v003"].is_published = True

    # new scene
    # version5 references version2
    maya_env.open(data["asset2_model_take1_v002"])
    maya_env.reference(data["asset2_model_main_v002"])
    pm.saveFile()
    data["asset2_model_take1_v002"].is_published = True
    pm.newFile(force=True)

    # version12 references version5
    maya_env.open(data["version12"])
    maya_env.reference(data["asset2_model_take1_v002"])
    maya_env.reference(data["asset2_model_take1_v002"])  # reference a second time
    pm.saveFile()
    data["version12"].is_published = True
    pm.newFile(force=True)

    # version15 references version12 two times
    maya_env.open(data["version15"])
    maya_env.reference(data["version12"])
    maya_env.reference(data["version12"])
    pm.saveFile()
    pm.newFile(force=True)

    # check the setup
    visited_versions = []
    for v in data["version15"].walk_inputs():
        visited_versions.append(v)
    expected_visited_versions = [
        data["version15"],
        data["version12"],
        data["asset2_model_take1_v002"],
        data["asset2_model_main_v002"],
    ]

    assert expected_visited_versions == visited_versions

    reference_resolution = maya_env.open(data["version15"])
    updated_versions = maya_env.update_versions(reference_resolution)

    assert 0 == len(updated_versions)

    # check if we are still in version15 scene
    assert data["version15"] == maya_env.get_current_version()

    # and expect maya have the updated references
    refs = pm.listReferences()
    version12_ref1 = refs[0]
    version12_ref2 = refs[1]

    refs = pm.listReferences(version12_ref1)
    version5_ref1 = refs[0]
    version5_ref2 = refs[1]

    refs = pm.listReferences(version12_ref2)
    version5_ref3 = refs[0]
    version5_ref4 = refs[1]

    version2_ref1 = pm.listReferences(version5_ref1)[0]
    version2_ref2 = pm.listReferences(version5_ref2)[0]
    version2_ref3 = pm.listReferences(version5_ref3)[0]
    version2_ref4 = pm.listReferences(version5_ref4)[0]

    # Version12
    published_version = data["version12"]
    assert published_version == maya_env.get_version_from_full_path(version12_ref1.path)
    assert published_version == maya_env.get_version_from_full_path(version12_ref2.path)

    # Version5
    published_version = data["asset2_model_take1_v002"]
    assert published_version == maya_env.get_version_from_full_path(version5_ref1.path)
    assert published_version == maya_env.get_version_from_full_path(version5_ref2.path)
    assert published_version == maya_env.get_version_from_full_path(version5_ref3.path)
    assert published_version == maya_env.get_version_from_full_path(version5_ref4.path)

    # Version2
    assert data["asset2_model_main_v002"] == maya_env.get_version_from_full_path(version2_ref1.path)
    assert data["asset2_model_main_v002"] == maya_env.get_version_from_full_path(version2_ref2.path)
    assert data["asset2_model_main_v002"] == maya_env.get_version_from_full_path(version2_ref3.path)
    assert data["asset2_model_main_v002"] == maya_env.get_version_from_full_path(version2_ref4.path)


def test_update_versions_is_working_properly_case_5(
    create_test_data, create_pymel, create_maya_env
):
    """testing if update_versions is working properly in following
    condition:

    Start Condition:

    version15
      version11 -> has a new version already using version6 (version12)
        version4 -> has a new published version (version6) using version3
          version2 -> has new published version (version3)
        version4 -> Referenced a second time
          version2 -> has new published version (version3)
      version11 -> Referenced a second time
        version4
          version2
        version4
          version2

    Expected Final Result (generates only one new version)
    version15 -> no new version based on version15
      version12
        version6
          version3
        version6
          version3
      version12
        version6
          version3
        version6
          version3
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env

    # create a deep relation
    data["asset2_model_main_v002"].is_published = True
    data["asset2_model_main_v003"].is_published = True

    # version4 references version2
    maya_env.open(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_main_v002"])
    pm.saveFile()
    data["asset2_model_take1_v001"].is_published = True
    pm.newFile(force=True)

    # version6 references version3
    maya_env.open(data["asset2_model_take1_v003"])
    maya_env.reference(data["asset2_model_main_v003"])
    pm.saveFile()
    data["asset2_model_take1_v003"].is_published = True
    pm.newFile(force=True)

    # version11 references version5
    maya_env.open(data["version11"])
    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v001"])  # reference a second time
    pm.saveFile()
    data["version11"].is_published = True
    pm.newFile(force=True)

    # version12 references version6
    maya_env.open(data["version12"])
    maya_env.reference(data["asset2_model_take1_v003"])
    maya_env.reference(data["asset2_model_take1_v003"])  # reference a second time
    pm.saveFile()
    data["version12"].is_published = True
    pm.newFile(force=True)

    # version15 references version11 two times
    maya_env.open(data["version15"])
    maya_env.reference(data["version11"])
    maya_env.reference(data["version11"])
    pm.saveFile()
    pm.newFile(force=True)

    # check the setup
    visited_versions = []
    for v in data["version15"].walk_inputs():
        visited_versions.append(v)
    expected_visited_versions = [
        data["version15"],
        data["version11"],
        data["asset2_model_take1_v001"],
        data["asset2_model_main_v002"],
    ]

    assert expected_visited_versions == visited_versions

    reference_resolution = maya_env.open(data["version15"])
    updated_versions = maya_env.update_versions(reference_resolution)

    assert 0 == len(updated_versions)

    # check if we are still in version15 scene
    assert data["version15"] == maya_env.get_current_version()

    # and expect maya have the updated references
    refs = pm.listReferences()
    version12_ref1 = refs[0]
    version12_ref2 = refs[1]

    refs = pm.listReferences(version12_ref1)
    version6_ref1 = refs[0]
    version6_ref2 = refs[1]

    refs = pm.listReferences(version12_ref2)
    version6_ref3 = refs[0]
    version6_ref4 = refs[1]

    version3_ref1 = pm.listReferences(version6_ref1)[0]
    version3_ref2 = pm.listReferences(version6_ref2)[0]
    version3_ref3 = pm.listReferences(version6_ref3)[0]
    version3_ref4 = pm.listReferences(version6_ref4)[0]

    # Version12
    published_version = data["version12"].latest_published_version
    assert published_version == maya_env.get_version_from_full_path(version12_ref1.path)
    assert published_version == maya_env.get_version_from_full_path(version12_ref2.path)

    # Version5
    published_version = data["asset2_model_take1_v002"].latest_published_version
    assert published_version == maya_env.get_version_from_full_path(version6_ref1.path)
    assert published_version == maya_env.get_version_from_full_path(version6_ref2.path)
    assert published_version == maya_env.get_version_from_full_path(version6_ref3.path)
    assert published_version == maya_env.get_version_from_full_path(version6_ref4.path)

    # Version2
    published_version = data["asset2_model_main_v002"].latest_published_version
    assert published_version == maya_env.get_version_from_full_path(version3_ref1.path)
    assert published_version == maya_env.get_version_from_full_path(version3_ref2.path)
    assert published_version == maya_env.get_version_from_full_path(version3_ref3.path)
    assert published_version == maya_env.get_version_from_full_path(version3_ref4.path)


def test_update_versions_is_working_properly_case_6(
    create_test_data, create_pymel, create_maya_env
):
    """testing if update_versions is working properly in following
    condition:

    Start Condition:

    version15
      version11 -> has a new version already using version6 (version12)
        version4 -> has a new published version (version6) using version3
          version2 -> has new published version (version3)
        version4 -> Referenced a second time
          version3 -> shallow updated before (let see what happens)

    Expected Final Result (generates only one new version)
    version15
      version12
        version6
          version3
        version6
          version3
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env

    # create a deep relation
    data["asset2_model_main_v002"].is_published = True
    data["asset2_model_main_v003"].is_published = True

    # version4 references version2
    maya_env.open(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_main_v002"])
    pm.saveFile()
    data["asset2_model_take1_v001"].is_published = True
    pm.newFile(force=True)

    # version6 references version3
    maya_env.open(data["asset2_model_take1_v003"])
    maya_env.reference(data["asset2_model_main_v003"])
    pm.saveFile()
    data["asset2_model_take1_v003"].is_published = True
    pm.newFile(force=True)

    # version11 references version5
    maya_env.open(data["version11"])
    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v001"])  # reference a second time
    pm.saveFile()
    data["version11"].is_published = True
    pm.newFile(force=True)

    # version12 references version6
    maya_env.open(data["version12"])
    maya_env.reference(data["asset2_model_take1_v003"])
    maya_env.reference(data["asset2_model_take1_v003"])  # reference a second time
    pm.saveFile()
    data["version12"].is_published = True
    pm.newFile(force=True)

    # version15 references version11 two times
    maya_env.open(data["version15"])
    maya_env.reference(data["version11"])

    # now simulate a shallow update on version2 -> version3 while under
    # in version4
    refs = pm.listReferences(recursive=1)
    # we should have all the references
    assert data["asset2_model_main_v002"].absolute_full_path == refs[-1].path
    refs[-1].replaceWith(data["asset2_model_main_v003"].absolute_full_path)

    pm.saveFile()
    pm.newFile(force=True)

    # check the setup
    visited_versions = []
    for v in data["version15"].walk_inputs():
        visited_versions.append(v)
    expected_visited_versions = [
        data["version15"],
        data["version11"],
        data["asset2_model_take1_v001"],
        data["asset2_model_main_v002"],
    ]

    assert expected_visited_versions == visited_versions

    reference_resolution = maya_env.open(data["version15"])
    updated_versions = maya_env.update_versions(reference_resolution)

    assert 0 == len(updated_versions)

    # check if we are still in version15 scene
    assert data["version15"] == maya_env.get_current_version()

    # and expect maya have the updated references
    refs = pm.listReferences()
    version12_ref1 = refs[0]

    refs = pm.listReferences(version12_ref1)
    version6_ref1 = refs[0]
    version6_ref2 = refs[1]

    version3_ref1 = pm.listReferences(version6_ref1)[0]
    version3_ref2 = pm.listReferences(version6_ref2)[0]

    # Version12
    published_version = data["version12"].latest_published_version
    assert published_version == maya_env.get_version_from_full_path(version12_ref1.path)

    # Version5
    published_version = data["asset2_model_take1_v002"].latest_published_version
    assert published_version == maya_env.get_version_from_full_path(version6_ref1.path)
    assert published_version == maya_env.get_version_from_full_path(version6_ref2.path)

    # Version2
    published_version = data["asset2_model_main_v002"].latest_published_version
    assert published_version == maya_env.get_version_from_full_path(version3_ref1.path)
    assert published_version == maya_env.get_version_from_full_path(version3_ref2.path)


def test_reference_updates_version_inputs_attribute(
    create_test_data, create_pymel, create_maya_env
):
    """testing if Maya.reference updates Version.inputs attribute"""
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create references to various versions
    maya_env.open(data["asset2_model_take1_v003"])

    maya_env.reference(data["asset2_model_take1_v002"])
    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_main_v003"])

    # at this point we should have data["asset2_model_take1_v003"].inputs filled correctly
    assert sorted(
        [data["asset2_model_take1_v002"], data["asset2_model_take1_v001"], data["asset2_model_main_v003"]], key=lambda x: x.name
    ) == sorted(data["asset2_model_take1_v003"].inputs, key=lambda x: x.name)


def test_get_referenced_versions_returns_a_list_of_Version_instances(
    create_test_data, create_pymel, create_maya_env
):
    """testing if Maya.get_referenced_versions returns a list of Versions
    instances referenced in the current scene
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create references to various versions
    maya_env.open(data["asset2_model_take1_v003"])

    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v002"])
    maya_env.reference(data["asset2_model_take1_v002"])  # duplicate refs
    maya_env.reference(data["asset2_model_take1_v001"])  # duplicate refs
    maya_env.reference(data["asset2_model_main_v003"])

    # now try to get the referenced versions
    referenced_versions = maya_env.get_referenced_versions()

    assert sorted(referenced_versions, key=lambda x: x.name) == sorted(
        [data["asset2_model_main_v003"], data["asset2_model_take1_v001"], data["asset2_model_take1_v002"]], key=lambda x: x.name
    )


def test_get_referenced_versions_returns_a_list_of_Version_instances_even_with_representations(
    create_test_data, create_pymel, create_maya_env, store_local_session
):
    """testing if Maya.get_referenced_versions returns a list of Versions
    instances referenced in the current scene
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env

    # Asset2 - Take1
    pm.newFile(force=True)
    root_node = pm.nt.Transform(name='Asset2_Take1')
    box = pm.polyCube(name="Box1")[0]
    pm.parent(box, root_node)
    pm.runtime.DeleteHistory()
    maya_env.save_as(data["asset2_model_main_v003"])
    maya_env.save_as(data["asset2_model_take1_v001"])
    maya_env.save_as(data["asset2_model_take1_v002"])

    from anima.dcc.mayaEnv.repr_tools import RepresentationGenerator

    gen = RepresentationGenerator()

    gen.version = data["asset2_model_take1_v001"]
    gen.generate_all()

    gen.version = data["asset2_model_take1_v002"]
    gen.generate_all()

    gen.version = data["asset2_model_main_v003"]
    gen.generate_all()

    # create references to various versions
    maya_env.open(data["asset2_model_take1_v003"])

    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v002"])
    maya_env.reference(data["asset2_model_take1_v002"])  # duplicate refs
    maya_env.reference(data["asset2_model_take1_v001"])  # duplicate refs
    maya_env.reference(data["asset2_model_main_v003"])

    # switch all references to bbox representation
    for ref in pm.listReferences():
        ref.to_repr("ASS")

    # now try to get the referenced versions
    referenced_versions = maya_env.get_referenced_versions()

    assert sorted(referenced_versions, key=lambda x: x.name) == sorted(
        [data["asset2_model_main_v003"], data["asset2_model_take1_v001"], data["asset2_model_take1_v002"]], key=lambda x: x.name
    )  # version4 will be skipped


def test_get_referenced_versions_returns_a_list_of_Version_instances_referenced_under_the_given_reference(
    create_test_data, create_pymel, create_maya_env
):
    """testing if Maya.get_referenced_versions returns a list of Versions
    referenced in the current scene under the given reference
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create references to various versions
    maya_env.open(data["asset2_model_take1_v003"])

    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v002"])
    maya_env.reference(data["asset2_model_take1_v002"])  # duplicate refs
    maya_env.reference(data["asset2_model_take1_v001"])  # duplicate refs
    maya_env.reference(data["asset2_model_main_v003"])

    # save the scene and start
    pm.saveFile()

    # open version7 and reference version6 to it
    maya_env.open(data["version7"])
    maya_env.reference(data["asset2_model_take1_v003"])

    # now try to get the referenced versions
    versions = maya_env.get_referenced_versions()

    assert sorted(versions, key=lambda x: x.name) == sorted(
        [data["asset2_model_take1_v003"]], key=lambda x: x.name
    )

    # and get a deeper one
    versions = maya_env.get_referenced_versions(pm.listReferences()[0])

    assert sorted(versions, key=lambda x: x.name) == sorted(
        [data["asset2_model_main_v003"], data["asset2_model_take1_v001"], data["asset2_model_take1_v002"]], key=lambda x: x.name
    )


def test_update_version_inputs_method_updates_the_inputs_of_the_open_version(
    create_test_data, create_pymel, create_maya_env
):
    """testing if Maya.update_version_inputs() returns updates the inputs
    attribute of the current open version by looking to the referenced
    versions
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # do not use maya_env to open and reference files
    # create references to various versions
    def open_(version):
        new_workspace = version.absolute_path
        pm.workspace.open(new_workspace)
        pm.openFile(
            version.absolute_full_path,
            f=True,
        )

    # create references
    def reference(version):
        namespace = os.path.basename(version.filename)
        namespace = namespace.replace(".", "_")
        ref = pm.createReference(
            version.absolute_full_path, gl=True, namespace=namespace, options="v=0"
        )

    open_(data["asset2_model_take1_v003"])
    reference(data["asset2_model_take1_v001"])
    reference(data["asset2_model_take1_v002"])
    reference(data["asset2_model_take1_v002"])  # duplicate refs
    reference(data["asset2_model_take1_v001"])  # duplicate refs
    reference(data["asset2_model_main_v003"])

    # save the scene and start
    pm.saveFile()

    # the version6.inputs should be an empty list
    assert data["asset2_model_take1_v003"].inputs == []

    # open version7 and reference version6 to it
    open_(data["version7"])
    reference(data["asset2_model_take1_v003"])

    # version7.inputs should be an empty list
    assert data["version7"].inputs == []

    # now try to update referenced versions
    maya_env.update_version_inputs()

    assert [data["asset2_model_take1_v003"]] == data["version7"].inputs

    # now get the version6.inputs right
    refs = pm.listReferences()
    maya_env.update_version_inputs(refs[0])

    assert sorted(
        [data["asset2_model_main_v003"], data["asset2_model_take1_v001"], data["asset2_model_take1_v002"]], key=lambda x: x.name
    ) == sorted(data["asset2_model_take1_v003"].inputs, key=lambda x: x.name)


def test_reference_method_updates_the_inputs_of_the_referenced_version(
    create_test_data, create_pymel, create_maya_env
):
    """testing if Maya.reference() method updates the Version.inputs of the
    referenced version
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create a new version
    maya_env.open(data["asset2_model_take1_v003"])

    # check prior to referencing
    assert data["asset2_model_take1_v002"] not in data["asset2_model_take1_v003"].inputs

    # reference something and let Maya update the inputs
    maya_env.reference(data["asset2_model_take1_v002"])

    # check if version5 is in version6.inputs
    assert data["asset2_model_take1_v002"] in data["asset2_model_take1_v003"].inputs

    # remove the reference and save the file (do not saveAs)
    pm.listReferences()[0].remove()

    # save the file over itself
    pm.saveFile()

    # check if version5 still in version6.inputs
    assert data["asset2_model_take1_v002"] in data["asset2_model_take1_v003"].inputs

    # create a new scene and reference the previous version and check if
    pm.newFile(f=True)
    maya_env.save_as(data["asset2_model_main_v003"])
    maya_env.reference(data["asset2_model_take1_v003"])

    # the Version.inputs is updated correctly
    assert data["asset2_model_take1_v002"] not in data["asset2_model_take1_v003"].inputs


def test_check_referenced_versions_is_working_properly(
    create_test_data, create_pymel, create_maya_env
):
    """testing if check_referenced_versions will return a list of tuples
    holding info like which ref needs to be updated or which reference
    needs a new version, what is the corresponding Version instance and
    what is the final action

    Start Condition:

    version15
      version11 -> has a new version already using version6 (version12)
        version4 -> has a new published version (version6) using version3
          version2 -> has new published version (version3)
        version4 -> Referenced a second time
          version2 -> has new published version (version3)
      version11 -> Referenced a second time
        version4
          version2
        version4
          version2
      version21
        version16 -> has a new published version version18
      version38 -> no update
        version27 -> no update

    Expected Final Result (generates only one new version)
    version15 -> same version of version15
      version12
        version6
          version3
        version6
          version3
      version12
        version6
          version3
        version6
          version3
      version21 -> same version of version21
        version18
      version38 -> no update
        version27 -> no update
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create a deep relation
    data["asset2_model_main_v002"].is_published = True
    data["asset2_model_main_v003"].is_published = True

    # version4 references version2
    maya_env.open(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_main_v002"])
    pm.saveFile()
    data["asset2_model_take1_v001"].is_published = True
    pm.newFile(force=True)

    # version6 references version3
    maya_env.open(data["asset2_model_take1_v003"])
    maya_env.reference(data["asset2_model_main_v003"])
    pm.saveFile()
    data["asset2_model_take1_v003"].is_published = True
    pm.newFile(force=True)

    # version11 references version5
    maya_env.open(data["version11"])
    maya_env.reference(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_take1_v001"])  # reference a second time
    pm.saveFile()
    data["version11"].is_published = True
    pm.newFile(force=True)

    # version12 references version6
    maya_env.open(data["version12"])
    maya_env.reference(data["asset2_model_take1_v003"])
    maya_env.reference(data["asset2_model_take1_v003"])  # reference a second time
    pm.saveFile()
    data["version12"].is_published = True
    pm.newFile(force=True)

    # version21 references version16
    maya_env.open(data["shot3_anim_main_v003"])
    maya_env.reference(data["version16"])
    pm.saveFile()
    data["version16"].is_published = True
    data["version18"].is_published = True
    data["shot3_anim_main_v003"].is_published = True
    pm.newFile(force=True)

    # version38 references version27
    maya_env.open(data["version38"])
    maya_env.reference(data["version27"])
    pm.saveFile()
    data["version38"].is_published = True
    data["version27"].is_published = True
    pm.newFile(force=True)

    # version15 references version11 two times
    maya_env.open(data["version15"])
    maya_env.reference(data["version11"])
    maya_env.reference(data["version11"])
    maya_env.reference(data["shot3_anim_main_v003"])
    maya_env.reference(data["version38"])
    pm.saveFile()
    # pm.newFile(force=True)
    DBSession.commit()

    # check the setup
    visited_versions = []
    for v in data["version15"].walk_inputs():
        visited_versions.append(v)
    expected_visited_versions = [
        data["version15"],
        data["version11"],
        data["asset2_model_take1_v001"],
        data["asset2_model_main_v002"],
        data["shot3_anim_main_v003"],
        data["version16"],
        data["version38"],
        data["version27"],
    ]

    assert expected_visited_versions == visited_versions

    root_refs = pm.listReferences()

    version11_ref_1 = root_refs[0]
    version4_ref_1 = pm.listReferences(version11_ref_1)[0]
    version2_ref_1 = pm.listReferences(version4_ref_1)[0]
    version4_ref_2 = pm.listReferences(version11_ref_1)[1]
    version2_ref_2 = pm.listReferences(version4_ref_2)[0]

    version11_ref_2 = root_refs[1]
    version4_ref_3 = pm.listReferences(version11_ref_2)[0]
    version2_ref_3 = pm.listReferences(version4_ref_3)[0]
    version4_ref_4 = pm.listReferences(version11_ref_2)[1]
    version2_ref_4 = pm.listReferences(version4_ref_4)[0]

    version21_ref = root_refs[2]
    version16_ref = pm.listReferences(version21_ref)[0]

    version38_ref = root_refs[3]
    version27_ref = pm.listReferences(version38_ref)[0]

    assert not data["asset2_model_main_v002"].is_latest_published_version()

    expected_reference_resolution = {
        "root": [data["version38"], data["version11"], data["shot3_anim_main_v003"]],
        "leave": [data["version27"], data["version38"]],
        "update": [
            data["version16"],
            data["asset2_model_main_v002"],
            data["asset2_model_take1_v001"],
            data["version11"],
        ],
        "create": [data["shot3_anim_main_v003"]],
    }

    result = maya_env.check_referenced_versions()

    # print('data["version27"]: %s' % data["version27"])
    # print('data["version38"]: %s' % data["version38"])
    # print('data["version16"]: %s' % data["version16"])
    # print('data["shot3_anim_main_v003"]: %s' % data["shot3_anim_main_v003"])
    # print('data["asset2_model_main_v002"] : %s' % data["asset2_model_main_v002"])
    # print('data["asset2_model_take1_v001"] : %s' % data["asset2_model_take1_v001"])
    # print('data["version11"]: %s' % data["version11"])
    # print('data["version15"]: %s' % data["version15"])
    #
    # print(expected_reference_resolution)
    # print('--------------------------')
    # print(result)

    assert sorted(
        expected_reference_resolution["root"], key=lambda x: x.name
    ) == sorted(result["root"], key=lambda x: x.name)
    assert sorted(
        expected_reference_resolution["leave"], key=lambda x: x.name
    ) == sorted(result["leave"], key=lambda x: x.name)
    assert sorted(
        expected_reference_resolution["update"], key=lambda x: x.name
    ) == sorted(result["update"], key=lambda x: x.name)
    assert sorted(
        expected_reference_resolution["create"], key=lambda x: x.name
    ) == sorted(result["create"], key=lambda x: x.name)


def test_check_referenced_versions_is_working_properly_case_2(
    create_test_data, create_pymel, create_maya_env
):
    """testing if check_referenced_versions will return a dictionary holding
    info like which ref needs to be updated or which reference needs a new
    version, what is the corresponding Version instance and what is the
    final action, even if the 2nd level of references has an update

    Start Condition:

    version15 -> has no new version
      version11 -> has no new version
        version4 -> has no new version
          version2 -> has new published version (version3)

    Expected Final Result (generates only one new version)
    version15 -> create
      version11 -> create
        version4 -> create
          version2 -> update
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create a deep relation
    data["asset2_model_main_v002"].is_published = True
    data["asset2_model_main_v003"].is_published = True

    # version4 references version2
    maya_env.open(data["asset2_model_take1_v001"])
    maya_env.reference(data["asset2_model_main_v002"])
    pm.saveFile()
    data["asset2_model_take1_v001"].is_published = True
    pm.newFile(force=True)

    # version11 references version4
    maya_env.open(data["version11"])
    maya_env.reference(data["asset2_model_take1_v001"])
    pm.saveFile()
    data["version11"].is_published = True
    pm.newFile(force=True)

    # version15 references version11 two times
    maya_env.open(data["version15"])
    maya_env.reference(data["version11"])
    pm.saveFile()

    DBSession.commit()

    # check the setup
    visited_versions = []
    for v in data["version15"].walk_inputs():
        visited_versions.append(v)
    expected_visited_versions = [
        data["version15"],
        data["version11"],
        data["asset2_model_take1_v001"],
        data["asset2_model_main_v002"],
    ]

    assert expected_visited_versions == visited_versions

    expected_reference_resolution = {
        "root": [data["version11"]],
        "leave": [],
        "update": [data["asset2_model_main_v002"]],
        "create": [data["asset2_model_take1_v001"], data["version11"]],
    }

    result = maya_env.check_referenced_versions()

    # print('data["version15"].id: %s' % data["version15"].id)
    # print('data["version11"].id: %s' % data["version11"].id)
    # print('data["asset2_model_take1_v001"].id : %s' % data["asset2_model_take1_v001"].id)
    # print('data["asset2_model_main_v002"].id : %s' % data["asset2_model_main_v002"].id)
    #
    # print(expected_reference_resolution)
    # print('--------------------------')s
    # print(result)

    assert sorted(
        expected_reference_resolution["root"], key=lambda x: x.name
    ) == sorted(result["root"], key=lambda x: x.name)
    assert sorted(
        expected_reference_resolution["leave"], key=lambda x: x.name
    ) == sorted(result["leave"], key=lambda x: x.name)
    assert sorted(
        expected_reference_resolution["update"], key=lambda x: x.name
    ) == sorted(result["update"], key=lambda x: x.name)
    assert sorted(
        expected_reference_resolution["create"], key=lambda x: x.name
    ) == sorted(result["create"], key=lambda x: x.name)
