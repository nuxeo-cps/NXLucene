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

class PythonDirLock(object):

    def __init__(self, name, path, lock):
        self.name = name # XXX Unused
        self.lock_file = path # XXX Unused
        self.lock = lock

    def isLocked(self):
        return self.lock.locked()

    def obtainTimeout(self, timeout):
        return self.lock.acquire(timeout)

    def obtain(self):
        return self.lock.acquire()

    def release(self):
        return self.lock.release()
