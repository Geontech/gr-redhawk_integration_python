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


import logging
import copy, time, threading

import CosNaming
from ossie.cf import CF
from ossie.cf import CF__POA
from ossie.utils import uuid

from ossie.component import Component
from ossie.resource import Resource
from ossie.threadedcomponent import *
from ossie.properties import simple_property

from ossie.resource import usesport, providesport
import bulkio

from omniORB import URI, any, CORBA


def _poll_queue(queue, poll_period_seconds=0.001, timeout_seconds=1):
    """
    Poll a Queue every pollPeriodSeconds for up to timeoutSeconds.
    Return the value on the queue once there is one.  Return None 
    if the polling times out.
    """

    while timeout_seconds > 0:
        if queue.full():
            # success
            return queue.get()
        time.sleep(poll_period_seconds)
        timeout_seconds -= poll_period_seconds
    return None


def callOmniorbpyWithTimeout(method, queue, pollPeriodSeconds = 0.001, timeoutSeconds = 1):
    """
    Some omniorbpy methods have been found to hang if the system runs out of 
    threads.  Call method and wait for up to timeoutSeconds.  If the method
    returns within timeoutSeconds, return the value placed on the queue; 
    otherwise, return None.

    """

    thread = threading.Thread(target = method)
    try:
        thread.start()
    except:
        # If the system is out of threads, the thread.start() method can
        # potentially fail.
        return None

    return _poll_queue(queue,
                       poll_period_seconds= pollPeriodSeconds,
                       timeout_seconds= timeoutSeconds)

def create_orb():
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


def get_poa(orb, thread_policy, name):
    # get the POA
    obj_poa = orb.resolve_initial_references("RootPOA")
    poaManager = obj_poa._get_the_POAManager()
    if thread_policy != None:
        policyList = []
        policyList.append(obj_poa.create_thread_policy(thread_policy))
        POA = obj_poa.create_POA(name, poaManager, policyList)
    else:
        POA = obj_poa
    poaManager.activate()
    return POA




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
            naming_context_ior="IOR:010000002000000049444c3a43462f4170706c69636174696f6e5265676973747261723a312e300001000000000000007c000000010102000a00000031302e302e322e3135009de329000000ff446f6d61696e4d616e61676572ff4170706c69636174696f6e73fe767e0c59040030ef00000000030000000200000000000000080000000100000000545441010000001c00000001000000010001000100000001000105090101000100000009010100",
            corba_namespace_name=None):

        self.naming_context_ior = naming_context_ior

        print "creating orb thread"
        orb_thread = threading.Thread(
                name="orb",
                target=self.start_orb)
        orb_thread.setDaemon(True)
        orb_thread.start()
        print "done creating orb thread"

        gr.sync_block.__init__(self,
            name="redhawk_sink",
            in_sig=[numpy.float],
            out_sig=None)

        print "sleeping"
        time.sleep(10)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        # TODO: push to self.port_data_short_out
        return len(input_items[0])

    def start_orb(self, thread_policy=None):
        nic = ""

        execparams = {
                "COMPONENT_IDENTIFIER": "sink_component_identifier",
                "PROFILE_NAME": "sink_profile_name",
                "NAME_BINDING": "sink_name_binding_2",
                "NAMING_CONTEXT_IOR": self.naming_context_ior}

        try:
            try:
                orb = create_orb()
                
                component_poa = get_poa(
                        orb=orb,
                        thread_policy=thread_policy,
                        name="component_poa")


                # Create the Resource
                component_Obj = UsesShort_i(
                        execparams["COMPONENT_IDENTIFIER"],
                        execparams)
                # Activate the component servent
                component_poa.activate_object(component_Obj)
                component_Var = component_Obj._this()

                component_Obj.orb = orb
                component_Obj.setAdditionalParameters(
                        softwareProfile=execparams["PROFILE_NAME"],
                        application_registrar_ior=self.naming_context_ior,
                        nic=nic)

                try:
                    binding_object = orb.string_to_object(self.naming_context_ior)
                except:
                    binding_object = None
                if binding_object == None:
                    logging.error("Failed to lookup application registrar and naming context")
                    sys.exit(-1)

                applicationRegistrar = binding_object._narrow(CF.ApplicationRegistrar)
                applicationRegistrar = None
                if applicationRegistrar == None:
                    name = URI.stringToName(execparams["NAME_BINDING"])
                    rootContext = binding_object._narrow(CosNaming.NamingContext)
                    rootContext.rebind(name, component_Var)
                else:
                    applicationRegistrar.registerComponent(
                            execparams["NAME_BINDING"],
                            component_Var)

                logging.info("Starting ORB event loop")
                orb.run()

                try:
                   orb.shutdown(true)
                except:
                    pass
            except SystemExit:
                pass
            except KeyboardInterrupt:
                pass
            except:
                logging.exception("Unexpected Error")
        finally:
            if orb:
                orb.destroy()


if __name__ == "__main__":
    redhawk_sink()
