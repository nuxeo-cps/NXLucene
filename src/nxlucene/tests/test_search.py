# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2006-2007 Nuxeo SAS <http://nuxeo.com>
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
import random

from nxlucene.server.core import LuceneServer

from nxlucene.rss.resultset import ResultSet
from nxlucene.rss.adapter import PythonResultSet

class FakeXMLInputStream(object):

    def __init__(self, ob, attributs=(), analyzer='Standard'):
        self._fields = {}
        for attr, type_ in attributs:
            id_ = attr
            self._fields[id_] = {
                'id' : id_,
                'attribute' : id_,
                'type' : type_,
                'value': getattr(ob, id_),
                'analyzer' : analyzer,
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

        # Try to return the stored value

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            return_fields=('name',),
            search_fields=({'id' : u'name',
                            'value': u'Foo'},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'1', u'name': u'Foo'},))

    def test_fulltext(self):

        # Indes a new document.
        ob = Foo(fulltext="ab cd")
        query = FakeXMLInputStream(ob, attributs=(('fulltext', 'UnStored'),))
        self._server.indexDocument('2', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'fulltext',
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

    def test_french_fulltest(self):
        text = "Test n�67-236: Les parts sociales ne peuvent �tre donn�es en " \
       "nantissement. Je suis un enfant de l'ind�pendance. Je ch?rche " \
       "f*rcement bien!"
        text = unicode(text, 'iso-8859-15')

        # Indes a new document.
        ob = Foo(fulltext=text)
        query = FakeXMLInputStream(ob, attributs=(('fulltext', 'UnStored'),),
                                   analyzer="french")
        self._server.indexDocument('2.1', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'fulltext',
                             'value': u"ind�pendance",
                             'analyzer': 'french'},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'2.1'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'fulltext',
                             'value': u"l'ind�pendance",
                             'analyzer': 'french'},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'2.1'},))


    def test_path(self):

        # Indes a new document.
        ob = Foo(path="/a/b/c")
        query = FakeXMLInputStream(
            ob,
            attributs=(('path', 'Path'),),
            )
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
                            'value': u'/a*'},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'3'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'path',
                            'type' : 'path',
                            'value': u'/a/*'},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'3'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'path',
                            'type' : 'path',
                            'value': u'/a/*'},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'3'},))

        # Not good.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'path',
                            'type' : 'path',
                            'value': u'/b'},))))
        self.assertEqual(res.getResults()[0], ())

    def test_multiple_path(self):

        # Index a new document.
        ob = Foo(path="/a/b/c")
        ob2 = Foo(path="/aa/bb")

        query = FakeXMLInputStream(ob, attributs=(('path', 'Path'),))
        self._server.indexDocument('1', query)

        query = FakeXMLInputStream(ob2, attributs=(('path', 'Path'),))
        self._server.indexDocument('2', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'path',
                            'type' : 'path',
                            'value': u'/a/b/c'},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'1'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'path',
                            'type' : 'path',
                            'value': u'/aa/bb'},))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'2'},))

        # Path as 2 configurations with condition
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'path',
             'type' : 'path',
             'value': u'/aa/bb',
             'condition' : 'OR'},

            {'id' : u'path',
             'type' : 'path',
             'value': u'/a/b/c',
             'condition' : 'OR'},

            ))))
        self.assertEqual(res.getResults()[0],
                         ({u'uid': u'1'}, {u'uid': u'2'},))

        # Path as 2 with  # separators
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'path',
             'type' : 'path',
             'value': '/aa/bb#/a/b/c',
             },
            ))))
        self.assertEqual(res.getResults()[0],
                         ({u'uid': u'1'}, {u'uid': u'2'},))

    def test_multi_fields(self):

        uid = unicode(str(random.randint(0, 1000)))

        ob = Foo(field='a#b')

        query = FakeXMLInputStream(ob, attributs=(('field', 'MultiKeyword'),))
        self._server.indexDocument(uid, query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            ('field',),
            search_fields=(

            {'id' : u'field',
             'type' : 'MultiKeyword',
             'value': 'a',
             },
            ))))
        self.assertEqual(res.getResults()[0],
                         ({u'field': [u'a', u'b'], u'uid': uid},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            ('field',),
            search_fields=(

            {'id' : u'field',
             'type' : 'MultiKeyword',
             'value': 'b',
             },
            ))))
        self.assertEqual(res.getResults()[0],
                         ({u'field': [u'a', u'b'], u'uid': uid},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            ('field',),
            search_fields=(

            {'id' : u'field',
             'type' : 'MultiKeyword',
             'value': 'a',
             'condition' : 'OR',
             },

            {'id' : u'field',
             'type' : 'MultiKeyword',
             'value': 'b',
             'condition' : 'OR',
             },
            ))))
        self.assertEqual(res.getResults()[0],
                         ({u'field': [u'a', u'b'], u'uid': uid},))


    def test_keyword_search(self):
        # Indes a new document.

        ob = Foo(allowedRolesAndUsers="Manager#Member")

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
                            'value': u'Manager#xxxxxx#Member',
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
            attributs=(('allowedRolesAndUsers', 'MultiKeyword'),),)
        self._server.indexDocument('5', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'allowedRolesAndUsers',
                            'type' : 'MultiKeyword',
                            'value': u'xx:yy',
                            },))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'5'},))


        ob = Foo(allowedRolesAndUsers="MMM#xx:zz")

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
                            'value': u'xx:zz#MMM',
                            },))))
        self.assertEqual(res.getResults()[0], ({u'uid': u'6'},))

    def test_keyword_not_search(self):
        attributs = ( ('allowedRolesAndUsers', 'MultiKeyword'),
                      ('type', 'Keyword'), )

        ob = Foo(allowedRolesAndUsers="xx:yy", type='foo')
        query = FakeXMLInputStream(ob, attributs=attributs)
        self._server.indexDocument('5', query)

        ob = Foo(allowedRolesAndUsers="MMM#xx:zz", type='bar')
        query = FakeXMLInputStream(ob, attributs=attributs)
        self._server.indexDocument('6', query)

        def _search(*fields):
            return PythonResultSet(
                ResultSet(self._server.searchQuery(
                (),
                search_fields=fields)))

        # non purely negative
        res = _search({'id' : u'allowedRolesAndUsers',
                       'type' : 'MultiKeyword',
                       'value': u'xx:yy',
                       },
                      {'id' : u'type',
                       'type' : 'Keyword',
                       'value': u'bar',
                       'condition': 'NOT',
                       },)
        self.assertEqual(res.getResults()[0], ({u'uid': u'5'},))

        res = _search({'id' : u'type',
                       'type' : 'Keyword',
                       'value': u'foo',
                       'condition': 'NOT',
                       },)
        self.assertEqual(res.getResults()[0], ({u'uid': u'6'},))

        # purely negative
        res = _search({'id' : u'allowedRolesAndUsers',
                       'type' : 'MultiKeyword',
                       'value': u'MMM',
                       'condition': 'NOT',
                       },
                      {'id' : u'type',
                       'type' : 'Keyword',
                       'value': u'bar',
                       'condition': 'NOT',
                       },)
        self.assertEqual(res.getResults()[0], ({u'uid': u'5'},))

        ob = Foo(allowedRolesAndUsers="xx:zz", type='bar')
        query = FakeXMLInputStream(ob, attributs=attributs)
        self._server.indexDocument('7', query)
        res = _search({'id' : u'allowedRolesAndUsers',
                       'type' : 'MultiKeyword',
                       'value': u'MMM#xx:yy',
                       'condition': 'NOT',
                       },)
        self.assertEqual(res.getResults()[0], ({u'uid': u'7'},))

    def test_text_more_keyword(self):

        uid = unicode(str(random.randint(0, 1000)))

        ob = Foo(portal_type="Section")

        query = FakeXMLInputStream(
            ob,
            attributs=(('portal_type', 'Keyword'),))
        self._server.indexDocument(uid, query)
        self._server.optimize()

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'portal_type',
                            'type' : 'Keyword',
                            'value': 'Section',
                            },))))
        self.assertEqual(res.getResults()[0], ({u'uid': uid},))

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

        # XXX UTC +1
        self.assertEqual(
            record['modified'],
            '2006-01-01 00:00:00')

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

    def test_sort_field(self):

        ob1 = Foo(name="aa", name_sort="aa")
        ob2 = Foo(name="ab", name_sort="ab")
        ob3 = Foo(name="ac", name_sort="ac")

        query = FakeXMLInputStream(
            ob1,
            attributs=(('name', 'Text'), ('name_sort', 'Sort'),))
        self._server.indexDocument(1, query)

        query = FakeXMLInputStream(
            ob2,
            attributs=(('name', 'Text'), ('name_sort', 'Sort'),))
        self._server.indexDocument(2, query)

        query = FakeXMLInputStream(
            ob3,
            attributs=(('name', 'Text'), ('name_sort', 'Sort'),))
        self._server.indexDocument(3, query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'name',
                            'type' : 'Text',
                            'value': 'a*',},),
            )))

        self.assertEqual(res.getResults()[0],
                         ({u'uid': u'1'}, {u'uid': u'2'}, {u'uid': u'3'}))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'name',
                            'type' : 'Text',
                            'value': 'a*',},
                           ),
            search_options={
                            'sort-on' : 'name_sort',
                            'sort-order' : '',
                            },
            )))

        self.assertEqual(res.getResults()[0],
                         ({u'uid': u'1'}, {u'uid': u'2'}, {u'uid': u'3'}))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=({'id' : u'name',
                            'type' : 'Text',
                            'value': 'a*',},
                           ),
            search_options={
                            'sort-on' : 'name_sort',
                            'sort-order' : 'reverse',
                            },
            )))

        self.assertEqual(res.getResults()[0],
                         ({u'uid': u'3'}, {u'uid': u'2'}, {u'uid': u'1'}))

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

        ob1 = Foo(content="l'homme eu chante")

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

        # Found here since no French Analyzer for stopwords
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': "eu",
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 1)

    def test_french_analyzer_stopwords(self):

        fr = unicode("eu avoir chant�", 'iso-8859-15')
        ob1 = Foo(content=fr)

        query = FakeXMLInputStream(
            ob1,
            attributs=(('content', 'Text'),),
            analyzer='french'
            )
        self._server.indexDocument('x', query)

        # This should be remove with stopwords using french analyzer
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': unicode('avoir', 'iso-8859-15'),
             'analyzer' : 'french',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 0)

        # This should be remove with stopwords using french analyzer
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': unicode('eu', 'iso-8859-15'),
             'analyzer' : 'french',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 0)

        # This should be remove since indexed without.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': unicode('avoir', 'iso-8859-15'),
             'analyzer' : 'standard',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 0)

    def test_french_filter(self):

        fr = unicode("L'enfant a chant�", 'iso-8859-15')
        ob1 = Foo(content=fr)

        query = FakeXMLInputStream(
            ob1,
            attributs=(('content', 'Text'),),
            analyzer='french'
            )
        self._server.indexDocument('x', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': 'chante',
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
             'value': 'enfant',
             'analyzer' : 'french',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 1)

    def test_french_stemmer(self):

        fr = unicode("chant�", "iso-8859-15")
        ob1 = Foo(content=fr)

        query = FakeXMLInputStream(
            ob1,
            attributs=(('content', 'Text'),),
            analyzer='french'
            )
        self._server.indexDocument('x', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Text',
             'value': unicode('chant�', 'iso-8859-15'),
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
             'value': unicode("chant�e", "iso-8859-15"),
             'analyzer' : 'french',
            },

            ))))
        self.assertEqual(len(res.getResults()[0]), 1)

    def test_french_stemmer_unstored(self):

        fr = unicode("chant�", "iso-8859-15")
        ob1 = Foo(content=fr)

        query = FakeXMLInputStream(
            ob1,
            attributs=(('content', 'UnStored'),),
            analyzer='french'
            )
        self._server.indexDocument('x', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'Unstored',
             'value': unicode('chant�', 'iso-8859-15'),
             'analyzer' : 'french',
            },

            ))))
        self.assertEqual(len(res.getResults()[0]), 1)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'UnStored',
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
             'type' : 'UnStored',
             'value': unicode("chant�e", "iso-8859-15"),
             'analyzer' : 'french',
            },

            ))))
        self.assertEqual(len(res.getResults()[0]), 1)

    def test_french_filter_unstored(self):

        fr = unicode("L'enfant a chant�", 'iso-8859-15')
        ob1 = Foo(content=fr)

        query = FakeXMLInputStream(
            ob1,
            attributs=(('content', 'UnStored'),),
            analyzer='french'
            )
        self._server.indexDocument('x', query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'UnStored',
             'value': 'chante',
             'analyzer' : 'french',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 1)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'UnStored',
             'value': 'enfant',
             'analyzer' : 'french',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 1)

    def test_french_analyzer_stopwords_unstored(self):

        fr = unicode("eu avoir chant�", 'iso-8859-15')
        ob1 = Foo(content=fr)

        query = FakeXMLInputStream(
            ob1,
            attributs=(('content', 'UnStored'),),
            analyzer='french'
            )
        self._server.indexDocument('x', query)

        # This should be remove with stopwords using french analyzer
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'UnStored',
             'value': unicode('avoir', 'iso-8859-15'),
             'analyzer' : 'french',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 0)

        # This should be remove with stopwords using french analyzer
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'UnStored',
             'value': unicode('eu', 'iso-8859-15'),
             'analyzer' : 'french',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 0)

        # This should be remove since indexed without.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            (),
            search_fields=(

            {'id' : u'content',
             'type' : 'UnStored',
             'value': unicode('avoir', 'iso-8859-15'),
             'analyzer' : 'standard',
            },

            ))))

        self.assertEqual(len(res.getResults()[0]), 0)

    def test_kw_with_integer(self):

        ob1 = Foo(value=unicode(2))

        query = FakeXMLInputStream(
            ob1,
            attributs=(('value', 'Keyword'),),
            )
        self._server.indexDocument(1, query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            ('value',),
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
            },

            ))))

        self.assertEqual(
            res.getResults()[0], ({u'uid': u'1', u'value': u'2'},))

    def test_search_sort_analyzer_no_french(self):

        ob1 = Foo(value=unicode('Bonjour', 'iso-8859-15'))
        ob2 = Foo(value=unicode('Assez bien', 'iso-8859-15'))
        ob3 = Foo(value=unicode('Tr�s bien', 'iso-8859-15'))

        for uid, ob in ((1, ob1), (2, ob2), (3, ob3)):

            # My Fake API sucks...
            query = FakeXMLInputStream(
                ob,
                attributs=(('value', 'Text',),),
                analyzer='French',
                )

            query._fields['value_sort'] = {
                'id' : 'value_sort',
                'attribute' : 'value',
                'type' : 'Sort',
                'value': ob.value,
                'analyzer' : 'Sort',
                }

            self._server.indexDocument(uid, query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '2',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '3',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },


            ))))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'1'}, {u'uid': u'2'}, {u'uid': u'3'}))

        # Now sort this on calue-sort

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '2',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '3',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },

            ),
            search_options={
            'sort-on' : 'value_sort',
            },
            )))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'2'}, {u'uid': u'1'}, {u'uid': u'3'}))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '2',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '3',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },

            ),
            search_options={
            'sort-on' : 'value_sort',
            'sort-order' : 'reverse',
            },
            )))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'3'}, {u'uid': u'1'}, {u'uid': u'2'}))

    def test_search_sort_analyzer_french(self):

        ob1 = Foo(value=unicode('�a va', 'iso-8859-15'))
        ob2 = Foo(value=unicode('� voir', 'iso-8859-15'))
        ob3 = Foo(value=unicode('Tr�s bien', 'iso-8859-15'))

        for uid, ob in ((1, ob1), (2, ob2), (3, ob3)):

            # My Fake API sucks...
            query = FakeXMLInputStream(
                ob,
                attributs=(('value', 'Text',),),
                analyzer='French',
                )

            query._fields['value_sort'] = {
                'id' : 'value_sort',
                'attribute' : 'value',
                'type' : 'Sort',
                'value': ob.value,
                'analyzer' : 'Sort',
                }

            self._server.indexDocument(uid, query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '2',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '3',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },


            ))))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'1'}, {u'uid': u'2'}, {u'uid': u'3'}))

        # Now sort this on calue-sort

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '2',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '3',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },

            ),
            search_options={
            'sort-on' : 'value_sort',
            },
            )))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'2'}, {u'uid': u'1'}, {u'uid': u'3'}))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '2',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },
            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '3',
             'analyzer' : 'Standard',
             'condition' : 'OR',
             },

            ),
            search_options={
            'sort-on' : 'value_sort',
            'sort-order' : 'reverse',
            },
            )))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'3'}, {u'uid': u'1'}, {u'uid': u'2'}))

    def test_keyword_tiry(self):

        ob = Foo(internet_user='ZopeFront:root')

        # My Fake API sucks...
        query = FakeXMLInputStream(
            ob,
            attributs=(('internet_user', 'Keyword',),),
            analyzer='Standard',
            )

        self._server.indexDocument(1, query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0], ({u'uid': u'1'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            return_fields=('internet_user',),
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'1', u'internet_user': u'ZopeFront:root'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            return_fields=('internet_user',),
            search_fields=(

            {'id' : u'internet_user',
             'type' : 'Keyword',
             'value': 'ZopeFront:root',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'1', u'internet_user': u'ZopeFront:root'},))

        # With unicode
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            return_fields=('internet_user',),
            search_fields=(

            {'id' : u'internet_user',
             'type' : 'Keyword',
             'value': unicode('ZopeFront:root'),
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'1', u'internet_user': u'ZopeFront:root'},))

    def test_multikeyword_tiry(self):

        ob = Foo(internet_user='ZopeFront:root#ZopeFront:julien')

        # My Fake API sucks...
        query = FakeXMLInputStream(
            ob,
            attributs=(('internet_user', 'MultiKeyword',),),
            analyzer='Standard',
            )

        self._server.indexDocument(1, query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0], ({u'uid': u'1'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            return_fields=('internet_user',),
            search_fields=(

            {'id' : u'uid',
             'type' : 'Keyword',
             'value': '1',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'1', u'internet_user': [u'ZopeFront:root', u'ZopeFront:julien']},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            return_fields=('internet_user',),
            search_fields=(

            {'id' : u'internet_user',
             'type' : 'MultiKeyword',
             'value': 'ZopeFront:root',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'1', u'internet_user': [u'ZopeFront:root', u'ZopeFront:julien']},))

        # With unicode
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            return_fields=('internet_user',),
            search_fields=(

            {'id' : u'internet_user',
             'type' : 'MultiKeyword',
             'value': unicode('ZopeFront:root'),
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0],
            ({u'uid': u'1', u'internet_user': [u'ZopeFront:root', u'ZopeFront:julien']},))

    def test_multikeyword_with_spaces(self):

        ob = Foo(portal_types='CPS Type1#CPS Type2')

        # My Fake API sucks...
        query = FakeXMLInputStream(
            ob,
            attributs=(('portal_types', 'MultiKeyword',),),
            analyzer='Standard',
            )

        self._server.indexDocument(1, query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'uid',
             'type' : 'MultiKeyword',
             'value': '1',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0], ({u'uid': u'1'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'portal_types',
             'type' : 'MultiKeyword',
             'value': 'CPS Type1',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0], ({u'uid': u'1'},))

    def test_keyword_with_special_chars(self):

        ob = Foo()
        setattr(ob, 'portal:types', 'CPS:type')

        # My Fake API sucks...
        query = FakeXMLInputStream(
            ob,
            attributs=(('portal:types', 'Keyword',),),
            analyzer='Standard',
            )

        self._server.indexDocument(1, query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'portal:types',
             'type' : 'Keyword',
             'value': 'CPS:type',
             'analyzer' : 'Standard',
             },

            ))))

    def test_multi_keyword_with_special_chars(self):

        ob = Foo()
        setattr(ob, 'portal:types', 'CPS:type#CPS:type2')

        # My Fake API sucks...
        query = FakeXMLInputStream(
            ob,
            attributs=(('portal:types', 'MultiKeyword',),),
            analyzer='Standard',
            )

        self._server.indexDocument(1, query)

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'portal:types',
             'type' : 'MultiKeyword',
             'value': 'CPS:type',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0], ({u'uid': u'1'},))

        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'portal:types',
             'type' : 'MultiKeyword',
             'value': 'CPS:type2',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0], ({u'uid': u'1'},))

    def test_queryparser_stemming_FR(self):

        ob = Foo()
        setattr(ob, 'SearchableText', 'INVENTAIRE')

        # My Fake API sucks...
        query = FakeXMLInputStream(
            ob,
            attributs=(('SearchableText', 'Unstored',),),
            analyzer='French',
            )
        self._server.indexDocument(1, query)

        setattr(ob, 'SearchableText', 'should not match')
        query = FakeXMLInputStream(
            ob,
            attributs=(('SearchableText', 'Unstored',),),
            analyzer='French',
            )
        self._server.indexDocument(2, query)

        # No wildcard here.
        search_fields=(
            {'id' : u'SearchableText',
             'type' : 'Unstored',
             'value': 'inventair',
             'analyzer' : 'French',
             },)
        query = self._server.searchQuery(search_fields=search_fields)
        rs = ResultSet(query)
        res = PythonResultSet(rs)
        res = res.getResults()
        self.assertEqual(res[-1], 1)
        self.assertEqual(res[0], ({u'uid': u'1'},))

        # Wildcard here.

    def notest_queryparser_stemming_with_wildcards_FR(self):
        # This does not work.

        ob = Foo()
        setattr(ob, 'SearchableText', 'GEIDE')

        # My Fake API sucks...
        query = FakeXMLInputStream(
            ob,
            attributs=(('SearchableText', 'Unstored',),),
            analyzer='French',
            )

        self._server.indexDocument(1, query)
        setattr(ob, 'SearchableText', 'should not match')
        self._server.indexDocument(2, query)

        # No wildcard here.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'SearchableText',
             'type' : 'Unstored',
             'value': 'GEIDE',
             'analyzer' : 'French',
             },

            ))))

        res = res.getResults()
        self.assertEqual(res[-1], 1)
        self.assertEqual(res[0], ({u'uid': u'1'},))

        # Wildcard here.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'SearchableText',
             'type' : 'Unstored',
             'value': 'GE?DE',
             'analyzer' : 'French',
             },

            ))))

        res = res.getResults()
        self.assertEqual(res[-1], 1)
        self.assertEqual(res[0], ({u'uid': u'1'},))

    def test_queryparser_stemming_with_wildcards_STD(self):

        ob = Foo()
        setattr(ob, 'SearchableText', 'GEIDE')

        # My Fake API sucks...
        query = FakeXMLInputStream(
            ob,
            attributs=(('SearchableText', 'Unstored',),),
            analyzer='Standard',
            )

        self._server.indexDocument(1, query)

        # No wildcard here.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'SearchableText',
             'type' : 'Unstored',
             'value': 'GEIDE',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0], ({u'uid': u'1'},))

        # Wildcard here.
        res = PythonResultSet(
            ResultSet(self._server.searchQuery(
            search_fields=(

            {'id' : u'SearchableText',
             'type' : 'Unstored',
             'value': 'GE?DE',
             'analyzer' : 'Standard',
             },

            ))))

        self.assertEqual(
            res.getResults()[0], ({u'uid': u'1'},))

    def tearDown(self):
        if os.path.exists(self._store_dir):
            shutil.rmtree(self._store_dir)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LuceneSeachTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
