# -*- coding:utf-8 -*-

import os
import nuke

# create environment variables
from anima import utils

utils.do_db_setup()

# iterate over environment and set it in TCL
for key, value in os.environ.iteritems():
    try:
        nuke.tcl("set", str(key), str(value))
    except RuntimeError:
        pass


def filter_env_vars_in_filepath(filename):
    """Expand variables in path such as ``$PROJECT_ROOT``."""
    import os

    expanded_path = os.path.expandvars(filename)
    return expanded_path


# register callback
nuke.addFilenameFilter(filter_env_vars_in_filepath)
