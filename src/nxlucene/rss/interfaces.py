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
"""RSS interfaces

$Id$
"""

import zope.interface

class IResultSet(zope.interface.Interface):
    """Result Set interface
    """

    def getStream(pretty=False):
        """Return the full RSS document as an XML stream.
        """

    def addItem(uid, fields_map={}):
        """Add an item to the RSS document.

        `guid` is the item uid
        `fields_map` XXX
        """

class IResultItem(zope.interface.Interface):
    """ RSS Result Item
    """

    def getElement(uid, fields_map={}):
        """Return an etree element

        `guid` is the item uid
        `fields_map` XXX
        """

class IPythonResultSet(zope.interface.Interface):
    """ Python Result set abstraction

    See adapter.PythonResultSet for the adapter implementation
    """

    def getResults():
        """Return a tuple of mapping
        """
