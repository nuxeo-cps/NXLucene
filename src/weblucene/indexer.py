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
"""lucene indexer

$Id$
"""

import os
import shutil
import PyLucene

import zope.interface
from interfaces import ILuceneIndexer

class LuceneIndexer(object):

    zope.interface.implements(ILuceneIndexer)

    _writer = None

    def __init__(self, store_dir, creation=False, analyzer=None):
        if creation:
            if os.path.exists(store_dir):
                shutil.rmtree(store_dir)
            os.makedirs(store_dir)
        self._store = PyLucene.FSDirectory.getDirectory(store_dir, creation)
        self._writer = self.get(creation, analyzer)
        self.close()

    def get(self, creation=False, analyzer=None):
        return self._get(creation, analyzer)

    def close(self):
        if self._writer:
            self._writer.close()
            self._writer = None

    def _get(self, creation=False, analyzer=None):
        if not self._writer:
            if analyzer is None:
                analyzer = PyLucene.StandardAnalyzer()
            self._writer = PyLucene.IndexWriter(self._store, analyzer, creation)
        return self._writer
    
    def __del__(self):
        self.close()    
