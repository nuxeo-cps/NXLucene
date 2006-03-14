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
"""XML-RPC Lucene Server adapter

$Id: server.py 30816 2006-02-28 18:09:59Z janguenot $
"""

import xmlrpclib

import zope.interface
from nxlucene.interfaces import IXMLRPCLuceneServer

from nxlucene.xmlrpc import XMLRPCLuceneServer
from nxlucene.core import LuceneServer

class IFakeXMLRPCLuceneServer(zope.interface.Interface):

    def indexDocument(uid, xml_query='', b64=False):
        """
        """

    def reindexDocument(uid, xml_query='', b64=False):
        """
        """

    def unindexDocument(uid):
        """
        """

    def searchQuery(xml_query=''):
        """
        """

    def hasUID(uid):
        """
        """

    def clean():
        """
        """

    def getStoreDir():
        """
        """

    def optimize():
        """
        """

    def getNumberOfDocuments():
        """
        """

    def debug(msg):
        """
        """

class FakeXMLRPCLuceneServer(object):
    """Fake XMLRPC server

    Adapts IXMLRPCLuceneServer.
    """

    zope.interface.implements(IFakeXMLRPCLuceneServer)
    __user_for__ = IXMLRPCLuceneServer

    def __init__(self, core):
        assert (core is not None)
        self._core = core

    def indexDocument(self, uid, xml_query='', b64=False):
        return self._core.xmlrpc_indexDocument(uid, xml_query, b64)

    def reindexDocument(self, uid, xml_query='', b64=False):
        return self._core.xmlrpc_reindexDocument(uid, xml_query, b64)

    def unindexDocument(self, uid):
        return self._core.xmlrpc_unindexDocument(uid)

    def searchQuery(self, xml_query=''):
        return self._core.xmlrpc_searchQuery(xml_query)

    def hasUID(self, uid):
        return self._core.xmlrpc_hasUID(uid)

    def clean(self):
        return self._core.xmlrpc_clean()

    def getStoreDir(self):
        return self._core.xmlrpc_getStoreDir()

    def optimize(self):
        return self._core.xmlrpc_optimize()

    def getNumberOfDocuments(self):
        return self._core.xmlrpc_getNumberOfDocuments()

    def debug(self, msg):
        return self._core.xmlrpc_debug(msg)

def _getFakeServerProxy(url):
    # XXX Use a RAMDirectory for tests    
    core = LuceneServer('/tmp/NXLuceneTesting')
    xmlrpc_server = XMLRPCLuceneServer(core)
    fake_server = FakeXMLRPCLuceneServer(xmlrpc_server)
    return fake_server

def setUp():
    xmlrpclib.ServerProxy = _getFakeServerProxy
    
