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
"""WebLucene interfaces

$Id$
"""

import zope.interface

class ILuceneServer(zope.interface.Interface):
    """Lucene server interface

    This is the core lucene server definition.
    """

    store_dir = zope.interface.Attribute(
        u"Directory where the lucene indexes are stored",
        )
    
    port = zope.interface.Attribute(
        u"Port on which the server is listening"
        )

    def optimize(indexer=None):
        """Optimze the lucene indexes store

        `indexer` : PyLucene.IndexWriter instance

        If `indexer` is not given as a parameter the internals of this
        function will create and close one to realize the
        optimization.
        """

    def clean():
        """Clean the whole indexes store.

        This method will remove *all* the documents stored within the
        store.
        """

    def __len__():
        """Return the amount of documents within the store.
        """

class IXMLRPCLuceneServer(zope.interface.Interface):
    """XML-RPC Lucene Server interface

    XXX This interface is really not final. Some signature need to be
    changed.
    """

    def xmlrpc_indexob(uid, xml_stream=''):
        """Index a Python object.

        `uid` is the key for this object.

        `xml_stream` is an xml stream containing the list of indexes,
                     values and types for a given object,

        <doc>
          <fields>
            <field id="name" attribute="name" type="text"
                   fulltext="True">
              The value of the field to index
            </field>
          </field>
        </doc>
        """

    def xmlrpc_reindexob(uid, xml_stream=''):
        """Reindex a Python object

        `uid` is the key for this object

        `xml_stream` is an xml stream containing the list of indexes,
                     values and types for a given object,
         <doc>
          <fields>
            <field id="name" attribute="name" type="text"
                   fulltext="True">
              The value of the field to index
            </field>
          </fields>
        </doc>
        """

    def xmlrpc_unindexob(uid):
        """Unindex a Python object given its uid
        """

    def xmlrpc_clean():
        """Clear the whole indexes
        """

    def xmlrpc_search(xml_stream=''):
        """Searching.

        `xml_stream` should look like this :

        <search>
          <analyzer>standard</analyzer>
          <return_fields>
            <field>name</field>
            <field>attr1</field>
          </return_fields>
          <fields>
            <field id="name" value="julien"/>
            <field id="uid" value="1"/>
          </fields>
        </search>

        This will return a RSS document as a resultset.
        Cf. weblucene.rss
        """

    def xmlrpc_getStoreDir():
        """Return the store dir location
        """

    def xmlrpc_optimize():
        """Optmize the index store.
        """

    def xmlrpc_getDocumentNumber():
        """Return the amount of document within the indexes store.
        """

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
        """Close IndexWriter instance
        """

class ILuceneSearcher(zope.interface.Interface):
    """Lucene Searcher
    """

    def get():
        """Return an IndexSearcher instance
        """
