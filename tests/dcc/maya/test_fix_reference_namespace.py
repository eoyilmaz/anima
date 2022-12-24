# -*- coding: utf-8 -*-

from stalker.db.session import DBSession


def test_fix_reference_namespace_is_working_properly(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly

    version15 -> has no new version
      version11 -> has no new version
        asset2_lookdev_take1_v001 -> has no new version
          version2 -> has no new version

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    data["version15"].is_published = True

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    loc = pm.spaceLocator(name="locator1")
    loc.t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(loc, tra_group)
    pm.saveFile()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # lookdev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    pm.saveFile()

    pm.newFile(force=True)
    # version11 references asset2_lookdev_take1_v001
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    asset2_lookdev_take1_v001_ref_node = refs[0]
    asset2_lookdev_take1_v001_ref_node.namespace = data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there is only one locator in the current scene
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)[0]
    loc.t.set(1, 0, 0)

    # we should have created an edit
    version2_ref_node = pm.listReferences(asset2_lookdev_take1_v001_ref_node)[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    pm.saveFile()
    pm.newFile(force=True)

    # version15 references version11 two times
    maya_env.open(data["version15"])
    maya_env.reference(data["version11"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["version11"].filename.replace(".", "_")
    pm.saveFile()

    DBSession.commit()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].filename.replace(".", "_")
    assert all_refs[1].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # now let it be fixed
    maya_env.fix_reference_namespaces()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].latest_published_version.nice_name
    assert (
        all_refs[1].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[2].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # now check we don't have any failed edits
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, fld=1)) == 0

    # and we have all successful edits
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, scs=1)) == 2

    # and check if the locator is in 1, 0, 0
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)[0]
    assert loc.tx.get() == 1.0
    assert loc.ty.get() == 0.0
    assert loc.tz.get() == 0.0
    pm.saveFile()


def test_fix_reference_namespace_is_working_properly_with_duplicate_refs(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly
    with duplicate references

    version15 -> has no new version
      version11 -> has no new version
        asset2_lookdev_take1_v001 -> has no new version
          version2 -> has no new version
      version11 -> has no new version
        asset2_lookdev_take1_v001 -> has no new version
          version2 -> has no new version

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    data["version15"].is_published = True

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    loc = pm.spaceLocator(name="locator1")
    loc.t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(loc, tra_group)
    pm.saveFile()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # lookdev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    asset2_lookdev_take1_v001_ref_node = refs[0]
    asset2_lookdev_take1_v001_ref_node.namespace = data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be two locators in the current scene
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(1, 0, 0)

    # we should have created an edit
    version2_ref_node = pm.listReferences(asset2_lookdev_take1_v001_ref_node)[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    pm.saveFile()
    pm.newFile(force=True)

    # version15 references version11 two times
    maya_env.open(data["version15"])
    maya_env.reference(data["version11"])
    maya_env.reference(data["version11"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["version11"].filename.replace(".", "_")
    refs[1].namespace = data["version11"].filename.replace(".", "_")
    pm.saveFile()

    DBSession.commit()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].filename.replace(".", "_")
    assert all_refs[1].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # the second copy
    assert all_refs[3].namespace == "%s1" % data["version11"].filename.replace(".", "_")
    assert all_refs[4].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[5].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # now let it be fixed
    maya_env.fix_reference_namespaces()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].latest_published_version.nice_name
    assert (
        all_refs[1].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[2].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name
    assert all_refs[3].namespace == "Test_Task_1_Test_Task_5_Take2"
    assert (
        all_refs[4].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[5].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # now check we don't have any failed edits
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, fld=1)) == 0

    # now check we don't have any failed edits
    assert len(pm.referenceQuery(all_refs[3], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[4], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[5], es=1, fld=1)) == 0

    # and we have all successful edits
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, scs=1)) == 2

    # and we have all successful edits
    assert len(pm.referenceQuery(all_refs[3], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[4], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[5], es=1, scs=1)) == 2

    # and check if the locator is in 1, 0, 0
    locs = pm.ls("locator1", type=pm.nt.Transform, r=1)
    assert locs[0].tx.get() == 1.0
    assert locs[0].ty.get() == 0.0
    assert locs[0].tz.get() == 0.0

    # the second locator
    assert locs[1].tx.get() == 1.0
    assert locs[1].ty.get() == 0.0
    assert locs[1].tz.get() == 0.0
    pm.saveFile()


def test_fix_reference_namespace_is_working_properly_with_shallower_duplicate_refs(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly
    with duplicate references

      version11 -> has no new version ->Layout
        asset2_lookdev_take1_v001 -> has no new version -> LookDev
          version2 -> has no new version -> Model
        asset2_lookdev_take1_v001 -> has no new version
          version2 -> has no new version
        asset2_lookdev_take1_v001 -> has no new version
          version2 -> has no new version
        asset2_lookdev_take1_v001 -> has no new version
          version2 -> has no new version

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    loc = pm.spaceLocator(name="locator1")
    loc.t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(loc, tra_group)
    pm.saveFile()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001 four times
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    refs[1].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    refs[2].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    refs[3].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be four locators in the current scene
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(1, 0, 0)
    loc[1].t.set(2, 0, 0)
    loc[2].t.set(3, 0, 0)
    loc[3].t.set(4, 0, 0)

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    version2_ref_node = pm.listReferences(refs[1])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    version2_ref_node = pm.listReferences(refs[2])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    version2_ref_node = pm.listReferences(refs[3])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    pm.saveFile()
    DBSession.commit()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[1].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # the second copy
    assert all_refs[2].namespace == "%s%s" % (
        data["asset2_lookdev_take1_v001"].filename.replace(".", "_"),
        all_refs[2].copyNumberList()[1],
    )
    assert all_refs[3].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # the third copy
    assert all_refs[4].namespace == "%s%s" % (
        data["asset2_lookdev_take1_v001"].filename.replace(".", "_"),
        all_refs[4].copyNumberList()[2],
    )
    assert all_refs[5].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # the forth copy
    assert all_refs[6].namespace == "%s%s" % (
        data["asset2_lookdev_take1_v001"].filename.replace(".", "_"),
        all_refs[6].copyNumberList()[3],
    )
    assert all_refs[7].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # now let it be fixed
    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    # first copy
    assert (
        all_refs[0].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[1].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # second copy
    assert all_refs[2].namespace == "Asset_2_LookDev_Take2"
    assert all_refs[3].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # third copy
    assert all_refs[4].namespace == "Asset_2_LookDev_Take3"
    assert all_refs[5].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # forth copy
    assert all_refs[6].namespace == "Asset_2_LookDev_Take4"
    assert all_refs[7].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0

    # second copy
    assert len(pm.referenceQuery(all_refs[2], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[3], es=1, fld=1)) == 0

    # third copy
    assert len(pm.referenceQuery(all_refs[4], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[5], es=1, fld=1)) == 0

    # forth copy
    assert len(pm.referenceQuery(all_refs[6], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[7], es=1, fld=1)) == 0

    # and we have all successful edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 2

    # second copy
    assert len(pm.referenceQuery(all_refs[2], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[3], es=1, scs=1)) == 2

    # third copy
    assert len(pm.referenceQuery(all_refs[4], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[5], es=1, scs=1)) == 2

    # forth copy
    assert len(pm.referenceQuery(all_refs[6], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[7], es=1, scs=1)) == 2

    # and check if the locator are where they should be
    locs = pm.ls("locator1", type=pm.nt.Transform, r=1)
    assert locs[0].tx.get() > 0.5
    assert locs[1].tx.get() > 0.5
    assert locs[2].tx.get() > 0.5
    assert locs[3].tx.get() > 0.5
    pm.saveFile()


def test_fix_reference_namespace_is_working_properly_with_refs_with_new_versions(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly
    with references which has new versions

      version11 -> has no new version ->Layout
        asset2_lookdev_take1_v001 -> has no new version -> LookDev
          version2 -> has no new version -> Model -> has a new version3

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    print("version2: {}".format(data["asset2_model_main_v002"]))
    print("version3: {}".format(data["asset2_model_main_v003"]))
    print("version2.full_path: {}".format(data["asset2_model_main_v002"].full_path))
    print("version3.full_path: {}".format(data["asset2_model_main_v003"].full_path))
    data["asset2_model_main_v002"].is_published = True
    data["asset2_model_main_v003"].is_published = True

    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    DBSession.commit()

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    loc = pm.spaceLocator(name="locator1")
    loc.t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(loc, tra_group)
    pm.saveFile()

    # save as version3
    maya_env.save_as(data["asset2_model_main_v003"])
    DBSession.commit()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001 four times
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be four locators in the current scene
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(1, 0, 0)

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    pm.saveFile()
    DBSession.commit()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[1].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # now let it be fixed
    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    # first copy
    assert (
        all_refs[0].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[1].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # check if the reference is created from version2
    assert (
        maya_env.get_version_from_full_path(all_refs[1].path).parent == data["asset2_model_main_v002"]
    )
    # and it is version3
    assert maya_env.get_version_from_full_path(all_refs[1].path) == data["asset2_model_main_v003"]

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0

    # and we have all successful edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 2

    # and check if the locator are where they should be
    locs = pm.ls("locator1", type=pm.nt.Transform, r=1)
    assert 1.0 == locs[0].tx.get()
    pm.saveFile()


def test_fix_reference_namespace_is_working_properly_with_refs_updated_in_a_previous_scene(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly
    with references which are updated in another scene

      version11 -> has no new version ->Layout
        asset2_lookdev_take1_v001 -> has no new version -> LookDev
          version2 -> has no new version -> Model

      version15 -> another scene which is referencing asset2_lookdev_take1_v001
        asset2_lookdev_take1_v001
          version2

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_lookdev_take1_v001"].is_published = True
    DBSession.commit()

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    loc = pm.spaceLocator(name="locator1")
    loc.t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(loc, tra_group)
    pm.saveFile()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be only one locator in the current scene
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(1, 0, 0)

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    pm.saveFile()
    DBSession.commit()

    # version15 also references asset2_lookdev_take1_v001
    pm.newFile(force=True)
    maya_env.open(data["version15"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be only one locator in the current scene
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(0, 1, 0)
    pm.saveFile()

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0
    DBSession.commit()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[1].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # now fix the namespaces in version15 let it be fixed
    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    version15_asset2_lookdev_take1_v001_path = all_refs[0].path
    version15_version2_path = all_refs[1].path

    # first copy
    assert (
        all_refs[0].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[1].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0

    # and we have all successful edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 2

    # and check if the locator are where they should be
    locs = pm.ls("locator1", type=pm.nt.Transform, r=1)
    assert 1.0 == locs[0].ty.get()
    pm.saveFile()

    # now open version11 and try to fix it also there
    maya_env.open(data["version11"])

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[1].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    version11_asset2_lookdev_take1_v001_path = all_refs[0].path
    version11_version2_path = all_refs[1].path

    # first copy
    assert (
        all_refs[0].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[1].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0

    # and we have all successful edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 2

    # and check if the locator are where they should be
    locs = pm.ls("locator1", type=pm.nt.Transform, r=1)
    assert 1.0 == locs[0].tx.get()
    pm.saveFile()

    # check if the two scenes are using the same assets
    assert (
        version15_asset2_lookdev_take1_v001_path
        == version11_asset2_lookdev_take1_v001_path
    )
    assert version15_version2_path == version11_version2_path


def test_fix_reference_namespace_is_working_properly_with_refs_updated_in_a_previous_scene_deeper(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly
    with references which are updated in another scene

    version15 -> Bigger Layout
      version11 -> Layout
        asset2_lookdev_take1_v001 -> LookDev
          version2 -> Model

      version23 -> Another Bigger Layout
        version18 -> Another Layout referencing asset2_lookdev_take1_v001
          asset2_lookdev_take1_v001 -> LookDev
            version2 -> Model

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    data["version15"].is_published = True
    data["version18"].is_published = True
    data["shot3_anim_take1_v002"].is_published = True
    DBSession.commit()

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    loc = pm.spaceLocator(name="locator1")
    loc.t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(loc, tra_group)
    pm.saveFile()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be only one locator in the current scene
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(1, 0, 0)
    pm.saveFile()

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    # version15 references version11
    pm.newFile(force=True)
    maya_env.open(data["version15"])  # bigger layout
    maya_env.reference(data["version11"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["version11"].filename.replace(".", "_")
    # now do some other edits here
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(0, 1, 0)
    pm.saveFile()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].filename.replace(".", "_")
    assert all_refs[1].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # version18 references asset2_lookdev_take1_v001
    pm.newFile(force=True)
    maya_env.open(data["version18"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be only one locator in the current scene
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(0, 0, 1)
    pm.saveFile()

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    # version23 references version18
    pm.newFile(force=True)
    maya_env.open(data["shot3_anim_take1_v002"])  # bigger layout
    maya_env.reference(data["version18"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["version18"].filename.replace(".", "_")
    # now do some other edits here
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(0, 0, 2)
    pm.saveFile()

    DBSession.commit()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version18"].filename.replace(".", "_")
    assert all_refs[1].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # check edits
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, scs=1)) == 2

    # now fix the namespaces in version23 let it be fixed
    assert maya_env.get_current_version() == data["shot3_anim_take1_v002"]
    assert data["shot3_anim_take1_v002"].is_published is True
    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    version23_asset2_lookdev_take1_v001_path = all_refs[1].path
    version23_version2_path = all_refs[2].path

    # first copy
    assert all_refs[0].namespace == data["version18"].latest_published_version.nice_name
    assert (
        all_refs[1].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[2].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, fld=1)) == 0

    # and we have all successful edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, scs=1)) == 3

    # and check if the locator are where they should be
    locs = pm.ls("locator1", type=pm.nt.Transform, r=1)
    assert 2.0 == locs[0].tz.get()
    pm.saveFile()

    # now open version11 and try to fix it also there
    maya_env.open(data["version15"])

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].filename.replace(".", "_")
    assert all_refs[1].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    version15_asset2_lookdev_take1_v001_path = all_refs[1].path
    version15_version2_path = all_refs[2].path

    # first copy
    assert all_refs[0].namespace == data["version11"].latest_published_version.nice_name
    assert (
        all_refs[1].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[2].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, fld=1)) == 0

    # and we have all successful edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, scs=1)) == 3

    # and check if the locator are where they should be
    locs = pm.ls("locator1", type=pm.nt.Transform, r=1)
    assert 1.0 == locs[0].ty.get()
    pm.saveFile()

    # check if the two scenes are using the same assets
    assert (
        version15_asset2_lookdev_take1_v001_path
        == version23_asset2_lookdev_take1_v001_path
    )
    assert version15_version2_path == version23_version2_path


def test_fix_reference_namespace_returns_a_list_of_newly_created_versions(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method will return newly
    created version instances in a list.

      version11 -> has no new version ->Layout
        asset2_lookdev_take1_v001 -> has no new version -> LookDev
          version2 -> has no new version -> Model -> has a new version3

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_model_main_v003"].is_published = True

    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    DBSession.commit()

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    loc = pm.spaceLocator(name="locator1")
    loc.t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(loc, tra_group)
    pm.saveFile()

    # save as version3
    maya_env.save_as(data["asset2_model_main_v003"])

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001 four times
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be four locators in the current scene
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(1, 0, 0)

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    pm.saveFile()
    DBSession.commit()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[1].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # now let it be fixed
    list_of_versions = maya_env.fix_reference_namespaces()

    assert list_of_versions == [
        data["asset2_lookdev_take1_v001"].latest_published_version
    ]


def test_fix_reference_namespace_returned_versions_have_correct_description(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method will return newly
    created version instances in a list.

      version11 -> has no new version ->Layout
        asset2_lookdev_take1_v001 -> has no new version -> LookDev
          version2 -> has no new version -> Model -> has a new version3

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_model_main_v003"].is_published = True

    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    DBSession.commit()

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    loc = pm.spaceLocator(name="locator1")
    loc.t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(loc, tra_group)
    pm.saveFile()

    # save as version3
    maya_env.save_as(data["asset2_model_main_v003"])

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001 four times
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be four locators in the current scene
    loc = pm.ls("locator1", type=pm.nt.Transform, r=1)
    loc[0].t.set(1, 0, 0)

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    pm.saveFile()
    DBSession.commit()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[1].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # now let it be fixed
    maya_env.fix_reference_namespaces()

    assert data["asset2_lookdev_take1_v001"].latest_published_version != data["asset2_lookdev_take1_v001"]
    assert (
        "Automatically created with Fix Reference Namespace"
        == data["asset2_lookdev_take1_v001"].latest_published_version.description
    )


def test_fix_reference_namespace_is_working_properly_with_complex_edits(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly
    with references which are updated in another scene

    version15 -> Bigger Layout -> Move the parent
      version11 -> Layout -> Parent it under a group
        asset2_lookdev_take1_v001 -> LookDev -> Assign new Material
          version2 -> Model

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    data["version15"].is_published = True
    DBSession.commit()

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    cube = pm.polyCube(name="test_cube")
    cube[0].t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(cube[0], tra_group)
    pm.saveFile()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    # assign a new material
    cube = pm.ls("test_cube", type=pm.nt.Transform, r=1)[0]
    blinn, blinn_sg = pm.createSurfaceShader("blinn")
    pm.sets(blinn_sg, e=True, fe=[cube])
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be only one locator in the current scene
    cube = pm.ls("test_cube", type=pm.nt.Transform, r=1)[0]
    # parent it to something else
    pm.group(cube.getParent(), name="test_group")
    cube.t.set(1, 0, 0)
    pm.saveFile()

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    # version15 references version11
    pm.newFile(force=True)
    maya_env.open(data["version15"])  # bigger layout
    maya_env.reference(data["version11"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["version11"].filename.replace(".", "_")
    # now do some other edits here
    group = pm.ls("test_group", type=pm.nt.Transform, r=1)[0]
    # move the one with no parent to somewhere in the scene
    group.t.set(10, 0, 0)
    pm.saveFile()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].filename.replace(".", "_")
    assert all_refs[1].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].filename.replace(".", "_")
    assert all_refs[1].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    # first copy
    assert all_refs[0].namespace == data["version11"].latest_published_version.nice_name
    assert (
        all_refs[1].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[2].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, fld=1)) == 0

    # and we have all successful edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 2
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 1
    assert len(pm.referenceQuery(all_refs[2], es=1, scs=1)) == 5

    # and check if the locator are where they should be
    group = pm.ls("test_group", type=pm.nt.Transform, r=1)[0]
    assert 10.0 == group.tx.get()
    pm.saveFile()


def test_fix_reference_namespace_is_working_properly_with_references_with_no_namespaces(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly
    with references which are not using namespaces

    version15 -> Bigger Layout -> Move the parent / Uses no namespaces
      version11 -> Layout -> Parent it under a group
        asset2_lookdev_take1_v001 -> LookDev -> Assign new Material
          version2 -> Model

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    data["version15"].is_published = True
    DBSession.commit()

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    cube = pm.polyCube(name="test_cube")
    cube[0].t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(cube[0], tra_group)
    pm.saveFile()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    # assign a new material
    cube = pm.ls("test_cube", type=pm.nt.Transform, r=1)[0]
    blinn, blinn_sg = pm.createSurfaceShader("blinn")
    pm.sets(blinn_sg, e=True, fe=[cube])
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use old namespace style
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_lookdev_take1_v001"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be only one locator in the current scene
    cube = pm.ls("test_cube", type=pm.nt.Transform, r=1)[0]
    # parent it to something else
    pm.group(cube.getParent(), name="test_group")
    # pm.parent(cube, group)
    cube.t.set(1, 0, 0)
    pm.saveFile()

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    # version15 references version11
    pm.newFile(force=True)
    maya_env.open(data["version15"])  # bigger layout
    maya_env.reference(data["version11"], use_namespace=False)
    # use no namespace for version11 (so do not edit to old version)
    # now do some other edits here
    group = pm.ls("test_group", type=pm.nt.Transform, r=1)[0]
    # move the one with no parent to somewhere in the scene
    group.t.set(10, 0, 0)
    pm.saveFile()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    #                                                 maya uses filename
    #                                                    |
    #                                                    V
    assert all_refs[0].namespace == data["version11"].filename.split(".")[0]
    assert all_refs[1].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    #                                              still using filename
    #                                                     |
    #                                                     V
    assert all_refs[0].namespace == data["version11"].filename.split(".")[0]

    assert all_refs[1].namespace == data[
        "asset2_lookdev_take1_v001"
    ].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    # first copy
    assert all_refs[0].namespace == data["version11"].filename.split(".")[0]
    assert (
        all_refs[1].namespace
        == data["asset2_lookdev_take1_v001"].latest_published_version.nice_name
    )
    assert all_refs[2].namespace == data["asset2_model_main_v002"].latest_published_version.nice_name

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, fld=1)) == 0

    # # and we have all successful edits
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 2
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 1
    assert len(pm.referenceQuery(all_refs[2], es=1, scs=1)) == 5

    # and check if the locator are where they should be
    group = pm.ls("test_group", type=pm.nt.Transform, r=1)[0]
    assert 10.0 == group.tx.get()
    pm.saveFile()


def test_fix_reference_namespace_is_working_properly_with_references_with_same_namespaces_with_its_children_ref(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly
    with references that has the same namespace with its children

    version15 -> Bigger Layout -> Move the parent
      version11 -> Layout -> Parent it under a group
        asset2_lookdev_take1_v001 -> LookDev -> Assign new Material / using the same
                    namespace with its child
          version2 -> Model

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    data["version15"].is_published = True
    DBSession.commit()

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    cube = pm.polyCube(name="test_cube")
    cube[0].t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(cube[0], tra_group)
    pm.saveFile()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    refs = pm.listReferences()
    ref = refs[0]
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    # assign a new material
    cube = pm.ls("test_cube", type=pm.nt.Transform, r=1)[0]
    blinn, blinn_sg = pm.createSurfaceShader("blinn")
    pm.sets(blinn_sg, e=True, fe=[cube])
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use version2 namespace in asset2_lookdev_take1_v001
    refs = pm.listReferences()
    refs[0].namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be only one locator in the current scene
    cube = pm.ls("test_cube", type=pm.nt.Transform, r=1)[0]
    # parent it to something else
    pm.group(cube.getParent(), name="test_group")
    # pm.parent(cube, group)
    cube.t.set(1, 0, 0)
    pm.saveFile()

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    # version15 references version11
    pm.newFile(force=True)
    maya_env.open(data["version15"])  # bigger layout
    maya_env.reference(data["version11"])
    # use old style namespace here
    refs = pm.listReferences()
    refs[0].namespace = data["version11"].filename.replace(".", "_")
    # now do some other edits here
    group = pm.ls("test_group", type=pm.nt.Transform, r=1)[0]
    # move the one with no parent to somewhere in the scene
    group.t.set(10, 0, 0)
    pm.saveFile()

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].filename.replace(".", "_")

    # asset2_lookdev_take1_v001 is using version2 namespace
    assert all_refs[1].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # check namespaces
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].filename.replace(".", "_")

    # asset2_lookdev_take1_v001 is using version2 filename
    assert all_refs[1].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    # first copy
    assert all_refs[0].namespace == data["version11"].nice_name
    assert all_refs[1].namespace == data["asset2_lookdev_take1_v001"].nice_name
    assert all_refs[2].namespace == data["asset2_model_main_v002"].nice_name

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, fld=1)) == 0

    # and we have all successful edits
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 2
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 1
    assert len(pm.referenceQuery(all_refs[2], es=1, scs=1)) == 5

    # and check if the locator are where they should be
    group = pm.ls("test_group", type=pm.nt.Transform, r=1)[0]
    assert 10.0 == group.tx.get()
    pm.saveFile()


def test_fix_reference_namespace_is_working_properly_with_references_with_same_namespaces_with_its_children_ref_in_a_shallower_setup(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly
    with references that has the same namespace with its children in a
    shallower setup

    version11 -> Layout -> Parent it under a group
      asset2_lookdev_take1_v001 -> LookDev -> Assign new Material / using the same
                  namespace with its child
        version2 -> Model

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    DBSession.commit()

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    cube = pm.polyCube(name="test_cube")[0]
    cube.t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(cube, tra_group)
    pm.runtime.DeleteHistory()
    pm.saveFile()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    ref = maya_env.reference(data["asset2_model_main_v002"])
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    # assign a new material
    cube = pm.ls("test_cube", type=pm.nt.Transform, r=1)[0]
    blinn, blinn_sg = pm.createSurfaceShader("blinn")
    pm.sets(blinn_sg, e=True, fe=[cube])
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    ref = maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use version2 namespace in asset2_lookdev_take1_v001
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    # now do the edits here
    # we need to do some edits
    # there should be only one locator in the current scene
    from anima.dcc.mayaEnv import auxiliary
    ref_root_nodes = auxiliary.get_root_nodes(ref)
    # parent it to something else
    pm.group(ref_root_nodes, name="test_group")
    ref_root_nodes[0].t.set(1, 0, 0)
    pm.saveFile()

    # we should have created an edit
    version2_ref_node = pm.listReferences(ref)[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    # check namespaces
    all_refs = pm.listReferences(recursive=1)

    # asset2_lookdev_take1_v001 is using version2 namespace
    assert all_refs[0].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")
    assert all_refs[1].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    # check namespaces
    # asset2_lookdev_take1_v001 is using version2 filename
    assert all_refs[0].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")
    assert all_refs[1].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    # first copy
    assert all_refs[0].namespace == data["asset2_lookdev_take1_v001"].nice_name
    assert all_refs[1].namespace == data["asset2_model_main_v002"].nice_name

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0

    # and we have all successful edits
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 1
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 5

    # and check if the locator are where they should be
    pm.saveFile()


def test_fix_reference_namespace_is_working_properly_with_references_with_correct_namespaces_but_has_wrong_namespace_children(
    create_test_data, create_pymel, create_maya_env
):
    """testing if the fix_reference_namespace method is working properly
    with references that has the same namespace with its children

    version15 -> Bigger Layout
      version11 -> Layout -> uses correct namespace
        asset2_lookdev_take1_v001 -> LookDev -> uses correct namespace
          version2 -> Model -> uses wrong namespace

    All uses wrong namespaces
    """
    data = create_test_data
    pm = create_pymel
    maya_env = create_maya_env
    # create deep reference
    data["asset2_model_main_v002"].is_published = True
    data["asset2_lookdev_take1_v001"].is_published = True
    data["version11"].is_published = True
    data["version15"].is_published = True
    DBSession.commit()

    # open version2 and create a locator
    maya_env.open(data["asset2_model_main_v002"])  # model
    cube = pm.polyCube(name="test_cube")
    cube[0].t.set(0, 0, 0)
    tra_group = pm.nt.Transform(name="asset1")
    pm.parent(cube[0], tra_group)
    pm.saveFile()

    # asset2_lookdev_take1_v001 references version2
    maya_env.open(data["asset2_lookdev_take1_v001"])  # look dev
    ref = maya_env.reference(data["asset2_model_main_v002"])
    # change the namespace to old one
    isinstance(ref, pm.system.FileReference)
    ref.namespace = data["asset2_model_main_v002"].filename.replace(".", "_")
    # assign a new material
    cube = pm.ls("test_cube", type=pm.nt.Transform, r=1)[0]
    blinn, blinn_sg = pm.createSurfaceShader("blinn")
    pm.sets(blinn_sg, e=True, fe=[cube])
    pm.saveFile()

    # version11 references asset2_lookdev_take1_v001
    pm.newFile(force=True)
    maya_env.open(data["version11"])  # layout
    maya_env.reference(data["asset2_lookdev_take1_v001"])
    # use version2 namespace in asset2_lookdev_take1_v001
    refs = pm.listReferences()
    # refs[0].namespace = data["asset2_lookdev_take1_v001"].nice_name
    # now do the edits here
    # we need to do some edits
    # there should be only one locator in the current scene
    cube = pm.ls("test_cube", type=pm.nt.Transform, r=1)[0]
    # parent it to something else
    pm.group(cube.getParent(), name="test_group")
    cube.t.set(1, 0, 0)
    pm.saveFile()

    # we should have created an edit
    version2_ref_node = pm.listReferences(refs[0])[0]
    edits = pm.referenceQuery(version2_ref_node, es=1)
    assert len(edits) > 0

    # version15 references version11
    pm.newFile(force=True)
    maya_env.open(data["version15"])  # bigger layout
    maya_env.reference(data["version11"])
    # use old style namespace here
    pm.listReferences()
    # refs[0].namespace = data["version11"].nice_name
    # now do some other edits here
    group = pm.ls("test_group", type=pm.nt.Transform, r=1)[0]
    # move the one with no parent to somewhere in the scene
    group.t.set(10, 0, 0)
    pm.saveFile()

    # check namespaces
    # version11 is using correct namespace
    all_refs = pm.listReferences(recursive=1)
    assert all_refs[0].namespace == data["version11"].nice_name

    # asset2_lookdev_take1_v001 is using correct namespace
    assert all_refs[1].namespace == data["asset2_lookdev_take1_v001"].nice_name
    assert all_refs[2].namespace == data["asset2_model_main_v002"].filename.replace(".", "_")

    maya_env.fix_reference_namespaces()
    pm.saveFile()

    # check if the namespaces are fixed
    all_refs = pm.listReferences(recursive=1)

    # first copy
    assert all_refs[0].namespace == data["version11"].nice_name
    assert all_refs[1].namespace == data["asset2_lookdev_take1_v001"].nice_name
    assert all_refs[2].namespace == data["asset2_model_main_v002"].nice_name

    # now check we don't have any failed edits
    # first copy
    assert len(pm.referenceQuery(all_refs[0], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[1], es=1, fld=1)) == 0
    assert len(pm.referenceQuery(all_refs[2], es=1, fld=1)) == 0

    # and we have all successful edits
    assert len(pm.referenceQuery(all_refs[0], es=1, scs=1)) == 2
    assert len(pm.referenceQuery(all_refs[1], es=1, scs=1)) == 1
    assert len(pm.referenceQuery(all_refs[2], es=1, scs=1)) == 5

    # and check if the locator are where they should be
    group = pm.ls("test_group", type=pm.nt.Transform, r=1)[0]
    assert 10.0 == group.tx.get()
    pm.saveFile()
