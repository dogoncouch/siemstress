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
import os
import MySQLdb as mdb
from argparse import ArgumentParser
import ConfigParser


class SiemQueryCore:

    def __init__(self):
        """Initialize SiemQuery"""

        self.arg_parser = ArgumentParser()
        self.args = None
        self.config = None

        self.server = None
        self.database = None
        self.user = None
        self.password = None
        self.table = None
        # To Do: finish, import modules, etc

    def get_args(self):
        """Set config options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
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
            myconf = (config)
        else: myconf = 'config/siemstress.conf'
        config.read(myconf)

        self.server = config.get('siemstress', 'server')
        self.user = config.get('siemstress', 'user')
        self.password = config.get('siemstress', 'password')
        self.database = config.get('siemstress', 'database')
        self.table = config.get(self.args.section, 'table')
        # self.parser = config.get(self.args.section, 'parser')



    def run_query(self):
        """Query SQL database for log events"""
        
        con = mdb.connect(self.server, self.user, self.password,
                self.database);
        
        with con: 
        
            cur = con.cursor()
            cur.execute("SELECT * FROM " + self.table)

            rows = cur.fetchall()
    
            desc = cur.description

            print "%4s %20s %10s %10s %10s %s" % (desc[0][0], desc[1][0],
                    desc[11][0], desc[15][0], desc[16][0], desc[18][0])

            for row in rows:
                print "%4s %20s %10s %10s %10s %s" % (row[0], row[1],
                        row[11], row[15], row[16], row[18])

    def run_job(self):
        """Run the siemquery job"""

        self.get_args()
        self.get_config()
        self.run_query()


def main():
    query = SiemQueryCore()
    query.run_job()


if __name__ ==  "__main__":
    query = SiemQueryCore()
    query.run_job()
