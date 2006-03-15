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
"""NXLucene core server definition.

$Id$
"""

import os
import threading
import logging
import PyLucene
import time

import zope.interface
from interfaces import ILuceneServer

from indexer import LuceneIndexer
from reader import LuceneReader
from searcher import LuceneSearcher

import rss.resultset

import nxlucene.query

class LuceneServer(object):
    """Lucene server.
    """

    zope.interface.implements(ILuceneServer)

    def __init__(self, store_dir):
        self.store_dir = store_dir
        self.write_lock = threading.Lock()
        self.log = logging.getLogger("LuceneServer")

    def __len__(self):
        reader = self.getReader()
        if reader is None:
            return 0
        return reader.get().numDocs()

    def getStore(self, creation=False):
        if not os.path.exists(self.store_dir):
            creation = True
        return PyLucene.FSDirectory.getDirectory(self.store_dir, creation)

    def getIndexer(self):
        creation = False
        if not os.path.exists(self.store_dir):
            creation = True
        analyzer = PyLucene.StandardAnalyzer()
        return LuceneIndexer(self.store_dir, creation, analyzer)

    def getSearcher(self):
        if not os.path.exists(self.store_dir):
            return None
        return LuceneSearcher(self.store_dir)

    def getReader(self):
        if not os.path.exists(self.store_dir):
            return None
        try:
            reader = LuceneReader(self.store_dir)
        except PyLucene.JavaError:
            # Store is not initialized yet.
            reader = None
        return reader

    def getDocumentByUID(self, uid):
        res = None
        searcher = self.getSearcher()
        if searcher is None:
            return res
        query = PyLucene.TermQuery(PyLucene.Term('uid', unicode(uid)))
        hits = list(searcher.get().search(query))
        if hits:
            res = hits[0][1]
        searcher.close()
        if res:
            self.log.debug("FOUND document with uid=%s" % str(uid))
        else:
            self.log.debug("Document with uid=%s NOT FOUND" % str(uid))
        return res

    def optimize(self, indexer=None):
        self.log.debug("Optimize indexes store")
        close = False
        if indexer is None:
            indexer = self.getIndexer().get()
            close = True
        self.write_lock.acquire()
        indexer.optimize()
        if close:
            indexer.close()
        self.write_lock.release()
        return True

    def clean(self):

        self.write_lock.acquire()

        indexer = LuceneIndexer(self.store_dir, creation=True)
        indexer.close()

        self.write_lock.release()

        self.log.info("Indexes Store has been cleaned up")
        return True

    def indexDocument(self, uid, query_instance):

        self.write_lock.acquire()

        # Check if we got an existing document given this UID.
        doc = self.getDocumentByUID(uid)
        delete_existing = doc and True or False

        # In case we need to update we'll have to take care of the
        # existing fields.
        existing_fields = ()

        if doc is not None:
            self.log.debug("FOUND document with uid=%s to update" % str(uid))
            # Keep fields for update purpose.
            existing_fields = doc.fields()
        else:
            self.log.debug(
                "Document with uid=%s does not exist yet" % str(uid))

        # Create a new document instance.
        doc = PyLucene.Document()
        doc.add(PyLucene.Field.Keyword('uid', unicode(uid)))

        for field in query_instance.getFields():

            field_id   = field['id']
            field_value = unicode(field['value'])
            field_type  = field['type']

            self.log.debug(
                "Adding Field on doc with id=%s with value %s of type %s"
                % (field_id, field_value, field_type))

            if field_type == 'Text':
                doc.add(PyLucene.Field.Text(field_id, field_value))

            elif field_type == 'UnStored':
                doc.add(PyLucene.Field.UnStored(field_id, field_value))

            elif field_type == 'UnIndexed':
                doc.add(PyLucene.Field.UnIndexed(field_id, field_value))

            elif field_type == 'Keyword':
                doc.add(PyLucene.Field.Keyword(field_id, field_value))

            elif field_type == 'Date':
                # The Date format must be an ISO one. This is a
                # requierment right now.  XXX check this is the case ?

                iso = 'yyyy-MM-dd HH:mm:ss'

                try:
                    date_formated = PyLucene.SimpleDateFormat(
                        iso).parse(field_value)
                except PyLucene.JavaError:
                    break

                try:
                    date_field = PyLucene.DateField.dateToString(date_formated)
                except PyLucene.JavaError:
                    # java.lang.RuntimeException: time too early
                    # Shoud be > 1970
                    date_formated = PyLucene.SimpleDateFormat(
                        iso).parse('1970-01-01 00:00:00')
                    date_field = PyLucene.DateField.dateToString(date_formated)

                doc.add(PyLucene.Field.Keyword(field_id, date_field))

            elif field_type == 'Path':
                # XXX implement me.
                doc.add(PyLucene.Field.Keyword(field_id, field_value))

            else:
                self.log.info(
                    "Field configuration does not match for "
                    "id=%s with value %s of type %s "
                    "Adding a PyLucene.Field unindexed but stored"
                    % (field_id, field_value, field_type))
                doc.add(
                    PyLucene.Field(field_id, field_value, True, False, False)
                    )

        # Update
        for field in existing_fields:
            if (field.name() not in
                [x['attribute'] for x in  query_instance.getFields()] and
                field.name() != 'uid'):
                doc.add(field)

        # We got to remove the document from the index first.
        # http://wiki.apache.org/jakarta
        # -lucene/LuceneFAQ#head-917dd4fc904aa20a34ebd23eb321125bdca1dea2
        if delete_existing:
            self.unindexDocument(uid, lock=False)

        # Merge indexes
        indexer = self.getIndexer()
        writer = indexer.get()
        writer.addDocument(doc)
#        writer.optimize()
        indexer.close()

        self.write_lock.release()

        return True

    def unindexDocument(self, uid, lock=True):

        cerror = True

        reader = self.getReader()
        if reader is None:
            return False

        if lock:
            self.write_lock.acquire()

        ireader = reader.get()

        t = PyLucene.Term('uid', unicode(uid))
        ireader.deleteDocuments(t)

        if ireader.hasDeletions():
            self.log.info("UNINDEXED document with uid=%s" % str(uid))
        else:
            self.log.info("CANNOT UNINDEXED document with uid=%s"
                          "NOT FOUND" % str(uid))
            cerror = False

        reader.close()

        if lock:
            self.write_lock.release()

        return cerror

    def reindexDocument(self, uid, query_instance):
        self.indexDocument(uid, query_instance)

    #
    # API : SEARCH
    #

    def search(self, query_str, **kw):
        raise NotImplementedError

    def searchQuery(self, return_fields=(), search_fields=()):

        # XXX make this configurable
        start = 0
        stop = 10

        # uid will be returned automatically
        return_fields = ('uid',) + return_fields

        results = rss.resultset.ResultSet()

        # This behavior is not allowed.
        if not search_fields:
            return results.getStream()

        # Probably no indexes are created yet.
        searcher = self.getSearcher()
        if not searcher:
            return results.getStream()

        #
        # Construct the query.
        #

        query = PyLucene.BooleanQuery()
        for field in search_fields:

            index = field['id']
            value = field['value']
            condition = field.get('condition', 'OR')

            term = PyLucene.Term(index, unicode(value.lower()))

            # XXX make the following tests configurable with fiel
            # types.

            if index == 'path':
                subquery = PyLucene.PrefixQuery(term)
            else:
                subquery = PyLucene.TermQuery(term)

            default_clause = PyLucene.BooleanClause.Occur.MUST
            query.add(
                subquery,
                nxlucene.query.boolean_clauses_map.get(
                condition, default_clause))
                
        self.log.debug('query %s' % query.toString())

        tstart = time.time()
        
        hits = searcher.get().search(query)

        tstop = time.time()
        self.log.debug("Time to find return results %s" % str(tstop-tstart))

        # XXX Change this it's sucky...
        tstart = time.time()
        hits = list(hits)[start:stop]
        tstop = time.time()
        self.log.debug("Time to find get results %s" % str(tstop-tstart))

        uids = []
        for i, doc in hits:
            table = dict([(field.name(), field.stringValue())
                          for field in doc
                          if unicode(field.name()) in return_fields])
            uid = table['uid']
            if uid not in uids:
                uids.append(uid)
                del table['uid']
#                self.log.debug("match for %s %s" %(uid, str(table)))
                results.addItem(uid, table)

        searcher.close()
        return results.getStream()
