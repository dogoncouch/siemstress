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
        """Query siemstress SQL database for events (simplified)"""

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

        qstatement = " ".join(qstatement)
        con = mdb.connect(self.server, self.user, self.password,
                self.database)

        with con:
            cur = con.cursor()
            cur.execute(qstatement)

            rows = cur.fetchall()
            desc = cur.description

        return desc, rows

    def query(self, tables=['default'], columns=[], last=None,
            daterange=None, sourcehosts=[], processes=[], greps = []):
        """Query siemstress SQL database for events"""
        
        lastunits = {'d': 'day', 'h': 'hour', 'm': 'minute', 's': 'second'}
        
        qstatement = []

        # Select statement
        if columns:
            selectstatement = "SELECT " + columns[0]
            for column in columns[1:]:
                selectstatement += ", " + column
        else:
            selectstatement = "SELECT *"
        qstatement.append(selectstatement)
            
        tablestatement = "FROM " + tables[0]
        for table in tables[1:]:
            selectstatement += ", " + table
        qstatement.append(tablestatement)

        # Date range
        if last:
            lastunit = lastunits[last[-1]]
            lastnum = last[:-1]

            datestatement = "WHERE DateStamp >= " + \
                    "timestamp(date_sub(now(), interval " + \
                    lastnum + " " + lastunit + "))"
        elif daterange:
            startdate, enddate = daterange.split('-')
            datestatement = "WHERE DateStamp BETWEEN \"" startdate + \
                    "\" AND \"" enddate + "\")"
        else:
            datestatement = "WHERE DateStamp >= " + \
                    "timestamp(date_sub(now(), interval " + \
                    "1 day))"
        qstatement.append(datestatement)

        # Attributes
        if sourcehosts:
            shoststatement = "AND (SourceHost LIKE \"" + \
                    sourcehosts[0] + "\""
            for host in sourcehosts[1:]:
                shoststatement += " OR SourceHost LIKE \"" + host + "\""
            shoststatement += ")"
            qstatement.append(shoststatement)

        if processes:
            procstatement = "AND (Process LIKE \"" + \
                    processes[0] + "\""
            for process in processes[1:]:
                procstatement += " OR Process LIKE \"" + process + "\""
            procstatement += ")"
            qstatement.append(procstatement)
        
        if greps:
            grepstatement = "AND (Message LIKE \"%" + \
                    greps[0] + "%\""
            for grep in greps[1:]:
                grepstatement += " OR Message LIKE \"%" + grep + "%\""
            grepstatement += ")"
            qstatement.append(grepstatement)

        qstatement = " ".join(qstatement)

        # Connect and execute
        con = mdb.connect(self.server, self.user, self.password,
                self.database)

        with con:
            cur = con.cursor()
            cur.execute(qstatement)

            rows = cur.fetchall()
            if columns:
                desc = columns
            else:
                desc = cur.description

        return desc, rows
            
