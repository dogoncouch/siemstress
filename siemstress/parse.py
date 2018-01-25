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
from datetime import timedelta
import re
import sys
import os
import socket
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
        self.supertzone = tzone
        self.tzone = tzone
        self.tdelta = None



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


    def parse_entries(self, inputfile, intstamps=False):
        """Parse log entries from a file like object"""

        # Get hostname, file name, tzone:
        parsepath = os.path.abspath(inputfile.name)
        parsehost = socket.getfqdn()
        self._get_tzone()

        # Read to the end of the file:
        inputfile.read()
        
        oldymdnum = 0
        ymdstamp = datetime.now().strftime('%Y%m%d')

        # NOTE: The default password is on a publicly available git repo.
        # It should only be used for development purposes on closed
        # systems.
        if intstamps:
            self.sqlstatement = 'INSERT INTO ' + self.table + \
                    ' (date_stamp, date_stamp_int, ' + \
                    'date_stamp_utc, date_stamp_utc_int, ' + \
                    't_zone, raw_text, facility, severity, source_host, ' + \
                    'source_port, dest_host, dest_port, source_process, ' + \
                    'source_pid, protocol, ' + \
                    'message, extended, parsed_on, source_path) VALUES ' + \
                    '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' + \
                    '%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        else:
            self.sqlstatement = 'INSERT INTO ' + self.table + \
                    ' (date_stamp, date_stamp_int, date_stamp_utc,' + \
                    't_zone, raw_text, facility, severity, source_host, ' + \
                    'source_port, dest_host, dest_port, source_process, ' + \
                    'source_pid, protocol, ' + \
                    'message, extended, parsed_on, source_path) VALUES ' + \
                    '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' + \
                    '%s, %s, %s, %s, %s, %s, %s)'
        
        rehelpers = []
        for h in helpers:
            reh = {}
            reh['var_name'] = h['var_name']
            reh['reg_exp'] = re.compile(h['reg_exp'])
            rehelpers.append(reh)

        is_connected = False
        
        while True:

            # Check for a new line:
            line = inputfile.readline()

            if line:
                # Do the parsing
                ourline = line.rstrip()
                
                entry = self.parser.parse_line(ourline)

                if entry:

                    if int(entry['tstamp'][0:8]) < oldymdnum:
                        ymdstamp = datetime.now().strftime('%Y%m%d')
                        self._get_tzone()
                    oldymdnum = str(int(entry['tstamp']))[0:8]
                    
                
                    # Set datestamp
                    if not entry['year']:
                        entry['year'] = ymdstamp[0:4]
                    if not entry['month']:
                        entry['month'] = ymdstamp[4:6]
                    if not entry['day']:
                        entry['day'] = ymdstamp[6:8]
                    if self.supertzone:
                        entry['tzone'] = self.supertzone
                    else:
                        if not entry['tzone']:
                            entry['tzone'] = self.tzone
                
                    datestamp = ymdstamp + entry['tstamp']

                    if not '.' in datestamp:
                        datestamp = datestamp + '.000000'

                    datestampobj = datetime.strptime(datestamp,
                            '%Y%m%d%H%M%S.%f')
                    datestamputcobj = datestampobj + self.tdelta
                    datestamputc = datetime.strftime(datestamputcobj,
                            '%Y%m%d%H%M%S.%f')
                    if intstamps:
                        datestampint = datestamp.split('.')[0]
                        datestamputcint = datestamputc.split('.')[0]
                    
                    # Parse extended attributes from helpers:
                    extattrs = {}

                    for h in rehelpers:
                        mlist = h['reg_exp'].findall(entry['message'])

                        try:
                            extattrs[h['var_name']] += mlist
                        except KeyError:
                            extattrs[h['var_name']] = mlist

                    extattrs = json.dumps(extattrs)


                    if not is_connected:
                        con = mdb.connect(self.db['host'], self.db['user'],
                                self.db['password'], self.db['database'])
                    # Put our attributes in our table:
                    with con:
                        cur = con.cursor()
                        if intstamps:
                            cur.execute(self.sqlstatement,
                                    (datestamp, datestampint,
                                        datestamputc, datestamputcint,
                                        entry['tzone'], ourline, 
                                        entry['facility'], entry['severity'],
                                        entry['source_host'], entry['source_port'],
                                        entry['dest_host'], entry['dest_port'],
                                        entry['source_process'],
                                        entry['source_pid'],
                                        entry['protocol'], entry['message'],
                                        extattrs, parsehost, parsepath))
                        else:
                            cur.execute(self.sqlstatement,
                                    (datestamp, datestamputc,
                                        entry['tzone'], ourline, 
                                        entry['facility'], entry['severity'],
                                        entry['source_host'], entry['source_port'],
                                        entry['dest_host'], entry['dest_port'],
                                        entry['source_process'],
                                        entry['source_pid'],
                                        entry['protocol'], entry['message'],
                                        extattrs, parsehost, parsepath))
                        con.commit()
                        cur.close()
                    #con.close()


                else:
                    # No match!?
                    # To Do: raise an error here.
                    print('No Match: ' + ourline)

            else:
                con.close()
                is_connected = False
                time.sleep(0.1)


    def _get_tzone(self):
        """Establish time zone (tzone) and delta to UTC (tdelta)"""
        if not self.supertzone:
            # Get tzone:
            if time.localtime().tm_isdst:
                tzone = \
                        str(int(float(time.altzone) / 60 // 60)).rjust(2,
                                '0') + \
                        str(int(float(time.altzone) / 60 % 60)).ljust(2, '0')
            else:
                tzone = \
                        str(int(float(time.timezone) / 60 // 60)).rjust(2,
                                '0') + \
                        str(int(float(time.timezone) / 60 % 60)).ljust(2, '0')
            if not '-' in tzone and not '+' in tzone:
                tzone = '+' + tzone

        else:
            if self.supertzone[0] not in ['+', '-']:
                # To Do: raise an error here for bad argument formatting
                pass
            else:
                tzone = self.supertzone

        # Get time delta:
        if tzone[0] == '-':
            tdelta = timedelta(hours = -int(tzone[1:3]),
                    minutes = -int(tzone[3:5]))
        else:
            tdelta = timedelta(hours = int(tzone[1:3]),
                    minutes = int(tzone[3:5]))

        self.tzone = tzone
        self.tdelta = tdelta


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
