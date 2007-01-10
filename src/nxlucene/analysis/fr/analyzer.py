# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2006-2007 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Julien Anguenot <ja@nuxeo.com>
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
"""Analyzer helper

$Id$
"""
import string
import os.path
import PyLucene

FR_STOPWORDS_PATH = os.path.join(os.path.split(__file__)[0], 'stopwords.txt')

FRENCH_STOP_WORDS = []
f = open(FR_STOPWORDS_PATH, 'r')
for each in f.readlines():
    FRENCH_STOP_WORDS.append(string.rstrip(each))
f.close()

FRENCH_STOP_WORDS = [unicode(x, 'utf-8') for x in FRENCH_STOP_WORDS]

FRENCH_EXCLUDED_WORDS = []

XLATE_TABLE = {
    ord(u'�'): u'a',
    ord(u'�'): u'a',
    ord(u'�'): u'e',
    ord(u'�'): u'e',
    ord(u'�'): u'e',
    ord(u'�'): u'e',
    ord(u'�'): u'i',
    ord(u'�'): u'o',
    ord(u'�'): u'u',
    ord(u'�'): u'c',
    ord(u'�'): u'oe',
    ord(u'�'): u'ae',
    }


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

class NXFrenchFilter(NXFilter):

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

        if "\'" in ttext:

            if (ttext.lower().startswith("l'") or
                ttext.lower().startswith("d'") or
                ttext.lower().startswith("n'") or
                ttext.lower().startswith("m'") or
                ttext.lower().startswith("s'") or
                ttext.lower().startswith("t'") or
                ttext.lower().startswith("c'") or
                ttext.lower().startswith("j'")):

                ttext = ttext[2:]

            if ttext.lower().startswith("qu'"):
                ttext = ttext[3:]

            if ttext.lower().endswith("'s"):
                ttext = ttext[:2]

        return PyLucene.Token(ttext, token.startOffset(),
                              token.endOffset(), token.type())

class NXAccentFilter(NXFilter):

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

        ttext = ttext.translate(XLATE_TABLE)
        return PyLucene.Token(ttext, token.startOffset(),
                              token.endOffset(), token.type())


class NXFrenchAnalyzer(object):
    """FrenchAnalyzer

    In comparaison with the standard Lucene FrenchAnalyzer,
    NXFrenchAnalyzer apply a specific NXFrenchFilter and extends stop
    words and exclusion lists.
    """

    def tokenStream(self, fieldName, reader):
        result = PyLucene.StandardTokenizer(reader)

        # Standard / Lowercase filtering
        result = PyLucene.StandardFilter(result)
        result = PyLucene.LowerCaseFilter(result)

        # Custom French filter (see below)
        result = NXFrenchFilter(result)

        # Stop filters.
        # The stop filters should be run before the stemmer otherwise too much
        # words (a stemmed word could look like a stop word) would be removed.
        result = PyLucene.StopFilter(result, PyLucene.StopAnalyzer.ENGLISH_STOP_WORDS)
        result = PyLucene.StopFilter(result, FRENCH_STOP_WORDS)

        # French stemmer
        result = PyLucene.FrenchStemFilter(result)

        # Get rid of accents.
        # The accents need to be removed in the end and especially after the
        # stemming, otherwise the stemming will of course not work.
        result = NXAccentFilter(result)

        return result

