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

from twisted.web import xmlrpc

import zope.interface
from interfaces import IXMLRPCLuceneServer
from interfaces import ILuceneServer

from stream import XMLInputStream
from stream import XMLQueryInputStream

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

    def xmlrpc_indexDocument(self, uid, xml_query=''):
        self._core.log.info("xmlrpc_indexDocument : requested "
                             "uid=%s, xml_query=%s" % (uid, xml_query))
        if xml_query:
            istream = XMLInputStream(xml_query)
            attributs = istream.getAttributNames()
            self._core.indexDocument(uid, istream, attributs)
            return True
        else:
            return False

    def xmlrpc_reindexDocument(self, uid, xml_query=''):
        self._core.log.info("xmlrpc_reindexob : requested "
                             "uid=%s, xml_query=%s" % (uid, xml_query))
        if xml_query:
            # XXX temporarly way of handling this.
            istream = XMLInputStream(xml_query)
            attributs = istream.getAttributNames()
            self._core.reindexDocument(uid, istream, attributs)
            return True
        else:
            return False

    def xmlrpc_unindexDocument(self, uid):
        self._core.log.info("xmlrpc_unindexob : requested " "uid=%s" % uid)
        # XXX handle error message
        # java.lang.ArrayIndexOutOfBoundsException ?
        self._core.unindexDocument(uid)
        return True

    def xmlrpc_searchQuery(self, xml_query=''):
        self._core.log.info("xmlrpc_search : requested " "xml_query=%s" %
                             xml_query)
        if xml_query:
            istream = XMLQueryInputStream(xml_query)
            # XXX istream.getAnalyzer()
            rss = self._core.searchQuery(
                istream.getReturnFields(), istream.getKwargs())
            self._core.log.info("search results %s" %rss)
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
