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
"""Python File Directory to avoid gcc-3.4.6 2go limitation

Code taken from the PyLucene mailing list.

Author : <a href="mailto:info@altervisionmedia.com">Yura Smolsky</a>

$Id: indexer.py 44973 2006-04-26 01:40:23Z janguenot $
"""

import os
import sys
import PyLucene
import md5
import time

DEBUG = False

class DebugWrapper( object ):

    def __init__(self, obj ):
        self.obj = obj

    def __getattr__(self, name):
        print self.obj.__class__.__name__, self.obj.name, name
        sys.stdout.flush()
        return getattr(self.obj, name )

class DebugFactory( object ):

    def __init__(self, klass):
        self.klass = klass

    def __call__(self, *args, **kw):
        instance = self.klass(*args, **kw)
        return DebugWrapper( instance )

class PythonFileLock( object ):
    # safe for a multimple processes

    LOCK_POLL_INTERVAL = 1000

    def __init__(self, lockDir, lockFile):
        self.name = lockFile
        self.lockDir = lockDir
        self.lockFile = os.path.join(lockDir, lockFile)
        #print self.lockFile

    def isLocked(self):
        return os.path.exists(self.lockFile)

    def obtainTimeout( self, timeout ):
        locked = self.obtain()
        maxSleepCount = round(timeout / self.LOCK_POLL_INTERVAL)
        sleepCount = 0
        while (not locked):
            if sleepCount >= maxSleepCount:
                raise Exception("Lock obtain timed out: " + self.toString())
            time.sleep(timeout/1000)
            locked = self.obtain()
            sleepCount += 1
        return locked

    def obtain( self ):
        if not os.path.exists(self.lockDir):
            os.makedirs(self.lockDir)

        if self.isLocked():
            return False

        try:
            open(self.lockFile, 'w')
        except:
            return False
        else:
            return True

    def release( self ):
        os.remove(self.lockFile)
        return True

    def toString(self):
        return 'Lock@' + self.lockFile


class PythonFileStream(object):

    def __init__(self, name, fh, size=0L):
        self.name = name
        self.fh = fh
        self._length = size
        self.isOpen = True

    def close(self, isClone=False):
        if isClone or not self.isOpen:
            return
        self.isOpen = False
        self.fh.close()

    def seek(self, pos):
        self.fh.seek(pos)

    def read(self, length, pos):
        self.fh.seek(pos)
        return self.fh.read(length)

    def write(self, buffer):
        self.fh.write(buffer)
        self.fh.flush()
        self._length += len(buffer)

    def length(self):
        return self._length


class PythonFileDirectory( object ):

    LOCK_DIR = PyLucene.System.getProperty("org.apache.lucene.lockDir",
      PyLucene.System.getProperty("java.io.tmpdir"));

    def __init__(self, path, create=False ):
        self.path = os.path.realpath(path)
        self.name = self.path
        self._locks = {}
        self._streams = []
        if not self.LOCK_DIR:
            self.LOCK_DIR = self.path
        if create:
            self.create()

        assert os.path.isdir( path )

    def create(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        oldFiles = os.listdir(self.path)
        for oldFile in oldFiles:
            os.remove(os.path.join(self.path, oldFile))

        lockPrefix = self.getLockPrefix()
        tmpFiles = os.listdir(self.LOCK_DIR)
        for tmpFile in tmpFiles:
            if tmpFile.startswith(lockPrefix):
                os.remove(os.path.join(self.LOCK_DIR, tmpFile))


    def close(self):
        for s in self._streams:
            s.close()

    def createOutput(self, name ):
        file_path = os.path.join( self.path, name )
        fh = open( file_path, "w" )
        stream = PythonFileStream( name, fh )
        self._streams.append(stream)
        return stream

    def deleteFile( self, name ):
        if self.fileExists(name):
            os.unlink( os.path.join( self.path, name ) )

    def fileExists( self, name ):
        return os.path.exists( os.path.join( self.path, name ) )

    def fileLength( self, name ):
        file_path = os.path.join( self.path, name )
        return os.path.getsize( file_path )

    def fileModified( self, name ):
        file_path = os.path.join( self.path, name )
        return int( os.path.getmtime( file_path ))

    def list(self):
        return os.listdir( self.path )

    def openInput( self, name ):
        file_path = os.path.join( self.path, name )
        fh = open( file_path, 'r')
        stream = PythonFileStream( name, fh, os.path.getsize(file_path) )
        self._streams.append(stream)
        return stream

    def renameFile(self, fname, tname):
        fromName = os.path.join( self.path, fname )
        toName = os.path.join( self.path, tname )
        if os.path.exists( toName ):
            os.remove( toName )
        os.rename( fromName, toName )

    def touchFile( self, name):

        file_path = os.path.join( self.path, name )
        fh = open( file_path, 'rw')
        c = fh.read(1)
        fh.seek(0)
        fh.write(c)
        fh.close()

    def makeLock( self, name ):
        lockDir = self.LOCK_DIR
        lockFile = self.getLockPrefix() + '-' + name
        lock = self._locks.setdefault( name, PythonFileLock(lockDir, lockFile) )
        #print lock.toString()
        return lock

    def getHexDigest(self, string):
        m = md5.new(string)
        return m.hexdigest()

    def getLockPrefix(self):
        dirName = os.path.realpath(self.path)
        prefix = 'lucene-' + self.getHexDigest(dirName)
        return prefix


if DEBUG:
    _globals = globals()
    _globals['PythonFileDirectory'] = DebugFactory( PythonFileDirectory )
    _globals['PythonFileStream'] = DebugFactory( PythonFileStream )
    _globals['PythonFileLock'] = DebugFactory( PythonFileLock )
    del _globals
