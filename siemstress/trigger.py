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
import threading
import os
from sys import exit
#import signal


class SiemTrigger:

    def __init__(self, db, rule):
        """Initialize trigger object"""
        
        self.db = db
        self.rule = rule
        self.tzone = None



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
            sleep(int(self.rule['time_int']) * 60)



    def check_rule(self):
        """Check a trigger rule"""
        
        # To Do: Add date_stamp_utc/int logic
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
        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            cur.execute(self.rule['sql_query'])
            rows = cur.fetchall()
            cur.close()
        con.close()
    
        # Evaluate the results:
        if len(rows) > int(self.rule['event_limit']):
            idtags = json.dumps([int(row[0]) for row in rows])

            datestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            magnitude = (((len(rows) // 2) // \
                    (self.rule['event_limit'] + 1) // 2) + 5) * \
                    ( 7 - self.rule['severity'])

            outstatement = 'INSERT INTO ' + \
                    self.rule['out_table'] + \
                    '(date_stamp, t_zone, ' + \
                    'source_rule, severity, source_table, event_limit, ' + \
                    'event_count, magnitude, time_int, message, source_ids) ' + \
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

            # Send an event to the database:
            con = mdb.connect(self.db['host'], self.db['user'],
                    self.db['password'], self.db['database'])
            with con:
                cur = con.cursor()
                cur.execute(outstatement, (datestamp, self.tzone,
                    self.rule['rule_name'], self.rule['severity'],
                    self.rule['source_table'],
                    self.rule['event_limit'], len(rows), magnitude,
                    self.rule['time_int'], self.rule['message'],
                    idtags))
                cur.close()
            con.close()

def start_rule(db, rule, oneshot):
    """Initialize trigger object and start watching"""

    # Create table if it doesn't exist:
    con = mdb.connect(db['host'], db['user'], db['password'], db['database'])
    with con:
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS ' + rule['out_table'] + \
                '(id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                'date_stamp TIMESTAMP, ' + \
                't_zone NVARCHAR(5), ' + \
                'source_rule NVARCHAR(25), ' + \
                'severity TINYINT UNSIGNED, ' + \
                'source_table NVARCHAR(25), ' + \
                'event_limit INT UNSIGNED, ' + \
                'event_count INT UNSIGNED, ' + \
                'magnitude INT UNSIGNED, ' + \
                'time_int INT UNSIGNED, ' + \
                'message NVARCHAR(1000), ' + \
                'source_ids NVARCHAR(2000))')
        cur.close()
    con.close()

    sentry = SiemTrigger(db, rule)

    if oneshot:
        sentry.check_rule()
    elif int(rule['time_int']) == 0:
        pass
    
    else:
        # Before starting, sleep randomly up to rule interval to stagger
        # database use:
        sleep(randrange(0, int(rule['time_int']) * 60))

        sentry.watch_rule()
