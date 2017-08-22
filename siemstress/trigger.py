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
import time.daylight
import time.timezone
import time.altzonze
from random import randrange
from datetime import datetime
import MySQLdb as mdb


class SiemTrigger:

    def __init__(self, server='127.0.0.1', user='siemstress',
            password='siems2bfine', database='siemstressdb', rule={}):
        """Initialize trigger object"""
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.rule = rule


    def watch_rule(self):
        """Enforce a trigger rule"""

        # Set time zone:
        if time.daylight:
            tzone = \
                    str(int(float(time.altzone) / 60 // 60)).rjust(2,
                            '0') + \
                    str(int(float(time.altzone) / 60 % 60)).ljust(2, '0')
        else:
            tzone = \
                    str(int(float(time.timezone) / 60 // 60)).rjust(2,
                            '0') + \
                    str(int(float(time.timezone) / 60 % 60)).ljust(2, '0')
        if not '-' in tzone:
            tzone = '+' + tzone

        # Create table if it doesn't exist:
        #con = mdb.connect(self.server, self.user, self.password,
        #        self.database)
        with mdb.connect(self.server, self.user, self.password,
                self.database) as con:
            cur = con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS ' + rule['outtable'] + \
                    '(Id INT PRIMARY_KEY AUTO_INCREMENT, ' + \
                    'DateStamp TIMESTAMP, ' + \
                    'TZone NVARCHAR(5), ' + \
                    'SourceRule NVARCHAR(25), ' + \
                    'SourceTable NVARCHAR(25), ' + \
                    'Limit INT, Count INT, ' + \
                    'Interval INT, '
                    'Message NVARCHAR(1000), ' + \
                    'SourceIDs NVARCHAR(2000))')

        outstatement = 'INSERT INTO ' + \
                self.rule['outtable'] + \
                ' (DateStamp, TZone, ' + \
                'SourceRule, SourceTable, Limit, Count, Interval, ' + \
                'Message, SourceIDs) ' + \
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'

        while True:
        
            # Query the database:
            with con:
                cur = con.cursor()
                cur.execute(self.rule['sqlquery'])
        
                rows = cur.fetchall
        
            # Evaluate the results:
            if len(rows) > self.rule['limit']:
                idtags = str([row[0] for row in rows])
                #outcon = mdb.connect(self.server, self.user,
                #        self.password, self.database)

                datestamp = datetime.now().strftime('%y%m%d%H%M%S')

                # Send an event to the database:
                with mdb.connect(self.server, self.user, self.password,
                        self.database) as outcon:
                    cur = con.cursor()

                    cur.execute(outstatement, (datestamp, tzone,
                        self.rule['name'], self.rule['sourcetable'],
                        self.rule['interval'], len(rows),
                        self.rule['count'], 
                        self.rule['message'], idtags))

            # Wait until the next interval
            sleep(int(self.rule['interval']) * 60)

def start_rule(rserver, ruser, rpassword, rdatabase, rrule={}):
    """Initialize trigger object and start watching"""

    sentry = SiemTrigger(server = rserver, user = ruser,
            password = rpassword, database = rdatabase, rule = rrule)

    # Sleep randomly up to rule interval:
    sleep(randrange(0, int(rrule['interval'] * 60)

    sentry.watch_rule()
