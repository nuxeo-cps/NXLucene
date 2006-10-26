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
"""Analyzer Helper

$Id: core.py 31300 2006-03-15 03:10:04Z janguenot $
"""

import PyLucene

from fr.analyzer import NXFrenchAnalyzer
from sort import NXSortAnalyzer

analyzers_map = {
    # XXX not complete
    'standard'       : PyLucene.StandardAnalyzer(),
    'french'         : NXFrenchAnalyzer(),
    'sort'           : NXSortAnalyzer(),
    'keyword'        : PyLucene.KeywordAnalyzer(),
    }

def getAnalyzerById(analyzer_id):
    if not analyzer_id.lower() in analyzers_map.keys():
        analyzer_id = 'standard'
    return analyzers_map.get(analyzer_id)

def getPerFieldAnalyzerWrapper(default_analyzer=None):
    if default_analyzer is None:
        default_analyzer = PyLucene.StandardAnalyzer()
    return PyLucene.PerFieldAnalyzerWrapper(default_analyzer)
