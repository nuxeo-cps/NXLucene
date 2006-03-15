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
"""XMLRPC Lucene server test case.

$Id$
"""

import unittest
import xmlrpclib

import nxlucene.testing.xmlrpc

from nxlucene.xmlrpc import XMLRPCLuceneServer
from nxlucene.core import LuceneServer

from nxlucene.rss.resultset import ResultSet
from nxlucene.rss.adapter import PythonResultSet

class XMLRPCLuceneServerTestCase(unittest.TestCase):

    def setUp(self):
        nxlucene.testing.xmlrpc.setUp()
        self._xmlrpc_client = xmlrpclib.ServerProxy('http://foo/bar')

    def test_implementation(self):
        from zope.interface.verify import verifyClass
        from nxlucene.interfaces import IXMLRPCLuceneServer
        self.assert_(verifyClass(IXMLRPCLuceneServer, XMLRPCLuceneServer))

    def test_adapter(self):
        core = LuceneServer('fake')
        xmlrpc = XMLRPCLuceneServer(core)
        self.assertEqual(core, xmlrpc._core)

    def test_rdv(self):

        sms = 'Hi there. Can we meet this evening ?'
        self.assertEqual(self._xmlrpc_client.debug(sms), sms)

    def test_optimize(self):
        self.assertEqual(self._xmlrpc_client.optimize(), True)
        

    def test_store_dir(self):
        # nxlucene.testing has its own tmp store dir
        self.assert_(isinstance(self._xmlrpc_client.getStoreDir(), str))

    def _indexObjects(self):


        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id="name" attribute="name">
              foo
            </field>
          </fields>
        </doc>"""

        res = self._xmlrpc_client.indexDocument('1', stream)
        self.assert_(res)

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id="name" attribute="name">
              bar
            </field>
          </fields>
        </doc>"""

        res = self._xmlrpc_client.indexDocument('2', stream)
        self.assert_(res)

    def test_indexing(self):
        # See test_searching
        self._indexObjects()

    def test_reindexing(self):

        self._indexObjects()

        # XXX serch back to check.

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id="name" attribute="name">
               newfoo
            </field>
          </fields>
        </doc>"""

        res = self._xmlrpc_client.reindexDocument('1', stream)
        self.assert_(res)

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id="name" attribute="name">
              newbar
            </field>
          </fields>
        </doc>"""

        res = self._xmlrpc_client.reindexDocument('2', stream)
        self.assert_(res)

    def test_unindexing(self):

        # XXX use searches

        self._indexObjects()

        res = self._xmlrpc_client.unindexDocument('1')
        self.assert_(res)

        res = self._xmlrpc_client.unindexDocument('2')
        self.assert_(res)

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
          </fields>
        </search>"""

        rss = self._xmlrpc_client.searchQuery(stream)
        res = PythonResultSet(ResultSet(rss)).getResults()

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
          </fields>
        </search>"""

        rss = self._xmlrpc_client.searchQuery(stream)
        res = PythonResultSet(ResultSet(rss)).getResults()

        self.assertNotEqual(res, {})
        self.assertEqual(len(res), 1)
        self.assertEqual(res, ({u'uid': u'2', u'name': u'bar'},))

    def tearDown(self):
        nxlucene.testing.xmlrpc.tearDown()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLRPCLuceneServerTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
