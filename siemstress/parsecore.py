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
import ConfigParser



class LiveParser:

    def __init__(self):
        """Initialize live parser"""

        self.args = None
        self.arg_parser = ArgumentParser()
        self.config = None

        self.parser = None
        self.parsername = None
        self.server = None
        self.user = None
        self.password = None
        self.database = None
        self.table = None



    def get_args(self):
        """Set argument options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('--clear',
                action = 'store_true', dest = 'clearsiem',
                help = ('delete the SQL table for selected section'))
        self.arg_parser.add_argument('--force',
                action = 'store_true', dest = 'force',
                help = ('really delete the table'))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = '/etc/siemstress/siemstress.conf',
                help = ('set the config file'))
        self.arg_parser.add_argument('-s',
                action = 'store', dest = 'section',
                default = 'default',
                help = ('set the config section'))
        self.arg_parser.add_argument('-z',
                action = 'store', dest = 'tzone',
                help = ("set the offset to UTC (e.g. '+0500')"))

        self.args = self.arg_parser.parse_args()



    def get_config(self):
        """Read the config file"""

        config = ConfigParser.ConfigParser()
        if os.path.isfile(self.args.config):
            myconf = self.args.config
        else: myconf = 'config/siemstress.conf'
        config.read(myconf)

        self.server = config.get('siemstress', 'server')
        self.user = config.get('siemstress', 'user')
        self.password = config.get('siemstress', 'password')
        self.database = config.get('siemstress', 'database')
        self.table = config.get(self.args.section, 'table')
        try:
            self.parsername = config.get(self.args.section, 'parser')
        except Exception:
            # To Do: narrow down exception
            self.parsername = 'syslogbsd'


        if self.parsername == 'syslogbsd':
            self.parser = logdissect.parsers.syslogbsd.ParseModule()
        elif self.parsername == 'syslogiso':
            self.parser = logdissect.parsers.syslogiso.ParseModule()
        elif self.parsername == 'nohost':
            self.parser = logdissect.parsers.nohost.ParseModule()
        elif self.parsername == 'tcpdump':
            self.parser = logdissect.parsers.tcpdump.ParseModule()



    def clear_siem(self):
        """Clear SQL table specified in section"""

        if self.args.force:
            con = mdb.connect(self.server, self.user, self.password,
                    self.database)
        
            with con:
                cur = con.cursor()
        
                cur.execute('DROP TABLE IF EXISTS ' + self.table)
        else: print("Use --force if you really want to drop table (" + \
                self.table + ")")



    def parse_entries(self):
        """Parse log entries from standard input"""
        recent_datestamp = '0000000000'
        oldtnum = 0
        ymdstamp = datetime.now().strftime('%Y%m%d')

        # NOTE: The default password is on a publicly available git repo.
        # It should only be used for development purposes on closed
        # systems.
        self.sqlstatement = 'INSERT INTO ' + self.table + \
                ' (DateStamp, FDateStamp, ' + \
                'TZone, RawStamp, Facility, Severity, SourceHost, ' + \
                'SourcePort, DestHost, DestPort, Process, PID, Protocol, ' + \
                'Message) VALUES ' + \
                '(%s, %s, %s, %s, %s, %s, %s, %s, %s, ' + \
                '%s, %s, %s, %s, %s)'

        if not self.args.tzone:
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

        
        con = mdb.connect(self.server, self.user,
                self.password, self.database)
        
        with con:
            cur = con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS ' + self.table + \
                    '(Id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                    'DateStamp TIMESTAMP, ' + \
                    'FDateStamp FLOAT(20, 6) UNSIGNED, ' + \
                    'TZone NVARCHAR(5), '+ \
                    'RawStamp NVARCHAR(80), ' + \
                    'Facility NVARCHAR(15), ' + \
                    'Severity NVARCHAR(10), ' + \
                    'SourceHost NVARCHAR(25), ' + \
                    'SourcePort NVARCHAR(25), ' + \
                    'DestHost NVARCHAR(25), ' + \
                    'DestPort NVARCHAR(25), ' + \
                    'Process NVARCHAR(25), ' + \
                    'PID MEDIUMINT UNSIGNED, ' + \
                    'Protocol NVARCHAR(5), ' + \
                    'Message NVARCHAR(2000))')
            cur.close()
        con.close()


        while True:

            line = sys.stdin.readline()

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
                    if self.args.tzone:
                        entry['tzone'] = args.tzone
                    else:
                        if not entry['tzone']:
                            entry['tzone'] = tzone
                
                    tstamp = entry['tstamp'].split('.')
                    intdatestamp = \
                            ymdstamp + tstamp[0]
                    
                    if not tstamp[1]:
                        datestamp = intdatestamp + '.000000'
                    else:
                        datestamp = '.'.join(intdatestamp,
                                tstamp[1].ljust(6, '0'))

                    # Put our attributes in our table:
                    con = mdb.connect(self.server, self.user,
                            self.password, self.database)
        
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
                                    entry['protocol'], entry['message']))
                        con.commit()
                        cur.close()
                    con.close()


                else:
                    # No match!?
                    # To Do: raise an error here.
                    print('No Match: ' + ourline)



    def run_parse(self):
        try:
            self.get_args()
            self.get_config()
            if self.args.clearsiem:
                self.clear_siem()
            else:
                self.parse_entries()

        except KeyboardInterrupt:
            pass
        # except Exception as err:
        #     print('Error: ' + str(err))

    
    
def main():
    parser = LiveParser()
    parser.run_parse()


if __name__ == "__main__":
    parser = LiveParser()
    parser.run_parse()
