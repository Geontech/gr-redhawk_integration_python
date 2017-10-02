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

def createSRI(streamID, xunits, xdelta, yunits, ydelta, subsize):
    sri = bulkio.sri.create(streamID)
    sri.xunits = xunits
    sri.xdelta = xdelta
    sri.yunits = yunits
    sri.ydelta = ydelta
    sri.subsize = subsize
    return sri

class redhawk_sink(gr.sync_block, UsesPorts_i):
    """
    GNURadio stream to REDHAWK (CORBA) BULKIO interface.
    
    Set the SRI parameters for the signal being sent to REDHAWK:
        streamID - Uniquely identify the stream
                 - Note: This will be replaced if the REHDAWK tag is found
                 -       at some point in the stream.
        xunits   - Type of data vs. X-axis
        yunits   - Type of data vs. Y-axis
        xdelta   - Spacing between data on the X-axis
        ydelta   - Spacing between data on the Y-axis
        subsize  - 0 if 1-dimensional, > 0 if matrix, etc.
    """
    def __init__(self, naming_context_ior, corba_namespace_name, gr_type, sri):
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

        self.tagsReceived = 0
        self.externalSRI = sri
        self.externalSRI.mode = 1 if gr_type == type_mapping.GR_COMPLEX else 0
        self.currentSRI = bulkio.sri.create()
        self.currentEOS = False

    def updateCurrent(self, tag=None):
        changed = False
        eos = False

        if tag is not None:
            # TODO: So if we do get an SRI over the tag stream, does it 
            # overwrite our internal state or what exactly?  
            # Guessing just keywords, stream ID, and eos behavior matter to us
            # since the flow graph may or may not be creating this tag.
            (sri, changed, eos) = tag_to_rh_packet(tag)
            changed = changed or bulkio.sri.compare(self.currentSRI, sri)
            self.externalSRI.keywords = sri.keywords[:]
            self.externalSRI.streamID = sri.streamID

        if not bulkio.sri.compare(self.externalSRI, self.currentSRI):
            # External and internal are different, favor external
            changed = True
            self.currentSRI = self.externalSRI

        # Forward eos, return changed
        self.currentEOS = eos
        return changed

    def work(self, input_items, output_items):
        input_buffer = input_items[0][:]
        ninput_items = len(input_buffer)

        self._log.debug("Sink: Entering work...")

        # Look for rh_packet stream tag
        self._log.debug("Sink: Searching for rh_packet tag")
        tags = self.get_tags_in_range(0, 0, ninput_items,
            gr.pmt.string_to_symbol(RH_PACKET_TAG_KEY))

        rh_tag = None
        if 0 < len(tags):
            # Grab the last SRI tag in the buffer and push it.
            self.tagsReceived += len(tags)
            self._log.debug("Sink: Found rh_packet Tag (num: {0}, total received: {1}).".format(len(tags), self.tagsReceived))
            rh_tag = tags[-1]

        # SRI Changed? Push.
        if self.updateCurrent(rh_tag):
            self._log.debug("Sink: Pushing SRI (indicated changed)")
            self.__active_port.pushSRI(self.currentSRI)
        
        # If complex, convert buffer format
        if self.currentSRI.mode == 1:
            input_buffer = bulkio_helpers.pythonComplexListToBulkioComplex(input_buffer)
        else:
            input_buffer = input_buffer.tolist()

        # Push packet
        self.__active_port.pushPacket(
            input_buffer,
            bulkio.timestamp.now(),
            self.currentEOS,
            self.currentSRI.streamID)

        # Return the number of elements processed.
        self._log.debug("Sink: Grand total processed {0}".format(ninput_items))
        self._log.debug("Sink: Exiting work...")
        return ninput_items

if __name__ == "__main__":
    redhawk_sink("", "")
