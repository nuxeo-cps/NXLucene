# Copyright (C) 2006-2007, Nuxeo SAS <http://www.nuxeo.com>
# Authors:
# Julien Anguenot <ja@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
# Benoit Delbosc <bdelbosc@nuxeo.com>
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
import shutil
import sys
import threading
import logging
import PyLucene
import time

import zope.interface
from nxlucene.server.interfaces import ILuceneServer

from nxlucene.index.indexer import LuceneIndexer
from nxlucene.index.reader import LuceneReader
from nxlucene.search.searcher import LuceneSearcher

import nxlucene.rss.resultset

import nxlucene.document
import nxlucene.search.query
import nxlucene.analysis

from nxlucene.server.store.registry import getRegistry

# support 64-bit architectures
MAXINT = int(2**31-1)

class LuceneServer(object):
    """Lucene server.
    """

    zope.interface.implements(ILuceneServer)

    def __init__(self, store_dir, store_backened_id='FSDirectory'):
        self.log = logging.getLogger("NXLucene.core")

        self.store_dir = store_dir
        self.store_backened_id = store_backened_id
        self.write_lock = threading.Lock()

        self.log.info("Using %s as a store backened.........." %
                      self.store_backened_id)

    def __len__(self):
        # We need it since we will IndexReader write a lock file.
        self.write_lock.acquire()
        reader = self.getReader()
        if reader is None:
            self.write_lock.release()
            return 0
        len_ = reader.get().numDocs()
        reader.close()
        self.write_lock.release()
        return len_

    def getStore(self, creation=False):

        if creation:
            if os.path.exists(self.store_dir):
                shutil.rmtree(self.store_dir)
            os.makedirs(self.store_dir)

        self.log.info("Using backened=%s in dir=%s with creation_flag=%s" % (
            self.store_backened_id, self.store_dir, str(creation)))

        return getRegistry().makeInstance(self.store_backened_id,
                                          self.store_dir, creation)

    def getIndexer(self, creation=False, analyzer=None):
        if not os.path.exists(self.store_dir):
            creation = True
        return LuceneIndexer(self.getStore(creation), creation, analyzer)

    def getSearcher(self):
        if not os.path.exists(self.store_dir):
            return None
        return LuceneSearcher(self.getStore(False))

    def getReader(self):
        if not os.path.exists(self.store_dir):
            return None
        try:
            reader = LuceneReader(self.getStore(False))
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

        # __del__ will be called  by the GC
        searcher.close()
        if res:
            self.log.debug("FOUND document with uid=%s" % str(uid))
        else:
            self.log.debug("Document with uid=%s NOT FOUND" % str(uid))
        return res

    def optimize(self, indexer=None):
        self.write_lock.acquire()
        close = False
        if indexer is None:
            indexer = self.getIndexer().get()
            close = True
        self.log.info("Indexes store optimization starts...")
        indexer.optimize()
        self.log.info("Indexes store optimization done...")
        if close:
            indexer.close()
        self.write_lock.release()
        return True

    def clean(self):

        self.write_lock.acquire()

        indexer = self.getIndexer(creation=True)
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

        doc = nxlucene.document.Document(uid)

        # Build a per-field analyzer wrapper we will use with the
        # IndexWriter.
        analyzer = nxlucene.analysis.getPerFieldAnalyzerWrapper()

        for field in query_instance.getFields():

            field_id   = field['id']
            field_value = field['value']
            field_type  = field['type']

            field_analyzer = field.get('analyzer', 'standard')
            if (not field_analyzer or
                field_analyzer.lower() not in
                nxlucene.analysis.analyzers_map.keys()):
                field_analyzer = 'standard'
            field_analyzer = field_analyzer.lower()

            self.log.debug(
                "Adding Field on doc with id=%s with value %s of type %s"
                % (field_id, field_value, field_type))

            if field_type.lower() == 'text':
                doc.add(
                    PyLucene.Field(field_id, field_value,
                                       PyLucene.Field.Store.YES,
                                       PyLucene.Field.Index.TOKENIZED))

            # :XXX: We can't use unstored index since this is amazingly not
            # supported by
            elif field_type.lower() == 'unstored':
                doc.add(PyLucene.Field(field_id, field_value,
                                       PyLucene.Field.Store.NO,
                                       PyLucene.Field.Index.TOKENIZED))

            elif field_type.lower() == 'unindexed':
                doc.add(PyLucene.Field(field_id, field_value,
                                       PyLucene.Field.Store.YES,
                                       PyLucene.Field.Index.NO))

            elif field_type.lower() == 'multikeyword':

                # Force analyzer to keyword here.
                field_analyzer = 'keyword'

                default_separator = '#'

                if '#' in field_value:
                    values = field_value.split('#')
                else:
                    values = [field_value]

                for value in values:
                    doc.add(PyLucene.Field(field_id, value,
                                       PyLucene.Field.Store.YES,
                                       PyLucene.Field.Index.UN_TOKENIZED))

            elif field_type.lower() == 'keyword':
                # Force analyzer to keyword here.
                field_analyzer = 'keyword'
                doc.add(PyLucene.Field(field_id, field_value,
                                       PyLucene.Field.Store.YES,
                                       PyLucene.Field.Index.UN_TOKENIZED))

            elif field_type.lower() == 'date':
                doc.add(PyLucene.Field(field_id, field_value,
                                       PyLucene.Field.Store.YES,
                                       PyLucene.Field.Index.UN_TOKENIZED))

            elif field_type.lower() == 'path':

                # We support both a string path separated by '/' or a
                # list representing the path elements.

                if '/' in field_value:
                    field_value  = field_value.split('/')

                if not isinstance(field_value, list):
                    field_value = [field_value]

                # Path field custom implementation for better
                # performances. Index the path as multiple keywords
                # for all subpaths so that we will be able to match
                # using simple keyword matches.

                for i in xrange(len(field_value)):
                    subpath = '/'.join(field_value[:i+1])
                    doc.add(
                        PyLucene.Field(field_id, subpath,
                                       PyLucene.Field.Store.YES,
                                       PyLucene.Field.Index.UN_TOKENIZED)
                        )

            elif field_type.lower() == 'sort':

                reader = PyLucene.StringReader(field_value)

                # We can't tokenized the field because we woudn't be
                # able to sort against it later on.

                # Let's analyze the value now before storing it.
                a = nxlucene.analysis.sort.NXSortAnalyzer()
                tokens = [token.termText() for token in a.tokenStream('',
                                                                      reader)]
                field_value = ' '.join(tokens)

                doc.add(
                    PyLucene.Field(field_id, field_value,
                                   PyLucene.Field.Store.NO,
                                   PyLucene.Field.Index.UN_TOKENIZED)
                    )

            else:
##                self.log.info(
##                    "Field configuration does not match for "
##                    "id=%s with value %s of type %s "
##                    "Adding a PyLucene.Field unindexed but stored"
##                    % (field_id, field_value, field_type))

                doc.add(
                    PyLucene.Field(field_id, field_value,
                                   PyLucene.Field.Store.YES,
                                   PyLucene.Field.Index.UN_TOKENIZED)
                    )

            analyzer.addAnalyzer(
                field_id,
                nxlucene.analysis.getAnalyzerById(field_analyzer))

#            print field_id, nxlucene.analysis.getAnalyzerById(field_analyzer)
##            self.log.debug("Adding analyzer of type %s for field %s"
##                           % (
##                nxlucene.analysis.getAnalyzerById(field_analyzer),
##                field_id
##                ))

        # Update
        for field in existing_fields:
            if (field.name() not in
                [x['id'] for x in  query_instance.getFields()] and
                field.name() != unicode('uid')):
                self.log.debug("Preserving existing field %s" % field.name())
                doc.add(field)

        # We got to remove the document from the index first.
        # http://wiki.apache.org/jakarta
        # -lucene/LuceneFAQ#head-917dd4fc904aa20a34ebd23eb321125bdca1dea2
        if delete_existing:
            self.unindexDocument(uid, lock=False)

        # Merge indexes
        indexer = self.getIndexer(analyzer=analyzer)
        writer = indexer.get()
##        self.log.debug("Using analyzer %s for adding document"
##                       % str(indexer._analyzer))
        writer.addDocument(doc)
#        writer.optimize()
        indexer.close()

        self.write_lock.release()

        return True

    def unindexDocument(self, uid, lock=True):

        cerror = True

        if lock:
            self.write_lock.acquire()

        reader = self.getReader()
        if reader is None:
            return False

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

    def searchQuery(self, return_fields=(), search_fields=(),
                    search_options={}):

        # Get batching information from search_options.
        start = search_options.get('start', 0)
        try:
            start = int(start)
        except TypeError:
            self.log.debug('Invalid batch start value %s' % repr(start))
            start = 0

        size = search_options.get('size', 100)
        try:
            size = int(size)
        except TypeError:
            self.log.debug('Invalid batch size value %s' % repr(size))
            size = 100

        # Get global request operator and get the clause we will use
        # for the boolean query below.
        default_query_operator = search_options.get('operator', 'AND').upper()
        default_clause = nxlucene.search.query.boolean_clauses_map.get(
            default_query_operator, 'AND',
            )

        # uid will be returned automatically
        if 'uid' not in return_fields:
            return_fields = ('uid',) + return_fields

        # Create a RSS ResultSet instance to stack result items.
        results = nxlucene.rss.resultset.ResultSet()

        # This behavior is not allowed.
        if not search_fields:
            return results.getStream()

        #
        # Construct the query.
        #

        query = PyLucene.BooleanQuery()
        query.setMaxClauseCount(MAXINT)
        date_filter = None

        # will be used to add MatchAllDocs to purely negative queries
        pure_negative = True
        from nxlucene.search.query import boolean_clauses_map
        for field in search_fields:
            index = field['id']
            value = field['value']
            type =  field.get('type', '')
            condition = field.get('condition', 'AND')
            # won't play well with QueryParser stuff
            if condition != 'NOT':
                pure_negative = False
            usage = field.get('usage', '')

            analyzer = field.get('analyzer', 'standard')
            if (not analyzer or
                analyzer.lower() not in nxlucene.analysis.analyzers_map.keys()):
                analyzer = 'standard'
            analyzer = analyzer.lower()

            if type.lower() in ('keyword', 'multikeyword'):
                subquery = PyLucene.BooleanQuery()

                # FIXME use tokenizer... this sucks...
                if '#' in value:
                    values = value.split('#')
                else:
                    values = [value]

                # FIXME use tokenizer... this sucks...
                sub_op = boolean_clauses_map.get('OR')
                for each in values:
                    subquery.add(
                        PyLucene.TermQuery(PyLucene.Term(index, each)), sub_op)
            elif type.lower() == 'path':

                subquery = PyLucene.BooleanQuery()

                # FIXME use tokenizer... this sucks...
                if '#' in value:
                    values = value.split('#')
                else:
                    values = value.split()

                # FIXME use tokenizer... this sucks...
                sub_op = boolean_clauses_map.get('OR')
                for each in values:

                    if each.endswith('*'):
                        # :FIXME:
                        each  = each[:-1]

                    # Remove trailing '/' since we did at indexation time
                    if each[-1] == '/':
                        each  = each[:-1]

                    term = PyLucene.Term(index, each)
                    subquery.add(PyLucene.TermQuery(term), sub_op)

            elif type.lower() == 'date':

                subquery = None

                start_date = end_date = None
                if usage and usage != 'range:min:max':
                    if usage == 'range:min':
                        start_date = PyLucene.Term(index, value)
                    elif usage == 'range:max':
                        end_date = PyLucene.Term(index, value)
                    else:
                        self.log.error("Usage not supported %s" % str(usage))

                    if start_date is not None or end_date is not None:
                        subquery = PyLucene.RangeQuery(
                            start_date, end_date, True)
                else:
                    values = value.split('#')
                    if len(values) == 2:
                        start_date = values[0]
                        end_date = values[1]

                        subquery = PyLucene.RangeQuery(
                            PyLucene.Term(index, start_date),
                            PyLucene.Term(index, end_date), True)
                    else:
                        term = PyLucene.Term(index, value)
                        subquery = PyLucene.TermQuery(term)

            else: # Fallback to Query Parser
                # Retrieving the matching analyzer.
                # Note that we may use a slightly different analyzer for search
                # than for indexation cf. analysis/__init__.py
                this_analyzer = nxlucene.analysis.getAnalyzerById(analyzer,
                                                                  mode='search')

                self.log.debug("Using analyzer of type %s for field %s" %
                               (str(this_analyzer), index))

                try:
                    qparser = PyLucene.QueryParser(index, this_analyzer)
                    # Set default operator
                    defaultop = nxlucene.search.query.query_parser_operators_map.get(default_query_operator,
                                nxlucene.search.query.query_parser_operators_map.get('OR'))
                    qparser.setDefaultOperator(defaultop)
                    subquery = qparser.parse(value)
                except PyLucene.JavaError:
                    return results.getStream()
                else:
                    if len(search_fields) == 1:
                        # pure QueryParser search, it might be purely negative
                        pure_negative = True

            if subquery is not None:
                query.add(subquery,
                          nxlucene.search.query.boolean_clauses_map.get(
                    condition, default_clause))

        if pure_negative:
            query.add(PyLucene.BooleanClause(PyLucene.MatchAllDocsQuery(),
                                             PyLucene.BooleanClause.Occur.SHOULD))

        self.log.debug('query "%s"' % query.toString())

        # Probably no indexes are created yet.
        searcher = self.getSearcher()
        if not searcher.get():
            return results.getStream()

        #
        # Extract sorting information from search options.
        #

        tstart = time.time()
        # desc / asc
        sort_order = search_options.get('sort-order')
        self.log.debug("Request sort-order is %s" % str(sort_order))
        if not sort_order:
            sort_order = False
        else:
            if sort_order == 'reverse':
                sort_order = True
            else:
                sort_order = False

        sort_on = search_options.get('sort-on', '')
        if sort_on:
            self.log.debug("Sorting on %s with order=%s" %
                           (str(sort_on), str(sort_order)))
            try:
                hits = searcher.get().search(
                    query, PyLucene.Sort(sort_on, sort_order))
            except PyLucene.JavaError:
                self.log.debug("Trying to sort on %s which is a "
                               "tokenized field. "
                               "Use another field instead since it's not "
                               "possible" % str(sort_on))
                try:
                    hits = searcher.get().search(query,
                                                 PyLucene.Sort.RELEVANCE)
                except PyLucene.JavaError:
                    self.log.info("Request %s failed..." % repr(query))
                    searcher.close()
                    return results.getStream()
        else:
            try:
                hits = searcher.get().search(query, PyLucene.Sort.RELEVANCE)
            except PyLucene.JavaError:
                self.log.info("Request %s failed..." % repr(query))
                searcher.close()
                return results.getStream()

        nb_results = hits.length()
        results.addNumberOfResults(nb_results)
        self.log.info("Number of results %s" % str(nb_results))

        tstop = time.time()
        self.log.info("Time to find return results %s" % str(tstop-tstart))

        # Use bits iterator here for performance reasons.  Don't ever
        # think about building a list and use offset for the batch the
        # performances would be really bad.
        # Consider the code below optimized and well tested with a
        # huge amount of records.

        tstart = time.time()

        i = start
        while i < start+size:
            try:
                doc = hits[i]
            except IndexError:
                break

            table = {}
            for field in doc:
                k = field.name()
                if k in return_fields:
                    v = field.stringValue()
                    if not table.has_key(k):
                        table[k] = v
                    else:
                        old = table[k]
                        if isinstance(old, list):
                            old.append(v)
                            table[k] = old
                        else:
                            table[k] = [table[k], v]

            results.addItem(table['uid'], table)

            i += 1

        tstop = time.time()
        self.log.info(
            "Time to construct the RSS query %s" % str(tstop-tstart))

        searcher.close()
        return results.getStream()

    def getFieldTerms(self, field):
        """Returns a list with all the terms for a specific field
        """
        reader = self.getReader()
        indexreader = reader.get()
        start_term = PyLucene.Term(field, '')
        terms = indexreader.terms(start_term)
        res = []
        while True:
            term = terms.term()
            if term is None or term.field() != field:
                break
            res.append(term.text())
            if not terms.next():
                break
        return res
