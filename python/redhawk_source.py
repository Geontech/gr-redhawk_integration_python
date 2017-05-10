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
    def __init__(
        self, 
        naming_context_ior="IOR:010000002000000049444c3a43462f4170706c69636174696f6e5265676973747261723a312e300001000000000000007c000000010102000a00000031302e302e322e3135009de329000000ff446f6d61696e4d616e61676572ff4170706c69636174696f6e73fe767e0c59040030ef00000000030000000200000000000000080000000100000000545441010000001c00000001000000010001000100000001000105090101000100000009010100",
        corba_namespace_name="sink_naming_binding"):

        self.exec_params = {
                "COMPONENT_IDENTIFIER": "source_component_identifier",
                "PROFILE_NAME": "source_profile_name",
                "NAME_BINDING": corba_namespace_name,
                "NAMING_CONTEXT_IOR": naming_context_ior}

        # TODO: determine if this is really needed
        ProvidesShort_i.__init__(
                self,
                self.exec_params["COMPONENT_IDENTIFIER"],
                self.exec_params)

        OrbCreator.__init__(self)

        gr.sync_block.__init__(
                self,
                name="redhawk_source",
                in_sig=None,
                out_sig=[numpy.float])

        print "sleeping"
        time.sleep(5)
        self.__del__()

    def __del__(self):
        OrbCreator.__del__(self)

    def work(self, input_items, output_items):
        out = output_items[0]
        # <+signal processing here+>
        #out[:] = whatever
        return len(output_items[0])


if __name__ == "__main__":
    redhawk_source()
