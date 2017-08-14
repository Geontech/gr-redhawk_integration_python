# This file is protected by Copyright. Please refer to the COPYRIGHT file
# distributed with this source distribution.
#
# This file is part of Geon's GNURadio-REDHAWK.
#
# GNURadio-REDHAWK is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# GNURadio-REDHAWK is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

.PHONY: all install uninstall

BUILD_DIR := build

all:
	@[ -f `which cmake` ] || { echo "Install cmake first"; exit 1; }
	@[ -f `which grcc` ] || { echo "Install GNURadio first"; exit 1; }
	@[ -d $(BUILD_DIR) ] || mkdir $(BUILD_DIR)
	@pushd $(BUILD_DIR); cmake -Wno-dev ..; make; popd

install: all
	@pushd $(BUILD_DIR); make install; popd

uninstall: all
	@pushd $(BUILD_DIR); make uninstall; popd
