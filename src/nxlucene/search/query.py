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
"""Query helper

$Id$
"""

import PyLucene

boolean_clauses_map = {
    'AND' : PyLucene.BooleanClause.Occur.MUST,
    'OR'  : PyLucene.BooleanClause.Occur.SHOULD,
    'NOT' : PyLucene.BooleanClause.Occur.MUST_NOT
    }

query_parser_operators_map = {
    'AND': PyLucene.QueryParser.Operator.AND,
    'OR' : PyLucene.QueryParser.Operator.OR,
    }

SPECIAL_CHARS = ('\\', '+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']',
                 '^', '"', '~', '*', '?', ':')

def escape(str_):
    for char in SPECIAL_CHARS:
        str_ = str_.replace(char, '\%s' % char)
    return str_
