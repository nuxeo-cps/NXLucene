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
try:
    import cElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

NS = 'http://namespaces.nuxeo.org/weblucene'

class WebLuceneConfiguration(object):
    """WebLucene configuration
    """

    def __init__(self, args=()):
        self.args = args
        conf = open(self.args[2], 'r').read()
        self._conf = etree.XML(conf)

    def getPort(self):
        port = self._conf.find('{http://namespaces.nuxeo.org/weblucene}port')
        return int(port.text.strip())

    def getStoreDirPath(self):
        store_dir_path = self._conf.find(
            '{http://namespaces.nuxeo.org/weblucene}store_dir').text.strip()
        if not store_dir_path.startswith('/'):
            return os.environ.get('INSTANCE_HOME') + '/var/' + store_dir_path
        return store_dir_path

    def getThreadsNumber(self):
        threads = self._conf.find(
            '{http://namespaces.nuxeo.org/weblucene}threads')
        return int(threads.text.strip())

    def getLogLevel(self):
        logs = self._conf.find(
            '{http://namespaces.nuxeo.org/weblucene}logs')
        loglevel = logs.find(
            '{http://namespaces.nuxeo.org/weblucene}level')
        return loglevel.text.strip()

    def getLogFile(self):
        logs = self._conf.find(
            '{http://namespaces.nuxeo.org/weblucene}logs')
        logfile = logs.find(
            '{http://namespaces.nuxeo.org/weblucene}file')
        logfilepath = logfile.text.strip()
        if not logfilepath.startswith('/'):
            return os.environ.get('INSTANCE_HOME') + '/log/' + logfilepath
