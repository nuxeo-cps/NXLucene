# Copyright (C) 2006, Nuxeo SAS <http://www.nuxeo.com>
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
"""Python directory using RLock.

Safe in multi-threaded env (not multi-processes)

$Id$
"""

import os

from threading import RLock

from nxlucene.debug import DebugFactory

from nxlucene.store.lock import PythonDirLock
from nxlucene.store.stream import PythonFileStream

class PythonFileDirectory(object):

    def __init__(self, path, create=False):
        self.path = os.path.realpath(path)
        self.name = self.path
        self._locks = {}
        self._streams = []
        if create:
            self.create()
        assert os.path.isdir(path)

    def create(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        oldFiles = os.listdir(self.path)
        for oldFile in oldFiles:
            os.remove(os.path.join(self.path, oldFile))

    def close(self):
        for s in self._streams:
            s.close()

    def createOutput(self, name):
        file_path = os.path.join(self.path, name)
        fh = open( file_path, "w" )
        stream = PythonFileStream(name, fh)
        self._streams.append(stream)
        return stream

    def deleteFile(self, name):
        if self.fileExists(name):
            os.unlink(os.path.join( self.path, name))

    def fileExists(self, name):
        return os.path.exists(os.path.join(self.path, name))

    def fileLength(self, name):
        file_path = os.path.join(self.path, name)
        return os.path.getsize(file_path)

    def fileModified(self, name):
        file_path = os.path.join(self.path, name)
        return int(os.path.getmtime(file_path))

    def list(self):
        return os.listdir(self.path)

    def openInput(self, name):
        file_path = os.path.join(self.path, name)
        fh = open(file_path, 'r')
        stream = PythonFileStream(name, fh, os.path.getsize(file_path))
        self._streams.append(stream)
        return stream

    def renameFile(self, fname, tname):
        fromName = os.path.join(self.path, fname)
        toName = os.path.join(self.path, tname)
        if os.path.exists(toName):
            os.remove(toName)
        os.rename(fromName, toName)

    def touchFile(self, name):
        file_path = os.path.join(self.path, name)
        fh = open(file_path, 'rw')
        c = fh.read(1)
        fh.seek(0)
        fh.write(c)
        fh.close()

    def makeLock(self, name):
        lock = self._locks.setdefault(name, RLock())
        return PythonDirLock(name, os.path.join( self.path, name ), lock)

    def __del__(self):
        for stream in self._streams:
            stream.close()

DEBUG = False

if DEBUG:
    _globals = globals()
    _globals['PythonFileDirectory'] = DebugFactory(PythonFileDirectory)
    _globals['PythonFileStream'] = DebugFactory(PythonFileStream)
    _globals['PythonFileLock'] = DebugFactory(PythonDirLock)
    del _globals
