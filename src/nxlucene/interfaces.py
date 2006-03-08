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

    def xmlrpc_hasUID(uid):
        """Has the store a document having this UID ?
        """

class ILuceneServer(zope.interface.Interface):
    """Lucene server interface

    This is the core lucene server definition.

    See IXMLRPCLuceneServer for an example of ILuceneServer
    adaptation.
    """

    store_dir = zope.interface.Attribute(
        u"Directory where the lucene indexes are stored",
        )

    port = zope.interface.Attribute(
        u"Port on which the server is listening"
        )

    def getStore(creation=False):
        """Returns a store instance.

        For the moment, it uses a FSDirectory instance only.
        """

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
        """Return the total amount of documents within the store.
        """

    def getDocumentByUID(uid):
        """Return a PyLucene.document instance from the lucene store
        given its UID.

        It will return None of not found.
        """

    def getIndexer():
        """Return a nxlucene.LuceneIndexer instance. See ILuceneIndexer.
        """
    
    def getReader():
        """Return a nxlucene.LuceneReader instance. See ILuceneReader.
        """

    def getSearcher():
        """Return a nxlucene.LuceneSearcher instance. See ILuceneSearcher.
        """

    def indexDocument(uid, ob, attributs=()):
        """Index a document.

        `uid` : uid to use for this document. Note, here uid has
        nothing to do with the internal Lucene docid. It uses a Lucene
        Keyword field.

        `ob` : Python object wrapper. This is a XMLInputSteam instance.

        `attributs` : tuple of wrapper attributs to index.
        """

    def unindexDocument(uid, lock=True):
        """Unindex a document.

        `uid` : uid of the target document.

        `lock` : boolean specifying if the store should be locked or
        not. May be useful if the method from which this is called
        already locked the store.
        """

    def reindexDocument(uid, ob, attributs=()):
        """Reindex a document.

        `uid` : uid to use for this document. Note, here uid has
        nothing to do with the internal Lucene docid. It uses a Lucene
        Keyword field.

        `ob` : Python object wrapper. This is a XMLInputSteam instance.

        `attributs` : tuple of wrapper attributs to reindex.
        """

    def searchQuery(return_fields=(), kws=None):
        """Search results.
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
