# SPDX-License-Identifier: GPL-3.0-or-later

#    ----------------------------------------------------------------------
#    Copyright © 2024, 2025  Pellegrino Prevete
#
#    All rights reserved
#    ----------------------------------------------------------------------
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

PREFIX ?= /usr/local
_PROJECT=soundscope-player
BIN_DIR=$(DESTDIR)$(PREFIX)/bin
DOC_DIR=$(DESTDIR)$(PREFIX)/share/doc/$(_PROJECT)
MAN_DIR?=$(DESTDIR)$(PREFIX)/share/man

_INSTALL_FILE=\
  install \
    -vDm644
_INSTALL_DIR=\
  install \
    -vdm755
_INSTALL_EXE=\
  install \
    -vDm755

DOC_FILES=\
  $(wildcard *.rst) \
  $(wildcard *.md)

_PYTHON_FILES=\
  soundscope-player

_INSTALL_DOC_TARGETS=\
  install-doc \
  install-man
_INSTALL_TARGETS=\
  install-program \
  install-android \
  $(_INSTALL_DOC_TARGETS)
_INSTALL_TARGETS_ALL=\
  install \
  $(_INSTALL_TARGETS)
_PHONY_TARGETS=\
  $(_INSTALL_TARGETS_ALL)

install: $(_INSTALL_TARGETS)

install-program:

	python \
	  "setup.py" \
	    install \
	    --root="$(DESTDIR)" \
	    --optimize=1

install-android:

	install \
	  -vDm755 \
	  "$(_PROJECT)/$(_PROJECT)-retroarch" \
	  "$(BIN_DIR)/$(_PROJECT)-retroarch"

install-doc:

	$(_INSTALL_FILE) \
	  $(DOC_FILES) \
	  -t \
	  "$(DOC_DIR)/"

install-man:

	$(_INSTALL_DIR) \
	  "$(MAN_DIR)/man1"
	rst2man \
	  "man/$(_PROJECT).1.rst" \
	  "$(MAN_DIR)/man1/$(_PROJECT).1"

.PHONY: $(_PHONY_TARGETS)
