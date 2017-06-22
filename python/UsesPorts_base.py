#!/usr/bin/env python
#
# AUTO-GENERATED CODE.  DO NOT MODIFY!
#
# Source: UsesPorts.spd.xml
from ossie.cf import CF
from ossie.cf import CF__POA
from ossie.utils import uuid

from component_ import Component
from ossie.threadedcomponent import *

import Queue, copy, time, threading
from ossie.resource import usesport, providesport
import bulkio

import type_mapping

class UsesPorts_base(CF__POA.Resource, Component, ThreadedComponent):
        # These values can be altered in the __init__ of your derived class

        PAUSE = 0.0125 # The amount of time to sleep if process return NOOP
        TIMEOUT = 5.0 # The amount of time to wait for the process thread to die when stop() is called
        DEFAULT_QUEUE_SIZE = 100 # The number of BulkIO packets that can be in the queue before pushPacket will block

        def __init__(self, identifier, execparams):
            loggerName = (execparams['NAME_BINDING'].replace('/', '.')).rsplit("_", 1)[0]
            Component.__init__(self, identifier, execparams, loggerName=loggerName)
            ThreadedComponent.__init__(self)

            # self.auto_start is deprecated and is only kept for API compatibility
            # with 1.7.X and 1.8.0 components.  This variable may be removed
            # in future releases
            self.auto_start = False
            # Instantiate the default implementations for all ports on this component
            self.port_data_float_out = bulkio.OutFloatPort("data_float_out")
            self.port_data_long_out  = bulkio.OutLongPort("data_long_out")
            self.port_data_short_out = bulkio.OutShortPort("data_short_out")
            self.port_data_octet_out = bulkio.OutOctetPort("data_octet_out")

        def gr_type_to_port(self, gr_type):
            if gr_type == type_mapping.GR_COMPLEX or gr_type == type_mapping.GR_FLOAT:
                return self.port_data_float_out
            if gr_type == type_mapping.GR_INT:
                return self.port_data_long_out
            if gr_type == type_mapping.GR_SHORT:
                return self.port_data_short_out
            if gr_type == type_mapping.GR_BYTE:
                return self.port_data_octet_out
            return None

        def start(self):
            Component.start(self)
            ThreadedComponent.startThread(self, pause=self.PAUSE)

        def stop(self):
            Component.stop(self)
            if not ThreadedComponent.stopThread(self, self.TIMEOUT):
                raise CF.Resource.StopError(CF.CF_NOTSET, "Processing thread did not die")

        def releaseObject(self):
            try:
                self.stop()
            except Exception:
                self._log.exception("Error stopping")
            Component.releaseObject(self)

        ######################################################################
        # PORTS
        # 
        # DO NOT ADD NEW PORTS HERE.  You can add ports in your derived class, in the SCD xml file, 
        # or via the IDE.

        port_data_float_out = usesport(name="data_float_out",
                                          repid="IDL:BULKIO/dataFloat:1.0",
                                          type_="control")
        port_data_long_out = usesport(name="data_long_out",
                                          repid="IDL:BULKIO/dataLong:1.0",
                                          type_="control")
        port_data_short_out = usesport(name="data_short_out",
                                          repid="IDL:BULKIO/dataShort:1.0",
                                          type_="control")
        port_data_octet_out = usesport(name="data_octet_out",
                                          repid="IDL:BULKIO/dataOctet:1.0",
                                          type_="control")

        ######################################################################
        # PROPERTIES
        # 
        # DO NOT ADD NEW PROPERTIES HERE.  You can add properties in your derived class, in the PRF xml file
        # or by using the IDE.


