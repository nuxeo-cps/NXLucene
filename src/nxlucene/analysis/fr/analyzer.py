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

class NXAccentFilter(object):

    def __init__(self, tokenStream):
        self.input = tokenStream

    def next(self):
        token = self.input.next()
        if token is None:
            return None

        ttext = token.termText()
        if not ttext:
            return None
        
        ttext = ttext.translate(xlate_table)
        return PyLucene.Token(ttext, token.startOffset(),
                              token.endOffset(), token.type())


#class WildCardTokenizer(PyLucene.Tokenizer):
    
    #def __init__(self, tokenStream):
        #if not isinstance(tokenStream, PyLucene.StringReader):
            ## Sometimes this is called with a PyLucene.Reader.
            ## I wrap it in a StringReader to get a consistent interface.
            #tokenStream = PyLucene.StringReader(tokenStream.read())
        #self.input = tokenStream
        #self.offset = 0
        
    #def _getChar(self):
        #val = self.input.read()
        #self.offset += 1
        #if val == -1:
            #return None
        #return unichr(val)
    
    #def next(self):
        #result = ''
        #old_offset = self.offset
        #while True:
            #char = self._getChar()
            #if char is None:
                #break
            #if char.isalnum():
                #result += char
                #continue
            #elif char == '*':
                ## Asterisks are wildcards if part of a word, ignored otherwise.
                #if len(result) == 0:
                    #next_char = self._getChar()
                    #if next_char is None:
                        ## End of stream.
                        #break
                    #if not next_char.isalnum():
                        ## First AND last character in the word. Skip.
                        #continue
                ## Part of a word. Keep:
                #result += char
                #continue
            #elif char == '?':
                ## Question marks can either be wildcards or end of sentences.
                ## We assume that if it comes at the end of a word, it's a 
                ## wildcard.
                #next_char = self._getChar()
                #if next_char is None:
                    ## End of stream.
                    #break
                #if next_char.isalnum():
                    ## The word continues after the question mark. It's a
                    ## wildcard, add both to the result.
                    #result += char
                    #result += next_char
                    #continue
                #if result:
                    ## The end of a word, and therefore probably the end of a 
                    ## sentence. We skip the question mark, and return the word,
                    #break
                ## This question mark was standing by itself. Ignore it and..
                #continue
            #else:
                ## Not a letter, not a wildcard. 
                #if result: # We have a word
                    #break
                ## We haven't found the start of the word yet. 
                #continue
        #if result:
            ##print result,
            #return PyLucene.Token(result, old_offset, self.offset, u'word')
        #return None



#class WildCardMagikBefore(PyLucene.Tokenizer):
    
    #def __init__(self, tokenstream, wildcards):
        #self._wildcards = wildcards
        #self.input = tokenstream
        #self.count = 0
        
    #def next(self):
        #term = self.input.next()
        #if term is None:
            #return None
        #text = term.termText()
        #self._wildcards[self.count] = {}
            
        #for wildcard in ('?', '*'):
            #pos = 0
            #while True:
                #pos = text.find(wildcard, pos+1)
                #if pos == -1:
                    #break
                #self._wildcards[self.count][pos] = wildcard
                #text = text[:pos] + 'n' + text[pos+1:]
        #self.count += 1
        #return PyLucene.Token(text, term.startOffset(), 
                              #term.endOffset(), u'word')
    
#class WildCardMagikAfter(PyLucene.Tokenizer):
    
    #def __init__(self, tokenstream, wildcards):
        #self._wildcards = wildcards
        #self.input = tokenstream
        #self.count = 0

    #def next(self):
        #term = self.input.next()
        #if term is None:
            #return None
        #text = term.termText()
        #for pos, char in self._wildcards[self.count].items():
            #text = text[:pos] + char + text[pos+1:]
        #self.count += 1
        #return PyLucene.Token(text, term.startOffset(), 
                              #term.endOffset(), u'word')


#class NXFrenchWildcardAnalyzer(object):
    #"""French analyzer with wildcard support"""
    
    #def tokenStream(self, fieldName, reader):

        #result = WildCardTokenizer(reader)

        ## Standard / Lowercase filtering
        #result = PyLucene.StandardFilter(result)
        #result = PyLucene.LowerCaseFilter(result)

        ##  French stemmer.
        #wildcards = {}
        #result = WildCardMagikBefore(result, wildcards)
        #result = PyLucene.FrenchStemFilter(result)
        #result = WildCardMagikAfter(result, wildcards)

        ## Get rid of accents:
        #result = NXAccentFilter(result)
        
        ## Stop filters.
        #result = PyLucene.StopFilter(result, PyLucene.StopAnalyzer.ENGLISH_STOP_WORDS)
        #result = PyLucene.StopFilter(result, FRENCH_STOP_WORDS)

        #return result

        
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

        #  French stemmer.
        result = PyLucene.FrenchStemFilter(result)

        # Get rid of accents:
        result = NXAccentFilter(result)
        
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

        return PyLucene.Token(ttext, token.startOffset(),
                              token.endOffset(), token.type())
