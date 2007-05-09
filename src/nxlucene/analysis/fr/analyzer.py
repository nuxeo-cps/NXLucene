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
import re

import PyLucene

from nxlucene.analysis.base import NXFilter
from nxlucene.analysis.base import NXAsciiFilter
from nxlucene.analysis.base import NXAccentFilter
from nxlucene.analysis.base import NXWordTokenizer
from nxlucene.analysis.base import NXTextTokenizer

FR_STOPWORDS_PATH = os.path.join(os.path.split(__file__)[0], 'stopwords.txt')

FRENCH_STOP_WORDS = []
f = open(FR_STOPWORDS_PATH, 'r')
for each in f.readlines():
    FRENCH_STOP_WORDS.append(string.rstrip(each))
f.close()

FRENCH_STOP_WORDS = [unicode(x, 'utf-8') for x in FRENCH_STOP_WORDS]

FRENCH_EXCLUDED_WORDS = []

class NXWordSplittingTokenizer(NXTextTokenizer):
    """A Tokenizer that does word splitting on non-alpha-numerical characters
    unless there's a number in the token, in which case the whole token is
    interpreted as a product number and is not split.

    This tokenizer also keeps the orginal non-splitted words.
    """

    def __init__(self, reader):
        text_splitted = self._tokenize(reader)
        words_set = set()
        for w in text_splitted:
            #print "w = [%s] of type = %s" % (w, type(w))
            words_set.add(w)
            pos = w.find('-')
            if pos >= 0:

                word_extracted = w[:pos]
                try:
                    # If one of the word is a number we don't split the word
                    # further.
                    number = int(word_extracted)
                    continue
                except ValueError:
                    pass
                words_set.add(word_extracted)

                word_extracted = w[pos + 1:]
                try:
                    # If one of the word is a number we don't split the word
                    # further.
                    number = int(word_extracted)
                    continue
                except ValueError:
                    pass
                words_set.add(word_extracted)

        words = [x for x in words_set if x]
        #print "words = %s" % words

        # XXX : offsets should be computed here and not set to 0 0 but this
        # works alright for our usage here.
        self.tokens = [PyLucene.Token(w, 0, 0) for w in words]
        self.iterator = iter(self.tokens)


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


class NXFrenchAnalyzer(object):
    """FrenchAnalyzer

    In comparaison with the standard Lucene FrenchAnalyzer,
    NXFrenchAnalyzer apply a specific NXFrenchFilter and extends stop
    words and exclusion lists.
    """

    def tokenStream(self, fieldName, reader):
        # Either use the StandardTokenizer or the NXWordSplittingTokenizer.
        # The NXWordSplittingTokenizer is specialized in dealing with words like
        # grand-mère.
        #stream = PyLucene.StandardTokenizer(reader)
        stream = NXWordSplittingTokenizer(reader)

        # Standard / Lowercase filtering
        stream = PyLucene.StandardFilter(stream)
        stream = PyLucene.LowerCaseFilter(stream)

        # Custom French filter which removes meaningless letters (l', s', etc.)
        stream = NXFrenchFilter(stream)

        # Stop filters which removes meaningless words (et, a, etc.)
        # The stop filters should be run before the stemmer otherwise too much
        # words (a stemmed word could look like a stop word) would be removed.
        stream = PyLucene.StopFilter(stream, PyLucene.StopAnalyzer.ENGLISH_STOP_WORDS)
        stream = PyLucene.StopFilter(stream, FRENCH_STOP_WORDS)

        words = set()
        token = stream.next()
        while token is not None:
            words.add(token.termText())
            token = stream.next()
        #print "words0 = %s" % words

        # Generate 2 streams
        stream1 = NXWordTokenizer(words)
        stream2 = NXWordTokenizer(words)
        words = set()

        # French stemming on accented characters
        stream1 = PyLucene.FrenchStemFilter(stream1)
        token = stream1.next()
        while token is not None:
            words.add(token.termText())
            token = stream1.next()
        #print "words1 = %s" % words

        # French stemming on non-accented characters
        stream2 = NXAccentFilter(stream2)
        stream2 = PyLucene.FrenchStemFilter(stream2)
        token = stream2.next()
        while token is not None:
            words.add(token.termText())
            token = stream2.next()
        #print "words2 = %s" % words

        # Finally getting rid of all accents
        stream = NXWordTokenizer(words)
        stream = NXAccentFilter(stream)

        # Removing duplicate words
        words = set()
        token = stream.next()
        while token is not None:
            words.add(token.termText())
            token = stream.next()
        stream = NXWordTokenizer(words)

##         # Debug
##         words = set()
##         token = stream.next()
##         while token is not None:
##             words.add(token.termText())
##             token = stream.next()
##         print "words = %s" % words

        return stream


class NXFrenchSearchAnalyzer(object):
    """FrenchSearchAnalyzer

    Search part analyzer.
    """

    def tokenStream(self, fieldName, reader):
        stream = NXTextTokenizer(reader)

        # Standard / Lowercase filtering
        stream = PyLucene.StandardFilter(stream)
        stream = PyLucene.LowerCaseFilter(stream)

        # Custom French filter (see below)
        stream = NXFrenchFilter(stream)

        # Stop filters.
        # The stop filters should be run before the stemmer otherwise too much
        # words (a stemmed word could look like a stop word) would be removed.
        stream = PyLucene.StopFilter(stream, PyLucene.StopAnalyzer.ENGLISH_STOP_WORDS)
        stream = PyLucene.StopFilter(stream, FRENCH_STOP_WORDS)

        # French stemmer
        stream = PyLucene.FrenchStemFilter(stream)

        # Get rid of accents.
        # The accents need to be removed in the end and especially after the
        # stemming, otherwise the stemming will of course not work.
        stream = NXAccentFilter(stream)

##         # Debug
##         words = set()
##         token = stream.next()
##         while token is not None:
##             words.add(token.termText())
##             token = stream.next()
##         print "words = %s" % words

        return stream

