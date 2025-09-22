#!/usr/bin/env python3
"""Setup for SoundScope player"""

#
#    setup.py
#
#    ----------------------------------------------------------------------
#    Copyright © 2022, 2023, 2024, 2025  Pellegrino Prevete
#
#    All rights reserved
#    ----------------------------------------------------------------------
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from os.path import join as _path_join
from pathlib import Path
from platform import system, machine
from setuptools import setup, find_packages

def _text_load(
      _file_path):
  with open(
         _file_path,
         "r") as fh:
    _text = fh.read()
  return _text

long_description = _text_load(
  "README.md")
data_files = []

# Variables
theme_dir = "data/icons/hicolor"
hicolor_path = "share/icons/hicolor"

# Auxiliary functions
# for paths
in_hicolor_src = lambda x: _path_join(
                             theme_dir,
                             x)
in_hicolor = lambda x: _path_join(
                         hicolor_path,
                         x)

# to install data files
encode = lambda src, dest: (dest,
                            [src])
add_data_file = lambda src, dest: data_files.append(
                                    encode(src,
                                           dest))

# to install icons
def encode_icon(
      icon):
  icon_path = str(
                Path(
                  icon).parents[
                    0])
  return encode(
           in_hicolor_src(
             icon),
           in_hicolor(
             icon_path))
add_icon = lambda icon: data_files.append(
                          encode_icon(
                            icon))

add_data_file(
  'data/com.sony.SoundScopePlayer.desktop',
  'share/applications'
)
icons = [
  'scalable/apps/com.sony.SoundScopePlayer.svg',
]

for _icon in icons:
  add_icon(
    _icon)

_setup_kwargs = {
  "name":
    "SoundScope Player",
  "version":
    "1.0",
  "author":
    "Pellegrino Prevete",
  "author_email":
    "pellegrinoprevete@gmail.com",
  "description":
    "SoundScope PlayStation media player",
  "long_description":
    long_description,
  "long_description_content_type":
    "text/markdown",
  "url":
    "https://github.com/tallero/soundscope-player",
  "packages":
    find_packages(),
  "package_data": {
    '': ['settings.ini'],
  },
  "data_files":
    data_files,
  "entry_points": {
    'console_scripts': [
      'soundscope-player = soundscope:_main']
  },
  "install_requires": [
    'appdirs',
  ],
  "classifiers": [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    "Operating System :: Unix",
  ]
}

setup(
  **_setup_kwargs)
