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
"""Store backeneds

$Id$
"""
import PyLucene

import zope.interface
from nxlucene.server.store.interfaces import IBdbDirectoryBackened
from nxlucene.server.store.interfaces import IPythonDirectoryBackened
from nxlucene.server.store.interfaces import IRamDirectoryBackened
from nxlucene.server.store.interfaces import IFSDirectoryBackened

from nxlucene.store.pythondirectory import PythonFileDirectory

class FSDirectoryBackened(object):

    zope.interface.implements(IFSDirectoryBackened)

    def get(self, *args, **kw):
        return PyLucene.FSDirectory.getDirectory(*args)

class PythonDirectoryBackened(object):

    zope.interface.implements(IPythonDirectoryBackened)

    def get(self, *args, **kw):
        return PythonFileDirectory(*args)

class RamDirectoryBackened(object):

    zope.interface.implements(IRamDirectoryBackened)

    def get(self, *args, **kw):
        return PyLucene.RAMDirectory()

class BdbDirectoryBackened(object):

    zope.interface.implements(IBdbDirectoryBackened)

    def get(self, *args, **kw):
        raise NotImplementedError