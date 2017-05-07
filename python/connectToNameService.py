from Queue import Queue
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

from UsesShort import UsesShort_i


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


def start_orb(thread_policy=None):
    naming_context_ior = "IOR:010000002000000049444c3a43462f4170706c69636174696f6e5265676973747261723a312e300001000000000000007c000000010102000a00000031302e302e322e3135009de329000000ff446f6d61696e4d616e61676572ff4170706c69636174696f6e73fe767e0c59040030ef00000000030000000200000000000000080000000100000000545441010000001c00000001000000010001000100000001000105090101000100000009010100"
    nic = ""

    try:
        try:
            orb = create_orb()
            globals()['__orb__'] = orb
            component_identifier=""
            
            component_poa = get_poa(orb, thread_policy, "component_poa")

            name_binding = "sink_name_binding"

            execparams = {
                    "COMPONENT_IDENTIFIER": "sink_component_identifier",
                    "PROFILE_NAME": "sink_profile_name",
                    "NAME_BINDING": "sink_name_binding",
                    "NAMING_CONTEXT_IOR": naming_context_ior}

            # Create the Resource
            component_Obj = UsesShort_i(
                    "sink_component_identifier",
                    execparams)
            # Activate the component servent
            component_poa.activate_object(component_Obj)
            component_Var = component_Obj._this()

            component_Obj.orb = orb
            component_Obj.setAdditionalParameters(
                    softwareProfile="sink_profile_name",
                    application_registrar_ior=naming_context_ior,
                    nic=nic)

            try:
                binding_object = orb.string_to_object(naming_context_ior)
            except:
                binding_object = None
            if binding_object == None:
                logging.error("Failed to lookup application registrar and naming context")
                sys.exit(-1)

            applicationRegistrar = binding_object._narrow(CF.ApplicationRegistrar)
            applicationRegistrar = None
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
    start_orb()
