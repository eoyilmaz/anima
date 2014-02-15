# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


def empty_reference_resolution(root=None, leave=None, update=None, create=None):
    """Generates an empty reference_resolution dictionary.

    Generates a ``Reference Resolution`` dictionary, where there are keys like
    'root', 'leave', 'update', 'create' showing:

    root: the versions referenced directly to the root,
    leave: Versions those doesn't have any new versions,
    update: Versions does have an updated version,
    create: Versions that should be updated by creating a new published version
      because its references has updated versions.

    :return: dict
    """
    if root is None:
        root = []

    if leave is None:
        leave = []

    if update is None:
        update = []

    if create is None:
        create = []

    return {
        'root': root,
        'leave': leave,
        'update': update,
        'create': create
    }
