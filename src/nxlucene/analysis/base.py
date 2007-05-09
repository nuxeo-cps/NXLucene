# -*- coding: ISO-8859-15 -*-
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
"""Module providing base functionnalities for analyzers.

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


class NXAsciiFilter(NXFilter):

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


class NXAccentFilter(NXFilter):

    XLATE_TABLE = {
        ord(u'à'): u'a',
        ord(u'â'): u'a',
        ord(u'é'): u'e',
        ord(u'è'): u'e',
        ord(u'ê'): u'e',
        ord(u'ë'): u'e',
        ord(u'ï'): u'i',
        ord(u'ô'): u'o',
        ord(u'ù'): u'u',
        ord(u'ç'): u'c',
        ord(u'œ'): u'oe',
        ord(u'æ'): u'ae',
        }

    def __init__(self, tokenStream):
        self.input = tokenStream

    def next(self):
        """Move to the next token.
        """
        token = self.input.next()
        if token is None:
            return None

        ttext = token.termText()
        if not ttext:
            return None

        ttext = ttext.translate(self.XLATE_TABLE)
        return PyLucene.Token(ttext, token.startOffset(),
                              token.endOffset(), token.type())


class NXWordTokenizer(NXFilter):
    """Utility class to provide a token stream from text words.
    """

    def __init__(self, words):
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
        try:
            return self.iterator.next()
        except StopIteration:
            return None


class NXTextTokenizer(object):
    """A Tokenizer that does word splitting on non-alpha-numerical characters.
    """
    # A regexp that does word splitting using alpha-numerical words.
    WORD_SPLITTING_REGEXP = re.compile(
        unicode('[^-a-zA-Z0-9ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöøùúûüýÿœæ]*',
                'iso-8859-15'))

    tokens = []
    iterator = None

    def _tokenize(self, reader):
        text = ''
        while True:
            res = reader.read()
            #print "res = [%s] of type = %s" % (res, type(res))
            if isinstance(res, str) or isinstance(res, unicode):
                if res == '':
                    break
                text += res
            elif isinstance(res, int):
                if res == -1:
                    break
                #print "res = %s" % res
                # XXX : Ugly ugly hack to deal with the "œ" character
                if res == 339:
                    res = 189
                text += chr(res)
            else:
                break

        #print "text = [%s] of type = %s" % (text, type(text))

        # XXX : This is ugly and why sometimes does a str appear here ?
        # It should always be unicode objects.
        if isinstance(text, str):
            text = unicode(text, 'iso-8859-15')

        #print "text = [%s] of type = %s" % (text, type(text))
        text_splitted = self.WORD_SPLITTING_REGEXP.split(text)
        return text_splitted

    def __init__(self, reader):
        text_splitted = self._tokenize(reader)
        words = [x for x in text_splitted if x]
        #print "words = %s" % words

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
        try:
            return self.iterator.next()
        except StopIteration:
            return None

