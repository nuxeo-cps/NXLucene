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

import PyLucene

class NXFrenchAnalyzer(object):

    FRENCH_STOP_WORDS = [
    "a", "afin", "ai", "ainsi", "apr�s", "attendu", "au", "aujourd", "auquel", "aussi",
    "autre", "autres", "aux", "auxquelles", "auxquels", "avait", "avant", "avec", "avoir",
    "c", "car", "ce", "ceci", "cela", "celle", "celles", "celui", "cependant", "certain",
    "certaine", "certaines", "certains", "ces", "cet", "cette", "ceux", "chez", "ci",
    "combien", "comme", "comment", "concernant", "contre", "d", "dans", "de", "debout",
    "dedans", "dehors", "del�", "depuis", "derri�re", "des", "d�sormais", "desquelles",
    "desquels", "dessous", "dessus", "devant", "devers", "devra", "divers", "diverse",
    "diverses", "doit", "donc", "dont", "du", "duquel", "durant", "d�s", "elle", "elles",
    "en", "entre", "environ", "est", "et", "etc", "etre", "eu", "eux", "except�", "hormis",
    "hors", "h�las", "hui", "il", "ils", "j", "je", "jusqu", "jusque", "l", "la", "laquelle",
    "le", "lequel", "les", "lesquelles", "lesquels", "leur", "leurs", "lorsque", "lui", "l�",
    "ma", "mais", "malgr�", "me", "merci", "mes", "mien", "mienne", "miennes", "miens", "moi",
    "moins", "mon", "moyennant", "m�me", "m�mes", "n", "ne", "ni", "non", "nos", "notre",
    "nous", "n�anmoins", "n�tre", "n�tres", "on", "ont", "ou", "outre", "o�", "par", "parmi",
    "partant", "pas", "pass�", "pendant", "plein", "plus", "plusieurs", "pour", "pourquoi",
    "proche", "pr�s", "puisque", "qu", "quand", "que", "quel", "quelle", "quelles", "quels",
    "qui", "quoi", "quoique", "revoici", "revoil�", "s", "sa", "sans", "sauf", "se", "selon",
    "seront", "ses", "si", "sien", "sienne", "siennes", "siens", "sinon", "soi", "soit",
    "son", "sont", "sous", "suivant", "sur", "ta", "te", "tes", "tien", "tienne", "tiennes",
    "tiens", "toi", "ton", "tous", "tout", "toute", "toutes", "tu", "un", "une", "va", "vers",
    "voici", "voil�", "vos", "votre", "vous", "vu", "v�tre", "v�tres", "y", "�", "�a", "�s",
    "�t�", "�tre", "�"
    ]

    FRENCH_EXCLUDED_WORDS = []

    def tokenStream(self, fieldName, reader):
        result = PyLucene.StandardFilter(reader)
        result = PyLucene.StopFilter(result, self.FRENCH_STOP_WORDS)
        result = PyLucene.FrenchStemFilter(result, self.EXCLUDED_WORDS)
        result = PyLucene.LowerCaseFilter(result)
        return result


analyzers_map = {
    # XXX not complete
    'standard' : PyLucene.StandardAnalyzer(),
#    'french'   : PyLucene.FrenchAnalyzer(),
     'french'   : NXFrenchAnalyzer(),
    }

def getAnalyzerById(analyzer_id):
    if not analyzer_id.lower() in analyzers_map.keys():
        analyzer_id = 'standard'
    return analyzers_map.get(analyzer_id)

def getPerFieldAnalyzerWrapper(default_analyzer=None):
    if default_analyzer is None:
        default_analyzer = PyLucene.StandardAnalyzer()
    return PyLucene.PerFieldAnalyzerWrapper(default_analyzer)
