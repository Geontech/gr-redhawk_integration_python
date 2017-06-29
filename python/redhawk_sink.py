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
import warnings
from gnuradio import gr
from UsesPorts import UsesPorts_i

import uuid, bulkio

from tag_utils import tag_to_rh_packet, RH_PACKET_TAG_KEY, RH_PACKET_TAG_INDEX
import type_mapping

class redhawk_sink(gr.sync_block, UsesPorts_i):
    """
    docstring for block redhawk_sink
    """
    def __init__(self, naming_context_ior, corba_namespace_name, gr_type):
        component_id = str(uuid.uuid4())
        self.exec_params = {
            "COMPONENT_IDENTIFIER": component_id,
            "PROFILE_NAME":         "sink_profile_name",
            "NAME_BINDING":         corba_namespace_name,
            "NAMING_CONTEXT_IOR":   naming_context_ior}

        # TODO: determine if this is really needed
        UsesPorts_i.__init__(
            self,
            self.exec_params["COMPONENT_IDENTIFIER"],
            self.exec_params)

        self.gr_type = gr_type
        if   gr_type == type_mapping.GR_COMPLEX or gr_type == type_mapping.GR_FLOAT:
            self.__active_port = self.port_data_float_out
        elif gr_type == type_mapping.GR_INT:
            self.__active_port = self.port_data_long_out
        elif gr_type == type_mapping.GR_SHORT:
            self.__active_port = self.port_data_short_out
        elif gr_type == type_mapping.GR_BYTE:
            self.__active_port = self.port_data_octet_out
        else:
            raise Exception('Invalid gr_type: {0}'.format(gr_type))

        gr.sync_block.__init__(
            self,
            name="redhawk_sink",
            in_sig=[ type_mapping.SUPPORTED_GR_TYPES[gr_type] ],
            out_sig=None)

    def work(self, input_items, output_items):
        # Get SRI from incoming stream tags
        tags = self.get_tags_in_range(
            0, 
            RH_PACKET_TAG_INDEX, 
            RH_PACKET_TAG_INDEX+1, 
            gr.pmt.string_to_symbol(RH_PACKET_TAG_KEY))
        dataOut = input_items[0][:]
        
        # If the tag is found, convert it, push as needed
        if len(tags) > 0:
            (SRI, changed, T, EOS) = tag_to_rh_packet(tags[0])

            # Verify if 'complex' port 0 was used that SRI mode is set 1
            if self.gr_type == type_mapping.GR_COMPLEX and SRI.mode == 0:
                warnings.warn('Port type was specified as complex, but SRI indicates real data')

            # If the SRI changed, push it.
            if changed:
                self.__active_port.pushSRI(SRI)

            # Push the data
            self.__active_port.pushPacket(dataOut.tolist(), T, EOS, SRI.streamID)
        return len(dataOut)

if __name__ == "__main__":
    redhawk_sink("", "")
