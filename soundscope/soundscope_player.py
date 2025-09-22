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
from mkaudiocdrimg import _mkimg as _mkimg
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
dirs = {
  'data':
    user_data_dir(
      *app_details),
  'config':
    user_config_dir(
      *app_details),
  'cache':
    user_cache_dir(
      *app_details)
}

def _is_android():
  if hasattr(
       sys,
       'getandroidapilevel'):
    return True
  else:
    return False

def _requirements_os():
  if not (_is_android()):
    from gi import require_version
    require_version(
      "Gtk",
      '3.0')
    from gi.repository import Gtk

def _msg_err(
      _msg,
      _exit):
  _print_err(
    _msg)
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
  programs = [
    'duckstation-nogui'
  ]
  for p in programs:
    if not which(p):
      _msg_err(
        (f"This program needs '{p}' to work."
         "Please install it."),
        0)
    ds_dirs = (
      _path_join(
        user_data_dir(
          "duckstation",
          "Connor McLaughlin"),
        "bios"),
        "/usr/share/psx/bios"
    )
    if not any("ps-20e.bin" in listdir(d) for d in ds_dirs):
      _msg_err(
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
      _cue):
  _activity = 'com.retroarch/.browser.retroactivity.RetroActivityFuture'
  _cores_path = "/data/user/0/com.retroarch/cores"
  _core_name = "pcsx_rearmed"
  _core = _path_join(
            _cores_path,
            f"{_core_name}_libretro_android.so")
  _retroarch_cmd = [
    "am",
      "start",
        "-a",
          "android.intent.action.MAIN",
        "-n",
          _activity,
        "-e",
          'ROM',
          _cue,
        "-e",
          'LIBRETRO',
          _core
  ]
  _retroarch_cmd_string = " ".join(
                                _cmd)
  _cmd = [
    "su",
      "-c",
        _retroarch_cmd_string
  ]
  _sh(
    _cmd)

def play(
      *media_src):
  ds_settings = _path_join(
                  dirname(
                    realpath(
                      __file__)),
                  "settings.ini")
  set_dirs()
  _mkimg(
    *media_src,
    out_dir=dirs['cache'],
    image_name="playback")
  _cue = _path_join(
          dirs[
            'cache'],
          "playback.cue")
  _fiximg(
    _cue)
  _ds_cmd = [
    "duckstation-nogui",
    "-settings",
      ds_settings,
    _cue
  ]
  if ( not _is_android()):
    _cmd = _ds_cmd
    _sh(
      _cmd)
  else:
    _retroarch_launch(
      _cue)
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
  _parser.add_argument(
    *_media_source[
      'args'],
    **_media_source[
      'kwargs'])
  _args = _parser.parse_args()
  if not _args.media_source:
    if (not _is_android()):
      _media_source = _select_media()
  else:
    _media_source = _args._media_source
  if (not _is_android()):
    play(
      *_media_source)
  else:
    _msg_err(
      "To be implemented.",
      1)
