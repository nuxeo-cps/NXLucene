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
"""XML-RPC Lucene Server adapter

$Id: server.py 30816 2006-02-28 18:09:59Z janguenot $
"""

import base64

from twisted.web import xmlrpc

import zope.interface
from interfaces import IXMLRPCLuceneServer
from interfaces import ILuceneServer

from xmlquery import XMLQuery
from xmlquery import XMLSearchQuery

class XMLRPCLuceneServer(xmlrpc.XMLRPC, object):
    """Lucene XML-RPC server

    See ILuceeneXMLRPCServer for more exaustive comments
    """

    zope.interface.implements(IXMLRPCLuceneServer)

    __user_for__ = ILuceneServer

    def __init__(self, core):
        super(XMLRPCLuceneServer, self).__init__()
        assert (core is not None)
        self._core = core

    def xmlrpc_indexDocument(self, uid, xml_query='', b64=False):
        self._core.log.info("xmlrpc_indexDocument: uid=%s " % str(uid))
        if xml_query:
            if b64 is True:
                xml_query = base64.b64decode(xml_query)
            iquery = XMLQuery(xml_query)
            return self._core.indexDocument(uid, iquery)
        else:
            return False

    def xmlrpc_reindexDocument(self, uid, xml_query='', b64=False):
        self._core.log.info("xmlrpc_reindexob : uid=%s" % str(uid))
        return self.xmlrpc_indexDocument(uid, xml_query, b64)

    def xmlrpc_unindexDocument(self, uid):
        self._core.log.info("xmlrpc_unindexob : uid=%s" % str(uid))
        return self._core.unindexDocument(uid)

    def xmlrpc_search(self, query_str=''):
        # XXX not tested yet.
        if query_str:
            return self._core.search(query_str)
        else:
            # Return an empty resultset
            self._core.log.info("search results is empty")
            return rss.resultset.ResultSet().getStream()

    def xmlrpc_searchQuery(self, xml_query=''):
        self._core.log.info("xmlrpc_searchQuery")
        if xml_query:
#            print xml_query
            iquery = XMLSearchQuery(xml_query)
#            print iquery.getSearchFields()
            rss = self._core.searchQuery(iquery.getReturnFields(),
                                         iquery.getSearchFields(),
                                         iquery.getSearchOptions(),
                                         )
            return rss
        # Return an empty resultset
        self._core.log.info("search results is empty")
        return rss.resultset.ResultSet().getStream()

    def xmlrpc_hasUID(self, uid):
        return self._core.getDocumentByUID(uid) is not None

    def xmlrpc_clean(self):
        return self._core.clean()

    def xmlrpc_getStoreDir(self):
        return self._core.store_dir

    def xmlrpc_optimize(self):
        self._core.optimize()
        return True

    def xmlrpc_getNumberOfDocuments(self):
        return len(self._core)

    def xmlrpc_debug(self, msg):
        return msg
