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
import PyLucene

import zope.interface

from weblucene.server import LuceneServer
from weblucene.rss.adapter import PythonResultSet
from weblucene.rss.resultset import ResultSet

class P(object):
    zope.interface.implements(zope.interface.Interface)
    def __init__(self, name):
        self.name = name

class LuceneServerTestCase(unittest.TestCase):

    def setUp(self):
        self._store_dir = '/tmp/lucene'
        self._server = LuceneServer(self._store_dir)
        self._o1 = P('foo')
        self._o2 = P('bar')

    def tearDown(self):
        if os.path.exists(self._store_dir):
            shutil.rmtree(self._store_dir)

    def test_store_dir(self):
        self.assertEqual(self._store_dir, self._server.store_dir)

    def test_implementation(self):
        from zope.interface.verify import verifyClass
        from weblucene.interfaces import ILuceneServer
        self.assert_(verifyClass(ILuceneServer, LuceneServer))

    def test_optimize(self):
        self.assert_(self._server.optimize())

    def _indexObjects(self):
        self.assertEqual(len(self._server), 0)
        self._server._indexob(1, self._o1, attributs=('name',))
        self._server._indexob(2, self._o2, attributs=('name',))
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
        res = self._server._search(return_fields=(), kws={u'uid':u'1'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o1 on uid (with return fields)
        res = self._server._search(return_fields=('name',), kws={u'uid':u'1'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'1', u'name':u'foo'},))
 
        # Search o1 on name (no return fields)
        res = self._server._search(return_fields=(), kws={u'name':u'foo'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o1 on name (with return fields)
        res = self._server._search(return_fields=('name',), kws={u'name':u'foo'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'1', u'name':u'foo'},))

        # Search o2 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'uid':u'2'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'2'},))

        # Search o2 on uid (with return fields)
        res = self._server._search(return_fields=('name',), kws={u'uid':u'2'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'2', u'name':u'bar'},))
 
        # Search o2 on name (no return fields)
        res = self._server._search(return_fields=(), kws={u'name':u'bar'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'2'},))

        # Search o2 on name (with return fields)
        res = self._server._search(return_fields=('name',), kws={u'name':u'bar'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'2', u'name':u'bar'},))

    def test_unindexing(self):

        self._indexObjects()

        # Search o1 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'uid':u'1'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o1 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'uid':u'2'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'2'},))

        # Unindex o1
        self._server._unindexob(1)
        res = self._server._search(return_fields=(), kws={u'uid':u'1'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ())

        # Search o1 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'uid':u'2'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'2'},))

        # Unindex o1
        self._server._unindexob(2)
        res = self._server._search(return_fields=(), kws={u'uid':u'2'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ())

    def test_reindexing(self):

        self._indexObjects()

        # Search o1 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'name':u'foo'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o2 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'name':u'bar'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'2'},))

        # Reindex o1 with a new name
        self._o1.name = 'newfoo'
        self._server._reindexob(1, self._o1, attributs=('name',))

        # Search o1 on uid (no return fields)
        res = self._server._search(return_fields=('name',),
                                   kws={u'name':u'foo'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ())

        # Search o1 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'name':u'newfoo'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o2 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'name':u'bar'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'2'},))

        # Reindex o2 with a new name
        self._o2.name = 'newbar'
        self._server._reindexob(2, self._o2, attributs=('name',))

        # Search o1 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'name':u'foo'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ())

        # Search o1 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'name':u'newfoo'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o2 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'name':u'bar'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ())

        # Search o2 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'name':u'newbar'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'2'},))

    def test_clearing(self):

        self._indexObjects()

        # Search o1 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'uid':u'1'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'1'},))

        # Search o2 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'uid':u'1'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'1'},))

        self._server.clean()

        # Search o1 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'uid':u'1'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ())

        # Search o2 on uid (no return fields)
        res = self._server._search(return_fields=(), kws={u'uid':u'1'})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ())

    def test_withpathasindex(self):

        # Test with something else than an integer
        self.assertEqual(len(self._server), 0)

        uid1 = '/portal/foo/bar'
        uid2 = '/portal/foo/foo'

        # Index me
        self._server._indexob(uid1, self._o1, attributs=('name',))
        self.assertEqual(len(self._server), 1)

        # Index me
        self._server._indexob(uid2, self._o2, attributs=('name',))
        self.assertEqual(len(self._server), 2)

        # Search me
        res = self._server._search(kws={unicode('uid') : uid1})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'/portal/foo/bar'},))

        res = self._server._search(kws={unicode('uid') : uid2})
        res = PythonResultSet(ResultSet(res)).getResults()
        self.assertEqual(res, ({u'uid': u'/portal/foo/foo'},))

        # reIndex me
        self._server._reindexob(uid1, self._o1, attributs=('name',))
        self.assertEqual(len(self._server), 2)

        # unindex
        self._server._unindexob(uid1)
        self.assertEqual(len(self._server), 1)
        
        self._server._unindexob(uid2)
        self.assertEqual(len(self._server), 0)

class LuceneServerMultiThreadTestCase(unittest.TestCase):

    def setUp(self):
        self._store_dir = '/tmp/lucene_dir'
        self._server = LuceneServer(self._store_dir)
        self.counter = 0
        self.lock = threading.Lock()

    def _indexObjects(self):

        self._server._indexob(1, P('foo'), attributs=('name',))
        self._server._indexob(2, P('bar'), attributs=('name',))

        self.lock.acquire()
        self.counter += 1
        self.lock.release()

    def test_indexing_multi_thead(self):

        self.counter = 0

        tmax = 100

        threads = []
        for i in xrange(tmax):
            threads.append(PyLucene.PythonThread(
                target=self._indexObjects))

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
    suite.addTest(unittest.makeSuite(LuceneServerTestCase))
    suite.addTest(unittest.makeSuite(LuceneServerMultiThreadTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
