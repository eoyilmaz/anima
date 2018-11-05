# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Sets up a vertigo setup in the camera
"""

import pymel.core as pm


vertigo_attr_name = "vertigo_loc"
vertigo_global_attr_name = "vertigo_global_loc"


def setup_look_at(camera):
    """sets up the look at locator for the given camera
    """

    # just create a locator under the camera
    # and move it to -10

    loc = pm.spaceLocator(n=camera.name() + "vertigo_loc#")

    # create a new attribute under the camera
    global vertigo_attr_name

    camera_shape = camera.getShape()

    if not camera.hasAttr(vertigo_attr_name):
        pm.addAttr(camera, ln=vertigo_attr_name, at="message")

    # connect the message attribute of the locator to the camera
    loc.message >> camera.attr(vertigo_attr_name)

    pm.parent(loc, camera)

    loc.t.set(0, 0, -10)
    loc.r.set(0, 0, 0)

    # lock locators tx, ty and rotate channels
    loc.tx.lock()
    loc.ty.lock()
    loc.r.lock()


def setup_vertigo(camera):
    """sets up the vertigo for the given camera
    """

    # camera should have the vertigo locator

    global vertigo_attr_name
    global vertigo_global_attr_name

    vertigo_loc = camera.attr(vertigo_attr_name).inputs()[0]

    # get the initial distance of the vertigo locator
    z1 = vertigo_loc.tz.get()
    f1 = camera.focalLength.get()

    # create a locator under world to hold the locator at the same place
    world_loc = pm.spaceLocator(n=camera.name() + "vertigo_space_loc#")

    # connect world_loc to camera
    if not camera.hasAttr(vertigo_global_attr_name):
        pm.addAttr(camera, ln=vertigo_global_attr_name, at="message")

    world_loc.message >> camera.attr(vertigo_global_attr_name)

    # position the world_loc to the correct place
    pm.parent(world_loc, vertigo_loc)
    world_loc.t.set(0, 0, 0)
    world_loc.r.set(0, 0, 0)
    pm.parent(world_loc, w=True)

    # unlock vertigo_loc's translate
    vertigo_loc.tx.unlock()
    vertigo_loc.ty.unlock()

    pm.pointConstraint(world_loc, vertigo_loc)

    # create the expression
    expr_str = camera.name() + ".focalLength = (" + vertigo_loc.name() + \
        ".tz / " + str(z1) + ") * " + str(f1) + ";"

    expr = pm.expression(s=expr_str)


def delete(camera):
    """deletes the vertigo setup from the given camera
    """

    global vertigo_attr_name
    global vertigo_global_attr_name

    camera_shape = camera.getShape()

    expression = camera_shape.connections(type=pm.nt.Expression)
    vertigo_loc = camera.attr(vertigo_attr_name).inputs()[0]
    world_loc = camera.attr(vertigo_global_attr_name).inputs()[0]

    # delete them
    pm.delete(expression)
    pm.delete(vertigo_loc)
    pm.delete(world_loc)
