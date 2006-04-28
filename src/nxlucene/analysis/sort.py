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
"""Sort Analyzer

$Id: core.py 31300 2006-03-15 03:10:04Z janguenot $
"""

import PyLucene

class NXSortAnalyzer(object):
    """NX SortAnalyzer

    Dedicated analyzer for soring purpose. It only applies a standard
    and the lowercase analyzers.

    Use this analyzer applied on fields that you will use for soring
    purpose only.
    """

    def tokenStream(self, fieldName, reader):

        result = PyLucene.StandardTokenizer(reader)
        result = PyLucene.LowerCaseFilter(result)

        return result
