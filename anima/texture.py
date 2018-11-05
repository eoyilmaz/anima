# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


class ReferenceManager(object):
    """Manages references in the current maya scene.

    Can bake reference edits to new versions and automatically updates the
    referenced version with the latest one.

    Can check texture file versions. Uses a naming convention which ends with
    {TextureName}_v###.{ext}. The texture name is not important it should only
    have a version part, so that it can find new versions by traversing the
    texture folder.
    """
    pass


class Reference(object):
    """A Reference which also knows about Stalker

    A Reference in Anima is anything external to the current scene. It can be
    a FileReference or it can be a FileTexture or a FileCache which may be is
    an Alembic file or an FBX file.

    Any reference can directly or indirectly related to a Stalker Version. Any
    output of a Version instance can be considered as a Reference for the
    current scene.

    Any edits to a reference (especially if it is a FileReference) can be baked
    as a new version to the original one.
    """
    pass


class TicketGenerator(object):
    """Generates Stalker Tickets and communicates with Stalker Pyramid server.

    This class isolates all the technical detail about creating and sending a
    Ticket about a Reference to Stalker Pyramid server.
    """
    pass

