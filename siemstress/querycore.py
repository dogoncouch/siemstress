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
#import logdissect.parsers
#import time
#from datetime import datetime
#import re
#import sys
import os
#import MySQLdb as mdb
from argparse import ArgumentParser
import ConfigParser
from siemstress.query import SiemQuery



class QueryCore:

    def __init__(self):
        """Initialize live parser"""

        self.args = None
        self.arg_parser = ArgumentParser()
        self.config = None

        #self.parser = None
        #self.parsername = None
        self.server = None
        self.user = None
        self.password = None
        self.database = None
        self.tables = []
        self.queryfields = None



    def get_args(self):
        """Set argument options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('--verbose',
                action = 'store_true', dest = 'verbose',
                help = ('print SQL queries'))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = '/etc/siemstress/siemstress.conf',
                help = ('set the config file'))
        self.arg_parser.add_argument('-s',
                action = 'store', dest = 'section',
                default = 'default',
                help = ('set the config section'))
        self.arg_parser.add_argument('--table',
                action = 'append', dest = 'tables',
                metavar = 'TABLE',
                help = ('set a table to query'))
        self.arg_parser.add_argument('--last',
                action = 'store', dest = 'last', default = '24h',
                help = ('match a preceeding time range (5m, 24h, etc)'))
        self.arg_parser.add_argument('--range',
                action = 'store', dest = 'range',
                metavar = 'START-FINISH',
                help = ('match a date range (format: YYmmddHHMMSS)'))
        self.arg_parser.add_argument('--shost',
                action = 'append', dest = 'shosts',
                metavar = 'HOST',
                help = ('match a source host'))
        self.arg_parser.add_argument('--sport',
                action = 'append', dest = 'sports',
                metavar = 'PORT',
                help = ('match a source port'))
        self.arg_parser.add_argument('--dhost',
                action = 'append', dest = 'dhosts',
                metavar = 'HOST',
                help = ('match a destination host'))
        self.arg_parser.add_argument('--dport',
                action = 'append', dest = 'dports',
                metavar = 'PORT',
                help = ('match a destination port'))
        self.arg_parser.add_argument('--process',
                action = 'append', dest = 'processes',
                metavar = 'PROCESS',
                help = ('match a source process'))
        self.arg_parser.add_argument('--pid',
                action = 'append', dest = 'pids',
                metavar = 'PID',
                help = ('match a source Process ID'))
        self.arg_parser.add_argument('--protocol',
                action = 'append', dest = 'protocols',
                metavar = 'PROTOCOL',
                help = ('match a protocol'))
        self.arg_parser.add_argument('--grep',
                action = 'append', dest = 'greps',
                metavar = 'PATTERN',
                help = ('match a pattern'))
        self.arg_parser.add_argument('--rshost',
                action = 'append', dest = 'rshosts',
                metavar = 'HOST',
                help = ('filter out a source host'))
        self.arg_parser.add_argument('--rsport',
                action = 'append', dest = 'rsports',
                metavar = 'PORT',
                help = ('filter out a source port'))
        self.arg_parser.add_argument('--rdhost',
                action = 'append', dest = 'rdhosts',
                metavar = 'HOST',
                help = ('filter out a destination host'))
        self.arg_parser.add_argument('--rdport',
                action = 'append', dest = 'rdports',
                metavar = 'PORT',
                help = ('filter out a destination port'))
        self.arg_parser.add_argument('--rprocess',
                action = 'append', dest = 'rprocesses',
                metavar = 'PROCESS',
                help = ('filter out a source process'))
        self.arg_parser.add_argument('--rpid',
                action = 'append', dest = 'rpids',
                metavar = 'PID',
                help = ('filter out a source Process ID'))
        self.arg_parser.add_argument('--rprotocol',
                action = 'append', dest = 'rprotocols',
                metavar = 'PROTOCOL',
                help = ('filter out a protocol'))
        self.arg_parser.add_argument('--rgrep',
                action = 'append', dest = 'rgreps',
                metavar = 'PATTERN',
                help = ('filter out a pattern'))

        self.args = self.arg_parser.parse_args()



    def get_config(self):
        """Read the config file"""

        config = ConfigParser.ConfigParser()
        if os.path.isfile(self.args.config):
            myconf = (config)
        else: myconf = 'config/siemstress.conf'
        config.read(myconf)

        self.server = config.get('siemstress', 'server')
        self.user = config.get('siemstress', 'user')
        self.password = config.get('siemstress', 'password')
        self.database = config.get('siemstress', 'database')
        if self.args.tables:
            self.tables = self.args.tables
        else:
            self.tables.append(config.get(self.args.section, 'table'))
        self.queryfields = [int(x) for x in config.get(
            self.args.section, 'queryfields').split(',')]



    def clear_siem(self):
        """Clear SQL table specified in section"""

        con = mdb.connect(self.server, self.user, self.password,
                self.database)

        with con:
            cur = con.cursor()

            cur.execute('DROP TABLE IF EXISTS ' + self.table)



    def simple_query_siem(self):
        """Query SQL database for log events (simplified)"""
        

        query = SiemQuery(server = self.server, user = self.user,
                password = self.password, database = self.database)

        desc, rows = query.simple_query(table = self.table,
                last = self.args.last, shost = self.args.shost,
                process = self.args.process, grep = self.args.grep)

        print "%7s %20s %14s %14s %7s %s" % (
                desc[self.queryfields[0]][0],
                desc[self.queryfields[1]][0],
                desc[self.queryfields[2]][0],
                desc[self.queryfields[3]][0],
                desc[self.queryfields[4]][0],
                desc[self.queryfields[5]][0])

        for row in rows:
            print "%7s %20s %14s %14s %7s %s" % (
                    row[self.queryfields[0]],
                    row[self.queryfields[1]],
                    row[self.queryfields[2]],
                    row[self.queryfields[3]],
                    row[self.queryfields[4]],
                    row[self.queryfields[5]])


    def query_siem(self):
        """Query SQL database for log events"""
        

        query = SiemQuery(server = self.server, user = self.user,
                password = self.password, database = self.database)

        print(self.tables)
        
        qstatement, desc, rows = query.query(tables = self.tables,
                last = self.args.last, daterange = self.args.range,
                sourcehosts = self.args.shosts,
                sourceports = self.args.sports,
                desthosts = self.args.dhosts,
                destports = self.args.dports,
                processes = self.args.processes,
                pids = self.args.pids,
                protocols = self.args.protocols,
                greps = self.args.greps,
                rsourcehosts = self.args.rshosts,
                rsourceports = self.args.rsports,
                rdesthosts = self.args.rdhosts,
                rdestports = self.args.rdports,
                rprocesses = self.args.rprocesses,
                rpids = self.args.rpids,
                rprotocols = self.args.rprotocols,
                rgreps = self.args.rgreps)


        if self.args.verbose: print(qstatement)

        print("%7s %20s %14s %14s %7s %s" % (
                desc[self.queryfields[0]][0],
                desc[self.queryfields[1]][0],
                desc[self.queryfields[2]][0],
                desc[self.queryfields[3]][0],
                desc[self.queryfields[4]][0],
                desc[self.queryfields[5]][0]))

        for row in rows:
            print("%7s %20s %14s %14s %7s %s" % (
                    row[self.queryfields[0]],
                    row[self.queryfields[1]],
                    row[self.queryfields[2]],
                    row[self.queryfields[3]],
                    row[self.queryfields[4]],
                    row[self.queryfields[5]]))



    def run_query(self):
        try:
            self.get_args()
            self.get_config()
            self.query_siem()

        except KeyboardInterrupt:
            pass
        # except Exception as err:
        #     print('Error: ' + str(err))

    
    
def main():
    query = QueryCore()
    query.run_query()


if __name__ == "__main__":
    query = QueryCore()
    query.run_query()