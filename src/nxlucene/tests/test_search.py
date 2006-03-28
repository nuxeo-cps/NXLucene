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
            ResultSet(self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': u'Foo'},))))
        self.assertEqual(res.getResults(), ({u'uid': u'1'},))
                      
    def test_fulltext(self):

        # Indes a new document.
        ob = Foo(fulltext="ab cd")
        query = FakeXMLInputStream(ob, attributs=(('fulltext', 'UnStored'),))
        self._server.indexDocument('2', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            ()
,            search_fields=({'id' : u'fulltext',
                             'value': u'ab'},))))
        self.assertEqual(res.getResults(), ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
                (),
            search_fields=({'id' : u'fulltext',
                            'value': u'cd'},))))
        self.assertEqual(res.getResults(), ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
                (),
            search_fields=({'id' : u'fulltext',
                            'value': "ab OR cd"},))))
        self.assertEqual(res.getResults(), ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
                (),
            search_fields=({'id' : u'fulltext',
                            'value': "ab AND cd"},))))
        self.assertEqual(res.getResults(), ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
                (),
            search_fields=({'id' : u'fulltext',
                            'value': "'ab cd'"},))))
        self.assertEqual(res.getResults(), ({u'uid': u'2'},))

##        res = PythonResultSet(
##            ResultSet(self._server.searchQuery(
##                (),
##            search_fields=({'id' : u'fulltext',
##                            'value': "a*"},))))
##        self.assertEqual(res.getResults(), ({u'uid': u'2'},))

    def test_path(self):

        # Indes a new document.
        ob = Foo(path="/a/b/c")
        query = FakeXMLInputStream(ob, attributs=(('path', 'Path'),))
        self._server.indexDocument('3', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'path',
                            'type' : 'path',
                            'value': u'/a/b/c'},))))
        self.assertEqual(res.getResults(), ({u'uid': u'3'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'path',
                            'type' : 'path',
                            'value': u'/a'},))))
        self.assertEqual(res.getResults(), ({u'uid': u'3'},))

        # Not good.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'path',
                            'type' : 'path',
                            'value': u'/b'},))))
        self.assertEqual(res.getResults(), ())

    def test_keyword_search(self):
        # Indes a new document.

        ob = Foo(allowedRolesAndUsers="Manager Member")

        query = FakeXMLInputStream(
            ob,
            attributs=(('allowedRolesAndUsers', 'Keyword'),))
        self._server.indexDocument('4', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'Keyword',
                            'value': u'Member',
                            },))))
        self.assertEqual(res.getResults(), ({u'uid': u'4'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'Keyword',
                            'value': u'Manager',
                            },))))
        self.assertEqual(res.getResults(), ({u'uid': u'4'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'Keyword',
                            'value': u'Manager xxxxxx Member',
                            },))))
        self.assertEqual(res.getResults(), ({u'uid': u'4'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'Keyword',
                            'value': u'xxxxxx',
                            },))))
        self.assertEqual(res.getResults(), ())

    def test_keyword_search_02(self):
        # Indes a new document.

        ob = Foo(allowedRolesAndUsers="xx:yy")

        query = FakeXMLInputStream(
            ob,
            attributs=(('allowedRolesAndUsers', 'Keyword'),))
        self._server.indexDocument('5', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'Keyword',
                            'value': u'xx:yy',
                            },))))
        self.assertEqual(res.getResults(), ({u'uid': u'5'},))


        ob = Foo(allowedRolesAndUsers="MMM xx:zz")

        query = FakeXMLInputStream(
            ob,
            attributs=(('allowedRolesAndUsers', 'Keyword'),))
        self._server.indexDocument('6', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'Keyword',
                            'value': u'MMM',
                            },))))
        self.assertEqual(res.getResults(), ({u'uid': u'6'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'Keyword',
                            'value': u'xx:zz MMM',
                            },))))
        self.assertEqual(res.getResults(), ({u'uid': u'6'},))

    def test_textindex(self):
        ob = Foo(portal_type="Section")

        query = FakeXMLInputStream(
            ob,
            attributs=(('portal_type', 'Keyword'),))
        self._server.indexDocument('6', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'portal_type',
                            'type' : 'Keyword',
                            'value': u'Section',
                            },))))
        self.assertEqual(res.getResults(), ({u'uid': u'6'},))

        ob = Foo(portal_type="CPS Type")

        query = FakeXMLInputStream(
            ob,
            attributs=(('portal_type', 'Keyword'),))
        self._server.indexDocument('7', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'portal_type',
                            'type' : 'Keyword',
                            'value': u'CPS Type',
                            },))))
        self.assertEqual(res.getResults(), ({u'uid': u'7'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'portal_type',
                            'type' : 'Keyword',
                            'value': u'CPS',
                            },))))
        self.assertEqual(res.getResults(), ())

    def test_datesearch(self):

        ob = Foo(modified="2006-03-27 03:41:00")

        query = FakeXMLInputStream(
            ob,
            attributs=(('modified', 'Date'),))
        self._server.indexDocument('9', query)


        # Exact date match
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'modified',
                            'type' : 'Date',
                            'value': u'2006-03-27 03:41:00',
                            },))))

        self.assertEqual(res.getResults(), ({u'uid': u'9'},))

        # Use range:min now.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'modified',
                            'type' : 'Date',
                            'value': '2006-03-28 04:00:00',
                            'usage' : 'range:max',
                            },))))

        self.assertEqual(res.getResults(), ({u'uid': u'9'},))

        # Use range:min now.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'modified',
                            'type' : 'Date',
                            'value': '2006-02-27 00:00:00',
                            'usage' : 'range:min',
                            },))))

        self.assertEqual(res.getResults(), ({u'uid': u'9'},))
        
    def tearDown(self):
        if os.path.exists(self._store_dir):
            shutil.rmtree(self._store_dir)
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LuceneSeachTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
