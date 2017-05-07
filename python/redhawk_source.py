#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 Drew Cormier and Geon Technologies
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
from gnuradio import gr
from ProvidesShort import ProvidesShort_i
import time
from orb_creator import OrbCreator


class redhawk_source(gr.sync_block, ProvidesShort_i, OrbCreator):
    """
    docstring for block redhawk_source
    """
    def __init__(self, naming_context_ior, corba_namespace_name):

        self.exec_params = {
                "COMPONENT_IDENTIFIER": "source_component_identifier",
                "PROFILE_NAME": "source_profile_name",
                "NAME_BINDING": "source_name_binding_5",
                "NAMING_CONTEXT_IOR": naming_context_ior}

        # TODO: determine if this is really needed
        Provides_i.__init__(
                self,
                self.exec_params["COMPONENT_IDENTIFIER"],
                self.exec_params)

        OrbCreator.__init__(self)

        gr.sync_block.__init__(self,
            name="redhawk_source",
            in_sig=None,
            out_sig=[numpy.float])

        print "sleeping"
        time.sleep(5)
        self.__del__()

    def work(self, input_items, output_items):
        out = output_items[0]
        # <+signal processing here+>
        #out[:] = whatever
        return len(output_items[0])

