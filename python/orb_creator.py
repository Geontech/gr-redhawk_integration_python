import logging
import threading
import sys

import CosNaming
from ossie.cf import CF

from omniORB import URI

from ossie.resource import createOrb
from ossie.resource import getPOA


class OrbCreator(object):
    def __init__(self):
        """
        Requires self.exec_params to be defined and parent to inherit from
        a component class.
        """

        self.orb = None

        print "creating orb thread"
        orb_thread = threading.Thread(
                name="orb",
                target=self.start_orb)
        orb_thread.setDaemon(True)
        orb_thread.start()
        print "done creating orb thread"

    def __del__(self):
        print "Destructor called"
        if self.orb:
            try:
                self.orb.shutdown(True)
            except:
                pass
            self.orb.destroy()
            print "done calling orb destroy"

    def start_orb(self, thread_policy=None):
        nic = ""

        self.orb = createOrb()

        component_poa = getPOA(
                orb=self.orb,
                thread_policy=thread_policy,
                name="component_poa")

        # Create the Resource
        component_obj = self
        # Activate the component servent
        component_poa.activate_object(component_obj)
        component_var = component_obj._this()

        component_obj.orb = self.orb
        component_obj.setAdditionalParameters(
                softwareProfile=self.exec_params["PROFILE_NAME"],
                application_registrar_ior=self.exec_params["NAMING_CONTEXT_IOR"],
                nic=nic)

        try:
            binding_object = self.orb.string_to_object(
                    self.exec_params["NAMING_CONTEXT_IOR"])
        except:
            binding_object = None
        if not binding_object:
            logging.error("Failed to lookup application registrar and naming context")
            sys.exit(-1)

        application_registrar = binding_object._narrow(
                CF.ApplicationRegistrar)
        if not application_registrar:
            name = URI.stringToName(self.exec_params["NAME_BINDING"])
            root_context = binding_object._narrow(
                    CosNaming.NamingContext)
            root_context.rebind(name, component_var)
        else:
            application_registrar.registerComponent(
                    self.exec_params["NAME_BINDING"],
                    component_var)

        logging.info("Starting ORB event loop")
        self.orb.run()
