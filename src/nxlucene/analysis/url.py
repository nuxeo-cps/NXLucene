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
"""URL Analyzer

$Id$
"""

import string
import re

import PyLucene

from nxlucene.analysis.base import NXAsciiFilter
from nxlucene.analysis.base import NXWordTokenizer

class NXUrlTokenizer(object):

    # A regexp that does word splitting using alpha-numerical words.
    WORD_SPLITTING_REGEXP = re.compile('[^a-zA-Z0-9]*')
    WORD_SPLITTING_WITHOUT_DASH_REGEXP = re.compile('[^-a-zA-Z0-9]*')

    UNWANTED_WORDS = ['http://', 'https://', 'ftp://']

    tokens = []
    iterator = None

    def __init__(self, reader):
        text = ''

        # Simple code to use a reader, the only implemented in PyLucene
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
                text += chr(res)
            else:
                break

        words_set = set()
        # Adding the whole URL
        words_set.add(text)

        for unwanted_word in self.UNWANTED_WORDS:
            pos = text.find(unwanted_word)
            if pos >= 0:
                text = text[len(unwanted_word):]
                break
        # Adding the address without the URL scheme and pontential trailing "/"
        if text.endswith('/'):
            text = text[:-1]
        words_set.add(text)

        text_splitted = self.WORD_SPLITTING_REGEXP.split(text)
        text_splitted2 = self.WORD_SPLITTING_WITHOUT_DASH_REGEXP.split(text)
        for w in text_splitted + text_splitted2:
            words_set.add(w)
        words = [x for x in words_set if x]
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


class NXUrlNormalizer(object):

    tokens = []
    iterator = None

    def __init__(self, reader):
        text = ''

        # Simple code to use a reader, the only implemented in PyLucene
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
                text += chr(res)
            else:
                break

        # XXX : offsets should be computed here and not set to 0 0 but this
        # works alright for our usage here.
        self.tokens = [PyLucene.Token(w, 0, 0) for w in [text]]
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


class NXUrlAnalyzer(object):
    """Dedicated analyzer for searching URLs.
    """
    def tokenStream(self, fieldName, reader):
        stream = NXUrlTokenizer(reader)
        stream = NXAsciiFilter(stream)
        stream = PyLucene.LowerCaseFilter(stream)
        return stream


class NXUrlSearchAnalyzer(object):
    """Dedicated analyzer for indexing URLs.
    """
    def tokenStream(self, fieldName, reader):
        stream = NXUrlNormalizer(reader)
        stream = NXAsciiFilter(stream)
        stream = PyLucene.LowerCaseFilter(stream)
        return stream
