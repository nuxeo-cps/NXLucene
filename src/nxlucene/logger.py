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
"""Specific logging configuration

$Id$
"""

import logging
from logging.handlers import RotatingFileHandler

format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def initLog(level, file_):
    """Initialize a Rotating File Handler.
    """
    # XXX make maxBytes and backupCount configurable
    handler = RotatingFileHandler(file_, maxBytes=1000000, backupCount=50)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(getattr(logging, level))
    

