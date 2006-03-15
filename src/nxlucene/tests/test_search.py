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
"""Test core lucene search
"""

import os
import shutil
import unittest

from nxlucene.core import LuceneServer

from nxlucene.rss.resultset import ResultSet
from nxlucene.rss.adapter import PythonResultSet

class FakeXMLInputStream(object):

    def __init__(self, ob, attributs=()):
        self._fields = {}
        for attr, type_ in attributs:
            id_ = attr
            self._fields[id_] = {
                'id' : id_,
                'attribute' : id_,
                'type' : type_,
                'value': getattr(ob, id_),
                }

    def getFields(self):
        return self._fields.values()

class Foo(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)

class LuceneSeachTestCase(unittest.TestCase):

    def setUp(self):
        self._store_dir = '/tmp/lucene'
        self._server = LuceneServer(self._store_dir)

    def test_text(self):

        ob = Foo(name = 'Foo')
        query = FakeXMLInputStream(ob, attributs=(('name', 'Text'),))
        self._server.indexDocument('1', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery((), kws={'name': 'Foo'})))
        self.assertEqual(res.getResults(), ({u'uid': u'1'},))
        
    def xtest_fulltext(self):

        # Indes a new document.
        ob = Foo(fulltext="a b c d")
        query = FakeXMLInputStream(ob, attributs=(('fulltext', 'UnStored'),))
        self._server.indexDocument('2', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery((), kws={'fulltext': 'a'})))
        self.assertEqual(res.getResults(), ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery((), kws={'fulltext': 'b'})))
        self.assertEqual(res.getResults(), ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery((), kws={'fulltext': 'c'})))
        self.assertEqual(res.getResults(), ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery((), kws={'fulltext': 'd'})))
        self.assertEqual(res.getResults(), ({u'uid': u'2'},))


    def test_path(self):

        # Indes a new document.
        ob = Foo(path="/a/b/c")
        query = FakeXMLInputStream(ob, attributs=(('path', 'Path'),))
        self._server.indexDocument('3', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery((), kws={'path': '/a/b/c'})))
        self.assertEqual(res.getResults(), ({u'uid': u'3'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery((), kws={'path': '/a'})))
        self.assertEqual(res.getResults(), ({u'uid': u'3'},))

        # Not good.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery((), kws={'path': '/b'})))
        self.assertEqual(res.getResults(), ())

    def tearDown(self):
        if os.path.exists(self._store_dir):
            shutil.rmtree(self._store_dir)
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LuceneSeachTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
