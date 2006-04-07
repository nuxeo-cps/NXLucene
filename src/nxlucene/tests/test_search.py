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
import PyLucene

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
        self.assertEqual(res.getResults()[0], ({u'uid': u'1'},))
                      
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
        self.assertEqual(res.getResults()[0], ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
                (),
            search_fields=({'id' : u'fulltext',
                            'value': u'cd'},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
                (),
            search_fields=({'id' : u'fulltext',
                            'value': "ab OR cd"},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
                (),
            search_fields=({'id' : u'fulltext',
                            'value': "ab AND cd"},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'2'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
                (),
            search_fields=({'id' : u'fulltext',
                            'value': "'ab cd'"},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'2'},))

##        res = PythonResultSet(
##            ResultSet(self._server.searchQuery(
##                (),
##            search_fields=({'id' : u'fulltext',
##                            'value': "a*"},))))
##        self.assertEqual(res.getResults()[0], ({u'uid': u'2'},))

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
        self.assertEqual(res.getResults()[0], ({u'uid': u'3'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'path',
                            'type' : 'path',
                            'value': u'/a'},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'3'},))

        # Not good.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'path',
                            'type' : 'path',
                            'value': u'/b'},))))
        self.assertEqual(res.getResults()[0], ())

    def test_keyword_search(self):
        # Indes a new document.

        ob = Foo(allowedRolesAndUsers="Manager Member")

        query = FakeXMLInputStream(
            ob,
            attributs=(('allowedRolesAndUsers', 'MultiKeyword'),))
        self._server.indexDocument('4', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'MultiKeyword',
                            'value': u'Member',
                            },))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'4'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'MultiKeyword',
                            'value': u'Manager',
                            },))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'4'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'MultiKeyword',
                            'value': u'Manager xxxxxx Member',
                            },))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'4'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'MultiKeyword',
                            'value': u'xxxxxx',
                            },))))
        self.assertEqual(res.getResults()[0], ())

    def test_keyword_search_02(self):
        # Indes a new document.

        ob = Foo(allowedRolesAndUsers="xx:yy")

        query = FakeXMLInputStream(
            ob,
            attributs=(('allowedRolesAndUsers', 'MultiKeyword'),))
        self._server.indexDocument('5', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'MultiKeyword',
                            'value': u'xx:yy',
                            },))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'5'},))


        ob = Foo(allowedRolesAndUsers="MMM xx:zz")

        query = FakeXMLInputStream(
            ob,
            attributs=(('allowedRolesAndUsers', 'MultiKeyword'),))
        self._server.indexDocument('6', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'MultiKeyword',
                            'value': u'MMM',
                            },))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'6'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'MultiKeyword',
                            'value': u'xx:zz MMM',
                            },))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'6'},))

    def test_text_more_keyword(self):

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
                            'value': 'Section',
                            },))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'6'},))

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
        self.assertEqual(res.getResults()[0], ({u'uid': u'7'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'portal_type',
                            'type' : 'Keyword',
                            'value': u'CPS',
                            },))))
        self.assertEqual(res.getResults()[0], ())

    def test_datesearch(self):

        ob1 = Foo(modified="2006-01-01 00:00:00")
        ob2 = Foo(modified="2005-01-01 00:00:00")

        query = FakeXMLInputStream(
            ob1,
            attributs=(('modified', 'Date'),))
        self._server.indexDocument('9', query)

        query = FakeXMLInputStream(
            ob2,
            attributs=(('modified', 'Date'),))
        self._server.indexDocument('10', query)
        
        # Exact date match
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'modified',
                            'type' : 'Date',
                            'value': u'2006-01-01 00:00:00',
                            },))))

        self.assertEqual(res.getResults()[0], ({u'uid': u'9'},))

        # Exact date match
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'modified',
                            'type' : 'Date',
                            'value': u'2005-01-01 00:00:00',
                            },))))

        self.assertEqual(res.getResults()[0], ({u'uid': u'10'},))

        # Use range:min now.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'modified',
                            'type' : 'Date',
                            'value': '2006-01-01 00:00:00',
                            'usage' : 'range:min',
                            },))))

        self.assertEqual(res.getResults()[0], ({u'uid': u'9'},))

        # Use range:min now.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'modified',
                            'type' : 'Date',
                            'value': '2005-01-01 00:00:00',
                            'usage' : 'range:min',
                            },))))

        self.assertEqual(res.getResults()[0], ({u'uid': u'9'},{u'uid': u'10'}))

        # Use range:max now.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'modified',
                            'type' : 'Date',
                            'value': '2005-01-01 00:00:00',
                            'usage' : 'range:max',
                            },))))

        self.assertEqual(res.getResults()[0], ({u'uid': u'10'},))

        # Use range:max now.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'modified',
                            'type' : 'Date',
                            'value': '2006-01-01 00:00:00',
                            'usage' : 'range:max',
                            },))))

        self.assertEqual(res.getResults()[0], ({u'uid': u'9'},{u'uid': u'10'}))


    def test_date_returned(self):

        ob1 = Foo(modified="2006-01-01 00:00:00")

        query = FakeXMLInputStream(
            ob1,
            attributs=(('modified', 'Date'),))
        self._server.indexDocument('d1', query)


        # Use range:max now.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            ('modified',),
            search_fields=({'id' : u'modified',
                            'type' : 'Date',
                            'value': '2006-01-01 00:00:00',
                            'usage' : 'range:max',
                            },))))

        self.assertEqual(len(res.getResults()[0]), 1)

        record = res.getResults()[0][0]
        self.assertEqual(record['uid'], 'd1')

        from nxlucene.date import getPythonDateTimeFromJavaStr

        # XXX UTC +1
        self.assertEqual(
            str(getPythonDateTimeFromJavaStr(record['modified'])),
            '2006-01-01 01:00:00')
        
    def test_sorting(self):

        ob1 = Foo(type="contact", name="Bob")
        ob2 = Foo(type="contact", name="Jack")

        query = FakeXMLInputStream(
            ob1,
            attributs=(('name', 'Text'), ('type', 'Keyword')))
        self._server.indexDocument('bob', query)

        query = FakeXMLInputStream(
            ob2,
            attributs=(('name', 'Text'), ('type', 'Keyword')))
        self._server.indexDocument('jack', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'name',
                            'type' : 'Text',
                            'value': 'Jack',
                            },))))

        self.assertEqual(res.getResults()[0], ({u'uid': u'jack'},))
        
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'name',
                            'type' : 'Text',
                            'value': 'Bob',
                            },))))

        self.assertEqual(res.getResults()[0], ({u'uid': u'bob'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'type',
                            'type' : 'Keyword',
                            'value': 'contact',
                            },))))

        self.assertEqual(res.getResults()[0],
                         ({u'uid': u'bob'}, {u'uid': u'jack'}))

        # Let's sort now.

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'type',
                            'type' : 'Keyword',
                            'value': 'contact',},),
            search_options={
                            'sort-on' : 'name',
                            'sort-order' : 'reverse',
                            },)))

        self.assertEqual(res.getResults()[0],
                         ({u'uid': u'jack'}, {u'uid': u'bob'}))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'type',
                            'type' : 'Keyword',
                            'value': 'contact',},),
            search_options={
                            'sort-on' : 'name',
                            'sort-order' : '',
                            },)))

        self.assertEqual(res.getResults()[0],
                         ({u'uid': u'bob'}, {u'uid': u'jack'}))

    def test_kewyord_search_with_spaces(self):

        o1 = Foo(portal_type='CPS Type1')
        o2 = Foo(portal_type='CPS Type2')

        query = FakeXMLInputStream(
            o1,
            attributs=(('portal_type', 'Keyword'),))
        self._server.indexDocument('o1', query)

        query = FakeXMLInputStream(
            o2,
            attributs=(('portal_type', 'Keyword'),))
        self._server.indexDocument('o2', query)

        # Lookup for o1
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'portal_type',
                            'type' : 'Keyword',
                            'value': 'CPS Type1',
                            },))))

        self.assertEqual(res.getResults()[0], ({u'uid': u'o1'},))

        # Lookup for o1
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'portal_type',
                            'type' : 'Keyword',
                            'value': 'CPS Type2',
                            },))))

        self.assertEqual(res.getResults()[0], ({u'uid': u'o2'},))

        # Verify nothing's return if we only request for half of the
        # keyword element.

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'portal_type',
                            'type' : 'Keyword',
                            'value': 'CPS ',
                            },))))

        self.assertEqual(res.getResults()[0], ())
        
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'portal_type',
                            'type' : 'Keyword',
                            'value': 'Type1',
                            },))))

        self.assertEqual(res.getResults()[0], ())


        # Lookup for o1 and o2
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'portal_type',
             'type' : 'Keyword',
             'value': 'CPS Type2',
             'condition' : 'OR'
            },

            {'id' : u'portal_type',
             'type' : 'Keyword',
             'value': 'CPS Type1',
             'condition': 'OR'
            },
            
            ))))

        self.assertEqual(res.getResults()[0],
                         ({u'uid': u'o1'}, {u'uid': u'o2'},))


    def test_french_no_analyzer(self):

        ob1 = Foo(content="l'homme chante")

        query = FakeXMLInputStream(
            ob1,
            attributs=(('content', 'Text'),))
        self._server.indexDocument('x', query)


        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': "chante",
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 1)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': "l'homme",
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 1)

        # Not found here.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': "homme",
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 0)

    def xtest_french_analyzer(self):

        ob1 = Foo(content="l'homme chante")

        query = FakeXMLInputStream(
            ob1,
            attributs=(('content', 'Text'),))
        self._server.indexDocument('x', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': "chante",
             'analyzer' : 'french',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 1)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': "l'homme",
             'analyzer' : 'french',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 1)

        # Not found here.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': "homme",
             'analyzer' : 'french',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 1)
        
    def tearDown(self):
        if os.path.exists(self._store_dir):
            shutil.rmtree(self._store_dir)
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LuceneSeachTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
