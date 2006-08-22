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
"""lucene reader

$Id$
"""

import os
import shutil
import PyLucene

import zope.interface
from interfaces import ILuceneReader

from nxlucene.directory.PythonDirectory import PythonFileDirectory

class LuceneReader(object):
    """Lucene Reader
    """

    zope.interface.implements(ILuceneReader)

    _reader = None

    def __init__(self, store_dir, creation=False):
        if creation:
            if os.path.exists(store_dir):
                shutil.rmtree(store_dir)
            os.makedirs(store_dir)
        self._store = PythonFileDirectory(store_dir, creation)
        self._reader = self.get()
        self.close()

    def get(self):
        if not self._reader:
            self._reader = PyLucene.IndexReader.open(self._store)
        return self._reader

    def close(self):
        if self._reader:
            self._reader.close()
            self._reader = None

    def __del__(self):
        self.close()
