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
"""NXLucene interfaces

$Id$
"""

import zope.interface

class ILuceneIndexer(zope.interface.Interface):
    """Lucene indexer
    """

    def get(creation=False, analyzer=None):
        """Return an IndexWriter instance

        If analyzer is None then use a PyLucene.StandardAnalyzer
        """

    def close():
        """Close IndexWriter instance
        """

class ILuceneReader(zope.interface.Interface):
    """Lucene Reader
    """

    def get():
        """Return an IndexReader instance
        """

    def close():
        """Close IndexReader instance
        """