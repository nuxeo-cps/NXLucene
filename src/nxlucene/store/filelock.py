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
"""Python File Lock.

$Id$
"""

import os
import time

class PythonFileLock(object):

    # XXX this lock has some problems in a multi threading environement.
    # XXX this lock has a serious preformance issue.

    # This implementation is not used yet by the PythonFileDirectory.
    # See nxlucene.store.lock.py using

    LOCK_POLL_INTERVAL = 1000

    def __init__(self, lockDir, lockFile):
        self.name = lockFile
        self.lockDir = lockDir
        self.lockFile = os.path.join(lockDir, lockFile)

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

    def obtain(self):
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

    def release(self):
        try:
            os.remove(self.lockFile)
        except OSError:
            return False
        else:
            return True

    def toString(self):
        return 'Lock@' + self.lockFile