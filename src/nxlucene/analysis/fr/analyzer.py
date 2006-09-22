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
"""Analyzer helper

$Id: core.py 31300 2006-03-15 03:10:04Z janguenot $
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

FRENCH_STOP_WORDS = [unicode(x, 'latin-1') for x in FRENCH_STOP_WORDS]

FRENCH_EXCLUDED_WORDS = []

xlate_table = {ord(u'é'): u'e',
               ord(u'è'): u'e',
               ord(u'ê'): u'e',
               ord(u'ë'): u'e',
               ord(u'à'): u'a',
               ord(u'ù'): u'u',
               ord(u'ç'): u'c',
               }

class WildCardMagikBefore(PyLucene.Tokenizer):
    
    def __init__(self, tokenstream, wildcards):
        self._wildcards = wildcards
        self.input = tokenstream
        self.count = 0
        
    def next(self):
        term = self.input.next()
        if term is None:
            return None
        text = term.termText()
        self._wildcards[self.count] = {}
            
        for wildcard in ('?', '*'):
            pos = 0
            while True:
                pos = text.find(wildcard, pos+1)
                if pos == -1:
                    break
                self._wildcards[self.count][pos] = wildcard
                text = text[:pos] + 'n' + text[pos+1:]
        self.count += 1
        return PyLucene.Token(text, term.startOffset(), 
                              term.endOffset(), u'word')
    
class WildCardMagikAfter(PyLucene.Tokenizer):
    
    def __init__(self, tokenstream, wildcards):
        self._wildcards = wildcards
        self.input = tokenstream
        self.count = 0

    def next(self):
        term = self.input.next()
        if term is None:
            return None
        text = term.termText()
        for pos, char in self._wildcards[self.count].items():
            text = text[:pos] + char + text[pos+1:]
        self.count += 1
        return PyLucene.Token(text, term.startOffset(), 
                              term.endOffset(), u'word')
        
    
    
class NXFrenchAnalyzer(object):
    """FrenchAnalyzer

    In comparaison with the standard Lucene FrenchAnalyzer,
    NXFrenchAnalyzer apply a specific NXFrenchFilter and extends stop
    words and exclusion lists.
    """

    def tokenStream(self, fieldName, reader):

        #result = WildCardTokenizer(reader)
        result = PyLucene.WhitespaceTokenizer(reader)

        # Standard / Lowercase filtering
        result = PyLucene.StandardFilter(result)
        result = PyLucene.LowerCaseFilter(result)

        #  French stemmer.
        wildcards = {}
        result = WildCardMagikBefore(result, wildcards)
        result = PyLucene.FrenchStemFilter(result)
        result = WildCardMagikAfter(result, wildcards)

        # Custom French filter (see below)
        result = NXFrenchFilter(result)

        # Stop filters.
        result = PyLucene.StopFilter(result, PyLucene.StopAnalyzer.ENGLISH_STOP_WORDS)
        result = PyLucene.StopFilter(result, FRENCH_STOP_WORDS)

        return result

class NXFrenchFilter(object):

    def __init__(self, tokenStream):
        self.input = tokenStream

    def next(self):
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

        ttext = ttext.translate(xlate_table)

        return PyLucene.Token(ttext, token.startOffset(),
                              token.endOffset(), token.type())
