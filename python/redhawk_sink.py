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

    def resetCurrentSRI(self):
        self.currentSRI = None
        self.currentChanged = False
        self.currentT = None
        self.currentEOS = False
        self.currentLength = 0
        self.remainingLength = 0
        self.currentBuffer = numpy.array([])

    def pushPacket(self):
        self._log.info("Pushing Packet")
        self._log.debug("\tcurrentBuffer type:       {0}".format(self.currentBuffer.__class__.__name__))
        self._log.debug("\tcurrentT type:            {0}".format(self.currentT.__class__.__name__))
        self._log.debug("\tcurrentEOS type:          {0}".format(self.currentEOS.__class__.__name__))
        self._log.debug("\tcurrentSRI.streamID type: {0}".format(self.currentSRI.streamID.__class__.__name__))
        self.__active_port.pushPacket(
            self.currentBuffer.tolist(),
            bulkio.timestamp.now(),
            self.currentEOS,
            self.currentSRI.streamID)


    def work(self, input_items, output_items):
        # NOTE: ninput_items will never be 0
        num_processed = 0
        input_buffer = input_items[0][:]
        ninput_items = len(input_buffer)
        total_ninput = ninput_items

        self._log.info("Entering work...")

        while 0 < ninput_items:
            if 0 < self.remainingLength:
                # Copy some amount from one buffer to the other (either all of it
                # or just enough to finish off the remainingLength).
                amt = min([ninput_items, self.remainingLength])
                self._log.info("Copying {0} items min([{1},{2}])".format(amt, ninput_items, self.remainingLength))
                if 0 == self.currentBuffer.size:
                    self.currentBuffer.dtype = input_buffer.dtype
                self.currentBuffer = numpy.append(self.currentBuffer, input_buffer[0:amt])
                input_buffer = input_buffer[amt+1:]

                # adjust counters
                self.remainingLength -= amt
                ninput_items -= amt
                num_processed += amt
                self._log.info("remaining for packet: {0}".format(self.remainingLength))
                self._log.info("remaining from input: {0}".format(ninput_items))
                self._log.info("total processed:      {0}".format(num_processed))

            # Not waiting for more data for the current packet...
            if 0 >= self.remainingLength:
                if 0 < num_processed:
                    # Data was processed, so the buffer has something.
                    # Must be finished, so push the packet.
                    self.pushPacket()

                if 0 < ninput_items:
                    # Still some data remaining for next loop
                    # Look for rh_packet stream tag
                    self._log.info("Searching for rh_packet tag")
                    self._log.info("Total vs. remaining {0} : {1}".format(total_ninput, ninput_items))
                    tags = self.get_tags_in_range(0, 0, total_ninput,
                        gr.pmt.string_to_symbol(RH_PACKET_TAG_KEY))

                    if 0 < len(tags):
                        self._log.info("Found rh_packet Tag (num: {0}).".format(len(tags)))
                        (   self.currentSRI,
                            self.currentChanged,
                            self.currentT,
                            self.currentEOS,
                            self.currentLength   ) = tag_to_rh_packet(tags[0])

                        # Verify if 'complex' port 0 was used that SRI mode is set 1
                        if self.gr_type == type_mapping.GR_COMPLEX and this.currentSRI.mode == 0:
                            self._log.warning('Port type was specified as complex, but SRI indicates real data')

                        # SRI Changed? Push.
                        if self.currentChanged:
                            self._log.info("Pushing SRI (indicated changed)")
                            self.__active_port.pushSRI(self.currentSRI)

                # Reset remaining length to current (stream tag's indicated) length.
                self.remainingLength = self.currentLength

        # Return the number of elements processed.
        self._log.info("Grand total processed {0}".format(num_processed))
        self._log.info("Exiting work...")
        return num_processed

if __name__ == "__main__":
    redhawk_sink("", "")
