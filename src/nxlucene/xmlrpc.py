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

import PyLucene
import threading
import base64

from twisted.web import xmlrpc

import zope.interface
from interfaces import IXMLRPCLuceneServer
from interfaces import ILuceneServer

from xmlquery import XMLQuery
from xmlquery import XMLSearchQuery

from threadpool import ThreadPool

class XMLRPCLuceneServer(xmlrpc.XMLRPC, object):
    """Lucene XML-RPC server

    See ILuceeneXMLRPCServer for more exaustive comments
    """

    zope.interface.implements(IXMLRPCLuceneServer)

    __user_for__ = ILuceneServer

    def __init__(self, core, write_pool_size=10):

        super(XMLRPCLuceneServer, self).__init__()
        assert (core is not None)
        self._core = core

        # Thread write pool
        self._write_sync = False
        self._write_pool = None
        self._write_pool_size = write_pool_size

    def _getWriteThreadPool(self):
        if not self._write_sync:
            if self._write_pool is None:
                self._write_pool = ThreadPool(self._write_pool_size)
        return self._write_pool

    #
    # API : Public
    #

    def xmlrpc_indexDocument(self, uid, xml_query='', b64=False, sync=False):

        args = (uid, xml_query, b64)
        pool = self._getWriteThreadPool()
        if sync is False and pool is not None:
            pool.queueTask(self._indexDocument, args, None)
        else:
            self._indexDocument(*args)
        return True

    def xmlrpc_reindexDocument(self, uid, xml_query='', b64=False, sync=False):
        return self.xmlrpc_indexDocument(uid, xml_query, b64, sync)

    def xmlrpc_unindexDocument(self, uid, sync=False):
        args = (uid,)
        pool = self._getWriteThreadPool()
        if sync is False and pool is not None:
            pool.queueTask(
                self._unindexDocument, (uid,), None)
        else:
            self._unindexDocument(*args)
        return True

    def xmlrpc_search(self, query_str=''):
        # XXX not tested yet.
        if query_str:
            return self._core.search(query_str)
        else:
            # Return an empty resultset
            self._core.log.info("search results is empty")
            return rss.resultset.ResultSet().getStream()

    def xmlrpc_searchQuery(self, xml_query=''):

        if xml_query:

            self._core.log.info("xmlrpc_searchQuery....")
            iquery = XMLSearchQuery(xml_query)

            params = (
                iquery.getReturnFields(),
                iquery.getSearchFields(),
                iquery.getSearchOptions(),
                )

            self._core.log.debug(
                "xmlrpc_searchQuery : search_fields=%s "
                "search_options=%s and search_options=%s" % params )

            return self._core.searchQuery(*params)

        else:
            # Return an empty resultset
            self._core.log.debug(
                "xmlrpc_searchQuery : "
                "result set is empty because xml_query is empty")
            return rss.resultset.ResultSet().getStream()

    def xmlrpc_hasUID(self, uid):
        return self._core.getDocumentByUID(uid) is not None

    def xmlrpc_clean(self):
        pool = self._getWriteThreadPool()
        if pool is not None:
            pool.queueTask(
                self._core.clean, (), None)
        else:
            self._core.clean()
        return True

    def xmlrpc_getStoreDir(self):
        return self._core.store_dir

    def xmlrpc_optimize(self):
        pool = self._getWriteThreadPool()
        if pool is not None:
            pool.queueTask(
                self._core.optimize, (), None)
        else:
            self._core.optimize()
        return True

    def xmlrpc_getNumberOfDocuments(self):
        return len(self._core)

    def xmlrpc_debug(self, msg):
        return msg


    #
    # Private API
    #

    def _indexDocument(self, uid, xml_query='', b64=False):
        self._core.log.info("xmlrpc_indexDocument: uid=%s " % str(uid))
        if xml_query:
            if b64 is True:
                xml_query = base64.b64decode(xml_query)
            iquery = XMLQuery(xml_query)
            res = self._core.indexDocument(uid, iquery)
            return res
        return False

    def _unindexDocument(self, uid):
        self._core.log.info("xmlrpc_unindexob : uid=%s" % str(uid))
        res = self._core.unindexDocument(uid)
        return res
