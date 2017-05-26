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
from UsesShort import UsesShort_i
import time
from orb_creator import OrbCreator


class redhawk_sink(gr.sync_block, UsesShort_i, OrbCreator):
    """
    docstring for block redhawk_sink
    """
    def __init__(
            self,
            naming_context_ior,
            corba_namespace_name):

        fp = open("/tmp/ior.txt", "r")
        naming_context_ior_ = fp.read()
        fp.close()

        corba_namespace_name_="sink_name_binding"

        self.exec_params = {
                "COMPONENT_IDENTIFIER": "sink_component_identifier",
                "PROFILE_NAME": "sink_profile_name",
                "NAME_BINDING": corba_namespace_name_,
                "NAMING_CONTEXT_IOR": naming_context_ior_}

        # TODO: determine if this is really needed
        UsesShort_i.__init__(
                self,
                self.exec_params["COMPONENT_IDENTIFIER"],
                self.exec_params)

        OrbCreator.__init__(self)

        gr.sync_block.__init__(
                self,
                name="redhawk_sink",
                in_sig=[numpy.float],
                out_sig=None)

    def __del__(self):
        OrbCreator.__del__(self)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        # TODO: push to self.port_data_short_out
        # TODO: initial push SRI
        # TODO: self.port_data_short_out.pushPacket()
        return len(input_items[0])


if __name__ == "__main__":
    redhawk_sink("", "")
