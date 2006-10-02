# -*- coding: ISO-8859-15 -*-
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
"""Test PythonResultSet class

$Id$
"""

import unittest

from nxlucene.rss.resultset import ResultSet
from nxlucene.rss.adapter import PythonResultSet

class PythonResultSetTestCase(unittest.TestCase):

    def setUp(self):
        self._rs = ResultSet()
        self._rs.addItem('1', {'name' : u'Anguenot', 'givenName' : u'Julien'})
        self._rs.addItem('2', {'name' : u'Barroca', 'givenName' : u'\xc9ric'})
        self._pyrs = PythonResultSet(self._rs)

    def test_getItems(self):
        items = self._pyrs._getItems()
        self.assertEqual(len(items), 2)

    def test_getResults(self):
        results = self._pyrs.getResults()
        self.assert_(isinstance(results, tuple))
        self.assertEqual(len(results[0]), 2)
        self.assertEqual(results[0], ({u'givenName': 'Julien', u'uid': '1', u'name': 'Anguenot'}, {u'givenName': u'\xc9ric', u'uid': '2', u'name': 'Barroca'}))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PythonResultSetTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
