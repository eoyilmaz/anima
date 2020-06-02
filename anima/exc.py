# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Anima Istanbul
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
"""This module contains exceptions
"""


class PublishError(RuntimeError):
    """Raised when the published version is not matching the quality
    """
    pass
