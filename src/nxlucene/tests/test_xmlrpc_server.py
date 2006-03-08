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
"""Lucene XML-RPC server tests

$Id$
"""

import os
import shutil
import unittest
import threading
import PyLucene
import xmlrpclib

from twisted.internet import reactor
from twisted.web import resource
from twisted.web import xmlrpc
from twisted.web import server

import zope.interface

from nxlucene.xmlrpc import XMLRPCLuceneServer
from nxlucene.server import LuceneServer
from nxlucene.rss.resultset import ResultSet
from nxlucene.rss.adapter import PythonResultSet

class P(object):
    zope.interface.implements(zope.interface.Interface)
    def __init__(self, name):
        self.name = name

class LuceneXMLRPCServerTestCase(unittest.TestCase):

    logs = []
    errors = []

    _server = None
    _client = None

    def setUp(self):

        self._store_dir = '/tmp/lucene'
        self._port = 9280

        self.logs = []
        self.errors = []

    def _callback(self, value):
        self.logs.append(value)

    def _errback(self, value):
        self.errors.append('error:'+repr(value))

    def test_implementation(self):
        from zope.interface.verify import verifyClass
        from nxlucene.interfaces import IXMLRPCLuceneServer
        self.assert_(verifyClass(IXMLRPCLuceneServer, XMLRPCLuceneServer))

    def test_adapter(self):
        core = LuceneServer(self._store_dir)
        xmlrpc = XMLRPCLuceneServer(core)
        self.assertEqual(core, xmlrpc._core)

    def test_01_alive(self):

        # Let's launch it here !

        self._client = None
        self._client = xmlrpc.Proxy('http://127.0.0.1:%s'%self._port)

        self._server = reactor.listenTCP(
            self._port,
            server.Site(XMLRPCLuceneServer(LuceneServer(self._store_dir))))

        defer = self._client.callRemote('debug', 'test')
        defer.addCallbacks(self._callback, self._errback)
        reactor.callLater(1, reactor.crash)
        reactor.run(installSignalHandlers=0)
        self.assertEqual(''.join(self.logs), 'test')

    def test_optimize(self):

        self._client = None
        self._client = xmlrpc.Proxy('http://127.0.0.1:%s'%self._port)
        
        defer = self._client.callRemote('optimize')
        defer.addCallbacks(self._callback, self._errback)

        reactor.callLater(1, reactor.crash)
        reactor.run(installSignalHandlers=0)

        self.assertEqual(self.logs, [True])

        self.logs = []

#        self._server.stopListening()

##    def test_store_dir(self):
##        self._client = None
##        self._client = xmlrpclib.Server('http://127.0.0.1:%s'%9180)
##        self.assertEqual(self._store_dir, self._client.getStoreDir())
##        self.logs = []

    def _indexObjects(self):

##        if not self._server:
##            self._server = reactor.listenTCP(
##                self._port,
##                server.Site(LuceneServer(self._store_dir)))

        self._client = None
        self._client = xmlrpc.Proxy('http://127.0.0.1:%s'%self._port)

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id="name" attribute="name">
              foo
            </field>
          </fields>
        </doc>"""
        
        defer = self._client.callRemote('indexDocument', '1', stream)
        defer.addCallbacks(self._callback, self._errback)
        
        reactor.callLater(1, reactor.crash)
        reactor.run(installSignalHandlers=0)

        self.assertEqual(self.logs, [True])

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id="name" attribute="name">
              bar
            </field>
          </fields>
        </doc>"""

        defer = self._client.callRemote('indexDocument', '2', stream)
        defer.addCallbacks(self._callback, self._errback)

        reactor.callLater(0.1, reactor.crash)
        reactor.run(installSignalHandlers=0)

        self.assertEqual(self.logs, [True, True])

    def test_indexing(self):
        # See test_searching
        self._indexObjects()

    def test_reindexing(self):
        self._indexObjects()

        self.logs = []

        self._client = None
        self._client = xmlrpc.Proxy('http://127.0.0.1:%s'%self._port)

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id="name" attribute="name">
               newfoo
            </field>
          </fields>
        </doc>"""
        
        defer = self._client.callRemote('reindexDocument', '1', stream)
        defer.addCallbacks(self._callback, self._errback)

        reactor.callLater(1, reactor.crash)
        reactor.run(installSignalHandlers=0)

        self.assertEqual(self.logs, [True])

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id="name" attribute="name">
              newbar
            </field>
          </fields>
        </doc>"""
        
        defer = self._client.callRemote('reindexDocument', '2', stream)
        defer.addCallbacks(self._callback, self._errback)

        reactor.callLater(1, reactor.crash)
        reactor.run(installSignalHandlers=0)

        self.assertEqual(self.logs, [True, True])

    def test_unindexing(self):

        # XXX use searches 

        self._indexObjects()

        self.logs = []
        
        self._client = None
        self._client = xmlrpc.Proxy('http://127.0.0.1:%s'%self._port)

        defer = self._client.callRemote('unindexDocument', '1')
        defer.addCallbacks(self._callback, self._errback)

        reactor.callLater(1, reactor.crash)
        reactor.run(installSignalHandlers=0)

        self.assertEqual(self.logs, [True])
        
        defer = self._client.callRemote('unindexDocument', '2')
        defer.addCallbacks(self._callback, self._errback)

        reactor.callLater(1, reactor.crash)
        reactor.run(installSignalHandlers=0)

        self.assertEqual(self.logs, [True, True])

    def test_searching(self):

        self._indexObjects()

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <analyzer>standard</analyzer>
          <return_fields>
            <field>uid</field>
            <field>name</field>
          </return_fields>
          <fields>
            <field
              id="uid"
              value="1"/>
            <field
              id="name"
              value="foo"/>
          </fields>
        </search>"""

        self._client = None
        self._client = xmlrpc.Proxy('http://127.0.0.1:%s'%self._port)

        self.logs = []

        defer = self._client.callRemote('searchQuery', stream)
        defer.addCallbacks(self._callback, self._errback)

        reactor.callLater(1, reactor.crash)
        reactor.run(installSignalHandlers=0)

        if self.logs:
            res = PythonResultSet(ResultSet(self.logs[0])).getResults()
            self.assertNotEqual(res, {})
            self.assertEqual(len(res), 1)
            self.assertEqual(res, ({u'uid': u'1', u'name': u'foo'},))

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <analyzer>standard</analyzer>
          <return_fields>
            <field>uid</field>
            <field>name</field>
          </return_fields>
          <fields>
            <field
              id="uid"
              value="2"/>
            <field
              id="name"
              value="bar"/>
          </fields>
        </search>"""

        self._client = None
        self._client = xmlrpc.Proxy('http://127.0.0.1:%s'%self._port)

        self.logs = []

        defer = self._client.callRemote('searchQuery', stream)
        defer.addCallbacks(self._callback, self._errback)

        reactor.callLater(1, reactor.crash)
        reactor.run(installSignalHandlers=0)

        if self.logs:
            res = PythonResultSet(ResultSet(self.logs[0])).getResults()
            self.assertNotEqual(res, {})
            self.assertEqual(len(res), 1)
            self.assertEqual(res, ({u'uid': u'2', u'name': u'bar'},))

    def tearDown(self):
        if os.path.exists(self._store_dir):
            shutil.rmtree(self._store_dir)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LuceneXMLRPCServerTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
