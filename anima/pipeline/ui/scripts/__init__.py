# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""
This package contains scripts to be used inside host environment to initialize
the UI.
"""
from sqlalchemy.exc import UnboundExecutionError


def do_db_setup():
    """the common routing for setting up the database
    """
    from stalker import db
    from stalker.db import DBSession

    DBSession.remove()
    DBSession.close()

    try:
        conn = DBSession.connection()
        print 'already connected, not creating any new connections'
    except UnboundExecutionError:
        # no connection do setup
        print 'doing a new connection'
        db.setup()