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
import logging
from Queue import Queue
import CosNaming
import signal
import Threading


def createOrb():
    '''
    Calls the omniorbpy CORBA.ORB_init() method in a thread.  Calling the method in a thread
    allows us to set a timeout for the ORB_init() call, as it will never return if the system
    has run out of threads.

    Return None on failure.
    '''
    # create a queue with one slot to hold the orb
    queue = Queue(maxsize=1) 

    def orbCreator():
        """
        A method to pass to callOmniorbpyWithTimeout.

        """

        orb = CORBA.ORB_init()
        queue.put(orb)

    orb = callOmniorbpyWithTimeout(orbCreator, queue)
    if orb == None:
        logging.error("omniorbpy failed to return from ORB_init.  This is often a result of an insufficient amount of threads available on the system.")
        sys.exit(-1)
    return orb


# COMPONENT_IDENTIFIER SigGen_noise:rh.basic_components_demo_125_093124097_1
# NAME_BINDING SigGen_noise
#drew     13044 12575  0 09:31 pts/1    00:00:00 /var/redhawk/sdr/dev/.DevMgr_localhost.localdomain/GPP_localhost_localdomain/components/rh/SigGen/cpp/SigGen DOM_PATH REDHAWK_DEV/rh.basic_components_demo_125_093124097_1 
# PROFILE_NAME /components/rh/SigGen/SigGen.spd.xml
# DEBUG_LEVEL 3
# NAMING_CONTEXT_IOR IOR:010000002000000049444c3a43462f4170706c69636174696f6e5265676973747261723a312e300001000000000000007c000000010102000a00000031302e302e322e3135009de329000000ff446f6d61696e4d616e61676572ff4170706c69636174696f6e73fe767e0c59040030ef00000000010000000200000000000000080000000100000000545441010000001c00000001000000010001000100000001000105090101000100000009010100



class redhawk_sink(gr.sync_block, UsesShort_i):
    """
    docstring for block redhawk_sink
    """
    def __init__(
            self,
            naming_context_ior="IOR:010000002000000049444c3a43462f4170706c69636174696f6e5265676973747261723a312e300001000000000000007c000000010102000a00000031302e302e322e3135009de329000000ff446f6d61696e4d616e61676572ff4170706c69636174696f6e73fe767e0c59040030ef00000000010000000200000000000000080000000100000000545441010000001c00000001000000010001000100000001000105090101000100000009010100"
            corba_namespace_name):

        orb_thread = threading.Thread(
                name="orb",
                target=self.start_orb)
        orb_thread.setDaemon(True)
        orb_thread.start()

        self.start_orb(naming_context_ior)
        gr.sync_block.__init__(self,
            name="redhawk_sink",
            in_sig=[numpy.float],
            out_sig=None)

    def start_orb(self, naming_context_ior, thread_policy=None):
        name_binding="NOT SET"
        setupSignalHandlers()
        orb = None
        globals()['__orb__'] = orb
        nic=""

        try:
            try:
                orb = createOrb()
                globals()['__orb__'] = orb
                name_binding=""
                component_identifier=""
                
                componentPOA = getPOA(orb, thread_policy, "componentPOA")

                name_binding="sink_name_binding"

                execparams = {
                        "COMPONENT_IDENTIFIER": "sink_component_identifier",
                        "PROFILE_NAME": "sink_profile_name",
                        "NAME_BINDING": "sink_name_binding",
                        "NAMING_CONTEXT_IOR": naming_context_ior}

                # Create the component
                component_Obj = Resource("sink_component_identifier", execparams)
                componentPOA.activate_object(component_Obj)
                component_Var = component_Obj._this()

                component_Obj.setAdditionalParameters"sink_profile_name", naming_context_ior, nic)

                try:
                    binding_object = orb.string_to_object(naming_context_ior)
                except:
                    binding_object = None
                if binding_object == None:
                    logging.error("Failed to lookup application registrar and naming context")
                    sys.exit(-1)

                applicationRegistrar = binding_object._narrow(CF.ApplicationRegistrar)
                if applicationRegistrar == None:
                    name = URI.stringToName("sink_name_binding")
                    rootContext = binding_object._narrow(CosNaming.NamingContext)
                    rootContext.rebind(name, component_Var)
                else:
                    applicationRegistrar.registerComponent("sink_name_binding", component_Var)

                logging.trace("Starting ORB event loop")
                orb.run()

                try:
                   orb.shutdown(true)
                except:
                    pass
                signal.signal(signal.SIGINT, signal.SIG_IGN)
            except SystemExit:
                pass
            except KeyboardInterrupt:
                pass
            except:
                logging.exception("Unexpected Error")
        finally:
            if orb:
                orb.destroy()

    def work(self, input_items, output_items):
        in0 = input_items[0]
        # TODO: push to self.port_data_short_out
        return len(input_items[0])

