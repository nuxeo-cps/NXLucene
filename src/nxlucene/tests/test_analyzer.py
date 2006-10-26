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
"""NXFrenchAnalyzer helper

$Id: core.py 31300 2006-03-15 03:10:04Z janguenot $
"""

import unittest
import PyLucene

from nxlucene.analysis.fr.analyzer import NXFrenchAnalyzer
from nxlucene.analysis.sort import NXSortAnalyzer

class NXFrenchAnalyzerTestCase(unittest.TestCase):

    def test_no_french_specifics(self):

        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader('Un test')

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'test'])

    def test_french_samples_pp(self):

        a = NXFrenchAnalyzer()

        term_str = unicode("chanté", 'latin-1')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'chant'])

        # Make sure it also works if you skip the accent:
        term_str = unicode("chante", 'latin-1')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'chant'])

    def test_french_samples_plurals(self):

        a = NXFrenchAnalyzer()

        term_str = unicode("messages", 'latin-1')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'messag'])

    def test_french_samples_fem(self):

        a = NXFrenchAnalyzer()

        term_str = unicode("jolie", 'latin-1')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'jol'])

    def test_french_apostrophe(self):

        a = NXFrenchAnalyzer()

        term_str = unicode("l'enfant", 'latin-1')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'enfant'])

    def test_french_stopwords(self):

        a = NXFrenchAnalyzer()

        term_str = "avoir de la chance"

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'chanc'])

    def test_sort_analyzer_lowercase(self):

        a = NXSortAnalyzer()

        term_str = unicode("A La MaiSon", 'latin-1')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'a', u'la', u'maison'])

    def test_standard_analyzer_with_columns(self):

        a = PyLucene.StandardAnalyzer()
        term_str = unicode('xx:yy')
        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'xx', u'yy'])

    def test_keyword_analyzer_with_columns(self):

        a = PyLucene.KeywordAnalyzer()
        term_str = unicode('xx:yy')
        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'xx:yy'])

    def test_french_chars(self):

        a = NXFrenchAnalyzer()

        term_str = unicode("éèëêàùc", 'latin-1')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'eeeeauc'])

    def test_french_case_accents_stemming(self):
        # This is to make sure that case, accent and endings all result
        # in the same index word.
        search_words = ('déontologie',
                        'Déontologie',
                        'DEONTOLOGIE',
                        'deontologie',
                        'Deontologie',
                        'DEONTOLOGIES',
                        'déontologies',
                        'Déontologies',
                        'DEONTOLOGI',
                        'déontologi',
                        'Déontologi',
                        'DEONTOLOGIS',
                        'déontologis',
                        'Déontologis',
                        'dEONTOLOGIE',
                    )

        a = NXFrenchAnalyzer()

        for word in search_words:
            term_str = unicode(word, 'latin-1')

            reader = PyLucene.StringReader(term_str)
            tokens = a.tokenStream('', reader)
            tokens = [token.termText() for token in tokens]
            self.assertEquals(tokens, [u'deontolog'])

    def test_french_wildcards(self):

        term_str = unicode("INVENTA?RE", 'latin-1')

        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]

        self.assertEquals(tokens_fr, [u"inventa?r"])

    def test_french_stemming_wildcards(self):

        term_str = unicode("GE?DE", 'latin-1')

        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]

        self.assertEquals(tokens_fr, ['ge?d'])

    def test_french_misc(self):

        term_str = unicode("l'enfant", 'latin-1')

        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(tokens_fr, ['enfant'])


    def test_french_complet(self):
        text = "Test n°67-236: Les parts sociales ne peuvent être données en "\
               "nantissement. ? Je suis un enfant de l'indépendance. Je "\
               "ch?rche f*rcement bien!"

        term_str = unicode(text, 'latin-1')

        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(tokens_fr, 
                          [u'test', u'67', u'236', u'part', u'social', 
                           u'peuvent', u'don', u'nant', u'suis', u'enfant',
                           u'independ', u'ch?rche', u'f*rcement', u'bien'])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NXFrenchAnalyzerTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
