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
"""Date related functions.

$Id: core.py 31300 2006-03-15 03:10:04Z janguenot $
"""

import datetime
import PyLucene

def getPythonDateTimeFromJavaStr(java_date_str):
    """Returns a Python datetime object given a string representation
    of a Java Date object.
    """

    # XXX : Here the date stays the same (and is correct), but we're
    # losing the timezone information (and using UTC). I'm not sure if
    # whether or not this will be an issue at this stage.

    date = PyLucene.DateField.stringToDate(java_date_str)
    timestamp = date.getTime()
    return datetime.datetime.utcfromtimestamp(timestamp/1000)
