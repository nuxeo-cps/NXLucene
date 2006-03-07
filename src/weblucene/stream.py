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
"""Stream

$Id$
"""

try:
    import cElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

class XMLInputStream(object):

    def __init__(self, xml_stream=''):

        self._xml_stream = xml_stream
        self._fields = {}

        if not xml_stream:
            return

        doc = etree.XML(self._xml_stream)

        fields = doc.findall('fields/field')

        for field in fields:
            # TODO Exclude id_ from the self namespace
            id_ = field.attrib.get('id', '').strip()
            if id_:
                value = ''
                if field.text:
                    value = field.text.strip()
                self._fields[id_] = {
                    'attribute' : field.attrib.get('attribute', '').strip(),
                    'fulltext' : field.attrib.get('fulltext', '').strip(),
                    'type' : field.attrib.get('type', '').strip(),
                    'value': value,
                    }

        for k, v in self._fields.items():
            setattr(self, k, v['value'])

    def getFields(self):
        return self._fields

    def getAttributNames(self):
        attributs = []
        for v in self.getFields().values():
            if v['attribute']:
                attributs.append(v['attribute'])
        return attributs

class XMLQueryInputStream(object):
    """XML Stream for search query
    """

    def __init__(self, xml_stream=''):

        self.xml_stream = xml_stream
        self._return_fields = []
        self._kwargs = {}
        self._analyzer = ''

        if not xml_stream:
            return

        doc = etree.XML(xml_stream)

        # Analyzer
        analyzers = doc.findall('analyzer')
        if analyzers:
            self._analyzer = unicode(analyzers[0].text.strip())

        # return fields
        return_fields = doc.findall('return_fields/field')
        for return_field in return_fields:
            if return_field.text:
                self._return_fields.append(unicode(return_field.text.strip()))

        # fields
        fields = doc.findall('fields/field')
        for field in fields:
            if field.attrib.get('id') and field.attrib.get('value'):
                self._kwargs[
                    unicode(field.attrib['id'].strip())
                    ] = unicode(field.attrib['value'].strip())

    def getAnalyzerType(self):
        if self._analyzer:
            return self._analyzer
        return 'standard'

    def getReturnFields(self):
        return tuple(self._return_fields)

    def getKwargs(self):
        return self._kwargs
