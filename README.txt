$Id: $

NXLucene
==========

What is is ? 

  NXLucene is a standalone multi threads remote server handling
  Lucene index store. It is based on the PyLucene Python bindings and
  uses twisted and zope.interface for its implementation.
  
  Currently, it supports the XML-RPC protocol but might be easily
  extended to other protocols, such as SOAP, thanks to its modular
  design.

  Note the FSDirectory backend is the only supported backend by
  NXLucene for now.

  The search results are returned as RSS streams.

  NXLucene exposes a custom query language for indexing and searching
  operations. Not the Lucene native search query is of course still
  supported.

  XXX

Motivation 

  XXX

Installation

  See INSTALL.txt

More information 

  - http://nxlucene.nuxeo.org

  - XXX 
  
License : 

  This Software is governed by the LGPL License. See LICENSE.txt
  http://www.gnu.org/copyleft/lesser.html

  This software includes as well softwares under the MIT and the ZPL.