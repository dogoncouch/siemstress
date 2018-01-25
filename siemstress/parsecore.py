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
from siemstress.parse import LiveParser
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



class ParseCore:

    def __init__(self):
        """Initialize live parser"""

        self.args = None
        self.arg_parser = ArgumentParser()
        self.config = None

        self.parser = None
        self.parsername = None
        self.db = {}
        self.table = None



    def get_args(self):
        """Set argument options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = '/etc/siemstress/db.conf',
                help = ('set the config file'))
        self.arg_parser.add_argument('-s',
                action = 'store', dest = 'section',
                default = 'siem_default',
                help = ('set the config section'))
        self.arg_parser.add_argument('-z',
                action = 'store', dest = 'tzone',
                help = ("set the offset to UTC (e.g. '+0500')"))
        self.arg_parser.add_argument('--intstamps',
                action = 'store_true', dest = 'intstamps'
                help = ("add non-fractional timestamps (becoming deprecated)"))
        self.arg_parser.add_argument('file',
                type = FileType('r'), nargs = '?',
                help = ('set a file to follow'))

        self.args = self.arg_parser.parse_args()



    def get_config(self):
        """Read the config file"""

        config = ConfigParser.ConfigParser()
        if os.path.isfile(self.args.config):
            myconf = self.args.config
        else: myconf = 'config/db.conf'
        config.read(myconf)

        self.db['host'] = config.get('siemstress', 'server')
        self.db['user'] = config.get('siemstress', 'user')
        self.db['password'] = config.get('siemstress', 'password')
        self.db['database'] = config.get('siemstress', 'database')
        sectionfile = config.get('siemstress', 'sectionfile')

        if not sectionfile.startswith('/'):
            sectionfile = '/'.join(os.path.abspath(myconf).split('/')[:-1]) + \
                    '/' + sectionfile

        config.read(sectionfile)
        
        self.table = config.get(self.args.section, 'table')
        self.helpers = config.get(self.args.section, 'helpers')
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



    def run_parse(self):
        try:
            self.get_args()
            self.get_config()
            parser = LiveParser(self.db, self.table, self.helpers,
                    tzone=self.args.tzone, intstamps=self.args.intstamps)

            parser.parse_file(self.args.file, self.parsername)

        except KeyboardInterrupt:
            pass
        # except Exception as err:
        #     print('Error: ' + str(err))

    
    
def main():
    parser = ParseCore()
    parser.run_parse()


if __name__ == "__main__":
    parser = ParseCore()
    parser.run_parse()
