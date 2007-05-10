# Copyright (C) 2006-2007, Nuxeo SAS <http://www.nuxeo.com>
# Authors:
# Julien Anguenot <ja@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
# Benoit Delbosc <bdelbosc@nuxeo.com>
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

$Id$
"""

import PyLucene

from fr import NXFrenchAnalyzer, NXFrenchSearchAnalyzer
from sort import NXSortAnalyzer
from url import NXUrlAnalyzer, NXUrlSearchAnalyzer

# LOGIC
#
# This is important to note that we may use different analyzers for indexing and
# for searching. This is the case here for the "french" analyzer and the
# "french-search" analyzer. Those analyzers are very close but a bit different
# due to the fact that when an indexation occurs there is an OR condition
# between multiple indexed terms while there is an AND condition between
# multiple search terms. We didn't know how to deal with this fact otherwise.
#
# Search analyzers should always return only one token for one word.
# Other analyzers or analyzers specialized in indexation should may return many
# tokens for one word.
analyzers_map = {
    'standard'       : PyLucene.StandardAnalyzer(),
    'french'         : NXFrenchAnalyzer(),
    'french-search'  : NXFrenchSearchAnalyzer(),
    'sort'           : NXSortAnalyzer(),
    'url'            : NXUrlAnalyzer(),
    'url-search'     : NXUrlSearchAnalyzer(),
    'keyword'        : PyLucene.KeywordAnalyzer(),
    }

def getAnalyzerById(analyzer_id, mode='index'):
    key = analyzer_id.lower()
    if mode == 'search' and key + '-search' in analyzers_map.keys():
        key += '-search'
    elif key not in analyzers_map.keys():
        key  = 'standard'
    return analyzers_map.get(key)

def getPerFieldAnalyzerWrapper(default_analyzer=None):
    if default_analyzer is None:
        default_analyzer = PyLucene.StandardAnalyzer()
    return PyLucene.PerFieldAnalyzerWrapper(default_analyzer)

