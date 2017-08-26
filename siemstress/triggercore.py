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
import siemstress.trigger
import threading
import os
from sys import exit
from argparse import ArgumentParser
import ConfigParser
import json
import MySQLdb as mdb
import signal


class SiemTriggerCore:

    def __init__(self):
        """Initialize trigger engine"""

        self.args = None
        self.arg_parser = ArgumentParser()

        self.server = None
        self.user = None
        self.password = None
        self.database = None
        self.rules = {}
        self.threads = []

        signal.signal(signal.SIGTERM, self.sigterm_handler)


    def sigterm_handler(self, signal, frame):
        """Exit cleanly on sigterm"""
        self.stop_threads()
        exit(0)



    def get_args(self):
        """Set argument options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = '/etc/siemstress/siemstress.conf',
                help = ('set the config file'))
        self.arg_parser.add_argument('--table',
                action = 'append', dest = 'tables',
                metavar = 'TABLE',
                help = ('set a rule table'))
        self.arg_parser.add_argument('--oneshot',
                action = 'store_true',
                help = ('check database once and exit'))
        self.arg_parser.add_argument('--import',
                action = 'store', dest = 'importfile',
                metavar = 'FILE',
                help = ('set a JSON file to import rules'))
        self.arg_parser.add_argument('--export',
                action = 'store', dest = 'exportfile',
                metavar = 'FILE',
                help = ('set a JSON file to export rules'))

        self.args = self.arg_parser.parse_args()



    def get_config(self):
        """Read the config file"""

        config = ConfigParser.ConfigParser()
        if os.path.isfile(self.args.config):
            myconf = self.args.config
        else: myconf = 'config/siemstress.conf'
        config.read(myconf)

        # Read /etc/triggers.d/*.conf in a for loop

        self.server = config.get('siemstress', 'server')
        self.user = config.get('siemstress', 'user')
        self.password = config.get('siemstress', 'password')
        self.database = config.get('siemstress', 'database')


        
    def get_rules(self):
        """Get rules from tables"""

        self.rules = []
        for table in self.args.tables:
            con = mdb.connect(self.server, self.user,
                    self.password, self.database)
            with con:
                cur = con.cursor(mdb.cursors.DictCursor)
                cur.execute('SELECT * FROM ' + table)
                rules = cur.fetchall()
                cur.close()
            con.close()
            self.rules = self.rules + list(rules)



    def import_rules(self):
        """Import rules from a JSON file"""
        
        with open(self.args.importfile, 'r') as f:
            rules = json.loads(f.read())

        # Create table if it doesn't exist:
        con = mdb.connect(self.server, self.user, self.password,
                self.database)
        with con:
            cur = con.cursor()
            for table in rules:
                cur.execute('CREATE TABLE IF NOT EXISTS ' + \
                        table + \
                        '(Id INT PRIMARY KEY AUTO_INCREMENT, ' + \
                        'RuleName NVARCHAR(25), ' + \
                        'IsEnabled BOOLEAN, Severity TINYINT, ' + \
                        'TimeInt INT, EventLimit INT, ' + \
                        'SQLQuery NVARCHAR(1000), ' + \
                        'SourceTable NVARCHAR(25), ' + \
                        'OutTable NVARCHAR(25), ' + \
                        'Message NVARCHAR(1000))')
            cur.close()
        con.close()
        
        con = mdb.connect(self.server, self.user, self.password,
                self.database)
        with con:
            cur = con.cursor()
            for table in rules:
                # Set up SQL insert statement:
                insertstatement = 'INSERT INTO ' + table + \
                        '(RuleName, IsEnabled, Severity, ' + \
                        'TimeInt, EventLimit, SQLQuery, ' + \
                        'SourceTable, OutTable, Message) VALUES ' + \
                        '(%s, %s, %s, %s, %s, %s, %s, %s, %s)'


                for rule in rules[table]:
                    cur.execute(insertstatement, (rule['RuleName'],
                        rule['IsEnabled'], rule['Severity'],
                        rule['TimeInt'], rule['EventLimit'], 
                        rule['SQLQuery'], rule['SourceTable'],
                        rule['OutTable'], rule['Message']))
            cur.close()
        con.close()


    def export_rules(self):
        """Export rules from a table into a JSON file"""

        rules = {}
        con = mdb.connect(self.server, self.user, self.password,
                self.database)
        with con:
            cur = con.cursor(mdb.cursors.DictCursor)
            for table in self.args.tables:
                cur.execute('SELECT * FROM ' + table)
                rules[table] = cur.fetchall()
            cur.close()
        con.close()

        with open(self.args.exportfile, 'w') as f:
            f.write(json.dumps(rules, indent=2, sort_keys=True,
                separators=(',', ': ')) + '\n')



    def stop_threads(self):
        for thread in self.threads:
            thread.stop()


    def start_triggers(self):
        """Start siemstress event triggers"""

        # Start one thread per rule:
        self.threads = []
        for r in self.rules:
            if r['IsEnabled'] == 1:
                thread = StoppableThread(name=r,
                        target=siemstress.trigger.start_rule,
                        args=(self.server, self.user, self.password,
                        self.database, r, self.args.oneshot))
                thread.start()

            self.threads.append(thread)


    def run_triggers(self):
        """Start trigger engine"""
        try:
            self.get_args()
            self.get_config()
            if self.args.importfile:
                self.import_rules()
                exit(0)
            self.get_rules()
            if self.args.exportfile:
                self.export_rules()
                exit(0)
            self.start_triggers()

        except KeyboardInterrupt:
            self.stop_threads()
            exit(0)
        except Exception as err:
            self.stop_threads()
            exit(0)
            print('Error: ' + str(err))

    
class StoppableThread(threading.Thread):
    def __init__(self, args):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def main():
    parser = SiemTrigger()
    parser.run_triggers()


if __name__ == "__main__":
    parser = SiemTrigger()
    parser.run_triggers()
