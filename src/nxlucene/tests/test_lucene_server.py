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
"""Test core Lucene server API.

This does *not* test the actual server but its internal on an object
instance. See test_xmlrpc_server for tests against an actual

$Id$
"""

import os
import shutil
import unittest
import threading

import zope.interface

from nxlucene.server.PatchPythonThread import PythonThread
from nxlucene.server.core import LuceneServer
from nxlucene.rss.adapter import PythonResultSet
from nxlucene.rss.resultset import ResultSet

class P(object):
    zope.interface.implements(zope.interface.Interface)
    def __init__(self, name, givenName='', fulltext=''):
        self.name = name
        if givenName == '':
            self.givenName = name
        else:
            self.givenName = givenName
        self.fulltext = fulltext

class FakeXMLInputStream(object):

    def __init__(self, ob, attributs=()):
        self._fields = {}
        for id_ in attributs:
            self._fields[id_] = {
                'id' : id_,
                'attribute' : id_,
                'type' : id_ == 'fulltext' and 'Unstored' or 'Text',
                'value': getattr(ob, id_),
                }

    def getFields(self):
        return self._fields.values()

class LuceneServerTestCase(unittest.TestCase):

    def setUp(self):
        self._store_dir = '/tmp/lucene'
        self._server = LuceneServer(self._store_dir)
        self._o1 = P('foo', fulltext="Fulltext on object1")
        self._o2 = P('bar', fulltext="Fulltext on object2")

    def tearDown(self):
        if os.path.exists(self._store_dir):
            shutil.rmtree(self._store_dir)

    def test_store_dir(self):
        self.assertEqual(self._store_dir, self._server.store_dir)

    def test_implementation(self):
        from zope.interface.verify import verifyClass
        from nxlucene.server.interfaces import ILuceneServer
        self.assert_(verifyClass(ILuceneServer, LuceneServer))

    def test_optimize(self):
        self.assert_(self._server.optimize())

    def _indexObjects(self):
        self.assertEqual(len(self._server), 0)
        self._server.indexDocument(1, FakeXMLInputStream(self._o1, 
                                   attributs=('name','fulltext')))
        self._server.indexDocument(2, FakeXMLInputStream(self._o2, 
                                   attributs=('name','fulltext')))
        self.assertEqual(len(self._server), 2)

    def test_clean(self):
        self.assertEqual(len(self._server), 0)
        self._indexObjects()
        self.assertEqual(len(self._server), 2)
        self.assert_(self._server.clean())
        self.assertEqual(len(self._server), 0)

    def test_indexing(self):
        self._indexObjects()

    def test_searching(self):

        self._indexObjects()

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'1'},))
        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o1 on uid (with return fields)
        res = self._server.searchQuery(return_fields=('name',),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'1'},))
        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1', u'name':u'foo'},))

        # Search o1 on name (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'name',
                                                       'value': u'foo'},))
        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o1 on name (with return fields)
        res = self._server.searchQuery(return_fields=('name',),
                                       search_fields=({'id' : u'name',
                                                       'value': u'foo'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1', u'name':u'foo'},))

        # Search o2 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'2'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2'},))

        # Search o2 on uid (with return fields)
        res = self._server.searchQuery(return_fields=('name',),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'2'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2', u'name':u'bar'},))

        # Search o2 on name (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'name',
                                                       'value': u'bar'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2'},))

        # Search o2 on name (with return fields)
        res = self._server.searchQuery(return_fields=('name',),
                                       search_fields=({'id' : u'name',
                                                       'value': u'bar'},))
        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2', u'name':u'bar'},))

    def test_unindexing(self):

        self._indexObjects()

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'1'},))
        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'2'},))
        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2'},))

        # Unindex o1
        self._server.unindexDocument(1)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'1'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ())

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'2'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2'},))

        # Unindex o1
        self._server.unindexDocument(2)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'2'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ())

    def test_reindexing(self):
        self._indexObjects()

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'name',
                                                       'value': u'foo'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o2 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'name',
                                                       'value': u'bar'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2'},))

        # Search o1 on fulltext (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'fulltext',
                                                       'value': u'object1'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o2 on fulltext (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'fulltext',
                                                       'value': u'object2'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2'},))

        # Reindex o1 with a new name
        self._o1.name = 'newfoo'
        self._server.reindexDocument(1, FakeXMLInputStream(
            self._o1, attributs=('name','fulltext')))

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=('name',),
                                       search_fields=({'id' : u'name',
                                                       'value': u'foo'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ())

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'name',
                                                       'value': u'newfoo'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o2 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'name',
                                                       'value': u'bar'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2'},))

        # Search o1 on fulltext (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'fulltext',
                                                       'value': u'object1'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1'},))

        # Reindex o2 with a new name, reindex only the name field
        self._o2.name = 'newbar'
        self._server.reindexDocument(2, FakeXMLInputStream(
            self._o2, attributs=('name',)))

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'name',
                                                       'value': u'foo'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ())

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'name',
                                                       'value': u'newfoo'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o2 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'name',
                                                       'value': u'bar'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ())

        # Search o2 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'name',
                                                       'value': u'newbar'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2'},))

        # Reindexing just one field cleares unstored indexes. This is a known
        # problem with Lucene, for which we have no solution at the moment.
        # So the following test which demonstrates this) is currently 
        # commented out.
        ## Search o2 on fulltext (no return fields)
        #res = self._server.searchQuery(return_fields=(),
                                       #search_fields=({'id' : u'fulltext',
                                                       #'value': u'object2'},))

        #res = PythonResultSet(ResultSet(res)).getResults()[0]
        #self.assertEqual(res, ({u'uid': u'2'},),) 

    def test_clearing(self):

        self._indexObjects()

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'1'},))
        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o2 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'2'},))
        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'2'},))

        self._server.clean()

        # Search o1 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'1'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ())

        # Search o2 on uid (no return fields)
        res = self._server.searchQuery(return_fields=(),
                                       search_fields=({'id' : u'uid',
                                                       'value': u'2'},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ())

    def test_withpathasindex(self):

        # Test with something else than an integer
        self.assertEqual(len(self._server), 0)

        uid1 = '/portal/foo/bar'
        uid2 = '/portal/foo/foo'

        # Index me
        self._server.indexDocument(
            uid1, FakeXMLInputStream(self._o1, attributs=('name',)))
        self.assertEqual(len(self._server), 1)

        # Index me
        self._server.indexDocument(
            uid2, FakeXMLInputStream(self._o2, attributs=('name',)))
        self.assertEqual(len(self._server), 2)

        # Search me
        res = self._server.searchQuery(search_fields=({'id' : u'uid',
                                                       'value': uid1,
                                                       'type' : 'Path',},))
        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'/portal/foo/bar'},))

        res = self._server.searchQuery(search_fields=({'id' : u'uid',
                                                       'value': uid2,
                                                       'type' : 'Path',},))
        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(res, ({u'uid': u'/portal/foo/foo'},))

        # reIndex me
        self._server.reindexDocument(
            uid1, FakeXMLInputStream(self._o1, attributs=('name',)))
        self.assertEqual(len(self._server), 2)

        # unindex
        self._server.unindexDocument(uid1)
        self.assertEqual(len(self._server), 1)

        self._server.unindexDocument(uid2)
        self.assertEqual(len(self._server), 0)

    def test_batched_search(self):

        self.assertEqual(len(self._server), 0)

        uid1 = '/portal/foo/bar'
        uid2 = '/portal/foo/foo'
        uid3 = '/portal/foo/foo/bar'

        o1 = P('bob')
        o2 = P('Jack')
        o3 = P('bob')
        o4 = P('Jack')
        o5 = P('Jack')
        o6 = P('Jack')
        o7 = P('Jack')

        uid = 0
        for ob in (o1, o2, o3, o4, o5, o6, o7):
            self._server.indexDocument(
                uid, FakeXMLInputStream(ob, attributs=('name',)))
            uid += 1

        self.assertEqual(len(self._server), 7)

        # We find two documents matching here.
        res = self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': 'bob',
                            'type' : 'Text',},))

        res = PythonResultSet(ResultSet(res)).getResults()[0]

        self.assertEqual(len(res), 2)

        # Let's ask for a one document batch and check if it works.
        res = self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': 'bob',
                            'type' : 'Text',},),
            search_options={'start': 0, 'size':1,},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]

        self.assertEqual(len(res), 1)

        # All results matching Jack
        res = self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': 'jack',
                            'type' : 'Text',},),
            search_options={},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(len(res), 5)

        # All results matching Jack with a border < total results
        res = self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': 'jack',
                            'type' : 'Text',},),
            search_options={'start': 0, 'size':10,},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(len(res), 5)

        # Let's check batch window. 0->2
        res = self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': 'jack',
                            'type' : 'Text',},),
            search_options={'start': 0, 'size':2,},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(len(res), 2)

        # Let's check batch window. 2->4
        res = self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': 'jack',
                            'type' : 'Text',},),
            search_options={'start': 2, 'size':2,},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(len(res), 2)

        # Let's check batch window. 4->5
        res = self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': 'jack',
                            'type' : 'Text',},),
            search_options={'start': 4, 'size':2,},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(len(res), 1)

    def test_reindexSelectedField(self):

        self.assertEqual(len(self._server), 0)

        uid = '/portal/foo/bar'

        object = P('Anguenot', 'Julien')

        self._server.indexDocument(
           uid, FakeXMLInputStream(object, attributs=('name', 'givenName')))

        self.assertEqual(len(self._server), 1)

        # Search using name attr
        res = self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': 'Anguenot',
                            'type' : 'Text',},),
            search_options={},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(len(res), 1)

        # Search using givenName attr
        res = self._server.searchQuery(
            search_fields=({'id' : u'givenName',
                            'value': 'Julien',
                            'type' : 'Text',},),
            search_options={},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(len(res), 1)

        # Reindex givenName only
        object.name = 'Bond'
        self._server.reindexDocument(uid, FakeXMLInputStream(object, attributs=('name',)))

        # Search using name attr
        res = self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': 'Anguenot',
                            'type' : 'Text',},),
            search_options={},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(len(res), 0)

        res = self._server.searchQuery(
            search_fields=({'id' : u'name',
                            'value': 'Bond',
                            'type' : 'Text',},),
            search_options={},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(len(res), 1)

        # Search using givenName attr
        res = self._server.searchQuery(
            search_fields=({'id' : u'givenName',
                            'value': 'Julien',
                            'type' : 'Text',},),
            search_options={},
            )

        res = PythonResultSet(ResultSet(res)).getResults()[0]
        self.assertEqual(len(res), 1)

class LuceneServerWithPyDirectoryTestCase(LuceneServerTestCase):

    def setUp(self):
        LuceneServerTestCase.setUp(self)
        self._server = LuceneServer(self._store_dir, 'PythonDirectory')

class LuceneServerWithFSDirectoryTestCase(LuceneServerTestCase):

    def setUp(self):
        LuceneServerTestCase.setUp(self)
        self._server = LuceneServer(self._store_dir, 'FSDirectory')

class LuceneServerWithRAMDirectoryTestCase(LuceneServerTestCase):

    def setUp(self):
        LuceneServerTestCase.setUp(self)
        self._server = LuceneServer(self._store_dir, 'RamDirectory')

class LuceneServerMultiThreadTestCase(unittest.TestCase):

    def setUp(self):
        self._store_dir = '/tmp/lucene_dir'
        self._server = LuceneServer(self._store_dir)
        self.counter = 0
        self.lock = threading.Lock()

    def _indexObjects(self):

        self._server.indexDocument(1, FakeXMLInputStream(P('foo'), attributs=('name',)))
        self._server.indexDocument(2, FakeXMLInputStream(P('bar'), attributs=('name',)))

        self.lock.acquire()
        self.counter += 1
        self.lock.release()

    def test_indexing_multi_thead(self):

        self.counter = 0

        tmax = 100

        threads = []
        for i in xrange(tmax):
            threads.append(PythonThread(target=self._indexObjects))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(self.counter, tmax)

        self.counter = 0

    def tearDown(self):
        if os.path.exists(self._store_dir):
            shutil.rmtree(self._store_dir)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LuceneServerWithFSDirectoryTestCase))
    suite.addTest(unittest.makeSuite(LuceneServerWithPyDirectoryTestCase))
    #suite.addTest(unittest.makeSuite(LuceneServerWithRAMDirectoryTestCase))
    suite.addTest(unittest.makeSuite(LuceneServerMultiThreadTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
