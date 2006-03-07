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
"""Test Lucene indexer

$Id$
"""

import shutil
import unittest

import PyLucene

from nxlucene.indexer import LuceneIndexer

class LuceneIndexerTestCase(unittest.TestCase):

    def setUp(self):
        self._indexer = LuceneIndexer('/tmp/lucene-indexer', creation=True)

    def test_01_get(self):
        index_writer = self._indexer.get(creation=True)
        # XXX
#        self.assert_(isinstance(index_writer, PyLucene.IndexWriter))

    def test_02_close(self):
        self._indexer.get(creation=False)
        self._indexer.close()
                
    def tearDown(self):
        shutil.rmtree('/tmp/lucene-indexer')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LuceneIndexerTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
