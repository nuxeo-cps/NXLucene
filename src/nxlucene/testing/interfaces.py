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
"""Fake XML-RPC Lucene Server interfaces.

$Id: server.py 30816 2006-02-28 18:09:59Z janguenot $
"""

import zope.interface

class IFakeXMLRPCLuceneServer(zope.interface.Interface):
    """ Fake XMLROCLucene Server interface

    See nxlucene.interfaces.IXMLRPCLuceneServer for documentation.
    """

    def indexDocument(uid, xml_query='', b64=False):
        pass

    def reindexDocument(uid, xml_query='', b64=False):
        pass

    def unindexDocument(uid):
        pass

    def searchQuery(xml_query=''):
        pass

    def hasUID(uid):
        pass

    def clean():
        pass

    def getStoreDir():
        pass

    def optimize():
        pass

    def getNumberOfDocuments():
        pass

    def debug(msg):
        pass
