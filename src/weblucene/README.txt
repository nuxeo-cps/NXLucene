$Id: $

weblucene
==========

This is the core lib of WebLucene. WebLucene is a standalone multi
threads remote server handling Lucene index store. It uses twisted and
zope librairies for its implementation.

One of the server ressource is XML-RPC.

You may use your favorite language and xml-rpc client to request WebLucene.

Let's take an example using the the xmlrpclib proxy server of the
standard Python library :

    >>> import xmlrpclib
    >>> proxy = xmlrpclib.Server('http://127.0.0.1:9080')

XXX TODO
