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
"""NXLucene runner

$Id: run.py 31105 2006-03-08 12:05:26Z janguenot $
"""

import gc
import os
import sys
import logging
import threading
import PyLucene

from twisted.web import resource
from twisted.web import server

from twisted.application import service
from twisted.application import internet

from nxlucene.core import LuceneServer
from nxlucene.logger import initLog
from nxlucene.configuration import NXLuceneConfiguration

from nxlucene.xmlrpc import XMLRPCLuceneServer

# Ensure Python standard Thread is never used within NXLucene.
threading.Thread = PyLucene.PythonThread

from twisted.internet import reactor
reactor.suggestThreadPoolSize(10)

application = service.Application("NXLucene")

class NXLuceneController(object):

    def __init__(self):

        config_file = os.environ['CONFIG_FILE']
        self._conf = NXLuceneConfiguration(config_file)

        initLog(self._conf.getLogLevel(), self._conf.getLogFile())

        self.log = logging.getLogger()

        if self._conf.getLogLevel() == 'DEBUG':
            self.log.info("gc.set_debug(gc.DEBUG_LEAK)")
            gc.set_debug(gc.DEBUG_LEAK)
            
        self._root = resource.Resource()
        self.initializeResources()

    def initializeResources(self):
        """Initialize server resources

        We could define SOAP here for instance as well.
        """

        # Create a core server instance.
        core = LuceneServer(self._conf.getStoreDirPath())

        # Optimize the indexes at startup 
        core.optimize()

        # Adapt to RPC and register this resource.
        self._root.putChild('RPC2', XMLRPCLuceneServer(
            core, self._conf.getThreadsNumber()))

        self.log.info(
            "XML-RPC server "
            "is listening on port %s..." % self._conf.getPort())

    def start(self):
        self.log.info(
            "Indexes are located here : %s" % self._conf.getStoreDirPath())
        res = internet.TCPServer(self._conf.getPort(),
                         server.Site(self._root))
        res.setServiceParent(application)

NXLuceneController().start()
