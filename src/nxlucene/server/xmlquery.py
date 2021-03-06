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

import base64
import logging

import cElementTree as etree

import zope.interface

from nxlucene.server.interfaces import IXMLQuery
from nxlucene.server.interfaces import IXMLSearchQuery

logger = logging.getLogger('nxlucene.xmlquery')

class XMLQuery(object):

    zope.interface.implements(IXMLQuery)

    def __init__(self, xml_stream='', encoding='utf-8'):

        self._xml_stream = xml_stream
        self._encoding = encoding
        self._fields = ()

        if not xml_stream:
            return

        doc = etree.XML(self._xml_stream)

        fields = doc.findall('fields/field')
        for field in fields:

            id_ = field.attrib.get('id', '').strip()
            if not id_:
                continue

            value = ''

            if field.text:

                # Deal with base64 if encoded
                try:
                    value = base64.b64decode(field.text)
                except:
                    value = field.text.strip()

                # Convert to unicode.
                try:
                    value = unicode(value)
                except UnicodeError:
                    try:
                        value = unicode(value, self._encoding)
                    except UnicodeError:
                        # BBB
                        value = unicode(value, 'iso-8859-15')

            logger.debug('Found id=%s with value=%s' % (id_, value))
            self._fields += ({
                'id' : id_,
                'attribute' : field.attrib.get('attribute', '').strip(),
                'type' : field.attrib.get('type', '').strip(),
                'value': value,
                'analyzer' : field.attrib.get('analyzer', 'standard').strip()
                },)

    def getFields(self):
        return self._fields

    def getFieldNames(self):
        return tuple([x['id'] for x in self._fields])


class XMLSearchQuery(object):

    zope.interface.implements(IXMLSearchQuery)

    def __init__(self, xml_stream=''):

        self.xml_stream = xml_stream

        self._analyzer = 'standard'

        self._return_fields = []
        self._search_fields = []
        self._search_options = {}

        self._operator = 'AND'

        self._start = 0
        self._results = 10

        if not xml_stream:
            return

        doc = etree.XML(xml_stream.encode('utf-8'))


        #
        # Analyzer
        #

        analyzers = doc.findall('analyzer')
        if analyzers:
            self._analyzer = unicode(analyzers[0].text.strip())

        #
        # return fields
        #

        return_fields = doc.findall('return_fields/field')
        for return_field in return_fields:
            if return_field.text:
                self._return_fields.append(unicode(return_field.text.strip()))

        #
        # fields
        #

        fields = doc.findall('fields/field')
        for field in fields:
            if field.attrib.get('id') and field.attrib.get('value'):
                mapping = {
                    'id' : unicode(field.attrib['id'].strip()),
                    'value' : unicode(field.attrib['value'].strip()),
                    'type' : unicode(field.attrib.get('type', '').strip()),
                    'analyzer' : unicode(field.attrib.get('analyzer',
                                                          'standard')).strip(),
                    }

                if field.attrib.get('usage') is not None:
                    mapping['usage'] = unicode(field.attrib['usage']).strip()

                condition = field.attrib.get('condition')
                if condition is not None:
                    mapping['condition'] = unicode(condition.strip())

                usage = field.attrib.get('usage')
                if usage is not None:
                    mapping['usage'] = usage.strip()
                self._search_fields.append(mapping)

        #
        # Batching
        #

        batch = doc.find('batch')
        if batch is not None:
            for attr in ('start', 'size'):
                self._search_options[attr] = batch.attrib.get(attr)

        #
        # sort options
        #

        sort = doc.find('sort')
        if sort is not None:
            for tagname in ('sort-on', 'sort-limit', 'sort-order'):
                elt = sort.find(tagname)
                if elt is not None:
                    self._search_options[tagname] = elt.text

        #
        # Query operator
        #

        elt = doc.find('operator')
        if elt is not None:
            self._search_options['operator'] = elt.text

    def getReturnFields(self):
        return tuple(self._return_fields)

    def getSearchFields(self):
        # Add path field type at the end

        _fields = []
        _ends = []
        for each in self._search_fields:
            if each['type'].lower() == 'path':
                _ends.append(each)
            else:
                _fields.append(each)

        for each in _ends:
            _fields.append(each)

        return tuple(_fields)

    def getSearchOptions(self):
        return self._search_options

    def getAnalyzerType(self):
        return self._analyzer
