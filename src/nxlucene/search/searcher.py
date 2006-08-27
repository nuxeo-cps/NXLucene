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
"""lucene searcher

$Id$
"""

import PyLucene

import zope.interface
from nxlucene.search.interfaces import ILuceneSearcher

class LuceneSearcher(object):
    """Lucene Searcher
    """

    zope.interface.implements(ILuceneSearcher)

    _searcher = None

    def __init__(self, store):
        self._store = store
        try:
            self._searcher = self.get()
        except PyLucene.JavaError:
            # No indexes yet
            self.close()

    def __nonzero__(self):
        return self._searcher is not None

    def get(self):
        if self._searcher is None:
            self._searcher = PyLucene.IndexSearcher(self._store)
        return self._searcher

    def close(self):
        if self._searcher is not None:
            self._searcher.close()
            self._searcher = None

    def __del__(self):
        self.close()
