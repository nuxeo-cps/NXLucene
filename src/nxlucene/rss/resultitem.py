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
"""RSS result item

$Id$
"""

try:
    import cElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

import zope.interface

from weblucene.rss.interfaces import IResultItem
from weblucene.rss import RSSElement
from weblucene.rss import WebLuceneElement

class ResultItem(object):
    """RSS Result item 
    """

    zope.interface.implements(IResultItem)

    def getElement(self, uid, fields_map={}):

        # XXX metadata <title/> <description/> <link/>

        elt = RSSElement('item')

        # <guid/>
        iguid = RSSElement('guid')
        iguid.text = unicode(uid)
        elt.append(iguid)

        # fields
        ifields = WebLuceneElement('fields')
        for k, v in fields_map.items():
            ielt = WebLuceneElement('field')
            ielt.attrib['id'] = k
            ielt.text = v
            ifields.append(ielt)
        elt.append(ifields)
        return elt
