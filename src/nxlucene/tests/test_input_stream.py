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
"""XML Input Stream tests

$Id$
"""

import unittest

from nxlucene.stream import XMLInputStream
from nxlucene.stream import XMLQueryInputStream

class InputStreamTestCase(unittest.TestCase):

    def test_O1_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field/>
          </fields>
        </doc>"""

        istream = XMLInputStream(stream)
        self.assertEqual(istream.getFields(), {})

    def test_O2_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name'/>
          </fields>
        </doc>"""

        istream = XMLInputStream(stream)
        self.assertEqual(istream.getFields(),
                         {u'name':
                          {'fulltext': '',
                           'type': '',
                           'attribute': '',
                           'value':''}})

    def test_O3_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name' attribute="__name__"/>
          </fields>
        </doc>"""

        istream = XMLInputStream(stream)
        self.assertEqual(istream.getFields(),
                         {u'name':
                          {'fulltext': '',
                           'type': '',
                           'attribute': u'__name__',
                           'value':''}})

    def test_O4_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name' attribute="__name__" fulltext="True"/>
          </fields>
        </doc>"""

        istream = XMLInputStream(stream)
        self.assertEqual(istream.getFields(),
                         {u'name':
                          {'fulltext': u'True',
                           'type': '',
                           'attribute': u'__name__',
                           'value':''}})

    def test_O5_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name' attribute="__name__" fulltext="True" type="text"/>
          </fields>
        </doc>"""

        istream = XMLInputStream(stream)
        self.assertEqual(istream.getFields(),
                         {u'name':
                          {'fulltext': u'True',
                           'type': u'text',
                           'attribute': u'__name__',
                           'value':''}})

    def test_O6_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name' attribute="__name__" fulltext="True" type="text"/>
            <field id='attr' attribute="attr" fulltext="False" type="text"/>
          </fields>
        </doc>"""

        istream = XMLInputStream(stream)
        self.assertEqual(istream.getFields(),
                         {u'name':
                          {'fulltext': u'True',
                           'type': u'text',
                           'attribute': u'__name__',
                           'value':''},
                          u'attr':
                          {'fulltext': u'False',
                           'type': u'text',
                           'attribute': u'attr',
                           'value':''}}
                         )

    def test_empty_stream(self):
        stream = ''
        istream = XMLInputStream(stream)

    def test_getAttr(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name' attribute="__name__" fulltext="True" type="text"/>
            <field id='attr' attribute="attr" fulltext="False" type="text"/>
          </fields>
        </doc>"""
        istream = XMLInputStream(stream)
        attrs = istream.getAttributNames()
        self.assertEqual(attrs, ['__name__', 'attr'])

class QueryStreamTestCase(unittest.TestCase):

    def test_empty_stream(self):
        stream = ''
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {})

    def test_empty_doc_stream(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {})

    def test_with_analyzer(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <analyzer>myanalyzer</analyzer>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'myanalyzer')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {})

    def test_with_analyzer_strip(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <analyzer>   myanalyzer
          </analyzer>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'myanalyzer')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {})

    def test_with_empty_return_fields(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <return_fields/>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {})

    def test_with_return_fields_invalid(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <return_fields>
            <field></field>
          </return_fields>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {})

    def test_with_return_fields_valid(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <return_fields>
            <field>name</field>
            <field>attr1</field>
            <field>attr2</field>
          </return_fields>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ('name', 'attr1', 'attr2'))
        self.assertEqual(istream.getKwargs(), {})

    def test_with_return_fields_valid_strip(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <return_fields>
            <field>name   </field>
            <field>   attr1</field>
            <field>
            attr2   </field>
          </return_fields>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ('name', 'attr1', 'attr2'))
        self.assertEqual(istream.getKwargs(), {})

    def test_with_fields_empty(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields/>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {})

    def test_with_fields_invalid(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field/>
          </fields>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {})

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field id='name'/>
          </fields>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {})

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field value='foo'/>
          </fields>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {})

    def test_with_fields_(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field id='name' value='foo'/>
          </fields>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {u'name': u'foo'})

    def test_with_fields_strip(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field id=' name  ' value='  foo  '/>
          </fields>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {u'name': u'foo'})

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field
              id=' name  '
              value='  foo  '/>
          </fields>
        </search>"""
        istream = XMLQueryInputStream(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getKwargs(), {u'name': u'foo'})

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InputStreamTestCase))
    suite.addTest(unittest.makeSuite(QueryStreamTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
