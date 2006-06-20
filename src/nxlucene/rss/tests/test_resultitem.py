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
"""RSS result item tests

$Id$
"""

import unittest

import cElemenTree as etree

from nxlucene.rss.resultitem import ResultItem

class ResultItemTestCase(unittest.TestCase):

    def test_interface(self):
        from nxlucene.rss.interfaces import IResultItem
        from zope.interface.verify import verifyClass
        self.assert_(verifyClass(IResultItem, ResultItem))

    def test_getElement_empty(self):
        ri = ResultItem()
        elt = ri.getElement('1', {})
        xml = etree.tostring(elt)
        self.assertEqual(
            xml,
            """<ns0:item xmlns:ns0="http://backend.userland.com/rss2"><ns0:guid>1</ns0:guid><ns1:fields xmlns:ns1="http://namespaces.nuxeo.org/nxlucene/" /></ns0:item>""")

    def test_getElement_with_prop(self):
        ri = ResultItem()
        elt = ri.getElement('1', {'name':'Anguenot', 'givenName':'Julien'})
        xml = etree.tostring(elt)
        self.assertEqual(xml, """<ns0:item xmlns:ns0="http://backend.userland.com/rss2"><ns0:guid>1</ns0:guid><ns1:fields xmlns:ns1="http://namespaces.nuxeo.org/nxlucene/"><ns1:field id="givenName">Julien</ns1:field><ns1:field id="name">Anguenot</ns1:field></ns1:fields></ns0:item>""")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ResultItemTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

