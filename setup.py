# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os.path
from setuptools import setup, find_packages
import anima


def read(fname):
    """Utility function to read the README file.

    Used for the long_description.  It's nice, because now:

      1) we have a top level README file and
      2) it's easier to type in the README file than to put a raw string in
         below ...

    :param str fname: the file name
    :return:
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="anima",
    version=anima.__version__,
    authors=["Erkan Ozgur Yilmaz"],
    author_emails=["eoyilmaz@gmail.com"],
    description="VFX and Animation pipeline developed in Anima Istanbul",
    long_description=read("README"),
    keywords=["animation", "character", "studio", "vfx", "pipeline"],
    packages=find_packages(exclude=["tests*"]),
    platforms=["any"],
    url="https://github.com/eoyilmaz/anima",
    license="http://www.opensource.org/licenses/bsd-license.php",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    requires=['stalker', 'edl', 'timecode', 'sqlalchemy', 'pillow', 'exifread',
              'jinja2', 'pytz'],
    install_requires=['stalker', 'edl', 'timecode', 'sqlalchemy'],
    test_requires=['pytest', 'pytest-xdist', 'coverage', 'pytest-cov']
)

