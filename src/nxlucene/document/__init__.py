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
"""NXLucene document.definition

$Id: $
"""

import PyLucene

UID_FIELD_ID = 'uid'

class Document(PyLucene.Document):

    def __init__(self, uid=None):

        if uid is None:
            raise ValueError("You need to provide an uid for this document")

        PyLucene.Document.__init__(self)
        self.add(PyLucene.Field.Keyword(UID_FIELD_ID, unicode(uid)))

    def getUID(self):
        return self.get(UID_FIELD_ID)


