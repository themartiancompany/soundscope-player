#!/usr/bin/env python3
"""SoundScope PlayStation media player."""

#
#    soundscope_player.py
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

from appdirs import *
from argparse import ArgumentParser
from copy import deepcopy as cp
import os
from mkaudiocdrimg.mkaudiocdrimg import _mkimg as _mkimg
from platform import system as _system
import glob
from os import getcwd, listdir, makedirs, umask
from os.path import abspath, basename, exists, dirname, isdir, realpath
from os.path import join as _path_join
from pathlib import Path
from shutil import which
import subprocess
from subprocess import run as _sh
import sys

_app_id = "com.sony.SoundScopePlayer"
app_details = (
  "soundscope-player",
  "Pellegrino Prevete"
)

def _is_android():
  if hasattr(
       sys,
       'getandroidapilevel'):
    return True
  else:
    return False

def _cache_dir_get():
  if _is_android():
    _android_dir = "/storage/emulated/0/Android"
    _cache_dir = _path_join(
                   f"{_android_dir}",
                   "media",
                   _app_id)
  else:
    _cache_dir = user_cache_dir(
                   *app_details)
  return _cache_dir

dirs = {
  'data':
    user_data_dir(
      *app_details),
  'config':
    user_config_dir(
      *app_details),
  'cache':
    _cache_dir_get()
}

def _requirements_os():
  if not (_is_android()):
    from gi import require_version
    require_version(
      "Gtk",
      '3.0')
    from gi.repository import Gtk

def _msg_print(
      _type,
      _msg):
  print(
    f"[soundscope-player]: {_type}: {_msg}")

def _msg_info(
      _msg):
  _msg_print(
    "INFO",
    _msg)

def _msg_error(
      _msg,
      _exit):
  _msg_print(
    "ERROR",
    _msg)
  if (_exit != 0):
    exit(
      _exit)

def _zenity_err(
      msg):
  _zenity_cmd = [
    "zenity",
    "--icon=input-gaming",
    f"--error={msg}"
  ]
  _sh(
    _zenity_cmd)

def _requirements_check():
  _requirements_os()
  if which(
       "zenity"):
    _print_err = _zenity_err
  else:
    _print_err = print
  _programs_gnu = [
    'duckstation-nogui'
  ]
  if not _is_android():
    for p in _programs_gnu:
      if not which(p):
        _msg_error(
          (f"This program needs '{p}' to work. "
           "Please install it."),
          0)
  _ds_dirs = (
    _path_join(
      user_data_dir(
        "duckstation",
        "Connor McLaughlin"),
      "bios"),
      "/usr/share/psx/bios",
      "/data/data/com.termux/files/usr/share/psx/bios"
  )
  _ds_dirs_existing = []
  for _dir in _ds_dirs:
    if exists(
         _dir):
      _ds_dirs_existing.append(
        _dir)
  if not any("ps-20e.bin" in listdir(d) for d in _ds_dirs_existing):
    _msg_error(
      ("No SoundScope-enabled PlayStation bios found."
       "Install `psx-bios` from the Ur."),
      1)

def set_dirs(
      tmp_dir=dirs['cache']):
  _original_umask = umask(0)
  path = _path_join(
           tmp_dir,
           "convert")
  for d in dirs:
    try:
      makedirs(
        dirs[
          d],
        0o700,
        exist_ok=True)
    except OSError:
      pass
  umask(
    _original_umask)

def _clean_cache():
  files = glob.glob(
            f"{dirs['cache']}/*")
  for _file in files:
    print(
      _file)

def _fiximg(
      cue):
  with open(
         cue,
         "r") as handle:
    text = handle.read()
  with open(
         cue,
         "w") as handle:
    handle.write(
      text.replace(
        "WAVE",
        "BINARY"))

def _retroarch_launch(
      _cue,
      _verbose=False):
  _activity = "'com.retroarch/.browser.retroactivity.RetroActivityFuture'"
  _cores_path = "/data/user/0/com.retroarch/cores"
  _core_name = "pcsx_rearmed"
  _core = _path_join(
            _cores_path,
            f"{_core_name}_libretro_android.so")
  _retroarch_cmd = [
    "am",
      "start",
        "-a",
          "'android.intent.action.MAIN'",
        "-n",
          _activity,
        "-e",
          'ROM',
          f"'{_cue}'",
        "-e",
          'LIBRETRO',
          f"'{_core}'"
  ]
  _retroarch_cmd_string = " ".join(
                                _retroarch_cmd)
  _cmd = [
    "su",
      "-c",
        _retroarch_cmd_string
  ]
  if _verbose:
    _msg_info(
      f"Running '{_cmd}'.")
  _sh(
    _cmd)

def play(
      *_media_src,
      _verbose=False):
  _ds_settings = _path_join(
                   dirname(
                     realpath(
                       __file__)),
                   "settings.ini")
  set_dirs()
  _mkimg_kwargs = {
    "_out_dir":
      dirs['cache'],
    "_image_name":
      "playback",
    "_verbose":
      _verbose
  }
  if _verbose:
    _playlist = " ".join(
                  _media_src)
    _msg_info(
      f"Playing '{_playlist}'.")
  _mkimg(
    *_media_src,
    **_mkimg_kwargs)
  _cue = _path_join(
          dirs[
            'cache'],
          "playback.cue")
  _fiximg(
    _cue)
  if ( not _is_android()):
    _ds_cmd = [
      "duckstation-nogui",
      "-settings",
        _ds_settings,
      _cue
    ]
    _cmd = _ds_cmd
    _sh(
      _cmd)
  else:
    _retroarch_launch(
      _cue,
      _verbose)
  _clean_cache()

def on_activate(
      app,
      media_prompt):
  response = media_prompt.run()
  if response  == Gtk.ResponseType.OK:
    app.filenames = media_prompt.get_filenames()
    print(
      f"File(s) selected: '{app.filenames}'.")
  elif response == Gtk.ResponseType.CANCEL:
    print(
      "Canceled.")
    media_prompt.hide()
  return True

def _select_media():
  _app = Gtk.Application(
          application_id=_app_id)
  _win = Gtk.ApplicationWindow(
          application=_app)
  _dialog_kwargs = {
    "title":
      "Select media files",
    "parent":
      _win,
    "action":
      Gtk.FileChooserAction.OPEN
  }
  _dialog_buttons = (
    Gtk.STOCK_CANCEL,
    Gtk.ResponseType.CANCEL,
    Gtk.STOCK_OPEN,
    Gtk.ResponseType.OK
  )
  _media_prompt = Gtk.FileChooserDialog(
                   **_dialog_kwargs)
  _media_prompt.add_buttons(
    *_dialog_buttons)
  _media_prompt.set_select_multiple(
    True)
  _app.connect(
    "activate",
    on_activate,
    _media_prompt)
  _app.run(
    None)
  return _app.filenames

def _main():
  _requirements_check()
  _parser_args = {
    "description":
      "PlayStation SoundScope player"
  }
  _parser = ArgumentParser(
             **_parser_args)
  _media_source = {
    'args':
      ['media_source'],
    'kwargs': {
      'nargs':
        '*',
      'action':
        'store',
      'help':
        ("media source; "
         "default: current directory")
    }
  }
  _verbose = {
    'args': [
      '--verbose'],
    'kwargs': {
      'dest':
        'verbose',
      'action':
        'store_true',
      'default':
        False,
      'help':
        ("verbose output; "
         "default: False")
    }
  }
  _parser.add_argument(
    *_media_source[
      'args'],
    **_media_source[
      'kwargs'])
  _parser.add_argument(
    *_verbose[
      'args'],
    **_verbose[
      'kwargs'])
  _args = _parser.parse_args()
  if not _args.media_source:
    if (not _is_android()):
      _media_source = _select_media()
    else:
      _msg_error(
        "To be implemented.",
        1)
  else:
    _media_source = _args.media_source
  play(
    *_media_source,
    _verbose=_args.verbose)
