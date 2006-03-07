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
"""WebLucene runner

$Id$
"""

import os
import sys
import logging

from twisted.web import resource
from twisted.web import server
from twisted.internet import reactor

from server import LuceneServer
from logger import initLog
from configuration import WebLuceneConfiguration

from xmlrpc import XMLRPCLuceneServer

class WebLuceneController(object):

    def __init__(self):

        self.log = logging.getLogger('WebLucene')

        self._conf = WebLuceneConfiguration(sys.argv)
        initLog(self._conf.getLogLevel(), self._conf.getLogFile())

        self._root = resource.Resource()
        self.initializeResources()

    def initializeResources(self):
        """Initialize server resources

        We could define SOAP here for instance as well.
        """
        
        # Create a core server instance.
        core = LuceneServer(self._conf.getStoreDirPath())

        # Adapt to RPC and register this resource.
        self._root.putChild('RPC2', XMLRPCLuceneServer(core))

        reactor.listenTCP(self._conf.getPort(), server.Site(self._root))
        reactor.suggestThreadPoolSize(self._conf.getThreadsNumber())
        self.log.info(
            "XML-RPC server "
            "is listening on port %s..." % self._conf.getPort())

    def start(self):
        self.log.info(
            "Indexes are located there : %s" % self._conf.getStoreDirPath())
        reactor.run()

def main():
    controller = WebLuceneController().start()
