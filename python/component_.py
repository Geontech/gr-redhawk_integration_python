#
# This file is protected by Copyright. Please refer to the COPYRIGHT file
# distributed with this source distribution.
#
# This file is part of REDHAWK core.
#
# REDHAWK core is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# REDHAWK core is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
from ossie.cf import CF
from resource_ import Resource
from ossie import containers
from omniORB import CORBA

class Component(Resource):
    def __init__(self, identifier, execparams, propertydefs=(), loggerName=None):
        super(Component,self).__init__(identifier, execparams, propertydefs, loggerName)
        self._app = None
        self._net = None
        
    def getApplication(self):
        return self._app
        
    def getNetwork(self):
        return self._net
    
    def setAdditionalParameters(self, softwareProfile, application_registrar_ior, nic):
        print softwareProfile
        print application_registrar_ior
        print nic
        super(Component,self).setAdditionalParameters(softwareProfile, application_registrar_ior, nic)
        orb = CORBA.ORB_init()
        obj = orb.string_to_object(application_registrar_ior)
        self._net = containers.NetworkContainer(nic)
        applicationRegistrar = obj._narrow(CF.ApplicationRegistrar)
        if applicationRegistrar != None:
            self._app = containers.ApplicationContainer(applicationRegistrar._get_app())

