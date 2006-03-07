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

    See ILuceeneXMLRPCServer for exaustive comments
    """

    zope.interface.implements(IXMLRPCLuceneServer)
    __user_for__ = ILuceneServer

    def __init__(self, core):
        super(XMLRPCLuceneServer, self).__init__()
        assert (core is not None)
        self._core = core

    # XXX implementation is here only for testing purpose. The stream
    # must be passed as arguments to the internal API so that it can
    # extract and use the additional information (i.e : field type,
    # fulltext, ...)

    def xmlrpc_indexob(self, uid, xml_stream=''):
        self._core.log.info("xmlrpc_indexob : requested "
                             "uid=%s, xml_stream=%s" % (uid, xml_stream))
        # XXX return an error code
        if xml_stream:
            istream = XMLInputStream(xml_stream)
            attributs = istream.getAttributNames()
            self._core._indexob(uid, istream, attributs)
            return True
        else:
            return False

    def xmlrpc_reindexob(self, uid, xml_stream=''):
        self._core.log.info("xmlrpc_reindexob : requested "
                             "uid=%s, xml_stream=%s" % (uid, xml_stream))
        # XXX return an error code
        if xml_stream:
            # XXX temporarly way of handling this.
            istream = XMLInputStream(xml_stream)
            attributs = istream.getAttributNames()
            self._core._reindexob(uid, istream, attributs)
            return True
        else:
            return False

    def xmlrpc_unindexob(self, uid):
        self._core.log.info("xmlrpc_unindexob : requested " "uid=%s" % uid)
        # XXX handle error message
        # java.lang.ArrayIndexOutOfBoundsException ?
        self._core._unindexob(uid)
        return True

    def xmlrpc_search(self, xml_stream=''):
        self._core.log.info("xmlrpc_search : requested " "xml_stream=%s" %
                             xml_stream)
        if xml_stream:
            istream = XMLQueryInputStream(xml_stream)
            # XXX istream.getAnalyzer()
            rss = self._core._search(
                istream.getReturnFields(), istream.getKwargs())
            self._core.log.info("search results %s" %rss)
            return rss
        # Return an empty resultset
        self._core.log.info("search results is empty")
        return rss.resultset.ResultSet().getStream()

    def xmlrpc_clean(self):
        return self._core.clean()

    def xmlrpc_debug(self, msg):
        return msg

    def xmlrpc_getStoreDir(self):
        return self._core.store_dir

    def xmlrpc_optimize(self):
        self._core.optimize()
        return True

    def xmlrpc_getDocumentNumber(self):
        return len(self._core)
