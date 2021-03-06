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
"""NXFrenchAnalyzer helper

$Id$
"""

import unittest
import PyLucene

from nxlucene.analysis.fr import NXFrenchAnalyzer, NXFrenchSearchAnalyzer
from nxlucene.analysis.sort import NXSortAnalyzer
from nxlucene.analysis.url import NXUrlAnalyzer, NXUrlSearchAnalyzer

class NXFrenchAnalyzerTestCase(unittest.TestCase):

    def test_no_french_specifics(self):

        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader('Un test')

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'test'])

    def test_french_samples_pp(self):

        a = NXFrenchAnalyzer()

        term_str = unicode("chant�", 'iso-8859-15')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'chant'])

        # Make sure it also works if you skip the accent:
        term_str = unicode("chante", 'iso-8859-15')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'chant'])

    def test_french_samples_plurals(self):

        a = NXFrenchAnalyzer()

        term_str = unicode("messages", 'iso-8859-15')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'messag'])

    def test_french_samples_fem(self):

        a = NXFrenchAnalyzer()

        term_str = unicode("jolie", 'iso-8859-15')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'jol'])

    def test_french_apostrophe(self):

        a = NXFrenchAnalyzer()

        term_str = unicode("l'enfant", 'iso-8859-15')

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

        term_str = unicode("A La MaiSon", 'iso-8859-15')

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

        term_str = unicode("������ � ��", 'iso-8859-15')

        reader = PyLucene.StringReader(term_str)

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        res = [u'aaeeee', u'aaeee', u'i', u'ou']
        tokens.sort()
        res.sort()
        self.assertEquals(tokens, res)

    def test_french_case_accents_stemming(self):
        # This is to make sure that case, accent and endings all result
        # in the same index word.
        search_words = ('d�ontologie',
                        'D�ontologie',
                        'DEONTOLOGIE',
                        'deontologie',
                        'Deontologie',
                        'DEONTOLOGIES',
                        'd�ontologies',
                        'D�ontologies',
                        'DEONTOLOGI',
                        'd�ontologi',
                        'D�ontologi',
                        'DEONTOLOGIS',
                        'd�ontologis',
                        'D�ontologis',
                        'dEONTOLOGIE',
                    )

        a = NXFrenchAnalyzer()

        for word in search_words:
            term_str = unicode(word, 'iso-8859-15')

            reader = PyLucene.StringReader(term_str)
            tokens = a.tokenStream('', reader)
            tokens = [token.termText() for token in tokens]
            self.assertEquals(tokens, [u'deontolog'])


    def testFrenchSeparators1(self):
        a = NXFrenchAnalyzer()
        term_str = unicode("grand-m�re", 'iso-8859-15')
        reader = PyLucene.StringReader(term_str)
        tokens = [token.termText() for token in a.tokenStream('', reader)]
        res = [u'grand-mere', u'grand', u'mer']
        tokens.sort()
        res.sort()
        self.assertEquals(tokens, res)

    def testFrenchSeparators2(self):
        a = NXFrenchAnalyzer()
        term_str = unicode("midi-pyr�n�e", 'iso-8859-15')
        reader = PyLucene.StringReader(term_str)
        tokens = [token.termText() for token in a.tokenStream('', reader)]
        res = [u'midi-pyrenee', u'mid', u'pyren', u'pyrene']
        tokens.sort()
        res.sort()
        self.assertEquals(tokens, res)

    def testFrenchSeparators3(self):
        a = NXFrenchAnalyzer()
        term_str = unicode("Franche-Comt�", 'iso-8859-15')
        reader = PyLucene.StringReader(term_str)
        tokens = [token.termText() for token in a.tokenStream('', reader)]
        res = [u'franche-comte', u'franch', u'comt']
        tokens.sort()
        res.sort()
        self.assertEquals(tokens, res)

    def testFrenchSearchAnalyzer1(self):
        a = NXFrenchSearchAnalyzer()
        term_str = unicode("midi-pyr�n�e", 'iso-8859-15')
        reader = PyLucene.StringReader(term_str)
        tokens = [token.termText() for token in a.tokenStream('', reader)]
        res = [u'midi-pyrenee']
        tokens.sort()
        res.sort()
        self.assertEquals(tokens, res)

    def test_french_misc_00(self):
        term_str = unicode("l'enfant", 'iso-8859-15')
        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(tokens_fr, ['enfant'])

    def test_french_misc_01(self):
        term_str = unicode("d�bat", 'iso-8859-15')
        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(tokens_fr, ['debat'])

    def test_french_misc_02(self):
        term_str = unicode("chant�e", 'iso-8859-15')
        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(tokens_fr, ['chant', 'chante'])

    def test_french_misc_021(self):
        term_str = unicode("chant�", 'iso-8859-15')
        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(tokens_fr, ['chant'])

    def test_french_misc_03(self):
        term_str = unicode("Paris", 'iso-8859-15')
        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(tokens_fr, ['par'])

    def test_french_misc_04(self):
        term_str = unicode("hame�on", 'iso-8859-15')
        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(tokens_fr, ['hamecon'])

    def test_french_misc_05(self):
        term_str = unicode("�uvre", 'iso-8859-15')
        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(tokens_fr, ['oeuvr'])

    def test_french_misc_06(self):
        term_str = unicode("�gyrine", 'iso-8859-15')
        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens_fr = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(tokens_fr, ['aegyrin'])


    def testUrlAnalyzer1(self):
        term_str = unicode("http://www.cite-musique.fr", 'iso-8859-15')
        a = NXUrlAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens = [token.termText() for token in a.tokenStream('', reader)]
        res = [u'http://www.cite-musique.fr',
               u'www.cite-musique.fr',
               u'cite-musique.fr',
               u'cite-musique',
               u'cite', u'musique', u'fr']
        tokens.sort()
        res.sort()
        self.assertEquals(tokens, res)

    def testUrlAnalyzer2(self):
        term_str = unicode("http://www.epoch-net.org/", 'iso-8859-15')
        a = NXUrlAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens = [token.termText() for token in a.tokenStream('', reader)]
        res = [u'http://www.epoch-net.org/',
               u'www.epoch-net.org',
               u'epoch-net.org',
               u'epoch-net',
               u'epoch', u'net', u'org']
        tokens.sort()
        res.sort()
        self.assertEquals(tokens, res)

    def testUrlAnalyzer3(self):
        term_str = unicode("http://www.culture.gouv.fr/culture/fouilles/accueil.html",
                           'iso-8859-15')

        a = NXUrlAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens = [token.termText() for token in a.tokenStream('', reader)]
        res = [u'http://www.culture.gouv.fr/culture/fouilles/accueil.html',
               u'www.culture.gouv.fr/culture/fouilles/accueil.html',
               u'culture.gouv.fr/culture/fouilles/accueil.html',
               u'culture', u'gouv', u'fr', u'fouilles', u'accueil',
               u'html']
        tokens.sort()
        res.sort()
        self.assertEquals(tokens, res)

        # Testing the next call on the token stream
        a = NXUrlAnalyzer()
        reader = PyLucene.StringReader(term_str)
        stream = a.tokenStream('', reader)
        token = stream.next()
        while token:
            token = stream.next()
        self.assertEquals(token, None)

    def testUrlSearchAnalyzer1(self):
        term_str = unicode("http://www.cite-musique.fr", 'iso-8859-15')
        a = NXUrlSearchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens = [token.termText() for token in a.tokenStream('', reader)]
        res = [u'http://www.cite-musique.fr']
        tokens.sort()
        res.sort()
        self.assertEquals(tokens, res)

    def test_french_complet(self):
        text = "Test n�67-236: Les parts sociales ne peuvent �tre donn�es en "\
               "nantissement par des auteurs. ? "\
               "Je suis un enfant de l'ind�pendance. "\
               "Je cherche forcement bien chant� !"
        term_str = unicode(text, 'iso-8859-15')
        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader(term_str)
        tokens = [token.termText() for token in a.tokenStream('', reader)]
        res = [u'test', u'67-236', u'part', u'social',
               u'peuvent', u'donne', u'don', u'nant', u'auteur', u'suis', u'enfant',
               u'independ', u'cherch', u'forc', u'bien', u'chant']
        tokens.sort()
        res.sort()
        self.assertEquals(tokens, res)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NXFrenchAnalyzerTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
