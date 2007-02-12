# Copyright (C) 2007 Nuxeo SAS <http://www.nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
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
"""URL Analyzer

$Id$
"""

import string
import re
import PyLucene

class NXFilter(object):
    """Base class which provides the __iter__ method.
    """

    def __init__(self):
        raise RuntimeError, "You must inherit from this class."

    def __iter__(self):
        """Returns an iterator over the tokens returned by this filter.
        """
        result = []
        while True:
            token = self.next()
            if token is not None:
                result.append(token)
            else:
                break
        return iter(result)


class NXUrlTokenizer(NXFilter):

    # A regexp that does word splitting using alpha-numerical words.
    WORD_SPLITTING_REGEXP = re.compile('[^a-zA-Z0-9]*')

    UNWANTED_URL_WORDS = ['http', 'https', 'ftp']

    def __init__(self, reader):
        self.tokens = []
        self.iterator = None

        text = ''
        # Good optimized code to use a reader but not implemented in PyLucene
##         while True:
##             chars = []
##             res = reader.read(chars)
##             if res == -1:
##                 break
##             text += ''.join(chars)

        # Simple code to use a reader, the only implemented in PyLucene
        while True:
            res = reader.read()
            if res == -1:
                break
            text += chr(res)

        words = self.WORD_SPLITTING_REGEXP.split(text)
        words = [x for x in words if x not in self.UNWANTED_URL_WORDS]
        # XXX : offsets should be computed here and not set to 0 0 but this
        # works alright for our usage here.
        self.tokens = [PyLucene.Token(w, 0, 0) for w in words]
        self.iterator = iter(self.tokens)

    def __iter__(self):
        """Returns an iterator over the tokens returned by this filter.
        """
        return self.iterator

    def next(self):
        """Returns an iterator over the tokens returned by this filter.
        """
        return self.iterator.next()


class NXAsciiFilter(NXFilter):

    ACCENTED_CHARS_TRANSLATIONS = string.maketrans(
        r"""¿¡¬√ƒ≈«»… ÀÃÕŒœ—“”‘’÷ÿŸ⁄€‹›‡·‚„‰ÂÁËÈÍÎÏÌÓÔÒÚÛÙıˆ¯˘˙˚¸˝ˇ""",
        r"""AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyy""")

    def __init__(self, tokenStream):
        self.input = tokenStream

    def toAscii(self, s):
        """Change accented and special characters by ASCII characters.
        """
        s = s.translate(self.ACCENTED_CHARS_TRANSLATIONS)
        s = s.replace('∆', 'AE')
        s = s.replace('Ê', 'ae')
        s = s.replace('º', 'OE')
        s = s.replace('Ω', 'oe')
        s = s.replace('ﬂ', 'ss')
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

class NXUrlAnalyzer(object):
    """NX UrlAnalyzer

    Dedicated analyzer for sorting purpose. It only applies a standard
    and the lowercase analyzers.

    Use this analyzer applied on fields that you will use for sorting
    purpose only.
    """

    def tokenStream(self, fieldName, reader):

        result = NXUrlTokenizer(reader)
        result = NXAsciiFilter(result)
        result = PyLucene.LowerCaseFilter(result)

        return result
