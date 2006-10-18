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
"""Weblucene functionnal tests against an xml-rpc server instance.

The idea here is to use this testcase to generate preformance metrics.

$Id$
"""

import unittest

from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.Lipsum import Lipsum

INDEX_SIMPLE_DOCUMENT = "Index a simple document"
SEARCH_DOCUMENT = "Search a document"

class WebLucene(FunkLoadTestCase):
    """Testing WebLucene

    This testcase uses WebLucene.conf
    """

    def setUp(self):
        self.logd("setUp.")
        self.weblucene_url = self.conf_get('main', 'url')
        # To generate words
        self._lipsum = Lipsum()

    def test_simple_document_indexation(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <doc>
          <fields>
            <field id="name" attribute="name">
              %s
            </field>
          </fields>
        </doc>""" % self._lipsum.getWord()

        uid = self._lipsum.getWord()
        self.xmlrpc(self.weblucene_url, 'indexDocument',
                    params=(uid, stream), description=INDEX_SIMPLE_DOCUMENT)

    def test_simple_search(self):

        stream = """<?xml version="1.0" encoding="UTF-8"?>
        <search>
          <analyzer>standard</analyzer>
          <return_fields>
            <field>uid</field>
            <field>name</field>
          </return_fields>
          <fields>
            <field
              id="uid"
              value="1"/>
            <field
              id="name"
              value="foo"/>
          </fields>
        </search>"""
              
        self.xmlrpc(self.weblucene_url, 'search',
                    params=(stream,), description=SEARCH_DOCUMENT)

    def tearDown(self):
        self.logd("tearDown.")

if __name__ in ('main', '__main__'):
    unittest.main()
    
