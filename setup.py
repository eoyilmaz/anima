# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os.path
from setuptools import setup, find_packages
import anima

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

required_packages = [
    'stalker'
]

setup(name="anima",
      version=anima.__version__,
      authors=["Eda Gokce", "Erkan Ozgur Yilmaz"],
      author_emails=["anima.eda@gmail.com", "eoyilmaz@gmail.com"],
      description=("VFX and animation tools used in Anima Istanbul"),
      long_description=read("README"),
      keywords=["animation", "character", "studio", "vfx", "pipeline"],
      packages=find_packages(exclude=["tests*"]),
      platforms=["any"],
      url="http://code.google.com/p/anima-tools/",
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
      requires=required_packages,
      install_requires=required_packages,
)

