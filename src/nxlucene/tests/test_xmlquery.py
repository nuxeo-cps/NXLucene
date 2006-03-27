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

from zope.interface.verify import verifyClass

from nxlucene.interfaces import IXMLQuery
from nxlucene.interfaces import IXMLSearchQuery

from nxlucene.xmlquery import XMLQuery
from nxlucene.xmlquery import XMLSearchQuery

class XMLQueryTestCase(unittest.TestCase):

    def test_implementation(self):
        verifyClass(IXMLQuery, XMLQuery)

    def test_O1_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field/>
          </fields>
        </doc>"""

        istream = XMLQuery(stream)
        self.assertEqual(istream.getFields(), ())

    def test_O2_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name'/>
          </fields>
        </doc>"""

        istream = XMLQuery(stream)
        self.assertEqual(istream.getFields(),
                         ({'attribute': '', 'type': '', 'id': 'name', 'value': ''},)
                         )

    def test_O3_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name' attribute="__name__"/>
          </fields>
        </doc>"""

        istream = XMLQuery(stream)
        self.assertEqual(istream.getFields(),
                        ({'attribute': '__name__', 'type': '', 'id': 'name', 'value': ''},)
                         )

    def test_O4_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name' attribute="__name__"/>
          </fields>
        </doc>"""

        istream = XMLQuery(stream)
        self.assertEqual(istream.getFields(),
                          ({'attribute': '__name__', 'type': '', 'id': 'name', 'value': ''},)
                         )

    def test_O5_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name' attribute="__name__" type="text"/>
          </fields>
        </doc>"""

        istream = XMLQuery(stream)
        self.assertEqual(istream.getFields(),
                         ({'attribute': '__name__', 'type': 'text', 'id': 'name', 'value': ''},)
                         )

    def test_O6_stream(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id='name' attribute="__name__" type="text"/>
            <field id='attr' attribute="attr" type="text"/>
          </fields>
        </doc>"""

        istream = XMLQuery(stream)
        self.assertEqual(istream.getFields(),
                         ({'attribute': '__name__', 'type': 'text', 'id': 'name', 'value': ''},
                          {'attribute': 'attr', 'type': 'text', 'id': 'attr', 'value': ''},)
                         )

    def test_empty_stream(self):
        stream = ''
        istream = XMLQuery(stream)

class XMLSearchQueryTestCase(unittest.TestCase):

    def test_implementation(self):
        verifyClass(IXMLSearchQuery, XMLSearchQuery)

    def test_empty_stream(self):
        stream = ''
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(), ())

    def test_empty_doc_stream(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(), ())

    def test_with_analyzer(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <analyzer>myanalyzer</analyzer>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'myanalyzer')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(), ())

    def test_with_analyzer_strip(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <analyzer>   myanalyzer
          </analyzer>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'myanalyzer')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(), ())

    def test_with_empty_return_fields(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <return_fields/>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(), ())

    def test_with_return_fields_invalid(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <return_fields>
            <field></field>
          </return_fields>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(), ())

    def test_with_return_fields_valid(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <return_fields>
            <field>name</field>
            <field>attr1</field>
            <field>attr2</field>
          </return_fields>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ('name', 'attr1', 'attr2'))
        self.assertEqual(istream.getSearchFields(), ())

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
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ('name', 'attr1', 'attr2'))
        self.assertEqual(istream.getSearchFields(), ())

    def test_with_fields_empty(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields/>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(), ())

    def test_with_fields_invalid(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field/>
          </fields>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(), ())

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field id='name'/>
          </fields>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(), ())

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field value='foo'/>
          </fields>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(), ())

    def test_with_fields_(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field id='name' value='foo'/>
          </fields>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(),
                         ({'type': u'', 'condition': u'', 'id': u'name', 'value': u'foo'},))

    def test_with_fields_strip(self):
        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field id=' name  ' value='  foo  '/>
          </fields>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(),
                         ({'type': u'', 'condition': u'', 'id': u'name', 'value': u'foo'},))

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <fields>
            <field
              id=' name  '
              value='  foo  '/>
          </fields>
        </search>"""
        istream = XMLSearchQuery(stream)
        self.assertEqual(istream.getAnalyzerType(), 'standard')
        self.assertEqual(istream.getReturnFields(), ())
        self.assertEqual(istream.getSearchFields(),
                         ({'type': u'', 'condition': u'', 'id': u'name', 'value': u'foo'},))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLQueryTestCase))
    suite.addTest(unittest.makeSuite(XMLSearchQueryTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
