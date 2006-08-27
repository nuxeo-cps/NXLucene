# Copyright (C) 2006, Nuxeo SAS <http://www.nuxeo.com>
# Author: Julien Anguenot <ja@nuxeo.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-13
"""Registry of IStoreBackened

$Id$
"""
import logging

from zope.interface.exceptions import DoesNotImplement
from zope.interface.verify import verifyClass

from nxlucene.server.store.interfaces import IStoreBackened
from nxlucene.server.store.backeneds import BdbDirectoryBackened
from nxlucene.server.store.backeneds import RamDirectoryBackened
from nxlucene.server.store.backeneds import PythonDirectoryBackened
from nxlucene.server.store.backeneds import FSDirectoryBackened

LOG = logging.getLogger("nxlucene.server.store.registry")

class RegistryKlass(object):

    def __init__(self):
        self.__store_backened_classes = {}

    def register(self, name, klass=None):
        if klass is not None:
            try:
                verifyClass(IStoreBackened, klass)
            except DoesNotImplement:
                raise
            else:
                if name.lower() not in self.listNames():
                    self.__store_backened_classes[name] = klass
                    return True
        return False

    def listNames(self):
        names = self.__store_backened_classes.keys()
        names.sort()
        return tuple([name.lower() for name in names])

    def getClass(self, name):
        return self.__store_backened_classes.get(name)

    def makeInstance(self, name, *args, **kw):
        if name.lower() in self.listNames():
            return self.getClass(name)().get(*args, **kw)
        return None

registry_ = RegistryKlass()

# XXX monkey patch here to add new backeneds
# Would be better as server extensions...
backeneds = (('FSDirectory', FSDirectoryBackened),
             ('PythonDirectory', PythonDirectoryBackened),
             ('RamDirectory', RamDirectoryBackened),
             ('BdbDirectory', BdbDirectoryBackened),
             )
for name, klass in backeneds:
    registry_.register(name, klass)

def getRegistry():
    return registry_
