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

import uuid

from tag_utils import rh_packet_to_tag

class redhawk_source(gr.sync_block, ProvidesShort_i, OrbCreator):
    """
    docstring for block redhawk_source
    """
    def __init__(self, naming_context_ior, corba_namespace_name):
        component_id = str(uuid.uuid4())
        self.exec_params = {
            "COMPONENT_IDENTIFIER": component_id,
            "PROFILE_NAME":         "source_profile_name",
            "NAME_BINDING":         corba_namespace_name,
            "NAMING_CONTEXT_IOR":   naming_context_ior}

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

    def __del__(self):
        OrbCreator.__del__(self)

    def work(self, input_items, output_items):
        # Get packet from CORBA port
        packet = self.port_data_short_in.getPacket()
        
        if packet.dataBuffer is None:
            return 0
        
        # Convert packet members to stream tag
        # Copy the buffer
        # Attach the tag to the stream
        packetTag = rh_packet_to_tag(packet)
        output_items[0] = packet.dataBuffer[:]
        self.add_item_tag(0, packetTag)
        return len(output_items[0])


if __name__ == "__main__":
    redhawk_source("", "")
