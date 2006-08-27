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
import PyLucene

import zope.interface
from nxlucene.index.interfaces import ILuceneIndexer

class LuceneIndexer(object):

    zope.interface.implements(ILuceneIndexer)

    _writer = None

    def __init__(self, store, creation=False, analyzer=None):

        if analyzer is None:
            analyzer = PyLucene.StandardAnalyzer()
        self._analyzer = analyzer

        self._store = store
        self._writer = self.get(creation, analyzer)

    def __nonzero__(self):
        return self._writer is not None

    def get(self, creation=False, analyzer=None):
        return self._get(creation, analyzer)

    def close(self):
        if self._writer is not None:
            self._writer.close()
            self._writer = None

    def _get(self, creation=False, analyzer=None):
        if self._writer is None or analyzer != self._analyzer:
            if self._writer is not None:
                self._writer.close()
                self._writer = None
            self._writer = PyLucene.IndexWriter(self._store, self._analyzer, creation)
        return self._writer

    def __del__(self):
        self.close()
