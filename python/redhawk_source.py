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
from ProvidesPorts import ProvidesPorts_i
import time

import uuid

from tag_utils import rh_packet_to_tag
import type_mapping

from ossie.utils.bulkio import bulkio_helpers

from collections import deque

class DTRecord(object):
    def __init__(self, data_transfer, gr_type):
        self.packet = data_transfer
        np_type = type_mapping.SUPPORTED_GR_TYPES[gr_type]

        # NOTE: We're trusting REDHAWK here.  If there is a mismatch between
        # the SRI and the port selected on this source, there will be trouble.
        if self.packet.SRI.mode == 1:
            self.buffer_out = numpy.array(
                bulkio_helpers.bulkioComplexToPythonComplexList(data_transfer.dataBuffer),
                dtype=np_type)
        elif np_type == numpy.int8:
            self.buffer_out = numpy.fromstring(data_transfer.dataBuffer, dtype=np_type)
        else:
            self.buffer_out = numpy.array(data_transfer.dataBuffer, dtype=np_type)

class redhawk_source(gr.sync_block, ProvidesPorts_i):
    """
    REDHAWK (CORBA) BULKIO interface to GNURadio stream
    
    The packet depth controls how many bulkio packets are queued if downstream
    blocks are not keeping up or are occasionally bottlenecking.

    This block also conveys the SRI (Signal Related Information, see REDHAWK 
    ICD 2.0 section 3.1.1.2.5 for format), time stamp, and other flags as a 
    stream tag.  See rh_packet_to_tag, tag_to_rh_packet for help converting
    between the fields and a PMT.
    """
    def __init__(self, naming_context_ior, corba_namespace_name, gr_type='short', packet_depth=4):
        if packet_depth < 1:
            raise Exception('packet_depth must be greater than or equal to 1')

        component_id = str(uuid.uuid4())
        self.exec_params = {
            "COMPONENT_IDENTIFIER": component_id,
            "PROFILE_NAME":         "source_profile_name",
            "NAME_BINDING":         corba_namespace_name,
            "NAMING_CONTEXT_IOR":   naming_context_ior}

        # TODO: determine if this is really needed
        ProvidesPorts_i.__init__(
            self,
            self.exec_params["COMPONENT_IDENTIFIER"],
            self.exec_params)

        self.gr_type = gr_type
        if   gr_type == type_mapping.GR_COMPLEX or gr_type == type_mapping.GR_FLOAT:
            self.__active_port = self.port_data_float_in
        elif gr_type == type_mapping.GR_INT:
            self.__active_port = self.port_data_long_in
        elif gr_type == type_mapping.GR_SHORT:
            self.__active_port = self.port_data_short_in
        elif gr_type == type_mapping.GR_BYTE:
            self.__active_port = self.port_data_octet_in
        else:
            raise Exception('Invalid gr_type: {0}'.format(gr_type))

        gr.sync_block.__init__(
            self,
            name="redhawk_source",
            in_sig=None,
            out_sig=[ type_mapping.SUPPORTED_GR_TYPES[gr_type] ])

        self.dtRecords = deque([], packet_depth)
        self.queueFullWarnOnce = True
        self.tagsSent = 0

    '''
    Get a data transfer record either from the queue or the port.
    This will block until a valid data buffer is returned if the queue is
    empty.
    '''
    def getDTRecord(self):
        first = False

        # Check for empty buffer, if so remove it. Next returned packet is
        # definitively the first of the number of times it has been returned.
        if 0 < len(self.dtRecords) and 0 == len(self.dtRecords[0].buffer_out):
            self._log.debug('Source: Current packet has been sent; continuing to next')
            first = True
            self.dtRecords.popleft()

        # Attempt to get a new packet off the port if there is room in the queue.
        if len(self.dtRecords) < self.dtRecords.maxlen:
            self.queueFullWarnOnce = True

            packet = self.__active_port.getPacket()
            if packet.dataBuffer is not None:
                self._log.debug('Source: New packet received from REDHAWK')
                self.dtRecords.append(DTRecord(packet, self.gr_type))
                if 1 == len(self.dtRecords):
                    first = True

        elif self.queueFullWarnOnce:
            self._log.warning('Source: Packet queue full.')
            self.queueFullWarnOnce = False

        record = None
        if 0 < len(self.dtRecords):
            record = self.dtRecords[0]
        return (record, first)

    def work(self, input_items, output_items):
        # Flow:
        #    Get the current or next DTRecord.
        #    If first, check SRI, create and tag the stream.
        #    If not first, I'm sure it's grand.
        #    Move items l2r from the dataBuffer into the output buffer.
        #    Return number of items processed
        dtRecord = None
        first = False
        pauseCount = 4
        while True:
            (dtRecord, first) = self.getDTRecord()
            if dtRecord:
                break;
            else:
                time.sleep(1.0/pauseCount)
                pauseCount -= 1
                if 0 >= pauseCount:
                    return 0; # Abort.  This is to give work() a chance to exit.

        if first:
            # Sanity check SRI vs. data type and warn user JIC.
            if self.gr_type == type_mapping.GR_COMPLEX and dtRecord.packet.SRI.mode == 0:
                self._log.warning('Source: Port type was specified as complex, but SRI indicates real data')

            # If the packet's SRI changed:
            # Convert packet members to stream tag and add it to the stream
            if dtRecord.packet.sriChanged:
                self.tagsSent += 1
                self._log.debug('Source: Adding packet data as stream tag (total: {0})'.format(self.tagsSent))
                packetTag = rh_packet_to_tag(dtRecord.packet, 0)
                self.add_item_tag(0, packetTag)

        # Determine number of items that can be moved, move them.
        noutput_items = len(output_items[0])
        db_len = len(dtRecord.buffer_out)
        num_to_send = min([db_len, noutput_items])
        output_items[0][0:num_to_send] = dtRecord.buffer_out[0:num_to_send]
        dtRecord.buffer_out = dtRecord.buffer_out[num_to_send+1:]

        self._log.debug('Source: Number of elements sent: {0}'.format(num_to_send))

        return num_to_send


if __name__ == "__main__":
    redhawk_source("", "")
