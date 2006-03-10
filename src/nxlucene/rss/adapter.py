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
"""RSS adapter

$Id$
"""

try:
    import cElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

import zope.interface

from nxlucene.rss.interfaces import IResultSet
from nxlucene.rss.interfaces import IPythonResultSet

class PythonResultSet(object):
    """Transform a IResultSet to IPythonResultSet
    """

    zope.interface.implements(IPythonResultSet)

    __used_for__ = IResultSet

    def __init__(self, resultset):
        self._elt = etree.XML(resultset.getStream())
        self._results = ()

    def getResults(self):
        for item in self._getItems():
            res = {}
            res[unicode('uid')] = unicode(self._getUidFor(item))
            for field in self._getFieldsFor(item):
                res[unicode(field.attrib['id'])] = unicode(field.text)
            self._results += (res,)
        return self._results

    def _getItems(self):
        return tuple(
            self._elt.getiterator("{http://backend.userland.com/rss2}item"))

    def _getFieldsFor(self, fields_node):
        return fields_node.getiterator(
            "{http://namespaces.nuxeo.org/nxlucene/}field")

    def _getUidFor(self, item_node):
        return item_node.find(
            "{http://backend.userland.com/rss2}guid").text
        