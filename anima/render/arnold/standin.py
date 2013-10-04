# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
# 
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

class StandIn(object):
    """Manages Arnold stand ins in a Maya scene.

    Loads or unloads an arnold standin to be modified in the current scene (as
    in Katana). So it gives the user the ability to change the standin on the
    fly.

    
    """

    def __init__(self):
        self.standing_path = None
        self.original_file_path = None

        self.proxy_geomety = None

    
