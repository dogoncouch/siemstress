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

import time
from time import strftime
from time import sleep
from time import daylight
from time import timezone
from time import altzone
from random import randrange
from datetime import datetime
import MySQLdb as mdb
import json
from sys import exit
import signal


class SiemTrigger:

    def __init__(self, server, user, password, database, rule):
        """Initialize trigger object"""
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.rule = rule
        self.tzone = None

        signal.signal(signal.SIGTERM, self.sigterm_handler)


    def sigterm_handler(self, signal, frame):
        """Exits cleanly on sigterm"""
        exit(0)



    def watch_rule(self):
        """Watch a trigger rule"""

        # Set time zone:
        if daylight:
            self.tzone = \
                    str(int(float(altzone) / 60 // 60)).rjust(2,
                            '0') + \
                    str(int(float(altzone) / 60 % 60)).ljust(2, '0')
        else:
            self.tzone = \
                    str(int(float(timezone) / 60 // 60)).rjust(2,
                            '0') + \
                    str(int(float(timezone) / 60 % 60)).ljust(2, '0')
        if not '-' in self.tzone:
            self.tzone = '+' + self.tzone

        while True:

            # Check the rule:
            self.check_rule()
        
            # Wait until the next interval
            sleep(int(self.rule['TimeInt']) * 60)



    def check_rule(self):
        """Check a trigger rule"""
        
        if not self.tzone:
            # Set time zone:
            if daylight:
                self.tzone = \
                        str(int(float(altzone) / 60 // 60)).rjust(2,
                                '0') + \
                        str(int(float(altzone) / 60 % 60)).ljust(2, '0')
            else:
                self.tzone = \
                        str(int(float(timezone) / 60 // 60)).rjust(2,
                                '0') + \
                        str(int(float(timezone) / 60 % 60)).ljust(2, '0')
            if not '-' in self.tzone:
                self.tzone = '+' + self.tzone

        # Query the database:
        con = mdb.connect(self.server, self.user, self.password,
                self.database)
        with con:
            cur = con.cursor()
            cur.execute(self.rule['SQLQuery'])
            rows = cur.fetchall()
            cur.close()
        con.close()
    
        # Evaluate the results:
        if len(rows) > int(self.rule['EventLimit']):
            idtags = json.dumps([int(row[0]) for row in rows])

            datestamp = datetime.now().strftime('%Y%m%d%H%M%S')

            outstatement = 'INSERT INTO ' + \
                    self.rule['OutTable'] + \
                    '(DateStamp, TZone, ' + \
                    'SourceRule, Severity, SourceTable, EventLimit, ' + \
                    'EventCount, TimeInt, Message, SourceIDs) ' + \
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

            # Send an event to the database:
            con = mdb.connect(self.server, self.user,
                    self.password, self.database)
            with con:
                cur = con.cursor()
                cur.execute(outstatement, (datestamp, self.tzone,
                    self.rule['RuleName'], self.rule['Severity'],
                    self.rule['SourceTable'],
                    self.rule['EventLimit'], len(rows),
                    self.rule['TimeInt'], self.rule['Message'],
                    idtags))
                cur.close()
            con.close()

def start_rule(server, user, password, database, rule, oneshot):
    """Initialize trigger object and start watching"""

    # Create table if it doesn't exist:
    con = mdb.connect(server, user, password, database)
    with con:
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS ' + rule['OutTable'] + \
                '(Id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                'DateStamp TIMESTAMP, ' + \
                'TZone NVARCHAR(5), ' + \
                'SourceRule NVARCHAR(25), ' + \
                'Severity TINYINT UNSIGNED, ' + \
                'SourceTable NVARCHAR(25), ' + \
                'EventLimit INT, EventCount INT, ' + \
                'TimeInt INT, ' + \
                'Message NVARCHAR(1000), ' + \
                'SourceIDs NVARCHAR(2000))')
        cur.close()
    con.close()

    sentry = SiemTrigger(server, user, password, database, rule)

    if oneshot:
        sentry.check_rule()
    
    else:
        # Before starting, sleep randomly up to rule interval to stagger
        # database use:
        sleep(randrange(0, int(rule['TimeInt']) * 60))

        sentry.watch_rule()
