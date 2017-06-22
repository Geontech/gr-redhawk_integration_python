#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 Thomas Goodwin and Geon Technologies
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy

GR_COMPLEX = 'complex'
GR_FLOAT   = 'float'
GR_INT     = 'int'
GR_SHORT   = 'short'
GR_BYTE    = 'byte'

SUPPORTED_GR_TYPES = {
    GR_COMPLEX: numpy.complex,
    GR_FLOAT:   numpy.float32,
    GR_INT:     numpy.int32,
    GR_SHORT:   numpy.short,
    GR_BYTE:    numpy.int8,  
    }

if __name__ == "__main__":
    pass