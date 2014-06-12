# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import re
import itertools
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def all_equal(elements):
    """return True if all the elements are equal, otherwise False.
    """
    first_element = elements[0]

    for other_element in elements[1:]:
        if other_element != first_element: return False

    return True


def common_prefix(*sequences):
    """return a list of common elements at the start of all sequences, then a
    list of lists that are the unique tails of each sequence.
    """
    # if there are no sequences at all, we're done
    if not sequences: return [], []
    # loop in parallel on the sequences
    common = []
    for elements in itertools.izip(*sequences):
        # unless all elements are equal, bail out of the loop
        if not all_equal(elements):
            break

        # got one more common element, append it and keep looping
        common.append(elements[0])

    # return the common prefix and unique tails
    return common, [sequence[len(common):] for sequence in sequences]


def relpath(p1, p2, sep=os.path.sep, pardir=os.path.pardir):
    """return a relative path from p1 equivalent to path p2.

    In particular:

        the empty string, if p1 == p2;
        p2, if p1 and p2 have no common prefix.

    """
    # replace any trailing slashes at the end
    p1 = re.sub(r"[/]+$", "", p1)
    p1 = re.sub(r"[\\]+$", "", p1)

    common, (u1, u2) = common_prefix(p1.split(sep), p2.split(sep))
    if not common:
        return p2  # leave path absolute if nothing at all in common

    return sep.join([pardir] * len(u1) + u2)


def open_browser_in_location(path):
    """Opens the os native browser at the given path

    :param path: The path that the browser should be opened at.
    """
    import os
    import subprocess
    import platform

    command = []

    platform_info = platform.platform()

    path = os.path.normpath(path)

    if not os.path.exists(path):
        path = os.path.dirname(path)

    if platform_info.startswith('Linux'):
        command = 'nautilus ' + path
    elif platform_info.startswith('Windows'):
        if os.path.isdir(path):
            command = 'explorer ' + path.replace('/', '\\')
        elif os.path.isfile(path):
            command = 'explorer /select,' + path.replace('/', '\\')
    elif platform_info.startswith('Darwin'):
        # TODO: finder can not open files for now, fix it later
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        command = 'open -a /System/Library/CoreServices/Finder.app ' + path

    if os.path.exists(path):
        subprocess.call(command, shell=True)
    else:
        raise IOError("%s doesn't exists!" % path)


def md5_checksum(path):
    """generates md5 of a file with the given path

    :param path: absolute path to  the file
    """
    import hashlib

    m = hashlib.md5()
    with open(path) as f:
        chunk = f.read(8192)
        while chunk:
            m.update(chunk)
            chunk = f.read(8192)
    return m.digest()


class StalkerThumbnailCache(object):
    """A simple file cache system
    """

    @classmethod
    def get(cls, thumbnail_full_path):
        """returns the file either from cache or from stalker server
        """
        import anima

        # look up in the cache first
        filename = os.path.basename(thumbnail_full_path)
        logger.debug('filename : %s' % filename)

        cache_path = os.path.expanduser(anima.local_cache_folder)
        cached_file_full_path = os.path.join(cache_path, filename)

        url = anima.stalker_server_address + '/' + thumbnail_full_path

        logger.debug('cache_path            : %s' % cache_path)
        logger.debug('cached_file_full_path : %s' % cached_file_full_path)
        logger.debug('url                   : %s' % url)

        if not os.path.exists(cached_file_full_path):
            # download the file and put it on to the cache
            import urllib2

            response = urllib2.urlopen(url)
            data = response.read()
            # put it in to a file
            # TODO: from header decide ascii or binary mode
            if not os.path.exists(cache_path):
                os.makedirs(cache_path)

            with open(cached_file_full_path, 'wb') as f:
                f.write(data)

        return cached_file_full_path
