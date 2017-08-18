#!/usr/bin/env python

#_MIT License
#_
#_Copyright (c) 2017 Dan Persons (dpersonsdev@gmail.com)
#_
#_Permission is hereby granted, free of charge, to any person obtaining a copy
#_of this software and associated documentation files (the "Software"), to deal
#_in the Software without restriction, including without limitation the rights
#_to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#_copies of the Software, and to permit persons to whom the Software is
#_furnished to do so, subject to the following conditions:
#_
#_The above copyright notice and this permission notice shall be included in all
#_copies or substantial portions of the Software.
#_
#_THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#_IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#_FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#_AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#_LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#_OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#_SOFTWARE.

import logdissect.parsers
import time
from datetime import datetime
import re
import sys
import os
import MySQLdb as mdb


class SiemQuery:

    def __init__(self, server='127.0.0.1', user='siemstress',
            password='siems2bfine', database='siemstressdb'):
        """Initialize query object"""
        self.server = server
        self.user = user
        self.password = password
        self.database = database


    def simple_query(self, table='default', last='24h', shost=None,
            process=None, grep=None):
        """Query SQL database for log events"""

        qstatement = []
        qstatement.append("SELECT * FROM " + table)
        
        if last[-1:] == 'm': timeint = 'minute'
        elif last[-1:] == 's': timeint = 'second'
        elif last[-1:] == 'd': timeint = 'day'
        else: timeint = 'hour'

        qstatement.append("WHERE DateStamp >= timestamp(date_sub(now(), " + \
                "interval " + str(int(last[:-1])) + " " + timeint + "))")
        
        if shost: qstatement.append("AND SourceHost LIKE \"" + shost + "\"")
        if process: qstatement.append("AND Process LIKE \"" + process + "\"")
        if grep: qstatement.append("AND Message LIKE \"%" + grep + "%\"")

        sqlstatement = " ".join(qstatement)
        con = mdb.connect(self.server, self.user, self.password,
                self.database)

        with con:
            cur = con.cursor()
            cur.execute(sqlstatement)

            rows = cur.fetchall()
            desc = cur.description

        return desc, rows
