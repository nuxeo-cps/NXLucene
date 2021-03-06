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

    def xmlrpc_indexDocument(uid, xml_query='', b64=False, sync=False):
        """Index a document

        `uid` is the key for this document.

        `xml_query` is an xml query containing the list of fields,
                    to index the document with and their properties.

        `b64` : xml_query compressed using base64 ?

        <doc>
          <fields>
            <field id="name" type="text" analyzer="French">
              The value of the field to index
            </field>
          </field>
        </doc>
        """

    def xmlrpc_reindexDocument(uid, xml_query='', sync=False):
        """Reindex a document

        `uid` is the key for this document.

        `xml_query` is an xml query containing the list of fields to
        reindex and their properties.

        `b64` : xml_query compressed using base64 ?

         <doc>
          <fields>
            <field id="name" type="text" analyzer="French">
              The value of the field to index
            </field>
          </fields>
        </doc>
        """

    def xmlrpc_unindexDocument(uid, sync=False):
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
            <field id="name" value="julien" type="Text" analyze="French"/>
            <field id="uid" value="1" type="Keyword" analyzer="KeywordAnalyzer"/>
          </fields>
          <sort>
            <sort-on>modified</sort-on>
            <sort-limit>100</sort-limit>
            <sort-order>reversed</sort-order>
          </sort>
          <operator>AND</operator>
          <batch start="0", size="10">
        </search>

        This will return a tuple containing the RSS document as a
        resultset with the total number of results.

        -> (<rss_stream>, <nb_items>)

        Cf. nxlucene.rss
        """

    def xmlrpc_search(query_str=''):
        """Searching using Lucene native query.

        `query_str` : Lucene query string.

        For the Lucene query syntax see :
        http://lucene.apache.org/java/docs/queryparsersyntax.html
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
        
    def xmlrpc_getFieldTerms(field):
        """Return all the terms of a field.
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

    store_backened_id = zope.interface.Attribute(
        u"Identififier for the type of store backened the server will use"
        )

    port = zope.interface.Attribute(
        u"Port on which the server is listening"
        )

    def getStore(creation=False):
        """Returns a store instance.

        The store that will be created will depend on the store_backened_id.
        See nxlucene.conf
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

    def getIndexer(creation=False, analyzer=None):
        """Return a nxlucene.LuceneIndexer instance. See ILuceneIndexer.
        """

    def getReader():
        """Return a nxlucene.LuceneReader instance. See ILuceneReader.
        """

    def getSearcher():
        """Return a nxlucene.LuceneSearcher instance. See ILuceneSearcher.
        """

    def indexDocument(uid, query_instance):
        """Index a document.

        `uid` : uid to use for this document. Note, here uid has
        nothing to do with the internal Lucene docid. It uses a Lucene
        Keyword field.

        `query_instance` : XML Query Instance
        """

    def unindexDocument(uid, lock=True):
        """Unindex a document.

        `uid` : uid of the target document.

        `lock` : boolean specifying if the store should be locked or
        not. May be useful if the method from which this is called
        already locked the store.
        """

    def reindexDocument(uid, query_instance):
        """Reindex a document.

        `uid` : uid to use for this document. Note, here uid has
        nothing to do with the internal Lucene docid. It uses a Lucene
        Keyword field.

        `query_instance` : XML Query Instance
        """

    def searchQuery(return_fields=(), search_fields=(), search_options={}):
        """Search results.
        """

    def getFieldTerms(field):
        """Return all the terms of a field.
        """

class IXMLSearchQuery(zope.interface.Interface):
    """XML Search Query

    XML Custom query supported by NXLucene
    """

    def getReturnFields():
        """Get field names that should come with the results.

        Filter out stored values from Lucene record.

        Returns a tuple of strings representing the field names that
        are supposed to be returned.
        """

    def getSearchFields():
        """Search fields configuration.

        Returns a tuple of dictionnaries.

        XXX explicit about tne dict format.
        """

    def getSearchOptions():
        """Search options.

        XXX explicit
        """

    def getAnalyzerType():
        """Get the analyzer to use for this query.
        """

class IXMLQuery(zope.interface.Interface):
    """XML Query.

    XML Custom query used for indexing.
    """


    def getFields():
        """Returns a tuple of dictionnaries containing the fields to
        index and how to index them.

        XXX : explicit the dicts.
        """

    def getFieldNames():
        """Returns the field names to index. (tuple of string)
        """

