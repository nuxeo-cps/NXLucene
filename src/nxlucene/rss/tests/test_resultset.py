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
"""RSS result set

$Id$
"""

import unittest

try:
    import cElemenTree as etree
except ImportError:
    import elementtree.ElementTree as etree

from nxlucene.rss.resultset import ResultSet
from nxlucene.rss.adapter import PythonResultSet

class ResultSetTestCase(unittest.TestCase):

    def test_interface(self):
        from nxlucene.rss.interfaces import IResultSet
        from zope.interface.verify import verifyClass
        self.assert_(verifyClass(IResultSet, ResultSet))

    def test_getElementSkel(self):
        rs = ResultSet()
        skel = rs._getElementSkel()
        skel_xml = etree.tostring(skel)
        self.assertEqual(skel_xml, """<ns0:rss version="2.0" xmlns:ns0="http://backend.userland.com/rss2" />""")

    def test_addItem(self):
        rs = ResultSet()
        rs.addItem('1', {'name' : 'Anguenot', 'givenName' : 'Julien'})
        xml = etree.tostring(rs._doc)
        self.assertEqual(xml, """<ns0:rss version="2.0" xmlns:ns0="http://backend.userland.com/rss2"><ns0:item><ns0:guid>1</ns0:guid><ns1:fields xmlns:ns1="http://namespaces.nuxeo.org/nxlucene/"><ns1:field id="givenName">Julien</ns1:field><ns1:field id="name">Anguenot</ns1:field></ns1:fields></ns0:item></ns0:rss>""")

    def test_getStream_base(self):
        rs = ResultSet()
        rs.addItem('1', {'name' : 'Anguenot', 'givenName' : 'Julien'})
        self.assertEqual(rs.getStream(), """<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<ns0:rss version="2.0" xmlns:ns0="http://backend.userland.com/rss2"><ns0:item><ns0:guid>1</ns0:guid><ns1:fields xmlns:ns1="http://namespaces.nuxeo.org/nxlucene/"><ns1:field id="givenName">Julien</ns1:field><ns1:field id="name">Anguenot</ns1:field></ns1:fields></ns0:item></ns0:rss>""")

    def test_adapter(self):
        rs = ResultSet()
        rs.addItem('1', {'name' : 'Anguenot', 'givenName' : 'Julien'})
        pyrs = PythonResultSet(rs)
        self.assert_(pyrs)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ResultSetTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
