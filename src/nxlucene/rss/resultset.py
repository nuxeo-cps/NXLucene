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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-13x
"""RSS result set

$Id$
"""

import cElementTree as etree

import zope.interface

from nxlucene.rss import RSSElement
from nxlucene.rss import NXLuceneElement

from nxlucene.rss.interfaces import IResultSet
from nxlucene.rss.resultitem import ResultItem

class ResultSet(object):
    """RSS result set
    """

    zope.interface.implements(IResultSet)

    def __init__(self, xml_stream=''):
        if not xml_stream:
            self._doc = self._getElementSkel()
        else:
            self._doc = etree.XML(xml_stream)

    def getStream(self, pretty=False):
        if not pretty:
            return etree.tostring(self._doc)
        # XXX etree doesn't provide pretty print yet.
        raise NotImplementedError

    def getTree(self):
        return self._doc

    def addItem(self, uid, fields_map={}):
        item = ResultItem().getElement(uid, fields_map)
        self._doc.append(item)

    def addNumberOfResults(self, nb_items=0):
        elt = NXLuceneElement('nbitems')
        elt.text = str(nb_items)
        self._doc.append(elt)

    def _getElementSkel(self):
        elt = RSSElement('rss')
        elt.attrib['version'] = "2.0"
        return elt
