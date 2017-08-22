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
                "interval " + str(int(last[:-1])) + " " + timeint + ")")
        
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

    def query(self, tables=[], columns=[],
            last=None, daterange=None, sourcehosts=[], sourceports=[],
            desthosts=[], destports=[], processes=[],
            pids=[], protocols=[], greps = [],
            rsourcehosts=[], rsourceports=[], rdesthosts=[],
            rdestports=[], rprocesses=[], rpids=[], rprotocols=[],
            rgreps=[]):
        """Query siemstress SQL database for events"""
        
        lastunits = {'d': 'day', 'h': 'hour', 'm': 'minute', 's': 'second'}
        
        qstatement = []

        # Select statement (columns)
        if columns:
            statement = "SELECT " + columns[0]
            for column in columns[1:]:
                statement += ", " + column
        else:
            statement = "SELECT *"
        qstatement.append(statement)
        
        # From statement (tables)
        statement = "FROM " + tables[0]
        for table in tables[1:]:
            statement += ", " + table
        qstatement.append(statement)

        # Initial where statement (time period)
        if daterange:
            startdate, enddate = daterange.split('-')
            statement = "WHERE DateStamp BETWEEN \"" + startdate + \
                    "\" AND \"" + enddate + "\""
        elif last:
            lastunit = lastunits[last[-1]]
            lastnum = last[:-1]

            statement = "WHERE DateStamp >= " + \
                    "timestamp(date_sub(now(), interval " + \
                    lastnum + " " + lastunit + "))"
        else:
            statement = "WHERE DateStamp >= " + \
                    "timestamp(date_sub(now(), interval " + \
                    "1 day))"
        qstatement.append(statement)


        # Include attributes
        if sourcehosts:
            statement = "AND (SourceHost LIKE \"" + \
                    sourcehosts[0] + "\""
            for host in sourcehosts[1:]:
                statement += " OR SourceHost LIKE \"" + host + "\""
            statement += ")"
            qstatement.append(statement)

        if sourceports:
            statement = "AND (SourcePort LIKE \"" + \
                    sourceports[0] + "\""
            for port in sourceports[1:]:
                statement += " OR SourcePort LIKE \"" + port + "\""
            statement += ")"
            qstatement.append(statement)

        if desthosts:
            statement = "AND (DestHost LIKE \"" + \
                    desthosts[0] + "\""
            for host in desthosts[1:]:
                statement += " OR DestHost LIKE \"" + host + "\""
            statement += ")"
            qstatement.append(statement)

        if destports:
            statement = "AND (DestPort LIKE \"" + \
                    destports[0] + "\""
            for port in destports[1:]:
                statement += " OR DestPort LIKE \"" + port + "\""
            statement += ")"
            qstatement.append(statement)

        if processes:
            statement = "AND (Process LIKE \"" + \
                    processes[0] + "\""
            for process in processes[1:]:
                statement += " OR Process LIKE \"" + process + "\""
            statement += ")"
            qstatement.append(statement)
        
        if pids:
            statement = "AND (PID LIKE \"" + \
                    pids[0] + "\""
            for pid in pids[1:]:
                statement += " OR PID LIKE \"" + pid + "\""
            statement += ")"
            qstatement.append(statement)
        
        if protocols:
            statement = "AND (Protocol LIKE \"" + \
                    protocols[0] + "\""
            for protocol in protocols[1:]:
                statement += " OR Protocol LIKE \"" + protocol + "\""
            statement += ")"
            qstatement.append(statement)
        
        if greps:
            statement = "AND (Message LIKE \"%" + \
                    greps[0] + "%\""
            for grep in greps[1:]:
                statement += " OR Message LIKE \"%" + grep + "%\""
            statement += ")"
            qstatement.append(statement)

        # Filter out attributes
        if rsourcehosts:
            statement = "AND (SourceHost NOT LIKE \"" + \
                    rsourcehosts[0] + "\""
            for host in rsourcehosts[1:]:
                statement += " AND SourceHost NOT LIKE \"" + host + "\""
            statement += ")"
            qstatement.append(statement)

        if rsourceports:
            statement = "AND (SourcePort NOT LIKE \"" + \
                    rsourceports[0] + "\""
            for port in rsourceports[1:]:
                statement += " AND SourcePort NOT LIKE \"" + port + "\""
            statement += ")"
            qstatement.append(statement)

        if rdesthosts:
            statement = "AND (DestHost NOT LIKE \"" + \
                    rdesthosts[0] + "\""
            for host in rdesthosts[1:]:
                statement += " AND DestHost NOT LIKE \"" + host + "\""
            statement += ")"
            qstatement.append(statement)

        if rdestports:
            statement = "AND (DestPort NOT LIKE \"" + \
                    rdestports[0] + "\""
            for port in rdestports[1:]:
                statement += " AND DestPort NOT LIKE \"" + port + "\""
            statement += ")"
            qstatement.append(statement)

        if rprocesses:
            statement = "AND (Process NOT LIKE \"" + \
                    rprocesses[0] + "\""
            for process in rprocesses[1:]:
                statement += " AND Process NOT LIKE \"" + process + "\""
            statement += ")"
            qstatement.append(statement)
        
        if rpids:
            statement = "AND (PID NOT LIKE \"" + \
                    rpids[0] + "\""
            for pid in rpids[1:]:
                statement += " AND PID NOT LIKE \"" + pid + "\""
            statement += ")"
            qstatement.append(statement)
        
        if rprotocols:
            statement = "AND (Protocol NOT LIKE \"" + \
                    rprotocols[0] + "\""
            for protocol in rprotocols[1:]:
                statement += " AND Protocol NOT LIKE \"" + protocol + "\""
            statement += ")"
            qstatement.append(statement)
        
        if rgreps:
            statement = "AND (Message NOT LIKE \"%" + \
                    rgreps[0] + "%\""
            for grep in rgreps[1:]:
                statement += "AND Message NOT LIKE \"%" + grep + "%\""
            statement += ")"
            qstatement.append(statement)


        # Connect and execute
        qstatement = " ".join(qstatement)
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

        return qstatement, desc, rows
