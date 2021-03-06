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
"""Fake XML-RPC Lucene Server adapter

$Id$
"""

import threading
import PyLucene

import zope.interface

from nxlucene.server.interfaces import IXMLRPCLuceneServer
from nxlucene.testing.interfaces import IFakeXMLRPCLuceneServer

from nxlucene.server.xmlrpc import XMLRPCLuceneServer
from nxlucene.server.core import LuceneServer

class FakeXMLRPCLuceneServer(object):
    """Fake XMLRPC server

    Adapts IXMLRPCLuceneServer.
    """

    zope.interface.implements(IFakeXMLRPCLuceneServer)
    __user_for__ = IXMLRPCLuceneServer

    def __init__(self, core):
        assert (core is not None)
        self._core = core
        self._core._write_sync = True

    def indexDocument(self, uid, xml_query='', b64=False, sync=False):
        return self._core.xmlrpc_indexDocument(uid, xml_query, b64, sync)

    def reindexDocument(self, uid, xml_query='', b64=False, sync=False):
        return self._core.xmlrpc_reindexDocument(uid, xml_query, b64, sync)

    def unindexDocument(self, uid, sync=False):
        return self._core.xmlrpc_unindexDocument(uid, sync)

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

    def getFieldTerms(self, field):
        return self._core.xmlrpc_getFieldTerms(field)

import os
import xmlrpclib
import shutil

TMP_STORE_DIR = '/tmp/NXLuceneTesting'

def _getFakeServerProxy(url, transport=None):
    # XXX Use a RAMDirectory for tests
    core = LuceneServer(TMP_STORE_DIR,  store_backened_id='FSDirectory')
    xmlrpc_server = XMLRPCLuceneServer(core)
    fake_server = FakeXMLRPCLuceneServer(xmlrpc_server)
    return fake_server

def setUp():

    # Set PythonThread
    threading.Thread = PyLucene.PythonThread

    # Path xmlrpclib
    xmlrpclib._old_ServerProxy = xmlrpclib.ServerProxy
    xmlrpclib.ServerProxy = _getFakeServerProxy

def tearDown():
    xmlrpclib.ServerProxy = xmlrpclib._old_ServerProxy
    if os.path.exists(TMP_STORE_DIR):
        shutil.rmtree(TMP_STORE_DIR)



