#!/usr/bin/env python
#
#
# AUTO-GENERATED
#
# Source: gr_redhawk_integration_python.spd.xml
from ossie.resource import start_component
import logging

from gr_redhawk_integration_python_base import *

class gr_redhawk_integration_python_i(gr_redhawk_integration_python_base):
    """<DESCRIPTION GOES HERE>"""
    def constructor(self):
        # TODO add customization here.
        
    def process(self):
        # TODO fill in your code here
        self._log.debug("process() example log message")
        return FINISH

  
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.debug("Starting Component")
    start_component(gr_redhawk_integration_python_i)

