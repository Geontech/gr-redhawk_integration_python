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

from gnuradio import gr
import bulkio

RH_PACKET_TAG_KEY       = 'rh_packet'

RH_PACKET_KEY_SRI       = 'sri'
RH_PACKET_KEY_CHANGED   = 'changed'
RH_PACKET_KEY_T         = 'T'
RH_PACKET_KEY_EOS       = 'EOS'

def rh_packet_to_tag(packet, tag_index=0):
    rh_dict = dict({ 
        RH_PACKET_KEY_SRI:      packet.SRI.__dict__, 
        RH_PACKET_KEY_CHANGED:  packet.sriChanged, 
        RH_PACKET_KEY_T:        packet.T.__dict__, 
        RH_PACKET_KEY_EOS:      packet.EOS
        })
    rh_pmt = gr.pmt.to_pmt(rh_dict)
    tag = gr.python_to_tag((
        tag_index, 
        gr.pmt.string_to_symbol(RH_PACKET_TAG_KEY), 
        rh_pmt, 
        gr.pmt.string_to_symbol(packet.SRI.streamID) 
        ))
    return tag

# Converts from a stream tag to a REDHAWK Packet fields
# Note: We omit the timestamp, T, since for some reason tags do not
#       reliably get delivered, and therefore we re-stamp at the sink.
def tag_to_rh_packet(tag):
    # Defaults
    changed = False
    EOS = False
    SRI = bulkio.sri.create()
    
    # Convert
    tag_p = gr.tag_to_python(tag)
    tag_dict = tag_p.__dict__
    if tag_dict['key'] == RH_PACKET_TAG_KEY:
        packet          = tag_dict.pop('value')
        SRI.__dict__    = packet.get(RH_PACKET_KEY_SRI, SRI.__dict__)
        changed         = packet.get(RH_PACKET_KEY_CHANGED, changed)
        EOS             = packet.get(RH_PACKET_KEY_EOS, EOS)
            
    return (SRI, changed, EOS)


if __name__ == "__main__":
    pass