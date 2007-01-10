# -*- coding: ISO-8859-15 -*-
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

$Id$
"""

import string
import PyLucene

class NXAsciiFilter(object):

    ACCENTED_CHARS_TRANSLATIONS = string.maketrans(
        r"""ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöøùúûüýÿ""",
        r"""AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyy""")

    def __init__(self, tokenStream):
        self.input = tokenStream

    def toAscii(self, s):
        """Change accented and special characters by ASCII characters.
        """
        s = s.translate(self.ACCENTED_CHARS_TRANSLATIONS)
        s = s.replace('Æ', 'AE')
        s = s.replace('æ', 'ae')
        s = s.replace('Œ', 'OE')
        s = s.replace('œ', 'oe')
        s = s.replace('ß', 'ss')
        return s

    def next(self):
        token = self.input.next()
        if token is None:
            return None

        ttext = token.termText()

        if not ttext:
            return None

        ttext = ttext.encode('ISO-8859-15', 'ignore')
        # ensure that this is really ASCII now, if some weird char
        # has gone through. Backend will convert to unicode anyway:
        ttext = unicode(self.toAscii(ttext), 'ascii', 'ignore')

        return PyLucene.Token(ttext, token.startOffset(),
                              token.endOffset(), token.type())

class NXSortAnalyzer(object):
    """NX SortAnalyzer

    Dedicated analyzer for soring purpose. It only applies a standard
    and the lowercase analyzers.
    
    Use this analyzer applied on fields that you will use for soring
    purpose only.
    """

    def tokenStream(self, fieldName, reader):

        result = PyLucene.StandardTokenizer(reader)
        result = NXAsciiFilter(result)
        result = PyLucene.LowerCaseFilter(result)

        return result
