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
"""Python File Stream

$Id$
"""

class PythonFileStream(object):

    def __init__(self, name, fh, size=0L):

        self.name = name
        # Optimization.
        self.seek = fh.seek

        self._flush = fh.flush
        self._write = fh.write
        self._read = fh.read
        self._close = fh.close

        # For being able to delete the reference with self.
        self._fh = fh

        self._length = size
        self._isOpen = True

    def close(self, isClone=False):
        if isClone or not self._isOpen:
            return
        self._isOpen = False
        self._close()

    def read(self, length, pos):
        self.seek(pos)
        return self._read(length)

    def write(self, buffer_):
        self._write(buffer_)
        self._flush()
        self._length += len(buffer_)

    def length(self):
        return self._length

    def __del__(self):
        # Ensure it's closed.
        self._fh.close()