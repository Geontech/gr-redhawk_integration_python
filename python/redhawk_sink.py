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
from UsesPorts import UsesPorts_i

import uuid, bulkio
from ossie.utils.bulkio import bulkio_helpers

from tag_utils import tag_to_rh_packet, RH_PACKET_TAG_KEY
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

        self.resetCurrentSRI()
        self.firstSriPushed = False

    def resetCurrentSRI(self):
        self.currentSRI = bulkio.sri.create()
        if self.gr_type == type_mapping.GR_COMPLEX:
            self.currentSRI.mode = 1
        self.currentChanged = True
        self.currentEOS = False

    def work(self, input_items, output_items):
        input_buffer = input_items[0][:]
        ninput_items = len(input_buffer)

        self._log.debug("Sink: Entering work...")

        # Look for rh_packet stream tag
        self._log.debug("Sink: Searching for rh_packet tag")
        tags = self.get_tags_in_range(0, 0, total_ninput,
            gr.pmt.string_to_symbol(RH_PACKET_TAG_KEY))

        if 0 < len(tags):
            # Grab the last SRI tag in the buffer and push it.
            self._log.debug("Sink: Found rh_packet Tag (num: {0}, total received: {1}).".format(len(tags), self.tagsReceived))
            (   self.currentSRI,
                self.currentChanged,
                self.currentEOS   ) = tag_to_rh_packet(tags[-1])

            # Verify if 'complex' port 0 was used that SRI mode is set 1
            # NOTE: We're going to trust the flow graph operator here and flag it.
            if self.gr_type == type_mapping.GR_COMPLEX and self.currentSRI.mode == 0:
                self._log.warning('Sink: Port type was specified as complex, but SRI indicates real data')
                self.currentSRI.mode = 1

        # SRI Changed? Push.
        if self.currentChanged or not self.firstSriPushed:
            self._log.debug("Sink: Pushing SRI (indicated changed)")
            self.__active_port.pushSRI(self.currentSRI)
            self.firstSriPushed = True
        
        # Push packet.  If complex, convert it to a float32 array.
        if self.currentSRI.mode == 1:        
            self.__active_port.pushPacket(
                bulkio_helpers.pythonComplexListToBulkioComplex(input_buffer),
                bulkio.timestamp.now(),
                self.currentEOS,
                self.currentSRI.streamID)
        else:
            self.__active_port.pushPacket(
                input_buffer.tolist(),
                bulkio.timestamp.now(),
                self.currentEOS,
                self.currentSRI.streamID)

        # Return the number of elements processed.
        self._log.debug("Sink: Grand total processed {0}".format(ninput_items))
        self._log.debug("Sink: Exiting work...")
        return ninput_items

if __name__ == "__main__":
    redhawk_sink("", "")
