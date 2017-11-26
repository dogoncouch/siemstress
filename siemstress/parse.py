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

from siemstress import __version__
import logdissect.parsers
import time
from datetime import datetime
import re
import sys
import os
import MySQLdb as mdb
from argparse import ArgumentParser
from argparse import FileType
import ConfigParser
import json



class LiveParser:

    def __init__(self, db, table, helpers, tzone=None):
        """Initialize live parser"""

        self.parser = None
        self.db = db
        self.table = table
        self.helpers = helpers
        self.tzone = tzone



    def get_parser(self, parsername):
        """Load the parser"""

        if parsername == 'syslogbsd':
            self.parser = logdissect.parsers.syslogbsd.ParseModule()
        elif parsername == 'syslogiso':
            self.parser = logdissect.parsers.syslogiso.ParseModule()
        elif parsername == 'nohost':
            self.parser = logdissect.parsers.nohost.ParseModule()
        elif parsername == 'tcpdump':
            self.parser = logdissect.parsers.tcpdump.ParseModule()


    def parse_entries(self, inputfile):
        """Parse log entries from a file like object"""

        # Read to the end of the file:
        inputfile.read()
        
        recent_datestamp = '0000000000'
        oldtnum = 0
        ymdstamp = datetime.now().strftime('%Y%m%d')

        # NOTE: The default password is on a publicly available git repo.
        # It should only be used for development purposes on closed
        # systems.
        self.sqlstatement = 'INSERT INTO ' + self.table + \
                ' (date_stamp, f_date_stamp, ' + \
                't_zone, raw_stamp, facility, severity, source_host, ' + \
                'source_port, dest_host, dest_port, source_process, ' + \
                'source_pid, protocol, ' + \
                'message, extended) VALUES ' + \
                '(%s, %s, %s, %s, %s, %s, %s, %s, %s, ' + \
                '%s, %s, %s, %s, %s, %s)'

        if not self.tzone:
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

        
        # Make sure the table exists:
        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute('CREATE TABLE IF NOT EXISTS ' + self.table + \
                    '(id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                    'date_stamp TIMESTAMP, ' + \
                    'f_date_stamp DECIMAL(20, 1), ' + \
                    't_zone NVARCHAR(5), '+ \
                    'date_stamp_utc TIMESTAMP, ' + \
                    'raw_stamp NVARCHAR(80), ' + \
                    'facility NVARCHAR(15), ' + \
                    'severity NVARCHAR(10), ' + \
                    'source_host NVARCHAR(25), ' + \
                    'source_port NVARCHAR(25), ' + \
                    'dest_host NVARCHAR(25), ' + \
                    'dest_port NVARCHAR(25), ' + \
                    'source_process NVARCHAR(25), ' + \
                    'source_pid MEDIUMINT UNSIGNED, ' + \
                    'protocol NVARCHAR(5), ' + \
                    'message NVARCHAR(2000), '
                    'extended NVARCHAR(1000))')
            cur.execute('CREATE TABLE IF NOT EXISTS ' + self.helpers + \
                    '(id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                    'var_name NVARCHAR(25), ' + \
                    'reg_exp NVARCHAR(200))')
            cur.execute('SELECT * FROM ' + self.helpers)
            helpers = cur.fetchall()
            cur.close()
        con.close()

        rehelpers = []
        for h in helpers:
            reh = {}
            reh['var_name'] = h['var_name']
            reh['reg_exp'] = re.compile(h['reg_exp'])
            rehelpers.append(reh)

        while True:

            # Check for a new line:
            line = inputfile.readline()

            if line:
                # Do the parsing
                ourline = line.rstrip()
                
                entry = self.parser.parse_line(ourline)

                if entry:

                    if float(entry['tstamp']) < oldtnum:
                        ymdstamp = datetime.now().strftime('%Y%m%d')
                    oldtnum = float(entry['tstamp'])
                    
                
                    # Set datestamp
                    if not entry['year']:
                        entry['year'] = ymdstamp[0:4]
                    if not entry['month']:
                        entry['month'] = ymdstamp[4:6]
                    if not entry['day']:
                        entry['day'] = ymdstamp[6:8]
                    if self.tzone:
                        entry['tzone'] = self.tzone
                    else:
                        if not entry['tzone']:
                            entry['tzone'] = tzone
                
                    tstamp = entry['tstamp'].split('.')
                    intdatestamp = \
                            ymdstamp + tstamp[0]
                    
                    if len(tstamp) == 1:
                        datestamp = intdatestamp + '.000000'
                    else:
                        datestamp = '.'.join(intdatestamp,
                                tstamp[1].ljust(6, '0'))
                    
                    # Parse extended attributes from helpers:
                    extattrs = {}

                    for h in rehelpers:
                        mlist = h['reg_exp'].findall(entry['message'])

                        try:
                            extattrs[h['var_name']] += mlist
                        except KeyError:
                            extattrs[h['var_name']] = mlist

                    extattrs = json.dumps(extattrs)


                    # Put our attributes in our table:
                    con = mdb.connect(self.db['host'], self.db['user'],
                            self.db['password'], self.db['database'])
                    with con:
                        cur = con.cursor()
                        cur.execute(self.sqlstatement,
                                (intdatestamp, datestamp,
                                    entry['tzone'], entry['raw_stamp'], 
                                    entry['facility'], entry['severity'],
                                    entry['source_host'], entry['source_port'],
                                    entry['dest_host'], entry['dest_port'],
                                    entry['source_process'],
                                    entry['source_pid'],
                                    entry['protocol'], entry['message'],
                                    extattrs))
                        con.commit()
                        cur.close()
                    con.close()


                else:
                    # No match!?
                    # To Do: raise an error here.
                    print('No Match: ' + ourline)

            else:
                time.sleep(0.1)



    def parse_file(self, filename, parser):
        try:
            self.get_parser(parser)
            self.parse_entries(filename)

        except KeyboardInterrupt:
            pass
        # except Exception as err:
        #     print('Error: ' + str(err))

    
    
#def main():
#    parser = LiveParser()
#    parser.run_parse()


#if __name__ == "__main__":
#    parser = LiveParser()
#    parser.run_parse()
