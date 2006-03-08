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

class IXMLRPCLuceneServer(zope.interface.Interface):
    """XML-RPC Lucene Server interface

    This is used as an adapter to ILuceneServer instance.
    """

    def xmlrpc_indexDocument(uid, xml_query=''):
        """Index a document

        `uid` is the key for this document.

        `xml_query` is an xml query containing the list of fields,
                    to index the document with and their properties.

        <doc>
          <fields>
            <field id="name" attribute="name" type="text">
              The value of the field to index
            </field>
          </field>
        </doc>
        """

    def xmlrpc_reindexDocument(uid, xml_query=''):
        """Reindex a document

        `uid` is the key for this document.

        `xml_query` is an xml query containing the list of fields to
        reindex and their properties.

         <doc>
          <fields>
            <field id="name" attribute="name" type="text">
              The value of the field to index
            </field>
          </fields>
        </doc>
        """

    def xmlrpc_unindexDocument(uid):
        """Unindex a document given its uid.
        """

    def xmlrpc_clean():
        """Clear the whole indexes.

        This method removve *all* the indexes and documents from the store.
        """

    def xmlrpc_searchQuery(xml_query=''):
        """Searching.

        `xml_query` should look like this :

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

    def xmlrpc_getNumberOfDocuments():
        """Return the amount of document within the indexes store.
        """

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
