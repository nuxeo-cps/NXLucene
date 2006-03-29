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
"""NXLucene configuration. 

$Id$
"""

import os
try:
    import cElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

NS = 'http://namespaces.nuxeo.org/nxlucene'

class NXLuceneConfiguration(object):
    """NXLucene configuration
    """

    def __init__(self, config_file):
        conf = open(config_file, 'r').read()
        self._conf = etree.XML(conf)
        self._nxlucened = self._conf.find('{%s}nxlucened' % NS)

    def getPort(self):
        port = self._nxlucened.find('{%s}port' % NS)
        return int(port.text.strip())

    def getStoreDirPath(self):
        store_dir_path = self._conf.find(
            '{%s}store_dir' % NS).text.strip()
        if not store_dir_path.startswith('/'):
            return os.environ.get('INSTANCE_HOME') + '/' + store_dir_path
        return store_dir_path

    def getThreadsNumber(self):        
        threads = self._nxlucened.find('{%s}threads' % NS)
        return int(threads.text.strip())

    def getPIDFilePath(self):
        pidpath = self._nxlucened.find('{%s}pidfile' % NS)
        pidpath = pidpath.text.strip()
        if not pidpath.startswith('/'):
            return os.environ.get('INSTANCE_HOME') + '/' + pidpath
        return pidpath

    def getTwistdLogFile(self):
        logfile = self._nxlucened.find('{%s}twistdlog' % NS)
        logfile = logfile.text.strip()
        if not logfile.startswith('/'):
            return os.environ.get('INSTANCE_HOME') + '/' + logfile
        return logfile

    def getTwistdServiceTac(self):
        tac = self._nxlucened.find('{%s}service' % NS)
        tac = tac.text.strip()
        if not tac.startswith('/'):
            return os.environ.get('INSTANCE_HOME') + '/' + tac
        return tac

    def getLogLevel(self):
        logs = self._conf.find(
            '{%s}logs' % NS)
        loglevel = logs.find(
            '{%s}level' % NS)
        return loglevel.text.strip()

    def getLogFile(self):
        logs = self._conf.find(
            '{%s}logs' % NS)
        logfile = logs.find(
            '{%s}file' % NS)
        logfilepath = logfile.text.strip()
        if not logfilepath.startswith('/'):
            return os.environ.get('INSTANCE_HOME') + '/' + logfilepath
