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

class NXFrenchAnalyzerTestCase(unittest.TestCase):

    def test_no_french_specifics(self):

        a = NXFrenchAnalyzer()
        reader = PyLucene.StringReader('Un test')

        tokens = [token.termText() for token in a.tokenStream('', reader)]
        self.assertEquals(
            tokens, [u'un', u'test'])

    def test_french_samples_pp(self):

        a = NXFrenchAnalyzer()

        term_str = unicode("chanté", 'latin-1')
        
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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NXFrenchAnalyzerTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
